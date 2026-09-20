from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from time import monotonic


class RateLimitExceeded(Exception):
    pass


@dataclass
class SlidingWindowRateLimiter:
    max_requests: int
    window_seconds: int
    events: deque[float] = field(default_factory=deque)

    def check(self) -> None:
        now = monotonic()
        while self.events and now - self.events[0] > self.window_seconds:
            self.events.popleft()
        if len(self.events) >= self.max_requests:
            raise RateLimitExceeded("rate limit exceeded")
        self.events.append(now)


@dataclass
class CircuitBreaker:
    failure_threshold: int = 3
    consecutive_failures: int = 0
    is_open: bool = False

    def on_success(self) -> None:
        self.consecutive_failures = 0
        self.is_open = False

    def on_failure(self) -> None:
        self.consecutive_failures += 1
        if self.consecutive_failures >= self.failure_threshold:
            self.is_open = True
