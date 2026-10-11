# MLOps Platform (AWS + Databricks)

Reusable, production-oriented MLOps starter repository implementing:

- automated testing across model deployment lifecycle
- model packaging, versioning, approval, promotion, and deployment controls
- blue/green, canary, shadow, and weighted traffic shifting strategies
- rollback and roll-forward for code, infra, models, prompts, and config
- secure inference service patterns for ML and LLM applications
- auditable deployment and promotion events

## Quick Start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest -q
uvicorn mlops_platform.api.app:app --reload
```

## Docker Compose (API + MLflow Server)

```bash
docker compose up --build -d
docker compose ps
```

- Inference API: `http://localhost:8000/health`
- MLflow server: `http://localhost:5000`
- Compose also runs a one-time `mlflow-bootstrap` job that seeds a sample
  registered model (`churn-model`) and transitions its latest version to
  `Production`.

Get seeded version from bootstrap logs:

```bash
docker compose logs mlflow-bootstrap
```

Then verify model approval from the app CLI:

```bash
python -m mlops_platform.lifecycle.cli verify-mlflow \
  --model-name churn-model \
  --model-version <SEEDED_VERSION> \
  --allowed-stage Production
```

Run an MLflow experiment smoke test:

```bash
python scripts/test_mlflow_experiment.py
```

Optional custom values:

```bash
python scripts/test_mlflow_experiment.py \
  --tracking-uri http://localhost:5000 \
  --experiment local-mlflow-smoke \
  --run-name smoke-run-1 \
  --steps 8
```

To stop:

```bash
docker compose down
```

## Repository Structure

```text
.
├── .github/workflows/                # CI/CD pipeline
├── docs/                             # architecture and operations docs
├── infra/terraform/                  # IaC modules and env overlays
├── perf/                             # load testing scripts
├── src/mlops_platform/
│   ├── api/                          # sync + async inference endpoints
│   ├── deployment/                   # strategies and rollback mechanisms
│   ├── lifecycle/                    # package, approve, promote, audit
│   ├── quality/                      # model + data validations
│   └── observability/                # event schemas
└── tests/                            # unit, integration, API, regression
```

## Key Workflows

- Package model artifact:
  `python -m mlops_platform.lifecycle.cli package --version 1.0.0`
- Approve model for release:
  `python -m mlops_platform.lifecycle.cli approve --version 1.0.0 --approver platform-ops`
- Promote to staging or production:
  `python -m mlops_platform.lifecycle.cli promote --version 1.0.0 --environment staging`
- Verify MLflow registry approval:
  `python -m mlops_platform.lifecycle.cli verify-mlflow --model-name churn-model --model-version 12 --allowed-stage Production`
- Deploy using canary:
  `python -m mlops_platform.deployment.cli deploy --strategy canary --target-version 1.0.0`
- Roll back:
  `python -m mlops_platform.deployment.cli rollback --reason "latency SLO breach"`

## Notes

- This repo provides an implementation scaffold and local execution model.
- Wire the Terraform modules and CI workflows to your AWS and Databricks accounts.
- MLflow/Databricks integration uses `DATABRICKS_HOST`, `DATABRICKS_TOKEN`, and
  optional `MLFLOW_TRACKING_URI`.
- Local Docker Compose sets `MLFLOW_TRACKING_URI=http://mlflow:5000` for the API
  container.
- See `docs/reference-architecture.md` and `docs/test-matrix.md`.
- Detailed architecture docs are available in:
  - `docs/ai-gateway.md`
  - `docs/architecture-overview.md`
  - `docs/architecture-components.md`
  - `docs/architecture-flows.md`
  - `docs/architecture-environments.md`
