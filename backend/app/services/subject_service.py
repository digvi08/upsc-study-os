"""Subject and Topic service."""
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import HTTPException, status
import uuid

from app.models.subject import Subject, Topic, TopicStatus
from app.models.user import User
from app.schemas.subject import SubjectCreate, SubjectUpdate, TopicCreate, TopicUpdate


class SubjectService:
    def __init__(self, db: Session):
        self.db = db

    # ── Subjects ──────────────────────────────────────────────────────────────

    def create_subject(self, user: User, data: SubjectCreate) -> Subject:
        subject = Subject(user_id=user.id, **data.model_dump())
        self.db.add(subject)
        self.db.commit()
        self.db.refresh(subject)
        return subject

    def get_subjects(self, user: User, include_inactive: bool = False) -> List[Subject]:
        query = self.db.query(Subject).filter(
            Subject.user_id == user.id,
            Subject.is_deleted == False,
        )
        if not include_inactive:
            query = query.filter(Subject.is_active == True)
        return query.order_by(Subject.order_index, Subject.name).all()

    def get_subject(self, user: User, subject_id: uuid.UUID) -> Subject:
        subject = self.db.query(Subject).filter(
            Subject.id == subject_id,
            Subject.user_id == user.id,
            Subject.is_deleted == False,
        ).first()
        if not subject:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subject not found")
        return subject

    def update_subject(self, user: User, subject_id: uuid.UUID, data: SubjectUpdate) -> Subject:
        subject = self.get_subject(user, subject_id)
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(subject, field, value)
        self.db.commit()
        self.db.refresh(subject)
        return subject

    def delete_subject(self, user: User, subject_id: uuid.UUID) -> None:
        subject = self.get_subject(user, subject_id)
        subject.is_deleted = True
        self.db.commit()

    def _update_subject_progress(self, subject_id: uuid.UUID) -> None:
        """Recalculate subject completion percentage."""
        total = self.db.query(func.count(Topic.id)).filter(
            Topic.subject_id == subject_id,
            Topic.is_deleted == False,
        ).scalar()

        completed = self.db.query(func.count(Topic.id)).filter(
            Topic.subject_id == subject_id,
            Topic.status == TopicStatus.COMPLETED,
            Topic.is_deleted == False,
        ).scalar()

        subject = self.db.query(Subject).filter(Subject.id == subject_id).first()
        if subject:
            subject.total_topics = total
            subject.completed_topics = completed
            subject.completion_percentage = (completed / total * 100) if total > 0 else 0.0
            self.db.commit()

    # ── Topics ────────────────────────────────────────────────────────────────

    def create_topic(self, user: User, data: TopicCreate) -> Topic:
        # Verify subject belongs to user
        self.get_subject(user, data.subject_id)

        topic = Topic(**data.model_dump())
        self.db.add(topic)
        self.db.commit()
        self._update_subject_progress(data.subject_id)
        self.db.refresh(topic)
        return topic

    def get_topics(
        self,
        user: User,
        subject_id: uuid.UUID,
        status: Optional[str] = None,
        search: Optional[str] = None,
    ) -> List[Topic]:
        self.get_subject(user, subject_id)
        query = self.db.query(Topic).filter(
            Topic.subject_id == subject_id,
            Topic.is_deleted == False,
            Topic.parent_id == None,  # Root topics only
        )
        if status:
            query = query.filter(Topic.status == status)
        if search:
            query = query.filter(Topic.name.ilike(f"%{search}%"))
        return query.order_by(Topic.importance_score.desc(), Topic.name).all()

    def get_topic(self, user: User, topic_id: uuid.UUID) -> Topic:
        topic = self.db.query(Topic).filter(
            Topic.id == topic_id,
            Topic.is_deleted == False,
        ).first()
        if not topic:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Topic not found")
        # Verify ownership via subject
        self.get_subject(user, topic.subject_id)
        return topic

    def update_topic(self, user: User, topic_id: uuid.UUID, data: TopicUpdate) -> Topic:
        topic = self.get_topic(user, topic_id)
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(topic, field, value)
        self.db.commit()
        self._update_subject_progress(topic.subject_id)
        self.db.refresh(topic)
        return topic

    def delete_topic(self, user: User, topic_id: uuid.UUID) -> None:
        topic = self.get_topic(user, topic_id)
        subject_id = topic.subject_id
        topic.is_deleted = True
        self.db.commit()
        self._update_subject_progress(subject_id)

    def get_topic_tree(self, user: User, subject_id: uuid.UUID) -> List[Topic]:
        """Get all topics with their subtopics as a tree."""
        self.get_subject(user, subject_id)
        return self.db.query(Topic).filter(
            Topic.subject_id == subject_id,
            Topic.is_deleted == False,
        ).order_by(Topic.importance_score.desc()).all()
