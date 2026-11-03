"""
tests/conftest.py — Pytest fixtures for TruthGuard AI with isolated in-memory SQLite and StaticPool.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import Base, get_db
from app.services.seed_data import seed_database


@pytest.fixture(scope="function")
def test_engine():
    """Isolated in-memory SQLite engine using StaticPool so connections share memory."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    import app.models.db_models  # noqa: F401
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture(scope="function")
def db_session(test_engine):
    """Session for the in-memory test database."""
    TestingSession = sessionmaker(bind=test_engine, autocommit=False, autoflush=False)
    session = TestingSession()
    # Seed initial test data
    seed_database(session)
    yield session
    session.close()


@pytest.fixture(scope="function")
def client(db_session):
    """TestClient overriding get_db to connect to in-memory session."""
    def _override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture()
def admin_headers(client):
    """Logs in as default seed admin and returns authorization header."""
    resp = client.post("/api/auth/demo-login/admin")
    assert resp.status_code == 200, resp.text
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture()
def user_headers(client):
    """Logs in as default seed user and returns authorization header."""
    resp = client.post("/api/auth/demo-login/user")
    assert resp.status_code == 200, resp.text
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
