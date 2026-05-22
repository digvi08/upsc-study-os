"""User model."""
from sqlalchemy import Column, String, Boolean, Integer, Text, Enum
from sqlalchemy.orm import relationship
import enum
from .base import BaseModel


class UserRole(str, enum.Enum):
    STUDENT = "student"
    ADMIN = "admin"
    MODERATOR = "moderator"


class ExamTarget(str, enum.Enum):
    UPSC = "upsc"
    MPSC = "mpsc"
    BOTH = "both"


class User(BaseModel):
    __tablename__ = "users"

    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    full_name = Column(String(255), nullable=False)
    hashed_password = Column(String(255), nullable=True)  # Null for OAuth users
    profile_picture = Column(Text, nullable=True)
    bio = Column(Text, nullable=True)

    # Auth
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    role = Column(Enum(UserRole), default=UserRole.STUDENT, nullable=False)

    # OAuth
    google_id = Column(String(255), unique=True, nullable=True, index=True)
    oauth_provider = Column(String(50), nullable=True)

    # Study preferences
    exam_target = Column(Enum(ExamTarget), default=ExamTarget.UPSC, nullable=False)
    daily_study_hours = Column(Integer, default=8, nullable=False)
    exam_year = Column(Integer, nullable=True)
    current_streak = Column(Integer, default=0, nullable=False)
    longest_streak = Column(Integer, default=0, nullable=False)
    total_study_hours = Column(Integer, default=0, nullable=False)

    # Password reset
    reset_token = Column(String(255), nullable=True)
    reset_token_expires = Column(String(255), nullable=True)

    # Relationships
    subjects = relationship("Subject", back_populates="user", lazy="dynamic")
    notes = relationship("Note", back_populates="user", lazy="dynamic")
    study_plans = relationship("StudyPlan", back_populates="user", lazy="dynamic")
    revision_history = relationship("RevisionHistory", back_populates="user", lazy="dynamic")
    answer_evaluations = relationship("AnswerEvaluation", back_populates="user", lazy="dynamic")
    analytics = relationship("UserAnalytics", back_populates="user", uselist=False)

    def __repr__(self):
        return f"<User {self.email}>"
