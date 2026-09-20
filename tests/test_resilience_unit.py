import pytest

from mlops_platform.api.controls import CircuitBreaker, RateLimitExceeded, SlidingWindowRateLimiter


def test_rate_limiter_blocks_when_exceeded():
    limiter = SlidingWindowRateLimiter(max_requests=1, window_seconds=60)
    limiter.check()
    with pytest.raises(RateLimitExceeded):
        limiter.check()


def test_circuit_breaker_opens_after_failures():
    breaker = CircuitBreaker(failure_threshold=2)
    breaker.on_failure()
    breaker.on_failure()
    assert breaker.is_open is True
