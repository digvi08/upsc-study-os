"""Base model with common fields."""
import uuid
from datetime import datetime
from sqlalchemy import Column, DateTime, Boolean, String
from sqlalchemy.dialects.postgresql import UUID
from app.database.connection import Base


class TimestampMixin:
    """Mixin for created_at and updated_at timestamps."""
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class SoftDeleteMixin:
    """Mixin for soft delete support."""
    is_deleted = Column(Boolean, default=False, nullable=False)
    deleted_at = Column(DateTime, nullable=True)


class BaseModel(Base, TimestampMixin, SoftDeleteMixin):
    """Abstract base model with UUID primary key, timestamps, and soft delete."""
    __abstract__ = True

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )
