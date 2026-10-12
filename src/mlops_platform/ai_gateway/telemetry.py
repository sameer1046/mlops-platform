from __future__ import annotations

import os
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Protocol


@dataclass
class GatewayTelemetryEvent:
    event_type: str
    provider: str
    model_id: str
    trace_id: str
    detail: str = ""
    prompt: str = ""
    completion: str = ""
    latency_ms: float = 0.0
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))


class TelemetrySink(Protocol):
    def emit(self, event: GatewayTelemetryEvent) -> None:
        """Store or publish telemetry event."""


@dataclass
class InMemoryTelemetrySink:
    events: list[GatewayTelemetryEvent] = field(default_factory=list)

    def emit(self, event: GatewayTelemetryEvent) -> None:
        self.events.append(event)


@dataclass
class MLflowTelemetrySink:
    tracking_uri: str = "http://localhost:5000"
    experiment_name: str = "ai-gateway"
    enabled: bool = True

    def emit(self, event: GatewayTelemetryEvent) -> None:
        if not self.enabled or not self.tracking_uri:
            return
        if os.getenv("MLFLOW_TELEMETRY_ENABLED", "true").lower() in ("false", "0", "no"):
            return
        try:
            import mlflow

            mlflow.set_tracking_uri(self.tracking_uri)
            mlflow.set_experiment(self.experiment_name)

            if hasattr(mlflow, "start_span"):
                with mlflow.start_span(name=f"{event.provider}_chat") as span:
                    span.set_inputs({"prompt": event.prompt})
                    span.set_attributes(
                        {
                            "provider": event.provider,
                            "model_id": event.model_id,
                            "trace_id": event.trace_id,
                            "event_type": event.event_type,
                            "latency_ms": event.latency_ms,
                        }
                    )
                    if event.event_type == "request_succeeded":
                        span.set_outputs({"completion": event.completion, "status": "ok"})
                    else:
                        span.set_outputs({"error": event.detail, "status": "failed"})
        except Exception:
            pass


@dataclass
class CompositeTelemetrySink:
    sinks: list[TelemetrySink] = field(default_factory=list)

    def emit(self, event: GatewayTelemetryEvent) -> None:
        for sink in self.sinks:
            try:
                sink.emit(event)
            except Exception:
                pass
