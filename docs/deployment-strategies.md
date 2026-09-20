# Deployment Strategies and Recovery

## Supported Strategies

- **Blue/Green**: swap stable and candidate environments.
- **Canary**: progressive exposure (10%, 25%, 50%, 100%).
- **Shadow**: mirror production requests to candidate without serving responses.
- **Traffic Shift**: weighted split based on latency/error SLOs.

## Rollback and Roll-Forward Scope

- application image versions
- model versions in registry
- prompt bundle versions
- environment configuration
- infrastructure module versions

## Recoverability Rules

- All deploys are immutable and versioned.
- Every deployment writes an audit event with traceable evidence.
- Rollback to previous known-good release must be one command.
- Roll-forward must pass the same lifecycle test gates as initial rollout.
