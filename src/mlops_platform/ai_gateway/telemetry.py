from __future__ import annotations

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
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))


class TelemetrySink(Protocol):
    def emit(self, event: GatewayTelemetryEvent) -> None:
        """Store or publish telemetry event."""


@dataclass
class InMemoryTelemetrySink:
    events: list[GatewayTelemetryEvent] = field(default_factory=list)

    def emit(self, event: GatewayTelemetryEvent) -> None:
        self.events.append(event)
