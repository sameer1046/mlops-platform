# Architecture Components

## 1) Inference API Layer

**Path:** `src/mlops_platform/api/`

Responsibilities:

- exposes health, sync inference, async enqueue, and batch endpoints
- enforces request schema validation via data contracts
- applies runtime protection controls (rate limiter, circuit breaker)
- emits deterministic response envelope (prediction, model version, trace id)

Design intent:

- keep the API contract stable while swapping underlying model backends
- centralize graceful degradation behavior at the serving edge

## 2) Lifecycle Governance Layer

**Path:** `src/mlops_platform/lifecycle/`

Responsibilities:

- builds immutable package manifests
- records approval state transitions
- records environment promotions with evidence URI
- validates MLflow stage approvals before promotion

Design intent:

- enforce deployment-by-artifact, not deployment-by-rebuild
- keep audit trail for who approved and what was promoted

## 3) Deployment Strategy Layer

**Path:** `src/mlops_platform/deployment/`

Responsibilities:

- models active/previous release state
- supports rollout modes:
  - blue/green
  - canary
  - shadow
  - controlled traffic shifting
- supports rollback to previously active release

Design intent:

- make strategy behavior explicit and testable before infra integration

## 4) Quality and Contract Layer

**Path:** `src/mlops_platform/quality/`

Responsibilities:

- validates request contracts (`InferenceRequest`)
- defines response contract (`InferenceResponse`)
- evaluates model quality thresholds (AUC, RMSE, drift)

Design intent:

- prevent invalid inputs from entering the model path
- codify objective promotion criteria

## 5) Observability Contract Layer

**Path:** `src/mlops_platform/observability/`

Responsibilities:

- defines typed audit event model with actor and trace ID

Design intent:

- preserve traceability from pipeline and runtime actions

## 6) Infrastructure and Delivery Layer

**Paths:** `infra/terraform/`, `.github/workflows/`

Responsibilities:

- provides Terraform skeleton for env overlays
- provides CI/CD execution order for quality/performance/release gates

Design intent:

- enforce repeatable, versioned infrastructure and deploy controls
