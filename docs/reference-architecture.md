# Reference Architecture

## Environment Separation

- `dev`, `test`, `staging`, and `prod` run in separate AWS accounts/workspaces.
- Databricks workspaces are mapped 1:1 to environment boundaries.
- Cross-environment promotion is controlled by dedicated IAM roles.

## Serving Patterns

- **Databricks Model Serving** for managed model APIs with MLflow-native registry.
- **SageMaker endpoints** for managed online inference and async inference.
- **EKS/ECS services** for custom containers, GPU serving, and advanced routing.
- **Lambda + API Gateway** for low-latency, low-throughput event-driven scoring.

## Inference Modes

- synchronous request/response APIs
- asynchronous queued jobs
- batch offline scoring
- streaming inference via event pipelines

## LLM Architecture

- hosted foundation model adapter
- open-source model serving on GPU workers
- fine-tuned model promotion via MLflow registry
- RAG pipeline with embeddings + vector index + prompt orchestration
- tool-calling and agentic orchestration layer with trace propagation

## Reliability and Recovery

- multi-AZ baseline for all production serving components
- optional multi-region failover for tier-1 services
- rollback-ready manifests for code/model/config/prompt/infra
- DR runbooks and routine failover simulations
