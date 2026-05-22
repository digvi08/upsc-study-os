"""Subject and Topic routes."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional, List
import uuid

from app.database import get_db
from app.auth.dependencies import get_current_user
from app.models.user import User
from app.services.subject_service import SubjectService
from app.schemas.subject import (
    SubjectCreate, SubjectUpdate, SubjectResponse,
    TopicCreate, TopicUpdate, TopicResponse,
)
from app.schemas.common import MessageResponse

router = APIRouter(prefix="/subjects", tags=["Subjects & Topics"])


# ── Subjects ──────────────────────────────────────────────────────────────────

@router.post("", response_model=SubjectResponse, status_code=201)
async def create_subject(
    data: SubjectCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new subject."""
    service = SubjectService(db)
    return service.create_subject(current_user, data)


@router.get("", response_model=List[SubjectResponse])
async def list_subjects(
    include_inactive: bool = False,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List all subjects for the current user."""
    service = SubjectService(db)
    return service.get_subjects(current_user, include_inactive)


@router.get("/{subject_id}", response_model=SubjectResponse)
async def get_subject(
    subject_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get a specific subject."""
    service = SubjectService(db)
    return service.get_subject(current_user, subject_id)


@router.put("/{subject_id}", response_model=SubjectResponse)
async def update_subject(
    subject_id: uuid.UUID,
    data: SubjectUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update a subject."""
    service = SubjectService(db)
    return service.update_subject(current_user, subject_id, data)


@router.delete("/{subject_id}", response_model=MessageResponse)
async def delete_subject(
    subject_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a subject (soft delete)."""
    service = SubjectService(db)
    service.delete_subject(current_user, subject_id)
    return MessageResponse(message="Subject deleted successfully")


# ── Topics ────────────────────────────────────────────────────────────────────

@router.post("/{subject_id}/topics", response_model=TopicResponse, status_code=201)
async def create_topic(
    subject_id: uuid.UUID,
    data: TopicCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new topic under a subject."""
    data.subject_id = subject_id
    service = SubjectService(db)
    return service.create_topic(current_user, data)


@router.get("/{subject_id}/topics", response_model=List[TopicResponse])
async def list_topics(
    subject_id: uuid.UUID,
    status: Optional[str] = None,
    search: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List topics for a subject."""
    service = SubjectService(db)
    return service.get_topics(current_user, subject_id, status, search)


@router.get("/{subject_id}/topics/tree", response_model=List[TopicResponse])
async def get_topic_tree(
    subject_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get full topic tree for a subject."""
    service = SubjectService(db)
    return service.get_topic_tree(current_user, subject_id)


@router.put("/topics/{topic_id}", response_model=TopicResponse)
async def update_topic(
    topic_id: uuid.UUID,
    data: TopicUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update a topic."""
    service = SubjectService(db)
    return service.update_topic(current_user, topic_id, data)


@router.delete("/topics/{topic_id}", response_model=MessageResponse)
async def delete_topic(
    topic_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a topic (soft delete)."""
    service = SubjectService(db)
    service.delete_topic(current_user, topic_id)
    return MessageResponse(message="Topic deleted successfully")
