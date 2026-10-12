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

## Endpoints & UIs

- **Built-in Chat UI**: `GET /` or `GET /ui` (browser chat interface with prompt chips, live metrics, and MLflow trace links).
- **Native Gateway Chat API**: `POST /chat` with `{"tenant_id": "...", "prompt": "..."}`.
- **OpenAI & OpenUI Compatible API**: `POST /v1/chat/completions` with standard `{"model": "...", "messages": [...]}` payload.
- **MLflow Tracing**: all chat calls automatically generate GenAI Traces in the `ai-gateway` experiment at `http://localhost:5000`.

## NVIDIA API Provider

`NvidiaProvider` calls the OpenAI-compatible endpoint
`https://integrate.api.nvidia.com/v1/chat/completions`.

When `NVIDIA_API_KEY` is set, calls route to NVIDIA first (`meta/llama-3.2-11b-vision-instruct`)
and fall back to the echo provider if the call fails. Without the key, the sample providers are
used.

| Variable | Default | Purpose |
|---|---|---|
| `NVIDIA_API_KEY` | unset | Bearer token (required to enable NVIDIA) |
| `NVIDIA_MODEL_ID` | `meta/llama-3.2-11b-vision-instruct` | Model to call |
| `NVIDIA_BASE_URL` | `https://integrate.api.nvidia.com/v1` | API base URL |
| `NVIDIA_VERIFY_SSL` | `true` (`false` in compose) | SSL cert verification |

Never commit the key. Put it in a git-ignored `.env` file next to
`docker-compose.yml`, which Compose reads automatically.

## OpenUI Integration

[OpenUI](https://www.openui.com/) by Thesys is an open standard for Intelligent / Generative UI.
Because the gateway exposes standard `POST /v1/chat/completions`, any OpenUI client, agent, or
SDK can connect directly by configuring its base URL:

```javascript
const client = new OpenAI({
  baseURL: "http://localhost:8000/v1",
  apiKey: "optional-or-ignored"
});
```

The gateway routes the request through policy enforcement, invokes NVIDIA NIM, applies fallback
protection, and records the trace in MLflow.

## Next Integration Step

Add more real adapters:

- Databricks Model Serving
- Amazon Bedrock
- self-hosted vLLM/TGI endpoint
