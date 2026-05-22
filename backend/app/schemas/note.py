"""Note schemas."""
from pydantic import BaseModel, Field
from typing import Optional, List, Any
from datetime import datetime
import uuid


class NoteCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)
    content: str
    topic_id: Optional[uuid.UUID] = None
    subject_id: Optional[uuid.UUID] = None
    note_type: str = "manual"
    tags: List[str] = []
    color: str = "#ffffff"
    is_pinned: bool = False


class NoteUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    topic_id: Optional[uuid.UUID] = None
    subject_id: Optional[uuid.UUID] = None
    tags: Optional[List[str]] = None
    color: Optional[str] = None
    is_pinned: Optional[bool] = None
    is_favorite: Optional[bool] = None


class NoteResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    title: str
    content: str
    topic_id: Optional[uuid.UUID]
    subject_id: Optional[uuid.UUID]
    note_type: str
    tags: List[str]
    color: str
    is_pinned: bool
    is_favorite: bool
    ai_summary: Optional[str]
    flashcards: Any
    key_points: Any
    revision_count: int
    last_revised_at: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class AIGenerateNoteRequest(BaseModel):
    topic: str
    subject: Optional[str] = None
    note_type: str = "summary"  # summary, flashcards, mind_map, revision
    detail_level: str = "medium"  # brief, medium, detailed


class FlashcardSet(BaseModel):
    topic_id: Optional[uuid.UUID] = None
    note_id: Optional[uuid.UUID] = None
    cards: List[dict]  # [{front: "", back: ""}]
