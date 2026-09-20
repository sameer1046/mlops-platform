from mlops_platform.api.app import infer


def test_prediction_regression_baseline():
    out = infer({"user_id": "u1", "features": {"x": 2.0, "y": 4.0}})
    assert out.prediction == 3.0
