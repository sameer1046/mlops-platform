from mlops_platform.ai_gateway.models import ChatRequest, GatewayPolicy, GatewayRoute
from mlops_platform.ai_gateway.providers import EchoProvider, FlakyProvider, ProviderError
from mlops_platform.ai_gateway.router import AIGateway
from mlops_platform.ai_gateway.telemetry import InMemoryTelemetrySink


def test_gateway_uses_primary_route_successfully():
    telemetry = InMemoryTelemetrySink()
    gateway = AIGateway(
        providers={
            "primary": FlakyProvider(provider_name="primary"),
            "fallback": EchoProvider(provider_name="fallback"),
        },
        policy=GatewayPolicy(
            routes=[
                GatewayRoute(provider_name="primary", model_id="m1"),
                GatewayRoute(provider_name="fallback", model_id="m2"),
            ]
        ),
        telemetry=telemetry,
    )
    response = gateway.generate(ChatRequest(tenant_id="t1", prompt="hello"))
    assert response.provider == "primary"
    assert response.fallback_used is False
    assert telemetry.events[-1].event_type == "request_succeeded"


def test_gateway_falls_back_when_primary_fails():
    telemetry = InMemoryTelemetrySink()
    gateway = AIGateway(
        providers={
            "primary": FlakyProvider(provider_name="primary"),
            "fallback": EchoProvider(provider_name="fallback"),
        },
        policy=GatewayPolicy(
            routes=[
                GatewayRoute(provider_name="primary", model_id="m1"),
                GatewayRoute(provider_name="fallback", model_id="m2"),
            ]
        ),
        telemetry=telemetry,
    )
    response = gateway.generate(ChatRequest(tenant_id="t1", prompt="[force-fail] hello"))
    assert response.provider == "fallback"
    assert response.fallback_used is True
    assert any(e.event_type == "request_failed" for e in telemetry.events)


def test_gateway_fails_if_all_routes_fail():
    telemetry = InMemoryTelemetrySink()
    gateway = AIGateway(
        providers={"primary": FlakyProvider(provider_name="primary", failure_marker="")},
        policy=GatewayPolicy(routes=[GatewayRoute(provider_name="primary", model_id="m1")]),
        telemetry=telemetry,
    )
    try:
        gateway.generate(ChatRequest(tenant_id="t1", prompt="hello"))
        assert False, "expected ProviderError when all routes fail"
    except ProviderError:
        assert True
