# MLOps Platform

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

- **Web Chat UI**: `http://localhost:8000/` (or `http://localhost:8000/ui`)
- **Inference & Health API**: `http://localhost:8000/health` (Swagger docs at `/docs`)
- **OpenAI & OpenUI Endpoint**: `http://localhost:8000/v1/chat/completions`
- **MLflow Tracking & Tracing UI**: `http://localhost:5000`
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

## How It Works

### Core Architecture

The platform decouples request serving (data plane) from lifecycle and promotion governance (control plane):

```text
                  ┌────────────────────────────────────────┐
                  │              FastAPI API               │
                  │        (src/mlops_platform/api/)       │
                  └───────────┬────────────────┬───────────┘
                              │                │
            /infer, /infer/batch               │ /chat
                              │                │
                              ▼                ▼
┌───────────────────────────────┐   ┌────────────────────────────────┐
│      Traditional Scoring      │   │           AI Gateway           │
│ (src/mlops_platform/quality/) │   │ (src/mlops_platform/ai_gateway)│
│    Contract validation +      │   │   Routes to NVIDIA API         │
│    feature-average mock       │   │   Fallback to EchoProvider     │
└───────────────────────────────┘   └────────────────────────────────┘

────────────────────── CONTROL PLANE ──────────────────────────────
┌───────────────────────────────┐   ┌────────────────────────────────┐
│      Lifecycle Engine         │   │     Deployment Controller      │
│(src/mlops_platform/lifecycle/)│   │(src/mlops_platform/deployment/)│
│   Package -> Approve ->       │   │   Canary, Blue/Green, Shadow,  │
│   Verify MLflow -> Promote    │   │   Traffic Shift + Rollback     │
└───────────────────────────────┘   └────────────────────────────────┘
```

### Key Subsystems

1. **Inference API & Resilience (`src/mlops_platform/api/`)**:
   - Synchronous (`/infer`), async queued (`/infer/async`), and batch (`/infer/batch`) tabular inference.
   - LLM chat completions (`/chat`) routed through the AI Gateway.
   - Built-in `SlidingWindowRateLimiter` (default: 200 req / 60s) and `CircuitBreaker` (trips after 3 consecutive failures to 503).

2. **AI Gateway (`src/mlops_platform/ai_gateway/`)**:
   - Centralized policy enforcement (tenant validation, max token budget).
   - Multi-route provider chain: calls `NvidiaProvider` (`https://integrate.api.nvidia.com/v1`) when `NVIDIA_API_KEY` is configured, automatically falling back to `EchoProvider` on failure (`fallback_used: true`).
   - Emits structured telemetry events (`InMemoryTelemetrySink`) tracking provider usage, latencies, and fallback activations.

3. **Lifecycle & Promotion Governance (`src/mlops_platform/lifecycle/`)**:
   - Enforces deployment-by-artifact rather than retraining in higher environments.
   - State machine: `package` (CANDIDATE) -> `approve` (APPROVED) -> `verify-mlflow` (checks registry stage/alias) -> `promote` (records evidence URI).
   - `MLflowRegistryClient` manages tracking and stage transitions against local MLflow or Databricks workspaces.

4. **Deployment Strategies (`src/mlops_platform/deployment/`)**:
   - `DeploymentController` manages version switching and traffic allocation.
   - Supports `blue-green` (100%), `canary` (10% initial, adjustable via `shift`), `shadow` (0% mirrored), and `traffic-shift` (50%).
   - Immediate single-command `rollback` swapping active to prior known-good version with 100% traffic restored.

5. **CI/CD Quality Gates (`.github/workflows/mlops-ci-cd.yml`)**:
   - 5-stage pipeline: unit tests -> integration & API -> regression & security -> performance smoke (< 2.0s for 200 reqs) -> release controls (MLflow stage check + immutable packaging).

### End-to-End Release Flow

1. **Train & Register**: Model artifacts and metrics logged to MLflow experiment runs.
2. **Validate**: CI runs test matrix (unit, integration, regression, security, perf).
3. **Approve & Package**: Model version transitioned in MLflow registry and packaged into an immutable `PackageManifest`.
4. **Deploy**: Selected rollout strategy (e.g. 10% canary) deployed via `DeploymentController`.
5. **Serve**: Real-time traffic served with rate-limiting, circuit-breaking, and AI Gateway routing.
6. **Recover**: If SLOs degrade, operator triggers single-command rollback to last known-good release.

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
