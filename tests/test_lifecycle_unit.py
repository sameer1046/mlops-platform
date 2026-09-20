from mlops_platform.lifecycle.service import approve_model, package_model, promote_model


def test_package_approve_promote_roundtrip(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    package_model(
        version="1.0.0",
        code_sha="abc123",
        image_uri="ecr/repo:1.0.0",
        prompt_bundle_version="p1",
        config_version="c1",
        created_by="dev1",
    )
    manifest = approve_model(version="1.0.0", approver="release-manager")
    assert manifest.state == "approved"

    record = promote_model(
        version="1.0.0",
        from_environment="test",
        to_environment="staging",
        promoted_by="release-bot",
        evidence_uri="s3://bucket/evidence.json",
    )
    assert record.to_environment == "staging"


class _FakeRegistryClient:
    def __init__(self, approved: bool):
        self._approved = approved

    def is_model_approved(self, **_: object) -> bool:
        return self._approved


def test_promote_rejects_unapproved_mlflow_model(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    package_model(
        version="1.0.1",
        code_sha="abc123",
        image_uri="ecr/repo:1.0.1",
        prompt_bundle_version="p1",
        config_version="c1",
        created_by="dev1",
    )
    approve_model(version="1.0.1", approver="release-manager")
    try:
        promote_model(
            version="1.0.1",
            from_environment="test",
            to_environment="staging",
            promoted_by="release-bot",
            evidence_uri="s3://bucket/evidence.json",
            model_name="churn-model",
            model_registry_version="7",
            registry_client=_FakeRegistryClient(approved=False),
        )
        assert False, "expected promotion failure"
    except ValueError as exc:
        assert "is not in approved stages" in str(exc)


def test_promote_accepts_approved_mlflow_model(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    package_model(
        version="1.0.2",
        code_sha="abc123",
        image_uri="ecr/repo:1.0.2",
        prompt_bundle_version="p1",
        config_version="c1",
        created_by="dev1",
    )
    approve_model(version="1.0.2", approver="release-manager")
    record = promote_model(
        version="1.0.2",
        from_environment="test",
        to_environment="staging",
        promoted_by="release-bot",
        evidence_uri="s3://bucket/evidence.json",
        model_name="churn-model",
        model_registry_version="8",
        registry_client=_FakeRegistryClient(approved=True),
    )
    assert record.to_environment == "staging"
