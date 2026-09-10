"""
Pytest fixtures for SentinelAI backend tests.

Uses SQLite in-memory database for fast, isolated tests.
"""
import os

# Set test environment BEFORE importing app
os.environ["SECRET_KEY"] = "test-secret-key-for-pytest-only"
os.environ["ALGORITHM"] = "HS256"
os.environ["ACCESS_TOKEN_EXPIRE_MINUTES"] = "30"
os.environ["POSTGRES_USER"] = "test"
os.environ["POSTGRES_PASSWORD"] = "test"
os.environ["POSTGRES_DB"] = "test"
os.environ["POSTGRES_HOST"] = "localhost"
os.environ["REDIS_HOST"] = "localhost"
os.environ["REDIS_PASSWORD"] = ""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from app.database import Base
from app import models  # noqa: F401 (register models)
from app.dependencies.auth import get_db as auth_get_db
from app.main import app


# ============ Test Database (SQLite in-memory) ============
TEST_DB_URL = "sqlite:///:memory:"

test_engine = create_engine(
    TEST_DB_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=test_engine,
)


# ============ Session-scoped setup ============
@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    """Create all tables once for the whole test session."""
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


# ============ Per-test clean DB ============
@pytest.fixture(autouse=True)
def clean_db():
    """Ensure each test starts with a clean database."""
    yield
    # Delete all rows from all tables
    session = TestingSessionLocal()
    try:
        for table in reversed(Base.metadata.sorted_tables):
            session.execute(table.delete())
        session.commit()
    finally:
        session.close()


# ============ DB session fixture ============
@pytest.fixture
def db_session():
    """Provide a fresh test DB session."""
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


# ============ TestClient with dependency override ============
@pytest.fixture
def client(db_session):
    """
    FastAPI TestClient with get_db overridden to use the test session.
    Lifespan is NOT triggered (no context manager) to avoid Redis/Postgres
    connections during tests.
    """
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[auth_get_db] = override_get_db
    test_client = TestClient(app)
    yield test_client
    app.dependency_overrides.clear()


# ============ Auth helpers ============
@pytest.fixture
def test_user_data():
    """Standard user data for tests."""
    return {
        "username": "testanalyst",
        "email": "testanalyst@example.com",
        "password": "SecureTestPass123!",
        "full_name": "Test Analyst",
    }


@pytest.fixture
def registered_user(client, test_user_data):
    """Register a test user and return the response data."""
    response = client.post("/api/auth/register", json=test_user_data)
    assert response.status_code == 201, response.text
    return response.json()


@pytest.fixture
def auth_token(client, registered_user, test_user_data):
    """Get a valid JWT token for the registered user."""
    response = client.post(
        "/api/auth/login",
        json={
            "username": test_user_data["username"],
            "password": test_user_data["password"],
        },
    )
    assert response.status_code == 200, response.text
    return response.json()["access_token"]


@pytest.fixture
def auth_headers(auth_token):
    """Authorization headers with Bearer token."""
    return {"Authorization": f"Bearer {auth_token}"}


@pytest.fixture
def admin_token(client, db_session):
    """Create an admin user and return its token."""
    from app.utils.security import get_password_hash
    from app.models import User, UserRole

    admin = User(
        username="testadmin",
        email="testadmin@example.com",
        hashed_password=get_password_hash("AdminPass123!"),
        full_name="Test Admin",
        role=UserRole.ADMIN.value,
        is_active=True,
    )
    db_session.add(admin)
    db_session.commit()

    response = client.post(
        "/api/auth/login",
        json={"username": "testadmin", "password": "AdminPass123!"},
    )
    assert response.status_code == 200, response.text
    return response.json()["access_token"]


@pytest.fixture
def admin_headers(admin_token):
    return {"Authorization": f"Bearer {admin_token}"}
