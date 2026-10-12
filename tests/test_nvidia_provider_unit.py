import io
import json
import urllib.error

import pytest

from mlops_platform.ai_gateway.models import ChatRequest
from mlops_platform.ai_gateway.providers import NvidiaProvider, ProviderError


class _FakeResponse(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *_):
        return False


def _request() -> ChatRequest:
    return ChatRequest(tenant_id="t1", prompt="hello", max_tokens=64, temperature=0.2)


def test_nvidia_provider_builds_openai_compatible_request(monkeypatch):
    captured = {}

    def fake_urlopen(req, *args, **kwargs):
        captured["url"] = req.full_url
        captured["auth"] = req.get_header("Authorization")
        captured["body"] = json.loads(req.data)
        body = {"choices": [{"message": {"content": "hi there"}}]}
        return _FakeResponse(json.dumps(body).encode())

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
    out = NvidiaProvider(api_key="k").generate(request=_request(), model_id="meta/llama-3.2-11b-vision-instruct")

    assert out == "hi there"
    assert captured["url"] == "https://integrate.api.nvidia.com/v1/chat/completions"
    assert captured["auth"] == "Bearer k"
    assert captured["body"]["model"] == "meta/llama-3.2-11b-vision-instruct"
    assert captured["body"]["messages"] == [{"role": "user", "content": "hello"}]


def test_nvidia_provider_maps_http_error_without_leaking_key(monkeypatch):
    def fake_urlopen(req, *args, **kwargs):
        raise urllib.error.HTTPError(req.full_url, 401, "unauthorized", {}, None)

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
    with pytest.raises(ProviderError) as exc:
        NvidiaProvider(api_key="secret-key").generate(request=_request(), model_id="m")
    assert "401" in str(exc.value)
    assert "secret-key" not in str(exc.value)


def test_nvidia_provider_rejects_malformed_response(monkeypatch):
    monkeypatch.setattr(
        "urllib.request.urlopen", lambda req, *args, **kwargs: _FakeResponse(b'{"choices": []}')
    )
    with pytest.raises(ProviderError):
        NvidiaProvider(api_key="k").generate(request=_request(), model_id="m")
