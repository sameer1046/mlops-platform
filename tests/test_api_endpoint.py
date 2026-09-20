from fastapi.testclient import TestClient

from mlops_platform.api.app import app

client = TestClient(app)


def test_health():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_sync_infer():
    resp = client.post("/infer", json={"user_id": "u1", "features": {"a": 1.0, "b": 3.0}})
    assert resp.status_code == 200
    payload = resp.json()
    assert payload["prediction"] == 2.0
    assert payload["model_version"] == "0.1.0"


def test_async_infer():
    resp = client.post("/infer/async", json={"user_id": "u1", "features": {"a": 1.0}})
    assert resp.status_code == 200
    assert resp.json()["state"] == "queued"
