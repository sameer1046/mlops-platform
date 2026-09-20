from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum

from pydantic import BaseModel, Field


class ApprovalState(StrEnum):
    CANDIDATE = "candidate"
    APPROVED = "approved"
    REJECTED = "rejected"


class PackageManifest(BaseModel):
    model_version: str
    code_sha: str
    image_uri: str
    prompt_bundle_version: str
    config_version: str
    mlflow_model_name: str | None = None
    mlflow_model_version: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    created_by: str
    state: ApprovalState = ApprovalState.CANDIDATE


class PromotionRecord(BaseModel):
    model_version: str
    from_environment: str
    to_environment: str
    promoted_by: str
    promoted_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    evidence_uri: str
