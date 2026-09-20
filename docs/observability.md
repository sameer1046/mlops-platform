# Observability and SLOs

## Core SLIs

- availability
- request volume and throughput
- latency (P50/P95/P99)
- error rate and saturation
- token usage and cost per request (LLM endpoints)

## Model/LLM Quality Signals

- prediction distributions
- data drift and concept drift indicators
- response quality and hallucination rate
- prompt and response safety events

## Tracing

- trace IDs propagated from API edge through retrieval/orchestration/model calls
- structured logs for root-cause analysis
- release/deployment metadata attached to traces

## Alerting

- latency and error SLO violation alerts
- model quality regression alerts
- cost anomaly alerts
- missing-heartbeat alerts for async workers and schedulers
