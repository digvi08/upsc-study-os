"""Analytics routes."""
from fastapi import APIRouter, Depends, Query, Body
from sqlalchemy.orm import Session
from typing import Optional, List

from app.database import get_db
from app.auth.dependencies import get_current_user
from app.models.user import User
from app.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/overview")
async def get_analytics_overview(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Comprehensive analytics overview."""
    service = AnalyticsService(db)
    return service.get_overview(current_user)


@router.get("/heatmap")
async def get_study_heatmap(
    days: int = Query(default=365, ge=30, le=365),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Study activity heatmap data."""
    service = AnalyticsService(db)
    return service.get_heatmap(current_user, days)


@router.get("/weekly-report")
async def get_weekly_report(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Weekly study report."""
    service = AnalyticsService(db)
    return service.get_weekly_report(current_user)


@router.get("/subject-performance")
async def get_subject_performance(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Detailed subject-wise performance."""
    service = AnalyticsService(db)
    return service.get_subject_performance(current_user)


@router.post("/log-study")
async def log_study_session(
    study_hours: float = Body(...),
    topics_studied: int = Body(default=0),
    revisions_done: int = Body(default=0),
    notes_created: int = Body(default=0),
    pyqs_attempted: int = Body(default=0),
    tasks_completed: int = Body(default=0),
    tasks_total: int = Body(default=0),
    mood: Optional[str] = Body(default=None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Log a study session."""
    service = AnalyticsService(db)
    return service.log_study_session(
        current_user,
        study_hours=study_hours,
        topics_studied=topics_studied,
        revisions_done=revisions_done,
        notes_created=notes_created,
        pyqs_attempted=pyqs_attempted,
        tasks_completed=tasks_completed,
        tasks_total=tasks_total,
        mood=mood,
    )
