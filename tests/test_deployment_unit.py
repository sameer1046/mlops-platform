import pytest

from mlops_platform.deployment.controller import DeploymentController
from mlops_platform.deployment.strategies import DeploymentStrategy


def test_canary_sets_initial_traffic():
    c = DeploymentController(current_version="1.0.0")
    state = c.deploy(target_version="1.1.0", strategy=DeploymentStrategy.CANARY)
    assert state.traffic_weight_new == 10


def test_rollback_to_previous():
    c = DeploymentController(current_version="1.0.0")
    c.deploy(target_version="1.1.0", strategy=DeploymentStrategy.BLUE_GREEN)
    state = c.rollback()
    assert state.active_version == "1.0.0"


def test_invalid_shift_rejected():
    c = DeploymentController(current_version="1.0.0")
    with pytest.raises(ValueError):
        c.advance_traffic(101)
