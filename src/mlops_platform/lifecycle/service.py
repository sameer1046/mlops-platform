from __future__ import annotations

from dataclasses import dataclass

from .mlflow_client import MLflowRegistryClient
from .models import ApprovalState, PackageManifest, PromotionRecord
from .store import load_package, save_package, save_promotion


@dataclass
class MLflowApprovalCheck:
    approved: bool
    model_name: str
    model_version: str
    allowed_stages: tuple[str, ...]


def package_model(
    *,
    version: str,
    code_sha: str,
    image_uri: str,
    prompt_bundle_version: str,
    config_version: str,
    created_by: str,
    mlflow_model_name: str | None = None,
    mlflow_model_version: str | None = None,
) -> PackageManifest:
    manifest = PackageManifest(
        model_version=version,
        code_sha=code_sha,
        image_uri=image_uri,
        prompt_bundle_version=prompt_bundle_version,
        config_version=config_version,
        mlflow_model_name=mlflow_model_name,
        mlflow_model_version=mlflow_model_version,
        created_by=created_by,
    )
    save_package(manifest)
    return manifest


def approve_model(
    *,
    version: str,
    approver: str,
    mlflow_stage: str | None = None,
    registry_client: MLflowRegistryClient | None = None,
) -> PackageManifest:
    manifest = load_package(version)
    manifest.state = ApprovalState.APPROVED
    manifest.created_by = approver
    if mlflow_stage and manifest.mlflow_model_name and manifest.mlflow_model_version:
        client = registry_client or MLflowRegistryClient()
        client.transition_model_version_stage(
            model_name=manifest.mlflow_model_name,
            model_version=manifest.mlflow_model_version,
            stage=mlflow_stage,
        )
    save_package(manifest)
    return manifest


def verify_mlflow_approval(
    *,
    model_name: str,
    model_version: str,
    allowed_stages: tuple[str, ...] = ("Staging", "Production"),
    registry_client: MLflowRegistryClient | None = None,
) -> MLflowApprovalCheck:
    client = registry_client or MLflowRegistryClient()
    approved = client.is_model_approved(
        model_name=model_name,
        model_version=model_version,
        allowed_stages=allowed_stages,
    )
    return MLflowApprovalCheck(
        approved=approved,
        model_name=model_name,
        model_version=model_version,
        allowed_stages=allowed_stages,
    )


def promote_model(
    *,
    version: str,
    from_environment: str,
    to_environment: str,
    promoted_by: str,
    evidence_uri: str,
    model_name: str | None = None,
    model_registry_version: str | None = None,
    allowed_stages: tuple[str, ...] = ("Staging", "Production"),
    registry_client: MLflowRegistryClient | None = None,
) -> PromotionRecord:
    manifest = load_package(version)
    if manifest.state != ApprovalState.APPROVED:
        raise ValueError(f"model {version} is not approved")
    if bool(model_name) ^ bool(model_registry_version):
        raise ValueError("model_name and model_registry_version must be provided together")
    if model_name and model_registry_version:
        check = verify_mlflow_approval(
            model_name=model_name,
            model_version=model_registry_version,
            allowed_stages=allowed_stages,
            registry_client=registry_client,
        )
        if not check.approved:
            raise ValueError(
                f"mlflow model {model_name} version {model_registry_version} "
                f"is not in approved stages {allowed_stages}"
            )
    record = PromotionRecord(
        model_version=version,
        from_environment=from_environment,
        to_environment=to_environment,
        promoted_by=promoted_by,
        evidence_uri=evidence_uri,
    )
    save_promotion(record)
    return record
