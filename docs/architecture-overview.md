# Architecture Overview

## Purpose

This project is a reference MLOps platform for AWS + Databricks with:

- model lifecycle controls (package, approve, promote)
- deployment strategy controls (blue/green, canary, shadow, traffic shift)
- secure API serving patterns (sync, async, batch)
- quality, observability, and governance guardrails

It is intentionally split into:

- **Control plane** responsibilities (model registry, approvals, promotion, audit)
- **Data plane** responsibilities (inference request handling and rollout traffic)

## Scope Boundaries

### In Scope

- MLOps workflow orchestration at application level
- rollout and rollback behavior
- MLflow approval checks and local registry bootstrap
- CI/CD stage wiring and test categories
- Terraform scaffolding for environment overlays

### Out of Scope (Current Scaffold)

- production-grade Kubernetes ingress/service mesh policies
- production Databricks workspace automation and account bootstrap
- full feature store and vector index provisioning
- advanced multi-region state replication implementation

## Repository-to-Architecture Mapping

| Area | Path | Architectural Concern |
|---|---|---|
| Inference API | `src/mlops_platform/api/` | runtime request handling and resilience |
| Lifecycle | `src/mlops_platform/lifecycle/` | model package/approve/promote governance |
| Rollouts | `src/mlops_platform/deployment/` | strategy selection and rollback control |
| Quality gates | `src/mlops_platform/quality/` | data contract and model threshold checks |
| Observability schema | `src/mlops_platform/observability/` | audit event contract |
| IaC skeleton | `infra/terraform/` | environment-specific platform provisioning |
| CI/CD | `.github/workflows/` | automated gates and release checks |

## Current Runtime Topology (Local)

Docker Compose deploys:

1. `mlflow` server for registry and metadata
2. `mlflow-bootstrap` one-shot seed job
3. `inference-api` FastAPI service

This local topology simulates control/data plane interactions before AWS
deployment.

## Target Runtime Topology (Cloud)

- **API edge**: API Gateway and/or ALB
- **Online serving**: EKS/ECS/SageMaker/Databricks Model Serving
- **Registry**: MLflow registry (Databricks-backed)
- **Artifacts**: object storage-backed model artifacts
- **Telemetry**: metrics/logs/traces and alert pipelines

See `reference-architecture.md` for high-level deployment target details.
