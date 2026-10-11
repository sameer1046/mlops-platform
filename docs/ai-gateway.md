# AI Gateway

## Purpose

The AI gateway provides a stable interface between application APIs and LLM
providers. It centralizes:

- provider routing
- fallback behavior
- policy checks (tenant and token limits)
- telemetry hooks for request outcomes

## Module Layout

- `src/mlops_platform/ai_gateway/models.py`
  - request/response types
  - route and policy models
- `src/mlops_platform/ai_gateway/providers.py`
  - provider protocol
  - sample providers (`FlakyProvider`, `EchoProvider`)
- `src/mlops_platform/ai_gateway/router.py`
  - routing + fallback engine (`AIGateway`)
- `src/mlops_platform/ai_gateway/telemetry.py`
  - telemetry event schema and sink protocol

## Runtime Behavior

1. API receives `/chat` request.
2. Gateway enforces policy constraints.
3. Gateway calls primary provider route.
4. If provider fails, gateway falls back to next route.
5. Telemetry events are emitted for failures/success.

## Next Integration Step

Replace sample providers with real adapters:

- Databricks Model Serving
- Amazon Bedrock / OpenAI
- self-hosted vLLM/TGI endpoint
