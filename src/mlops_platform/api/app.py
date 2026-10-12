from __future__ import annotations

import os
import time
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from mlops_platform.api.controls import CircuitBreaker, RateLimitExceeded, SlidingWindowRateLimiter
from mlops_platform.api.ui import CHAT_UI_HTML
from mlops_platform.ai_gateway.models import ChatRequest
from mlops_platform.ai_gateway.models import ChatResponse as GatewayChatResponse
from mlops_platform.ai_gateway.models import GatewayPolicy, GatewayRoute
from mlops_platform.ai_gateway.providers import (
    EchoProvider,
    FlakyProvider,
    NvidiaProvider,
    ProviderError,
)
from mlops_platform.ai_gateway.router import AIGateway
from mlops_platform.ai_gateway.telemetry import (
    CompositeTelemetrySink,
    InMemoryTelemetrySink,
    MLflowTelemetrySink,
)
from mlops_platform.quality.contracts import InferenceResponse, validate_data_contract

app = FastAPI(title="MLOps Platform Inference API", version="0.1.0")
ACTIVE_MODEL_VERSION = "0.1.0"
RATE_LIMITER = SlidingWindowRateLimiter(max_requests=200, window_seconds=60)
BREAKER = CircuitBreaker(failure_threshold=3)
MLFLOW_URI = os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000")
GATEWAY_TELEMETRY = CompositeTelemetrySink(
    sinks=[
        InMemoryTelemetrySink(),
        MLflowTelemetrySink(tracking_uri=MLFLOW_URI, experiment_name="ai-gateway"),
    ]
)
NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")
NVIDIA_MODEL_ID = os.getenv("NVIDIA_MODEL_ID", "meta/llama-3.2-11b-vision-instruct")
NVIDIA_VERIFY_SSL = os.getenv("NVIDIA_VERIFY_SSL", "true").lower() in ("true", "1", "yes")
NVIDIA_CA_BUNDLE = os.getenv("NVIDIA_CA_BUNDLE") or os.getenv("SSL_CERT_FILE")


def build_gateway() -> AIGateway:
    if NVIDIA_API_KEY:
        primary = NvidiaProvider(
            api_key=NVIDIA_API_KEY,
            base_url=os.getenv("NVIDIA_BASE_URL", "https://integrate.api.nvidia.com/v1"),
            verify_ssl=NVIDIA_VERIFY_SSL,
            ca_bundle=NVIDIA_CA_BUNDLE,
        )
        primary_route = GatewayRoute(provider_name="primary", model_id=NVIDIA_MODEL_ID)
    else:
        primary = FlakyProvider(provider_name="primary")
        primary_route = GatewayRoute(provider_name="primary", model_id="llm-primary-v1")
    return AIGateway(
        providers={"primary": primary, "fallback": EchoProvider(provider_name="fallback")},
        policy=GatewayPolicy(
            routes=[primary_route, GatewayRoute(provider_name="fallback", model_id="llm-fallback-v1")],
            max_tokens_limit=2048,
        ),
        telemetry=GATEWAY_TELEMETRY,
    )


AI_GATEWAY = build_gateway()


class BatchRequest(BaseModel):
    items: list[dict]


class OpenAIChatMessage(BaseModel):
    role: str = "user"
    content: str = ""


class OpenAIChatCompletionRequest(BaseModel):
    model: str | None = None
    messages: list[OpenAIChatMessage]
    max_tokens: int = 512
    temperature: float = 0.2


@app.get("/", response_class=HTMLResponse)
@app.get("/ui", response_class=HTMLResponse)
def chat_ui() -> HTMLResponse:
    return HTMLResponse(content=CHAT_UI_HTML)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/infer", response_model=InferenceResponse)
def infer(payload: dict) -> InferenceResponse:
    if BREAKER.is_open:
        # Graceful degradation path when downstream model serving is unstable.
        raise HTTPException(status_code=503, detail="service temporarily unavailable")
    try:
        RATE_LIMITER.check()
    except RateLimitExceeded as exc:
        raise HTTPException(status_code=429, detail=str(exc)) from exc
    req = validate_data_contract(payload)
    if not req.features:
        BREAKER.on_failure()
        raise HTTPException(status_code=400, detail="features are required")
    score = sum(req.features.values()) / len(req.features)
    BREAKER.on_success()
    return InferenceResponse(
        prediction=round(score, 6),
        model_version=ACTIVE_MODEL_VERSION,
        trace_id=str(uuid4()),
    )


@app.post("/infer/async")
def infer_async(payload: dict) -> dict[str, str]:
    validate_data_contract(payload)
    return {"job_id": str(uuid4()), "state": "queued"}


@app.post("/infer/batch")
def infer_batch(request: BatchRequest) -> dict[str, int]:
    for item in request.items:
        validate_data_contract(item)
    return {"accepted": len(request.items)}


@app.post("/chat", response_model=GatewayChatResponse)
def chat(request: ChatRequest) -> GatewayChatResponse:
    try:
        return AI_GATEWAY.generate(request)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except ProviderError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@app.post("/v1/chat/completions")
def openai_chat_completions(body: OpenAIChatCompletionRequest) -> dict:
    prompt = "\n".join([m.content for m in body.messages if m.content])
    chat_req = ChatRequest(
        tenant_id="openai-compat",
        prompt=prompt,
        max_tokens=body.max_tokens,
        temperature=body.temperature,
    )
    try:
        res = AI_GATEWAY.generate(chat_req)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except ProviderError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    return {
        "id": f"chatcmpl-{res.trace_id}",
        "object": "chat.completion",
        "created": int(time.time()),
        "model": res.model_id,
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": res.completion,
                },
                "finish_reason": "stop",
            }
        ],
        "usage": {
            "prompt_tokens": len(prompt.split()),
            "completion_tokens": len(res.completion.split()),
            "total_tokens": len(prompt.split()) + len(res.completion.split()),
        },
    }
