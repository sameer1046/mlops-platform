from __future__ import annotations

from dataclasses import dataclass
from time import monotonic

from .models import ChatRequest, ChatResponse, GatewayPolicy, make_trace_id
from .providers import LLMProvider, ProviderError
from .telemetry import GatewayTelemetryEvent, TelemetrySink


@dataclass
class AIGateway:
    providers: dict[str, LLMProvider]
    policy: GatewayPolicy
    telemetry: TelemetrySink

    def generate(self, request: ChatRequest) -> ChatResponse:
        self.policy.enforce(request)
        trace_id = make_trace_id()
        last_error = ""
        for index, route in enumerate(self.policy.routes):
            provider = self.providers.get(route.provider_name)
            if provider is None:
                last_error = f"unknown provider: {route.provider_name}"
                self.telemetry.emit(
                    GatewayTelemetryEvent(
                        event_type="provider_missing",
                        provider=route.provider_name,
                        model_id=route.model_id,
                        trace_id=trace_id,
                        detail=last_error,
                    )
                )
                continue
            start_time = monotonic()
            try:
                completion = provider.generate(request=request, model_id=route.model_id)
                duration_ms = (monotonic() - start_time) * 1000.0
                self.telemetry.emit(
                    GatewayTelemetryEvent(
                        event_type="request_succeeded",
                        provider=route.provider_name,
                        model_id=route.model_id,
                        trace_id=trace_id,
                        prompt=request.prompt,
                        completion=completion,
                        latency_ms=duration_ms,
                    )
                )
                return ChatResponse(
                    completion=completion,
                    provider=route.provider_name,
                    model_id=route.model_id,
                    trace_id=trace_id,
                    fallback_used=index > 0,
                )
            except ProviderError as exc:
                duration_ms = (monotonic() - start_time) * 1000.0
                last_error = str(exc)
                self.telemetry.emit(
                    GatewayTelemetryEvent(
                        event_type="request_failed",
                        provider=route.provider_name,
                        model_id=route.model_id,
                        trace_id=trace_id,
                        detail=last_error,
                        prompt=request.prompt,
                        latency_ms=duration_ms,
                    )
                )
        raise ProviderError(f"all gateway routes failed: {last_error}")
