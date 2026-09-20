from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime

from .strategies import DeploymentStrategy


@dataclass
class DeploymentState:
    active_version: str
    previous_version: str | None = None
    strategy: DeploymentStrategy = DeploymentStrategy.BLUE_GREEN
    traffic_weight_new: int = 100
    updated_at: datetime = datetime.now(UTC)


class DeploymentController:
    def __init__(self, current_version: str) -> None:
        self.state = DeploymentState(active_version=current_version)

    def deploy(self, *, target_version: str, strategy: DeploymentStrategy) -> DeploymentState:
        self.state.previous_version = self.state.active_version
        self.state.active_version = target_version
        self.state.strategy = strategy
        if strategy == DeploymentStrategy.CANARY:
            self.state.traffic_weight_new = 10
        elif strategy == DeploymentStrategy.SHADOW:
            self.state.traffic_weight_new = 0
        elif strategy == DeploymentStrategy.TRAFFIC_SHIFT:
            self.state.traffic_weight_new = 50
        else:
            self.state.traffic_weight_new = 100
        self.state.updated_at = datetime.now(UTC)
        return self.state

    def advance_traffic(self, percent: int) -> DeploymentState:
        if not 0 <= percent <= 100:
            raise ValueError("percent must be 0-100")
        self.state.traffic_weight_new = percent
        self.state.updated_at = datetime.now(UTC)
        return self.state

    def rollback(self) -> DeploymentState:
        if self.state.previous_version is None:
            raise ValueError("no previous deployment to roll back to")
        self.state.active_version, self.state.previous_version = (
            self.state.previous_version,
            self.state.active_version,
        )
        self.state.traffic_weight_new = 100
        self.state.updated_at = datetime.now(UTC)
        return self.state
