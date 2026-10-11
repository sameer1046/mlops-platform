from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from .models import ChatRequest


class ProviderError(Exception):
    pass


class LLMProvider(Protocol):
    provider_name: str

    def generate(self, *, request: ChatRequest, model_id: str) -> str:
        """Return LLM completion text or raise ProviderError."""


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
