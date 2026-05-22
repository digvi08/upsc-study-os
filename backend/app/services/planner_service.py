"""Study Planner service."""
from datetime import date, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
import uuid

from app.models.study_plan import StudyPlan, StudyTask, PlanStatus, TaskStatus
from app.models.user import User


class PlannerService:
    def __init__(self, db: Session):
        self.db = db

    # ── Plans ─────────────────────────────────────────────────────────────────

    def get_plans(self, user: User) -> List[StudyPlan]:
        return (
            self.db.query(StudyPlan)
            .filter(StudyPlan.user_id == user.id, StudyPlan.is_deleted == False)
            .order_by(StudyPlan.created_at.desc())
            .all()
        )

    def get_active_plan(self, user: User) -> Optional[StudyPlan]:
        return (
            self.db.query(StudyPlan)
            .filter(
                StudyPlan.user_id == user.id,
                StudyPlan.status == PlanStatus.ACTIVE,
                StudyPlan.is_deleted == False,
            )
            .first()
        )

    def create_plan(
        self,
        user: User,
        title: str,
        start_date: date,
        end_date: date,
        daily_hours: float,
        exam_date: Optional[date] = None,
        ai_generated: bool = False,
        plan_data: Optional[dict] = None,
    ) -> StudyPlan:
        plan = StudyPlan(
            user_id=user.id,
            title=title,
            start_date=start_date,
            end_date=end_date,
            daily_hours=daily_hours,
            exam_date=exam_date,
            ai_generated=ai_generated,
            plan_data=plan_data,
        )
        self.db.add(plan)
        self.db.commit()
        self.db.refresh(plan)
        return plan

    def save_ai_plan(
        self,
        user: User,
        plan_data: dict,
        daily_hours: float,
        exam_date: Optional[str] = None,
    ) -> StudyPlan:
        """Save an AI-generated plan and create tasks from it."""
        today = date.today()
        plan = self.create_plan(
            user=user,
            title=f"AI Study Plan — {today.strftime('%b %d, %Y')}",
            start_date=today,
            end_date=today + timedelta(days=90),
            daily_hours=daily_hours,
            exam_date=date.fromisoformat(exam_date) if exam_date else None,
            ai_generated=True,
            plan_data=plan_data,
        )

        # Create tasks from AI plan daily_schedule
        daily_schedule = plan_data.get("daily_schedule", [])
        day_map = {
            "Monday": 0, "Tuesday": 1, "Wednesday": 2, "Thursday": 3,
            "Friday": 4, "Saturday": 5, "Sunday": 6,
        }
        current_weekday = today.weekday()

        for day_entry in daily_schedule:
            day_name = day_entry.get("day", "")
            target_weekday = day_map.get(day_name, 0)
            days_ahead = (target_weekday - current_weekday) % 7
            task_date = today + timedelta(days=days_ahead)

            for idx, task in enumerate(day_entry.get("tasks", [])):
                study_task = StudyTask(
                    plan_id=plan.id,
                    title=f"{task.get('subject', '')} — {task.get('topic', '')}",
                    description=task.get("type", "study"),
                    task_type=task.get("type", "study"),
                    scheduled_date=task_date,
                    duration_minutes=int(task.get("hours", 1) * 60),
                    priority="medium",
                    order_index=idx,
                )
                self.db.add(study_task)

        self.db.commit()
        return plan

    # ── Tasks ─────────────────────────────────────────────────────────────────

    def get_today_tasks(self, user: User) -> List[Dict[str, Any]]:
        today = date.today()
        tasks = (
            self.db.query(StudyTask)
            .join(StudyPlan)
            .filter(
                StudyPlan.user_id == user.id,
                StudyTask.scheduled_date == today,
                StudyTask.is_deleted == False,
            )
            .order_by(StudyTask.order_index, StudyTask.priority)
            .all()
        )
        return [self._task_to_dict(t) for t in tasks]

    def get_weekly_tasks(self, user: User, week_start: Optional[date] = None) -> List[Dict[str, Any]]:
        if not week_start:
            today = date.today()
            week_start = today - timedelta(days=today.weekday())
        week_end = week_start + timedelta(days=6)

        tasks = (
            self.db.query(StudyTask)
            .join(StudyPlan)
            .filter(
                StudyPlan.user_id == user.id,
                StudyTask.scheduled_date >= week_start,
                StudyTask.scheduled_date <= week_end,
                StudyTask.is_deleted == False,
            )
            .order_by(StudyTask.scheduled_date, StudyTask.order_index)
            .all()
        )

        calendar: Dict[str, list] = {}
        for task in tasks:
            key = str(task.scheduled_date)
            if key not in calendar:
                calendar[key] = []
            calendar[key].append(self._task_to_dict(task))

        return [{"date": k, "tasks": v} for k, v in sorted(calendar.items())]

    def complete_task(
        self,
        user: User,
        task_id: uuid.UUID,
        actual_duration: Optional[int] = None,
    ) -> Dict[str, Any]:
        task = self._get_task(user, task_id)
        task.status = TaskStatus.COMPLETED
        if actual_duration:
            task.actual_duration_minutes = actual_duration

        # Log to analytics
        from app.models.analytics import DailyStudyLog
        today = date.today()
        log = self.db.query(DailyStudyLog).filter(
            DailyStudyLog.user_id == user.id,
            DailyStudyLog.date == today,
        ).first()
        if log:
            log.tasks_completed += 1
            if actual_duration:
                log.study_hours += actual_duration / 60
        else:
            log = DailyStudyLog(
                user_id=user.id,
                date=today,
                tasks_completed=1,
                study_hours=(actual_duration or 0) / 60,
            )
            self.db.add(log)

        self.db.commit()
        return {"message": "Task completed", "task": self._task_to_dict(task)}

    def skip_task(self, user: User, task_id: uuid.UUID) -> Dict[str, Any]:
        task = self._get_task(user, task_id)
        task.status = TaskStatus.RESCHEDULED
        task.scheduled_date = task.scheduled_date + timedelta(days=1)
        self.db.commit()
        return {"message": "Task rescheduled to tomorrow"}

    def add_task(
        self,
        user: User,
        plan_id: uuid.UUID,
        title: str,
        scheduled_date: date,
        duration_minutes: int = 60,
        task_type: str = "study",
        priority: str = "medium",
        description: Optional[str] = None,
        topic_id: Optional[uuid.UUID] = None,
        subject_id: Optional[uuid.UUID] = None,
    ) -> StudyTask:
        plan = self.db.query(StudyPlan).filter(
            StudyPlan.id == plan_id,
            StudyPlan.user_id == user.id,
        ).first()
        if not plan:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plan not found")

        task = StudyTask(
            plan_id=plan_id,
            title=title,
            description=description,
            task_type=task_type,
            scheduled_date=scheduled_date,
            duration_minutes=duration_minutes,
            priority=priority,
            topic_id=topic_id,
            subject_id=subject_id,
        )
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        return task

    def _get_task(self, user: User, task_id: uuid.UUID) -> StudyTask:
        task = (
            self.db.query(StudyTask)
            .join(StudyPlan)
            .filter(StudyTask.id == task_id, StudyPlan.user_id == user.id)
            .first()
        )
        if not task:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
        return task

    @staticmethod
    def _task_to_dict(task: StudyTask) -> Dict[str, Any]:
        return {
            "id": str(task.id),
            "title": task.title,
            "description": task.description,
            "task_type": task.task_type,
            "status": task.status.value,
            "scheduled_date": str(task.scheduled_date),
            "duration_minutes": task.duration_minutes,
            "actual_duration_minutes": task.actual_duration_minutes,
            "priority": task.priority,
            "subject_id": str(task.subject_id) if task.subject_id else None,
            "topic_id": str(task.topic_id) if task.topic_id else None,
        }
