from __future__ import annotations

from uuid import uuid4

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from mlops_platform.api.controls import CircuitBreaker, RateLimitExceeded, SlidingWindowRateLimiter
from mlops_platform.ai_gateway.models import ChatRequest
from mlops_platform.ai_gateway.models import ChatResponse as GatewayChatResponse
from mlops_platform.ai_gateway.models import GatewayPolicy, GatewayRoute
from mlops_platform.ai_gateway.providers import EchoProvider, FlakyProvider, ProviderError
from mlops_platform.ai_gateway.router import AIGateway
from mlops_platform.ai_gateway.telemetry import InMemoryTelemetrySink
from mlops_platform.quality.contracts import InferenceResponse, validate_data_contract

app = FastAPI(title="MLOps Platform Inference API", version="0.1.0")
ACTIVE_MODEL_VERSION = "0.1.0"
RATE_LIMITER = SlidingWindowRateLimiter(max_requests=200, window_seconds=60)
BREAKER = CircuitBreaker(failure_threshold=3)
GATEWAY_TELEMETRY = InMemoryTelemetrySink()
AI_GATEWAY = AIGateway(
    providers={
        "primary": FlakyProvider(provider_name="primary"),
        "fallback": EchoProvider(provider_name="fallback"),
    },
    policy=GatewayPolicy(
        routes=[
            GatewayRoute(provider_name="primary", model_id="llm-primary-v1"),
            GatewayRoute(provider_name="fallback", model_id="llm-fallback-v1"),
        ],
        max_tokens_limit=2048,
    ),
    telemetry=GATEWAY_TELEMETRY,
)


class BatchRequest(BaseModel):
    items: list[dict]


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
