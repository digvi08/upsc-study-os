"""Revision system models."""
from sqlalchemy import Column, String, Text, Integer, Boolean, ForeignKey, Float, DateTime, Enum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import enum
from datetime import datetime
from .base import BaseModel


class RevisionStatus(str, enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    SKIPPED = "skipped"
    OVERDUE = "overdue"


class RevisionHistory(BaseModel):
    __tablename__ = "revision_history"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    topic_id = Column(UUID(as_uuid=True), ForeignKey("topics.id", ondelete="CASCADE"), nullable=False, index=True)

    revision_number = Column(Integer, nullable=False)  # 1st, 2nd, 3rd revision
    scheduled_date = Column(DateTime, nullable=False)
    completed_date = Column(DateTime, nullable=True)
    status = Column(Enum(RevisionStatus), default=RevisionStatus.PENDING, nullable=False)

    # Performance
    confidence_before = Column(Integer, default=0, nullable=False)  # 0-100
    confidence_after = Column(Integer, nullable=True)  # 0-100
    time_spent_minutes = Column(Integer, default=0, nullable=False)
    notes = Column(Text, nullable=True)

    # Spaced repetition
    ease_factor = Column(Float, default=2.5, nullable=False)  # SM-2 algorithm
    interval_days = Column(Integer, default=1, nullable=False)
    next_review_date = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User", back_populates="revision_history")
    topic = relationship("Topic", back_populates="revision_history")

    def __repr__(self):
        return f"<RevisionHistory topic={self.topic_id} rev={self.revision_number}>"
