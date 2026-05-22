"""Pytest configuration and shared fixtures."""
import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from sqlalchemy import ARRAY as SA_ARRAY
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.dialects.postgresql import ARRAY as PG_ARRAY, JSONB, UUID

# SQLite does not support PostgreSQL ARRAY/JSONB/UUID — compile to compatible types
@compiles(SA_ARRAY, "sqlite")
@compiles(PG_ARRAY, "sqlite")
def _compile_array_sqlite(type_, compiler, **kw):
    return "TEXT"


@compiles(JSONB, "sqlite")
def _compile_jsonb_sqlite(type_, compiler, **kw):
    return "TEXT"


@compiles(UUID, "sqlite")
def _compile_uuid_sqlite(type_, compiler, **kw):
    return "CHAR(36)"


from app.main import app
from app.database.connection import Base, get_db
from app.models.user import User, UserRole, ExamTarget
from app.auth.password import hash_password
from app.auth.jwt_handler import create_access_token

# Use in-memory SQLite for tests
SQLALCHEMY_TEST_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_TEST_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db():
    """Create a fresh database for each test."""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db):
    """Create a test client with overridden DB dependency."""
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with patch("app.main.init_db"):
        with TestClient(app) as c:
            yield c
    app.dependency_overrides.clear()


@pytest.fixture
def test_user(db):
    """Create a test user."""
    user = User(
        email="test@example.com",
        username="testuser",
        full_name="Test User",
        hashed_password=hash_password("TestPass123"),
        is_active=True,
        is_verified=True,
        role=UserRole.STUDENT,
        exam_target=ExamTarget.UPSC,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def admin_user(db):
    """Create a test admin user."""
    user = User(
        email="admin@example.com",
        username="adminuser",
        full_name="Admin User",
        hashed_password=hash_password("AdminPass123"),
        is_active=True,
        is_verified=True,
        role=UserRole.ADMIN,
        exam_target=ExamTarget.UPSC,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def auth_headers(test_user):
    """Get auth headers for test user."""
    token = create_access_token({"sub": str(test_user.id), "email": test_user.email, "role": "student"})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def admin_headers(admin_user):
    """Get auth headers for admin user."""
    token = create_access_token({"sub": str(admin_user.id), "email": admin_user.email, "role": "admin"})
    return {"Authorization": f"Bearer {token}"}
