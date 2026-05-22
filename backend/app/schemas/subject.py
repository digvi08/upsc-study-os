"""Subject and Topic schemas."""
from pydantic import BaseModel, Field
from typing import Optional, List, Any
from datetime import datetime
import uuid


class SubjectCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    category: str
    color: str = "#6366f1"
    icon: Optional[str] = None
    order_index: int = 0


class SubjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    color: Optional[str] = None
    icon: Optional[str] = None
    order_index: Optional[int] = None
    is_active: Optional[bool] = None


class SubjectResponse(BaseModel):
    id: uuid.UUID
    name: str
    description: Optional[str]
    category: str
    color: str
    icon: Optional[str]
    order_index: int
    is_active: bool
    total_topics: int
    completed_topics: int
    completion_percentage: float
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TopicCreate(BaseModel):
    subject_id: uuid.UUID
    parent_id: Optional[uuid.UUID] = None
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    importance_score: int = Field(default=5, ge=1, le=10)
    priority: str = "medium"
    tags: List[str] = []


class TopicUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    importance_score: Optional[int] = None
    priority: Optional[str] = None
    tags: Optional[List[str]] = None
    confidence_level: Optional[int] = None
    study_time_minutes: Optional[int] = None


class TopicResponse(BaseModel):
    id: uuid.UUID
    subject_id: uuid.UUID
    parent_id: Optional[uuid.UUID]
    name: str
    description: Optional[str]
    status: str
    importance_score: int
    priority: str
    tags: List[str]
    study_time_minutes: int
    revision_count: int
    confidence_level: int
    pyq_frequency: int
    last_asked_year: Optional[int]
    ai_summary: Optional[str]
    key_concepts: Any
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TopicWithSubtopics(TopicResponse):
    subtopics: List["TopicWithSubtopics"] = []
