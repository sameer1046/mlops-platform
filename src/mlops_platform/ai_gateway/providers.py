from __future__ import annotations

import json
import ssl
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from typing import Protocol

from .models import ChatRequest


class ProviderError(Exception):
    pass


class LLMProvider(Protocol):
    provider_name: str

    def generate(self, *, request: ChatRequest, model_id: str) -> str:
        """Return LLM completion text or raise ProviderError."""


@dataclass
class NvidiaProvider:
    api_key: str = field(repr=False)
    provider_name: str = "nvidia"
    base_url: str = "https://integrate.api.nvidia.com/v1"
    timeout_seconds: float = 30.0
    verify_ssl: bool = True
    ca_bundle: str | None = None

    def _build_ssl_context(self) -> ssl.SSLContext | None:
        if not self.verify_ssl:
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            return ctx
        if self.ca_bundle:
            return ssl.create_default_context(cafile=self.ca_bundle)
        return None

    def generate(self, *, request: ChatRequest, model_id: str) -> str:
        body = json.dumps(
            {
                "model": model_id,
                "messages": [{"role": "user", "content": request.prompt}],
                "max_tokens": request.max_tokens,
                "temperature": request.temperature,
                "stream": False,
            }
        ).encode()
        http_request = urllib.request.Request(
            f"{self.base_url.rstrip('/')}/chat/completions",
            data=body,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            method="POST",
        )
        ctx = self._build_ssl_context()
        try:
            with urllib.request.urlopen(http_request, context=ctx, timeout=self.timeout_seconds) as response:
                payload = json.load(response)
            return payload["choices"][0]["message"]["content"]
        except urllib.error.HTTPError as exc:
            raise ProviderError(f"nvidia api returned HTTP {exc.code}") from exc
        except (urllib.error.URLError, TimeoutError, KeyError, IndexError, ValueError) as exc:
            raise ProviderError(f"nvidia api call failed: {type(exc).__name__}") from exc


@dataclass
class EchoProvider:
    provider_name: str = "echo"

    def generate(self, *, request: ChatRequest, model_id: str) -> str:
        return f"[{model_id}] {request.prompt}"


@dataclass
class FlakyProvider:
    provider_name: str = "flaky"
    failure_marker: str = "[force-fail]"

    def generate(self, *, request: ChatRequest, model_id: str) -> str:
        if self.failure_marker in request.prompt:
            raise ProviderError("simulated provider failure")
        return f"[{model_id}] {request.prompt}"
