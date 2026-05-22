"""Analytics service."""
from datetime import date, timedelta
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.analytics import UserAnalytics, DailyStudyLog
from app.models.subject import Subject, Topic, TopicStatus
from app.models.user import User


class AnalyticsService:
    def __init__(self, db: Session):
        self.db = db

    def get_overview(self, user: User) -> Dict[str, Any]:
        analytics = (
            self.db.query(UserAnalytics)
            .filter(UserAnalytics.user_id == user.id)
            .first()
        )

        subjects = (
            self.db.query(Subject)
            .filter(
                Subject.user_id == user.id,
                Subject.is_deleted == False,
                Subject.is_active == True,
            )
            .all()
        )

        subject_data = []
        for subject in subjects:
            total = (
                self.db.query(func.count(Topic.id))
                .filter(Topic.subject_id == subject.id, Topic.is_deleted == False)
                .scalar()
            )
            completed = (
                self.db.query(func.count(Topic.id))
                .filter(
                    Topic.subject_id == subject.id,
                    Topic.status == TopicStatus.COMPLETED,
                    Topic.is_deleted == False,
                )
                .scalar()
            )
            subject_data.append({
                "name": subject.name,
                "category": subject.category.value,
                "color": subject.color,
                "total_topics": total,
                "completed_topics": completed,
                "completion_percentage": round(completed / total * 100, 1) if total > 0 else 0,
            })

        return {
            "overview": {
                "total_study_hours": analytics.total_study_hours if analytics else 0,
                "total_topics_completed": analytics.total_topics_completed if analytics else 0,
                "total_revisions": analytics.total_revisions if analytics else 0,
                "total_notes": analytics.total_notes_created if analytics else 0,
                "total_pyqs_attempted": analytics.total_pyqs_attempted if analytics else 0,
                "total_answers_evaluated": analytics.total_answers_evaluated if analytics else 0,
                "total_ai_queries": analytics.total_ai_queries if analytics else 0,
                "current_streak": user.current_streak,
                "longest_streak": user.longest_streak,
            },
            "subjects": subject_data,
            "weak_subjects": analytics.weak_subjects if analytics else [],
            "strong_subjects": analytics.strong_subjects if analytics else [],
        }

    def get_heatmap(self, user: User, days: int = 365) -> Dict[str, Any]:
        start_date = date.today() - timedelta(days=days)
        logs = (
            self.db.query(DailyStudyLog)
            .filter(
                DailyStudyLog.user_id == user.id,
                DailyStudyLog.date >= start_date,
            )
            .all()
        )
        heatmap = {str(log.date): log.study_hours for log in logs}
        return {
            "heatmap": heatmap,
            "start_date": str(start_date),
            "end_date": str(date.today()),
        }

    def get_weekly_report(self, user: User) -> Dict[str, Any]:
        today = date.today()
        week_start = today - timedelta(days=today.weekday())
        week_end = week_start + timedelta(days=6)

        logs = (
            self.db.query(DailyStudyLog)
            .filter(
                DailyStudyLog.user_id == user.id,
                DailyStudyLog.date >= week_start,
                DailyStudyLog.date <= week_end,
            )
            .order_by(DailyStudyLog.date)
            .all()
        )

        daily_data = []
        for i in range(7):
            day = week_start + timedelta(days=i)
            log = next((l for l in logs if l.date == day), None)
            daily_data.append({
                "date": str(day),
                "day": day.strftime("%A"),
                "study_hours": log.study_hours if log else 0,
                "topics_studied": log.topics_studied if log else 0,
                "revisions_done": log.revisions_done if log else 0,
                "notes_created": log.notes_created if log else 0,
                "tasks_completed": log.tasks_completed if log else 0,
                "productivity_score": log.productivity_score if log else 0,
                "mood": log.mood if log else None,
            })

        total_hours = sum(d["study_hours"] for d in daily_data)
        return {
            "week_start": str(week_start),
            "week_end": str(week_end),
            "daily_data": daily_data,
            "total_hours": round(total_hours, 1),
            "average_hours": round(total_hours / 7, 1),
            "best_day": max(daily_data, key=lambda d: d["study_hours"])["day"] if daily_data else None,
        }

    def log_study_session(
        self,
        user: User,
        study_hours: float,
        topics_studied: int = 0,
        revisions_done: int = 0,
        notes_created: int = 0,
        pyqs_attempted: int = 0,
        tasks_completed: int = 0,
        tasks_total: int = 0,
        mood: str = None,
    ) -> Dict[str, Any]:
        today = date.today()
        log = (
            self.db.query(DailyStudyLog)
            .filter(DailyStudyLog.user_id == user.id, DailyStudyLog.date == today)
            .first()
        )

        if log:
            log.study_hours += study_hours
            log.topics_studied += topics_studied
            log.revisions_done += revisions_done
            log.notes_created += notes_created
            log.pyqs_attempted += pyqs_attempted
            log.tasks_completed += tasks_completed
            log.tasks_total += tasks_total
            if mood:
                log.mood = mood
        else:
            log = DailyStudyLog(
                user_id=user.id,
                date=today,
                study_hours=study_hours,
                topics_studied=topics_studied,
                revisions_done=revisions_done,
                notes_created=notes_created,
                pyqs_attempted=pyqs_attempted,
                tasks_completed=tasks_completed,
                tasks_total=tasks_total,
                mood=mood,
            )
            self.db.add(log)

        # Compute productivity score (0-100)
        score = min(study_hours / 8 * 40, 40)  # up to 40 pts for hours
        score += min(topics_studied * 5, 30)    # up to 30 pts for topics
        score += min(revisions_done * 5, 20)    # up to 20 pts for revisions
        score += 10 if mood in ("great", "good") else 0
        log.productivity_score = round(min(score, 100), 1)

        # Update streak
        yesterday = today - timedelta(days=1)
        yesterday_log = (
            self.db.query(DailyStudyLog)
            .filter(DailyStudyLog.user_id == user.id, DailyStudyLog.date == yesterday)
            .first()
        )
        if yesterday_log and yesterday_log.study_hours > 0:
            user.current_streak += 1
            if user.current_streak > user.longest_streak:
                user.longest_streak = user.current_streak
        elif not yesterday_log:
            user.current_streak = 1

        # Update global analytics
        analytics = (
            self.db.query(UserAnalytics)
            .filter(UserAnalytics.user_id == user.id)
            .first()
        )
        if analytics:
            analytics.total_study_hours += study_hours
            analytics.total_topics_completed += topics_studied
            analytics.total_revisions += revisions_done
            analytics.total_notes_created += notes_created
            analytics.last_active_date = today
            analytics.current_streak = user.current_streak
            analytics.longest_streak = user.longest_streak

        self.db.commit()
        return {
            "message": "Study session logged",
            "date": str(today),
            "productivity_score": log.productivity_score,
            "current_streak": user.current_streak,
        }

    def get_subject_performance(self, user: User) -> List[Dict[str, Any]]:
        """Detailed subject-wise performance breakdown."""
        subjects = (
            self.db.query(Subject)
            .filter(Subject.user_id == user.id, Subject.is_deleted == False)
            .all()
        )
        result = []
        for subject in subjects:
            topics = (
                self.db.query(Topic)
                .filter(Topic.subject_id == subject.id, Topic.is_deleted == False)
                .all()
            )
            if not topics:
                continue
            avg_confidence = (
                sum(t.confidence_level for t in topics) / len(topics) if topics else 0
            )
            result.append({
                "subject_id": str(subject.id),
                "name": subject.name,
                "category": subject.category.value,
                "color": subject.color,
                "total_topics": len(topics),
                "completed": sum(1 for t in topics if t.status == TopicStatus.COMPLETED),
                "in_progress": sum(1 for t in topics if t.status == "in_progress"),
                "not_started": sum(1 for t in topics if t.status == "not_started"),
                "avg_confidence": round(avg_confidence, 1),
                "total_study_time_hours": round(
                    sum(t.study_time_minutes for t in topics) / 60, 1
                ),
                "total_revisions": sum(t.revision_count for t in topics),
            })
        return sorted(result, key=lambda x: x["avg_confidence"])
