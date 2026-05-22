"""Answer Evaluation model."""
from sqlalchemy import Column, String, Text, Integer, Boolean, ForeignKey, Float, Enum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import enum
from .base import BaseModel


class EvaluationStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class AnswerEvaluation(BaseModel):
    __tablename__ = "answer_evaluations"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    topic_id = Column(UUID(as_uuid=True), ForeignKey("topics.id", ondelete="SET NULL"), nullable=True)

    question = Column(Text, nullable=False)
    answer_text = Column(Text, nullable=True)  # Typed answer
    answer_image_url = Column(Text, nullable=True)  # Handwritten answer image
    ocr_extracted_text = Column(Text, nullable=True)  # OCR result

    # Evaluation results
    status = Column(Enum(EvaluationStatus), default=EvaluationStatus.PENDING, nullable=False)
    total_marks = Column(Integer, nullable=True)
    obtained_marks = Column(Float, nullable=True)
    percentage = Column(Float, nullable=True)

    # Detailed scoring
    structure_score = Column(Float, nullable=True)
    content_score = Column(Float, nullable=True)
    keyword_score = Column(Float, nullable=True)
    analytical_score = Column(Float, nullable=True)
    grammar_score = Column(Float, nullable=True)
    examples_score = Column(Float, nullable=True)

    # AI feedback
    overall_feedback = Column(Text, nullable=True)
    strengths = Column(JSONB, default=[], nullable=False)
    improvements = Column(JSONB, default=[], nullable=False)
    suggested_answer = Column(Text, nullable=True)
    detailed_feedback = Column(JSONB, nullable=True)

    # Metadata
    word_count = Column(Integer, nullable=True)
    time_taken_minutes = Column(Integer, nullable=True)
    exam_type = Column(String(50), nullable=True)  # prelims, mains

    # Relationships
    user = relationship("User", back_populates="answer_evaluations")

    def __repr__(self):
        return f"<AnswerEvaluation {self.id}>"
