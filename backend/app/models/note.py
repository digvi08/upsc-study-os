"""Notes model."""
from sqlalchemy import Column, String, Text, Boolean, ForeignKey, Enum, JSON, Integer
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import enum
from .base import BaseModel


class NoteType(str, enum.Enum):
    MANUAL = "manual"
    AI_GENERATED = "ai_generated"
    SUMMARY = "summary"
    FLASHCARD = "flashcard"
    MIND_MAP = "mind_map"
    REVISION = "revision"


class Note(BaseModel):
    __tablename__ = "notes"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    topic_id = Column(UUID(as_uuid=True), ForeignKey("topics.id", ondelete="SET NULL"), nullable=True, index=True)
    subject_id = Column(UUID(as_uuid=True), ForeignKey("subjects.id", ondelete="SET NULL"), nullable=True, index=True)

    title = Column(String(500), nullable=False)
    content = Column(Text, nullable=False)  # Rich text / Markdown
    note_type = Column(Enum(NoteType), default=NoteType.MANUAL, nullable=False)

    # Organization
    tags = Column(JSON, default=list, nullable=False)
    color = Column(String(7), default="#ffffff", nullable=False)
    is_pinned = Column(Boolean, default=False, nullable=False)
    is_favorite = Column(Boolean, default=False, nullable=False)
    is_public = Column(Boolean, default=False, nullable=False)

    # AI features
    ai_summary = Column(Text, nullable=True)
    flashcards = Column(JSONB, default=[], nullable=False)  # [{front: "", back: ""}]
    key_points = Column(JSONB, default=[], nullable=False)
    mind_map_data = Column(JSONB, nullable=True)
    embedding_id = Column(String(255), nullable=True)

    # Revision tracking
    revision_count = Column(Integer, default=0, nullable=False)
    last_revised_at = Column(String(50), nullable=True)

    # Relationships
    user = relationship("User", back_populates="notes")
    topic = relationship("Topic", back_populates="notes")

    def __repr__(self):
        return f"<Note {self.title}>"
