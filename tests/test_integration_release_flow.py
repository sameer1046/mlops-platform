from mlops_platform.deployment.controller import DeploymentController
from mlops_platform.deployment.strategies import DeploymentStrategy
from mlops_platform.lifecycle.service import approve_model, package_model


def test_release_flow_integration(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    package_model(
        version="2.0.0",
        code_sha="sha2",
        image_uri="ecr/repo:2.0.0",
        prompt_bundle_version="p2",
        config_version="c2",
        created_by="ml-engineer",
    )
    approve_model(version="2.0.0", approver="ops-lead")
    controller = DeploymentController(current_version="1.9.0")
    state = controller.deploy(target_version="2.0.0", strategy=DeploymentStrategy.CANARY)
    assert state.active_version == "2.0.0"
    assert state.traffic_weight_new == 10
