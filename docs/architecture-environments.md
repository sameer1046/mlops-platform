# Environment Architecture

## Environment Separation Model

Recommended environment tiers:

- `dev`
- `test`
- `staging`
- `prod`

Each environment should isolate:

- IAM roles and credentials
- network boundaries and endpoint access
- model registry promotion permissions
- config and secret values

## Promotion Policy

- train/register in lower environments
- promote immutable artifacts upward
- deny production deploys unless lifecycle + MLflow checks pass

## Terraform Overlay Strategy

Use per-environment overlays in `infra/terraform/envs/` with shared modules in
`infra/terraform/modules/`.

Benefits:

- consistent base architecture
- environment-specific parameterization
- traceable infra drift via VCS

## Release Controls by Environment

- **Dev/Test:** flexible rollout, higher iteration speed
- **Staging:** production-like validation, full regression/performance gates
- **Prod:** controlled rollout + rollback-ready + mandatory audit evidence

## RTO/RPO Design Guidance

Define service tiers and map each endpoint/model class to RTO/RPO targets.
For business-critical endpoints, implement:

- multi-AZ baseline
- automated failover checks
- tested restore runbooks for model/artifact/config state
