"""Analytics models."""
from sqlalchemy import Column, String, Integer, Boolean, ForeignKey, Float, Date, Enum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import enum
from .base import BaseModel


class UserAnalytics(BaseModel):
    __tablename__ = "user_analytics"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)

    # Overall stats
    total_study_hours = Column(Float, default=0.0, nullable=False)
    total_topics_completed = Column(Integer, default=0, nullable=False)
    total_revisions = Column(Integer, default=0, nullable=False)
    total_notes_created = Column(Integer, default=0, nullable=False)
    total_pyqs_attempted = Column(Integer, default=0, nullable=False)
    total_answers_evaluated = Column(Integer, default=0, nullable=False)
    total_ai_queries = Column(Integer, default=0, nullable=False)

    # Streaks
    current_streak = Column(Integer, default=0, nullable=False)
    longest_streak = Column(Integer, default=0, nullable=False)
    last_active_date = Column(Date, nullable=True)

    # Subject-wise performance
    subject_performance = Column(JSONB, default={}, nullable=False)
    weak_subjects = Column(JSONB, default=[], nullable=False)
    strong_subjects = Column(JSONB, default=[], nullable=False)

    # Weekly/Monthly data
    weekly_data = Column(JSONB, default=[], nullable=False)
    monthly_data = Column(JSONB, default=[], nullable=False)
    heatmap_data = Column(JSONB, default={}, nullable=False)  # date -> hours

    # Relationships
    user = relationship("User", back_populates="analytics")


class DailyStudyLog(BaseModel):
    __tablename__ = "daily_study_logs"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)

    study_hours = Column(Float, default=0.0, nullable=False)
    topics_studied = Column(Integer, default=0, nullable=False)
    revisions_done = Column(Integer, default=0, nullable=False)
    notes_created = Column(Integer, default=0, nullable=False)
    pyqs_attempted = Column(Integer, default=0, nullable=False)
    tasks_completed = Column(Integer, default=0, nullable=False)
    tasks_total = Column(Integer, default=0, nullable=False)

    productivity_score = Column(Float, default=0.0, nullable=False)  # 0-100
    mood = Column(String(20), nullable=True)  # great, good, okay, bad
    notes = Column(String(500), nullable=True)

    def __repr__(self):
        return f"<DailyStudyLog {self.user_id} {self.date}>"


class MockTest(BaseModel):
    __tablename__ = "mock_tests"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    exam_type = Column(String(50), nullable=False)  # prelims, mains
    subject = Column(String(255), nullable=True)

    total_questions = Column(Integer, nullable=False)
    attempted_questions = Column(Integer, default=0, nullable=False)
    correct_answers = Column(Integer, default=0, nullable=False)
    wrong_answers = Column(Integer, default=0, nullable=False)
    unattempted = Column(Integer, default=0, nullable=False)

    total_marks = Column(Float, nullable=False)
    obtained_marks = Column(Float, default=0.0, nullable=False)
    percentage = Column(Float, default=0.0, nullable=False)
    time_taken_minutes = Column(Integer, nullable=True)

    question_data = Column(JSONB, nullable=True)
    analysis = Column(JSONB, nullable=True)

    def __repr__(self):
        return f"<MockTest {self.title}>"
