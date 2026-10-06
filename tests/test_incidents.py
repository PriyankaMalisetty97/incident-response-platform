PAYLOAD = {
    "title": "Payment service failure",
    "description": "Payment requests are returning 500 errors",
    "service": "payment-service",
    "severity": "HIGH",
}


def make(auth_client, **overrides):
    return auth_client.post("/incidents", json={**PAYLOAD, **overrides})


def test_create_defaults_to_open(auth_client):
    r = make(auth_client)
    assert r.status_code == 201
    body = r.json()
    assert body["status"] == "OPEN"
    assert body["severity"] == "HIGH"
    assert body["id"] > 0


def test_full_lifecycle(auth_client):
    incident_id = make(auth_client).json()["id"]

    assert auth_client.get(f"/incidents/{incident_id}").json()["title"] == PAYLOAD["title"]

    r = auth_client.patch(f"/incidents/{incident_id}", json={"status": "INVESTIGATING"})
    assert r.status_code == 200
    assert r.json()["status"] == "INVESTIGATING"
    assert r.json()["title"] == PAYLOAD["title"]  # untouched fields stay

    assert auth_client.delete(f"/incidents/{incident_id}").status_code == 204
    assert auth_client.get(f"/incidents/{incident_id}").status_code == 404


def test_not_found(auth_client):
    assert auth_client.get("/incidents/999").status_code == 404
    assert auth_client.patch("/incidents/999", json={"status": "CLOSED"}).status_code == 404
    assert auth_client.delete("/incidents/999").status_code == 404


def test_validation_rejects_bad_input(auth_client):
    assert make(auth_client, title="").status_code == 422
    assert make(auth_client, severity="SUPER-DANGER").status_code == 422
    assert auth_client.post("/incidents", json={}).status_code == 422


def test_patch_rejects_invalid_status(auth_client):
    incident_id = make(auth_client).json()["id"]
    r = auth_client.patch(f"/incidents/{incident_id}", json={"status": "EXPLODED"})
    assert r.status_code == 422


def test_filtering(auth_client):
    make(auth_client, service="payment-service", severity="CRITICAL")
    make(auth_client, service="auth-service", severity="LOW")
    make(auth_client, service="payment-service", severity="LOW")

    assert len(auth_client.get("/incidents").json()) == 3
    assert len(auth_client.get("/incidents?severity=LOW").json()) == 2
    assert len(auth_client.get("/incidents?service=payment-service").json()) == 2
    both = auth_client.get("/incidents?service=payment-service&severity=LOW").json()
    assert len(both) == 1
    assert len(auth_client.get("/incidents?status=RESOLVED").json()) == 0
    assert auth_client.get("/incidents?severity=NOPE").status_code == 422


def test_pagination(auth_client):
    for i in range(5):
        make(auth_client, title=f"incident {i}")
    assert len(auth_client.get("/incidents?limit=2").json()) == 2
    assert len(auth_client.get("/incidents?limit=10&offset=3").json()) == 2
    assert auth_client.get("/incidents?limit=0").status_code == 422
