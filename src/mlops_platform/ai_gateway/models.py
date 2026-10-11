from __future__ import annotations

from dataclasses import dataclass, field
from uuid import uuid4

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    tenant_id: str = Field(min_length=1)
    prompt: str = Field(min_length=1)
    max_tokens: int = Field(default=512, ge=1, le=8192)
    temperature: float = Field(default=0.1, ge=0.0, le=2.0)


class ChatResponse(BaseModel):
    completion: str
    provider: str
    model_id: str
    trace_id: str
    fallback_used: bool = False


@dataclass(frozen=True)
class GatewayRoute:
    provider_name: str
    model_id: str


@dataclass
class GatewayPolicy:
    routes: list[GatewayRoute]
    max_tokens_limit: int = 4096
    allowed_tenants: set[str] = field(default_factory=set)

    def enforce(self, request: ChatRequest) -> None:
        if self.allowed_tenants and request.tenant_id not in self.allowed_tenants:
            raise ValueError(f"tenant {request.tenant_id} is not allowed")
        if request.max_tokens > self.max_tokens_limit:
            raise ValueError(
                f"max_tokens {request.max_tokens} exceeds policy limit {self.max_tokens_limit}"
            )


def make_trace_id() -> str:
    return str(uuid4())
