"""PYQ schemas."""
from pydantic import BaseModel, Field
from typing import Optional, List, Any
from datetime import datetime
import uuid


class PYQCreate(BaseModel):
    year: int = Field(..., ge=1979, le=2030)
    exam: str
    exam_name: str = "UPSC"
    paper: Optional[str] = None
    subject: str
    topic: str
    subtopic: Optional[str] = None
    question: str
    question_type: str = "mcq"
    options: Optional[dict] = None
    correct_answer: Optional[str] = None
    explanation: Optional[str] = None
    word_limit: Optional[int] = None
    marks: Optional[int] = None
    model_answer: Optional[str] = None
    keywords: List[str] = []
    tags: List[str] = []
    difficulty: str = "medium"
    source: Optional[str] = None


class PYQResponse(BaseModel):
    id: uuid.UUID
    year: int
    exam: str
    exam_name: str
    paper: Optional[str]
    subject: str
    topic: str
    subtopic: Optional[str]
    question: str
    question_type: str
    options: Optional[Any]
    correct_answer: Optional[str]
    explanation: Optional[str]
    word_limit: Optional[int]
    marks: Optional[int]
    model_answer: Optional[str]
    keywords: List[str]
    tags: List[str]
    difficulty: str
    ai_analysis: Optional[Any]
    is_verified: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class PYQAnalysisRequest(BaseModel):
    topic: str
    subject: Optional[str] = None
    years: int = 10  # Last N years
    exam_type: Optional[str] = None  # prelims, mains, both


class PYQAnalysisResponse(BaseModel):
    topic: str
    total_questions: int
    year_wise_count: dict
    exam_type_distribution: dict
    recurring_keywords: List[dict]
    trend_analysis: str
    probability_score: float
    mains_angles: List[str]
    prelims_insights: List[str]
    questions: List[PYQResponse]
    ai_insights: str
