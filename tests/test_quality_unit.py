import pytest
from pydantic import ValidationError

from mlops_platform.quality.contracts import validate_data_contract
from mlops_platform.quality.validation import validate_model


def test_data_contract_validation_success():
    req = validate_data_contract({"user_id": "u1", "features": {"f1": 1.0}})
    assert req.user_id == "u1"


def test_data_contract_validation_failure():
    with pytest.raises(ValidationError):
        validate_data_contract({"user_id": "", "features": {"f1": 1.0}})


def test_model_validation_thresholds():
    ok = validate_model(auc=0.8, rmse=0.5, drift_score=0.1)
    bad = validate_model(auc=0.7, rmse=0.9, drift_score=0.4)
    assert ok.passed is True
    assert bad.passed is False
