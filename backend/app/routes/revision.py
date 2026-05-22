"""Revision system routes."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional, List
import uuid

from app.database import get_db
from app.auth.dependencies import get_current_user
from app.models.user import User
from app.services.revision_service import RevisionService
from app.schemas.common import MessageResponse

router = APIRouter(prefix="/revision", tags=["Revision System"])


@router.post("/schedule/{topic_id}", response_model=dict)
async def schedule_revision(
    topic_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Schedule spaced-repetition revisions for a topic (5 sessions)."""
    service = RevisionService(db)
    scheduled = service.schedule_topic(current_user, topic_id)
    return {"topic_id": str(topic_id), "scheduled_revisions": scheduled}


@router.get("/pending", response_model=List[dict])
async def get_pending_revisions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get all pending and overdue revisions."""
    service = RevisionService(db)
    return service.get_pending(current_user)


@router.get("/calendar", response_model=List[dict])
async def get_revision_calendar(
    days: int = Query(default=30, ge=7, le=90),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get upcoming revision calendar."""
    service = RevisionService(db)
    return service.get_upcoming(current_user, days)


@router.get("/stats", response_model=dict)
async def get_revision_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get revision statistics."""
    service = RevisionService(db)
    return service.get_stats(current_user)


@router.post("/{revision_id}/complete", response_model=dict)
async def complete_revision(
    revision_id: uuid.UUID,
    confidence_after: int = Query(default=70, ge=0, le=100),
    time_spent_minutes: int = Query(default=30, ge=1),
    notes: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Mark a revision as completed and schedule the next one."""
    service = RevisionService(db)
    return service.complete_revision(
        current_user, revision_id, confidence_after, time_spent_minutes, notes
    )


@router.post("/{revision_id}/skip", response_model=MessageResponse)
async def skip_revision(
    revision_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Skip a revision and reschedule to tomorrow."""
    service = RevisionService(db)
    result = service.skip_revision(current_user, revision_id)
    return MessageResponse(message=result["message"])
