PAYLOAD = {
    "title": "Payment service failure",
    "description": "Payment requests are returning 500 errors",
    "service": "payment-service",
    "severity": "HIGH",
}


def make(client, **overrides):
    return client.post("/incidents", json={**PAYLOAD, **overrides})


def test_create_defaults_to_open(client):
    r = make(client)
    assert r.status_code == 201
    body = r.json()
    assert body["status"] == "OPEN"
    assert body["severity"] == "HIGH"
    assert body["id"] > 0


def test_full_lifecycle(client):
    incident_id = make(client).json()["id"]

    assert client.get(f"/incidents/{incident_id}").json()["title"] == PAYLOAD["title"]

    r = client.patch(f"/incidents/{incident_id}", json={"status": "INVESTIGATING"})
    assert r.status_code == 200
    assert r.json()["status"] == "INVESTIGATING"
    assert r.json()["title"] == PAYLOAD["title"]  # untouched fields stay

    assert client.delete(f"/incidents/{incident_id}").status_code == 204
    assert client.get(f"/incidents/{incident_id}").status_code == 404


def test_not_found(client):
    assert client.get("/incidents/999").status_code == 404
    assert client.patch("/incidents/999", json={"status": "CLOSED"}).status_code == 404
    assert client.delete("/incidents/999").status_code == 404


def test_validation_rejects_bad_input(client):
    assert make(client, title="").status_code == 422
    assert make(client, severity="SUPER-DANGER").status_code == 422
    assert client.post("/incidents", json={}).status_code == 422


def test_patch_rejects_invalid_status(client):
    incident_id = make(client).json()["id"]
    r = client.patch(f"/incidents/{incident_id}", json={"status": "EXPLODED"})
    assert r.status_code == 422


def test_filtering(client):
    make(client, service="payment-service", severity="CRITICAL")
    make(client, service="auth-service", severity="LOW")
    make(client, service="payment-service", severity="LOW")

    assert len(client.get("/incidents").json()) == 3
    assert len(client.get("/incidents?severity=LOW").json()) == 2
    assert len(client.get("/incidents?service=payment-service").json()) == 2
    both = client.get("/incidents?service=payment-service&severity=LOW").json()
    assert len(both) == 1
    assert len(client.get("/incidents?status=RESOLVED").json()) == 0
    assert client.get("/incidents?severity=NOPE").status_code == 422


def test_pagination(client):
    for i in range(5):
        make(client, title=f"incident {i}")
    assert len(client.get("/incidents?limit=2").json()) == 2
    assert len(client.get("/incidents?limit=10&offset=3").json()) == 2
    assert client.get("/incidents?limit=0").status_code == 422
