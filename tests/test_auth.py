from tests.conftest import register_and_login

USER = {"name": "Alice", "email": "alice@example.com", "password": "supersecret1"}
INCIDENT = {
    "title": "DB down",
    "description": "Connections refused",
    "service": "db",
    "severity": "CRITICAL",
}


def test_register_returns_user_without_password(client):
    r = client.post("/auth/register", json=USER)
    assert r.status_code == 201
    body = r.json()
    assert body["email"] == "alice@example.com"
    assert "password" not in body and "password_hash" not in body


def test_password_is_not_stored_in_plain_text(client):
    from app.database.connection import get_db
    from app.main import app
    from app.models.user import User

    client.post("/auth/register", json=USER)
    db = next(app.dependency_overrides[get_db]())
    stored = db.query(User).one().password_hash
    assert stored != USER["password"]
    assert stored.startswith("$2")  # bcrypt


def test_duplicate_email_rejected(client):
    client.post("/auth/register", json=USER)
    r = client.post("/auth/register", json={**USER, "email": "ALICE@example.com"})
    assert r.status_code == 409


def test_register_validation(client):
    assert client.post("/auth/register", json={**USER, "password": "short"}).status_code == 422
    assert client.post("/auth/register", json={**USER, "email": "not-an-email"}).status_code == 422


def test_login_success_and_me(client):
    client.post("/auth/register", json=USER)
    r = client.post("/auth/login", data={"username": USER["email"], "password": USER["password"]})
    assert r.status_code == 200
    token = r.json()["access_token"]
    me = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200
    assert me.json()["email"] == USER["email"]


def test_login_wrong_password_and_unknown_email(client):
    client.post("/auth/register", json=USER)
    bad_pw = client.post("/auth/login", data={"username": USER["email"], "password": "wrongpass1"})
    unknown = client.post("/auth/login", data={"username": "nobody@example.com", "password": "x"})
    assert bad_pw.status_code == unknown.status_code == 401
    assert bad_pw.json() == unknown.json()  # same message: doesn't reveal which emails exist


def test_incidents_require_login(client):
    assert client.get("/incidents").status_code == 401
    assert client.post("/incidents", json=INCIDENT).status_code == 401
    assert client.get("/incidents", headers={"Authorization": "Bearer garbage"}).status_code == 401


def test_expired_token_rejected(client):
    from datetime import datetime, timedelta, timezone

    import jwt

    from app.config import settings

    client.post("/auth/register", json=USER)
    expired = jwt.encode(
        {"sub": "1", "exp": datetime.now(timezone.utc) - timedelta(minutes=1)},
        settings.secret_key,
        algorithm="HS256",
    )
    r = client.get("/auth/me", headers={"Authorization": f"Bearer {expired}"})
    assert r.status_code == 401


def test_incident_records_creator(client):
    headers = register_and_login(client)
    r = client.post("/incidents", json=INCIDENT, headers=headers)
    assert r.status_code == 201
    assert r.json()["user_id"] == client.get("/auth/me", headers=headers).json()["id"]


def test_only_creator_can_delete(client):
    alice = register_and_login(client, "alice@example.com", name="Alice")
    bob = register_and_login(client, "bob@example.com", name="Bob")
    incident_id = client.post("/incidents", json=INCIDENT, headers=alice).json()["id"]

    assert client.delete(f"/incidents/{incident_id}", headers=bob).status_code == 403
    # Bob can still update (any logged-in team member can work an incident)
    r = client.patch(f"/incidents/{incident_id}", json={"status": "INVESTIGATING"}, headers=bob)
    assert r.status_code == 200
    assert client.delete(f"/incidents/{incident_id}", headers=alice).status_code == 204
