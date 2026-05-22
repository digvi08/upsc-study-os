"""PYQ (Previous Year Questions) model."""
from sqlalchemy import Column, String, Text, Integer, Boolean, ForeignKey, Float, Enum, JSON
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import enum
from .base import BaseModel


class ExamType(str, enum.Enum):
    PRELIMS = "prelims"
    MAINS = "mains"
    INTERVIEW = "interview"


class QuestionType(str, enum.Enum):
    MCQ = "mcq"
    DESCRIPTIVE = "descriptive"
    ESSAY = "essay"
    CASE_STUDY = "case_study"


class PYQ(BaseModel):
    __tablename__ = "pyqs"

    year = Column(Integer, nullable=False, index=True)
    exam = Column(Enum(ExamType), nullable=False, index=True)
    exam_name = Column(String(100), default="UPSC", nullable=False)  # UPSC, MPSC, etc.
    paper = Column(String(50), nullable=True)  # GS1, GS2, GS3, GS4, CSAT
    subject = Column(String(255), nullable=False, index=True)
    topic = Column(String(255), nullable=False, index=True)
    subtopic = Column(String(255), nullable=True)

    question = Column(Text, nullable=False)
    question_type = Column(Enum(QuestionType), default=QuestionType.MCQ, nullable=False)

    # For MCQ
    options = Column(JSONB, nullable=True)  # {"a": "...", "b": "...", "c": "...", "d": "..."}
    correct_answer = Column(String(10), nullable=True)
    explanation = Column(Text, nullable=True)

    # For Mains
    word_limit = Column(Integer, nullable=True)
    marks = Column(Integer, nullable=True)
    model_answer = Column(Text, nullable=True)
    answer_structure = Column(JSONB, nullable=True)

    # Metadata
    keywords = Column(JSON, default=list, nullable=False)
    tags = Column(JSON, default=list, nullable=False)
    difficulty = Column(String(20), default="medium", nullable=False)
    source = Column(String(255), nullable=True)

    # AI analysis
    ai_analysis = Column(JSONB, nullable=True)
    trend_data = Column(JSONB, nullable=True)
    related_topics = Column(JSON, default=list, nullable=False)
    embedding_id = Column(String(255), nullable=True)

    # Admin
    is_verified = Column(Boolean, default=False, nullable=False)
    uploaded_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    def __repr__(self):
        return f"<PYQ {self.year} {self.exam} - {self.topic}>"
