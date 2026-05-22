"""Current Affairs model."""
from sqlalchemy import Column, String, Text, Boolean, ForeignKey, Date, JSON
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from .base import BaseModel


class CurrentAffair(BaseModel):
    __tablename__ = "current_affairs"

    title = Column(String(500), nullable=False)
    summary = Column(Text, nullable=False)
    content = Column(Text, nullable=True)
    source = Column(String(255), nullable=True)
    source_url = Column(Text, nullable=True)
    published_date = Column(Date, nullable=False, index=True)

    # Classification
    category = Column(String(100), nullable=True)  # Economy, Polity, Environment, etc.
    tags = Column(JSON, default=list, nullable=False)
    keywords = Column(JSON, default=list, nullable=False)

    # Static subject linkage
    related_subjects = Column(JSON, default=list, nullable=False)
    related_topics = Column(JSONB, default=[], nullable=False)  # [{topic_id, relevance_score, explanation}]
    ai_relevance_explanation = Column(Text, nullable=True)

    # UPSC relevance
    upsc_relevance_score = Column(String(10), nullable=True)  # High, Medium, Low
    prelims_relevant = Column(Boolean, default=False, nullable=False)
    mains_relevant = Column(Boolean, default=False, nullable=False)
    mains_angles = Column(JSONB, default=[], nullable=False)

    # Admin
    is_verified = Column(Boolean, default=False, nullable=False)
    uploaded_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    embedding_id = Column(String(255), nullable=True)

    def __repr__(self):
        return f"<CurrentAffair {self.title[:50]}>"
