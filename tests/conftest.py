import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import app.models  # noqa: F401
from app.database.connection import Base, get_db
from app.main import app


@pytest.fixture()
def client():
    """Each test gets a fresh in-memory SQLite DB, so tests never touch real data."""
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(bind=engine)
    TestingSession = sessionmaker(bind=engine, autoflush=False, autocommit=False)

    def override_get_db():
        db = TestingSession()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    # No `with` block on purpose: it would run the app lifespan and try to reach the real DB.
    yield TestClient(app, raise_server_exceptions=False)
    app.dependency_overrides.clear()


def register_and_login(client, email="alice@example.com", password="supersecret1", name="Alice"):
    """Helper: creates a user and returns the Authorization header for them."""
    client.post("/auth/register", json={"name": name, "email": email, "password": password})
    r = client.post("/auth/login", data={"username": email, "password": password})
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


@pytest.fixture()
def auth_client(client):
    """A client that is already logged in as Alice."""
    client.headers.update(register_and_login(client))
    return client
