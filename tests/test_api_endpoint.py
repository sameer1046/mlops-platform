import pytest
from fastapi.testclient import TestClient

from mlops_platform.api.app import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def disable_mlflow_telemetry_for_tests(monkeypatch):
    monkeypatch.setenv("MLFLOW_TELEMETRY_ENABLED", "false")


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


def test_chat_uses_primary_provider():
    resp = client.post("/chat", json={"tenant_id": "team-a", "prompt": "hello gateway"})
    assert resp.status_code == 200
    payload = resp.json()
    assert payload["provider"] == "primary"
    assert payload["fallback_used"] is False


def test_chat_fallback_when_primary_fails():
    resp = client.post(
        "/chat",
        json={"tenant_id": "team-a", "prompt": "[force-fail] trigger fallback"},
    )
    assert resp.status_code == 200
    payload = resp.json()
    assert payload["provider"] == "fallback"
    assert payload["fallback_used"] is True


def test_chat_ui_endpoint():
    resp = client.get("/")
    assert resp.status_code == 200
    assert "MLOps AI Gateway" in resp.text

    resp_ui = client.get("/ui")
    assert resp_ui.status_code == 200


def test_openai_chat_completions_endpoint():
    resp = client.post(
        "/v1/chat/completions",
        json={
            "model": "meta/llama-3.2-11b-vision-instruct",
            "messages": [{"role": "user", "content": "hi"}],
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["object"] == "chat.completion"
    assert len(data["choices"]) == 1
    assert data["choices"][0]["message"]["role"] == "assistant"

