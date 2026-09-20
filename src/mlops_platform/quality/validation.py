from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ModelValidationResult:
    auc: float
    rmse: float
    drift_score: float
    passed: bool


def validate_model(*, auc: float, rmse: float, drift_score: float) -> ModelValidationResult:
    passed = auc >= 0.75 and rmse <= 0.8 and drift_score <= 0.2
    return ModelValidationResult(auc=auc, rmse=rmse, drift_score=drift_score, passed=passed)
