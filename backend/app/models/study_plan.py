"""Study Plan model."""
from sqlalchemy import Column, String, Text, Integer, Boolean, ForeignKey, Float, DateTime, Enum, Date
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import enum
from .base import BaseModel


class PlanStatus(str, enum.Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    PAUSED = "paused"
    ABANDONED = "abandoned"


class TaskStatus(str, enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    SKIPPED = "skipped"
    RESCHEDULED = "rescheduled"


class StudyPlan(BaseModel):
    __tablename__ = "study_plans"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(Enum(PlanStatus), default=PlanStatus.ACTIVE, nullable=False)

    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    exam_date = Column(Date, nullable=True)

    daily_hours = Column(Float, default=8.0, nullable=False)
    ai_generated = Column(Boolean, default=False, nullable=False)
    plan_data = Column(JSONB, nullable=True)  # Full AI-generated plan

    # Relationships
    user = relationship("User", back_populates="study_plans")
    tasks = relationship("StudyTask", back_populates="plan", lazy="dynamic", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<StudyPlan {self.title}>"


class StudyTask(BaseModel):
    __tablename__ = "study_tasks"

    plan_id = Column(UUID(as_uuid=True), ForeignKey("study_plans.id", ondelete="CASCADE"), nullable=False, index=True)
    topic_id = Column(UUID(as_uuid=True), ForeignKey("topics.id", ondelete="SET NULL"), nullable=True)
    subject_id = Column(UUID(as_uuid=True), ForeignKey("subjects.id", ondelete="SET NULL"), nullable=True)

    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    task_type = Column(String(50), default="study", nullable=False)  # study, revision, mock, break
    status = Column(Enum(TaskStatus), default=TaskStatus.PENDING, nullable=False)

    scheduled_date = Column(Date, nullable=False)
    scheduled_time = Column(String(10), nullable=True)  # HH:MM
    duration_minutes = Column(Integer, default=60, nullable=False)
    actual_duration_minutes = Column(Integer, nullable=True)

    priority = Column(String(20), default="medium", nullable=False)
    order_index = Column(Integer, default=0, nullable=False)
    notes = Column(Text, nullable=True)

    # Relationships
    plan = relationship("StudyPlan", back_populates="tasks")

    def __repr__(self):
        return f"<StudyTask {self.title}>"
