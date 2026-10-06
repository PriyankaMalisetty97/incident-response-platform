from sqlalchemy.exc import OperationalError

from tests.conftest import register_and_login

INCIDENT = {"title": "x", "description": "y", "service": "s", "severity": "LOW"}


def test_blank_or_whitespace_title_rejected(auth_client):
    assert auth_client.post("/incidents", json={**INCIDENT, "title": "   "}).status_code == 422
    assert auth_client.post("/incidents", json={**INCIDENT, "service": ""}).status_code == 422


def test_title_is_trimmed(auth_client):
    r = auth_client.post("/incidents", json={**INCIDENT, "title": "  Payment down  "})
    assert r.json()["title"] == "Payment down"


def test_patch_null_on_required_field_is_422_not_500(auth_client):
    incident_id = auth_client.post("/incidents", json=INCIDENT).json()["id"]
    for field in ["title", "description", "service", "severity", "status"]:
        r = auth_client.patch(f"/incidents/{incident_id}", json={field: None})
        assert r.status_code == 422, field


def test_patch_can_clear_error_message(auth_client):
    body = {**INCIDENT, "error_message": "boom"}
    incident_id = auth_client.post("/incidents", json=body).json()["id"]
    r = auth_client.patch(f"/incidents/{incident_id}", json={"error_message": None})
    assert r.status_code == 200
    assert r.json()["error_message"] is None


def test_database_down_returns_503(auth_client, monkeypatch):
    def boom(*args, **kwargs):
        raise OperationalError("SELECT 1", {}, Exception("connection refused"))

    monkeypatch.setattr("app.routes.incidents.incident_service.list_incidents", boom)
    r = auth_client.get("/incidents")
    assert r.status_code == 503
    assert "connection refused" not in r.text  # internals are never leaked


def test_unexpected_error_returns_safe_500(auth_client, monkeypatch):
    def boom(*args, **kwargs):
        raise RuntimeError("secret internal detail")

    monkeypatch.setattr("app.routes.incidents.incident_service.list_incidents", boom)
    r = auth_client.get("/incidents")
    assert r.status_code == 500
    assert r.json() == {"detail": "Internal server error"}


def test_unknown_route_is_404(client):
    assert client.get("/nope").status_code == 404


def test_wrong_http_method_is_405(auth_client):
    assert auth_client.put("/incidents").status_code == 405
