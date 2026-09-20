from __future__ import annotations

from pydantic import BaseModel, Field


class InferenceRequest(BaseModel):
    user_id: str = Field(min_length=1)
    features: dict[str, float]
    prompt: str | None = None


class InferenceResponse(BaseModel):
    prediction: float
    model_version: str
    trace_id: str


def validate_data_contract(payload: dict) -> InferenceRequest:
    return InferenceRequest.model_validate(payload)
