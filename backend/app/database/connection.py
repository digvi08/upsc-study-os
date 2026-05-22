"""Database connection and session management."""
from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from typing import Generator
import logging

from app.config import settings

logger = logging.getLogger(__name__)

# Create engine with connection pooling
engine = create_engine(
    settings.database_url,
    poolclass=QueuePool,
    pool_size=settings.database_pool_size,
    max_overflow=settings.database_max_overflow,
    pool_pre_ping=True,  # Verify connections before use
    pool_recycle=3600,   # Recycle connections every hour
    echo=settings.debug,
)

# Session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

# Base class for all models
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
    """Initialize database tables."""
    # Import all models so SQLAlchemy registers them before create_all
    from app.models import (  # noqa: F401
        User, Subject, Topic, PYQ, Note,
        RevisionHistory, StudyPlan, StudyTask,
        CurrentAffair, AnswerEvaluation,
        UserAnalytics, DailyStudyLog, MockTest,
    )
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully")
