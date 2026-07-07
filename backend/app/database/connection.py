"""Database connection and session management."""
from sqlalchemy import create_engine
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from sqlalchemy.pool import QueuePool
from sqlalchemy.dialects.postgresql import JSONB, UUID
from typing import Generator
import logging

from app.config import settings


@compiles(JSONB, "sqlite")
def _compile_jsonb_for_sqlite(type_, compiler, **kw):
    return "JSON"


@compiles(UUID, "sqlite")
def _compile_uuid_for_sqlite(type_, compiler, **kw):
    return "CHAR(36)"

from pathlib import Path

logger = logging.getLogger(__name__)

# Neon pooler: keep SQLAlchemy pool small to avoid exhausting serverless connections
_pool_size = settings.database_pool_size
_max_overflow = settings.database_max_overflow
if settings.uses_neon_pooler:
    _pool_size = min(_pool_size, 5)
    _max_overflow = min(_max_overflow, 5)

# If using a local SQLite file DB, ensure the parent directory exists so SQLAlchemy can create the file.
if settings.database_url.startswith("sqlite"):
    # Expect formats like sqlite:///./data/dev.db or sqlite:///absolute/path.db
    try:
        # Extract path after the scheme (three slashes)
        path_part = settings.database_url.split("///", 1)[1] if "///" in settings.database_url else settings.database_url.split("//", 1)[1]
        db_path = Path(path_part).expanduser()
        if db_path.parent and not db_path.parent.exists():
            db_path.parent.mkdir(parents=True, exist_ok=True)
    except Exception:
        # Non-fatal: if parsing fails, continue and let SQLAlchemy raise any file errors
        logger.debug("Could not auto-create parent dir for sqlite database (parsing failed).")

engine = create_engine(
    settings.database_url,
    poolclass=QueuePool,
    pool_size=_pool_size,
    max_overflow=_max_overflow,
    pool_pre_ping=True,
    pool_recycle=300 if settings.uses_neon_pooler else 3600,
    echo=settings.debug,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """Dependency to get database session."""
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database session error: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def init_db() -> None:
    """Create tables if missing (development fallback; production uses Alembic)."""
    from app.models import (  # noqa: F401
        User, Subject, Topic, PYQ, Note,
        RevisionHistory, StudyPlan, StudyTask,
        CurrentAffair, AnswerEvaluation,
        UserAnalytics, DailyStudyLog, MockTest,
    )
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables verified/created")
