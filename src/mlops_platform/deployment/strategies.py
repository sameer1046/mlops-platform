from __future__ import annotations

from enum import StrEnum


class DeploymentStrategy(StrEnum):
    BLUE_GREEN = "blue-green"
    CANARY = "canary"
    SHADOW = "shadow"
    TRAFFIC_SHIFT = "traffic-shift"
