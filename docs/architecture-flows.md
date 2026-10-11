# Architecture Flows

## A) Model Promotion Flow

1. package artifact metadata into `PackageManifest`
2. approve model package (`ApprovalState.APPROVED`)
3. verify MLflow model version stage (Staging/Production by policy)
4. write promotion record with evidence URI
5. deploy chosen version with configured strategy

Primary implementation points:

- lifecycle service: `src/mlops_platform/lifecycle/service.py`
- lifecycle CLI: `src/mlops_platform/lifecycle/cli.py`

## B) Inference Request Flow

1. receive request at `/infer`, `/infer/async`, or `/infer/batch`
2. check circuit breaker state
3. apply rate limiting
4. validate input contract
5. execute model inference logic
6. return structured output with `model_version` and `trace_id`

Primary implementation points:

- API handler: `src/mlops_platform/api/app.py`
- resilience controls: `src/mlops_platform/api/controls.py`

## C) Deployment Rollout Flow

1. select target version and deployment strategy
2. set traffic weight baseline by strategy
3. optionally advance traffic weight manually
4. monitor SLOs/errors
5. roll back to previous stable version if needed

Primary implementation points:

- deployment controller: `src/mlops_platform/deployment/controller.py`

## D) Local Compose Bootstrap Flow

1. start MLflow server
2. run one-shot bootstrap to seed sample model in registry
3. start inference API after bootstrap success
4. run lifecycle CLI against local MLflow for verification

Primary implementation points:

- `docker-compose.yml`
- `src/mlops_platform/bootstrap/seed_mlflow.py`
