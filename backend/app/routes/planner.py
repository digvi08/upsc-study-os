"""Daily Planner routes."""
from fastapi import APIRouter, Depends, Query, Body
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import date
import uuid

from app.database import get_db
from app.auth.dependencies import get_current_user
from app.models.user import User
from app.services.planner_service import PlannerService
from app.ai.mentor_service import MentorService
from app.schemas.common import MessageResponse

router = APIRouter(prefix="/planner", tags=["Daily Planner"])


@router.post("/generate", response_model=dict)
async def generate_ai_plan(
    subjects: List[str] = Body(default=["History", "Geography", "Polity", "Economy", "Environment"]),
    weak_areas: List[str] = Body(default=[]),
    available_hours: float = Body(default=8.0),
    exam_date: str = Body(default="2025-06-01"),
    completed_topics: Optional[List[str]] = Body(default=[]),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Generate an AI-powered study plan and save it."""
    mentor = MentorService()
    plan_data = await mentor.generate_study_plan(
        subjects=subjects,
        weak_areas=weak_areas,
        available_hours=available_hours,
        exam_date=exam_date,
        completed_topics=completed_topics or [],
    )
    service = PlannerService(db)
    plan = service.save_ai_plan(current_user, plan_data, available_hours, exam_date)
    return {"plan_id": str(plan.id), "plan": plan_data}


@router.get("/today", response_model=List[dict])
async def get_today_tasks(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get today's study tasks."""
    service = PlannerService(db)
    return service.get_today_tasks(current_user)


@router.get("/weekly", response_model=List[dict])
async def get_weekly_plan(
    week_start: Optional[date] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get weekly study plan."""
    service = PlannerService(db)
    return service.get_weekly_tasks(current_user, week_start)


@router.get("/plans", response_model=List[dict])
async def list_plans(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List all study plans."""
    service = PlannerService(db)
    plans = service.get_plans(current_user)
    return [
        {
            "id": str(p.id),
            "title": p.title,
            "status": p.status.value,
            "start_date": str(p.start_date),
            "end_date": str(p.end_date),
            "daily_hours": p.daily_hours,
            "ai_generated": p.ai_generated,
            "created_at": p.created_at.isoformat(),
        }
        for p in plans
    ]


@router.post("/tasks", response_model=dict, status_code=201)
async def add_task(
    plan_id: uuid.UUID,
    title: str,
    scheduled_date: date,
    duration_minutes: int = 60,
    task_type: str = "study",
    priority: str = "medium",
    description: Optional[str] = None,
    topic_id: Optional[uuid.UUID] = None,
    subject_id: Optional[uuid.UUID] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Add a manual task to a plan."""
    service = PlannerService(db)
    task = service.add_task(
        current_user, plan_id, title, scheduled_date,
        duration_minutes, task_type, priority, description, topic_id, subject_id,
    )
    return PlannerService._task_to_dict(task)


@router.post("/tasks/{task_id}/complete", response_model=dict)
async def complete_task(
    task_id: uuid.UUID,
    actual_duration: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Mark a task as completed."""
    service = PlannerService(db)
    return service.complete_task(current_user, task_id, actual_duration)


@router.post("/tasks/{task_id}/skip", response_model=MessageResponse)
async def skip_task(
    task_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Skip a task and reschedule to tomorrow."""
    service = PlannerService(db)
    result = service.skip_task(current_user, task_id)
    return MessageResponse(message=result["message"])
