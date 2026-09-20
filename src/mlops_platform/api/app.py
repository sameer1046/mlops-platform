from __future__ import annotations

from uuid import uuid4

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from mlops_platform.api.controls import CircuitBreaker, RateLimitExceeded, SlidingWindowRateLimiter
from mlops_platform.quality.contracts import InferenceResponse, validate_data_contract

app = FastAPI(title="MLOps Platform Inference API", version="0.1.0")
ACTIVE_MODEL_VERSION = "0.1.0"
RATE_LIMITER = SlidingWindowRateLimiter(max_requests=200, window_seconds=60)
BREAKER = CircuitBreaker(failure_threshold=3)


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
