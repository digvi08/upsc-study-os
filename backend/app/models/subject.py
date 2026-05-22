"""Subject and Topic models."""
from sqlalchemy import Column, String, Text, Integer, Boolean, ForeignKey, Float, Enum, JSON
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import enum
from .base import BaseModel


class SubjectCategory(str, enum.Enum):
    GS1 = "gs1"
    GS2 = "gs2"
    GS3 = "gs3"
    GS4 = "gs4"
    CSAT = "csat"
    OPTIONAL = "optional"
    CURRENT_AFFAIRS = "current_affairs"


class TopicStatus(str, enum.Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    NEEDS_REVISION = "needs_revision"


class Subject(BaseModel):
    __tablename__ = "subjects"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(Enum(SubjectCategory), nullable=False)
    color = Column(String(7), default="#6366f1", nullable=False)  # Hex color
    icon = Column(String(50), nullable=True)
    order_index = Column(Integer, default=0, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    # Progress tracking
    total_topics = Column(Integer, default=0, nullable=False)
    completed_topics = Column(Integer, default=0, nullable=False)
    completion_percentage = Column(Float, default=0.0, nullable=False)

    # Relationships
    user = relationship("User", back_populates="subjects")
    topics = relationship("Topic", back_populates="subject", lazy="dynamic", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Subject {self.name}>"


class Topic(BaseModel):
    __tablename__ = "topics"

    subject_id = Column(UUID(as_uuid=True), ForeignKey("subjects.id", ondelete="CASCADE"), nullable=False, index=True)
    parent_id = Column(UUID(as_uuid=True), ForeignKey("topics.id", ondelete="SET NULL"), nullable=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(Enum(TopicStatus), default=TopicStatus.NOT_STARTED, nullable=False)

    # Importance and priority
    importance_score = Column(Integer, default=5, nullable=False)  # 1-10
    priority = Column(String(20), default="medium", nullable=False)  # low, medium, high, critical
    tags = Column(JSON, default=list, nullable=False)

    # Study tracking
    study_time_minutes = Column(Integer, default=0, nullable=False)
    revision_count = Column(Integer, default=0, nullable=False)
    last_studied_at = Column(String(50), nullable=True)
    confidence_level = Column(Integer, default=0, nullable=False)  # 0-100

    # PYQ linkage
    pyq_frequency = Column(Integer, default=0, nullable=False)
    last_asked_year = Column(Integer, nullable=True)

    # AI metadata
    ai_summary = Column(Text, nullable=True)
    key_concepts = Column(JSONB, default=[], nullable=False)
    embedding_id = Column(String(255), nullable=True)  # Vector DB reference

    # Relationships
    subject = relationship("Subject", back_populates="topics")
    parent = relationship("Topic", remote_side="Topic.id", backref="subtopics")
    notes = relationship("Note", back_populates="topic", lazy="dynamic")
    revision_history = relationship("RevisionHistory", back_populates="topic", lazy="dynamic")

    def __repr__(self):
        return f"<Topic {self.name}>"
