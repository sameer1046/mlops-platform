from __future__ import annotations

import os
from dataclasses import dataclass

import mlflow
from mlflow.tracking import MlflowClient


@dataclass
class MLflowModelStatus:
    model_name: str
    model_version: str
    current_stage: str
    status: str


class MLflowRegistryClient:
    """Small wrapper around MLflow model registry operations."""

    def __init__(self, tracking_uri: str | None = None) -> None:
        self._tracking_uri = tracking_uri or os.getenv("MLFLOW_TRACKING_URI")
        self._host = os.getenv("DATABRICKS_HOST")
        self._token = os.getenv("DATABRICKS_TOKEN")
        self._client = self._build_client()

    def _build_client(self) -> MlflowClient:
        if self._tracking_uri:
            mlflow.set_tracking_uri(self._tracking_uri)
        elif self._host and self._token:
            # Databricks MLflow registry via workspace URL.
            mlflow.set_tracking_uri("databricks")
        return MlflowClient()

    def get_model_status(self, *, model_name: str, model_version: str) -> MLflowModelStatus:
        mv = self._client.get_model_version(name=model_name, version=model_version)
        return MLflowModelStatus(
            model_name=model_name,
            model_version=model_version,
            current_stage=mv.current_stage,
            status=mv.status,
        )

    def is_model_approved(
        self,
        *,
        model_name: str,
        model_version: str,
        allowed_stages: tuple[str, ...] = ("Staging", "Production"),
    ) -> bool:
        status = self.get_model_status(model_name=model_name, model_version=model_version)
        return status.current_stage in allowed_stages

    def transition_model_version_stage(
        self,
        *,
        model_name: str,
        model_version: str,
        stage: str,
        archive_existing_versions: bool = True,
    ) -> None:
        self._client.transition_model_version_stage(
            name=model_name,
            version=model_version,
            stage=stage,
            archive_existing_versions=archive_existing_versions,
        )
