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

logger = logging.getLogger(__name__)

# Neon pooler: keep SQLAlchemy pool small to avoid exhausting serverless connections
_pool_size = settings.database_pool_size
_max_overflow = settings.database_max_overflow
if settings.uses_neon_pooler:
    _pool_size = min(_pool_size, 5)
    _max_overflow = min(_max_overflow, 5)

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
