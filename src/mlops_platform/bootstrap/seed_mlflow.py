from __future__ import annotations

import argparse
from datetime import UTC, datetime
from pathlib import Path
from tempfile import TemporaryDirectory

import mlflow
from mlflow.exceptions import MlflowException
from mlflow.tracking import MlflowClient


def _write_minimal_model(model_dir: Path) -> None:
    model_dir.mkdir(parents=True, exist_ok=True)
    mlmodel = model_dir / "MLmodel"
    if not mlmodel.exists():
        mlmodel.write_text(
            "\n".join(
                [
                    "artifact_path: model",
                    "flavors:",
                    "  python_function:",
                    "    loader_module: mlflow.pyfunc.model",
                    "    python_version: '3.11.0'",
                    "    env: conda.yaml",
                    "mlflow_version: '2.16.2'",
                    f"model_uuid: '{datetime.now(UTC).timestamp()}'",
                    f"utc_time_created: '{datetime.now(UTC).isoformat()}'",
                ]
            ),
            encoding="utf-8",
        )
    conda = model_dir / "conda.yaml"
    if not conda.exists():
        conda.write_text(
            "\n".join(
                [
                    "name: mlflow-env",
                    "channels:",
                    "  - conda-forge",
                    "dependencies:",
                    "  - python=3.11",
                ]
            ),
            encoding="utf-8",
        )


def _ensure_registered_model(client: MlflowClient, model_name: str) -> None:
    try:
        client.create_registered_model(model_name)
    except MlflowException as exc:
        if "RESOURCE_ALREADY_EXISTS" not in str(exc):
            raise


def _existing_latest_version(client: MlflowClient, model_name: str) -> str | None:
    versions = list(client.search_model_versions(filter_string=f"name='{model_name}'"))
    if not versions:
        return None
    latest = max(versions, key=lambda mv: int(mv.version))
    return str(latest.version)


def _create_model_version_from_run(client: MlflowClient, model_name: str) -> str:
    with TemporaryDirectory() as tmp:
        model_dir = Path(tmp) / "seed-model"
        _write_minimal_model(model_dir)
        with mlflow.start_run(run_name="mlflow-bootstrap-seed") as run:
            mlflow.log_artifacts(str(model_dir), artifact_path="model")
            artifact_uri = run.info.artifact_uri.rstrip("/")
            source = f"{artifact_uri}/model"
            mv = client.create_model_version(
                name=model_name,
                source=source,
                run_id=run.info.run_id,
            )
            return str(mv.version)


def seed_mlflow(model_name: str, stage: str) -> tuple[str, str]:
    client = MlflowClient()
    _ensure_registered_model(client, model_name)

    version = _existing_latest_version(client, model_name)
    if version is None:
        version = _create_model_version_from_run(client, model_name)

    client.transition_model_version_stage(
        name=model_name,
        version=version,
        stage=stage,
        archive_existing_versions=False,
    )
    return model_name, version


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Seed MLflow with a sample registered model")
    parser.add_argument("--model-name", default="churn-model")
    parser.add_argument("--stage", default="Production")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    model_name, model_version = seed_mlflow(model_name=args.model_name, stage=args.stage)
    print(f"seeded model={model_name} version={model_version} stage={args.stage}")


if __name__ == "__main__":
    main()
