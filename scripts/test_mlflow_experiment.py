#!/usr/bin/env python3
from __future__ import annotations

import argparse
import random
from typing import Iterable

import mlflow


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Log a smoke-test MLflow experiment run to the configured tracking server."
    )
    parser.add_argument(
        "--tracking-uri",
        default="http://localhost:5000",
        help="MLflow tracking URI (default: http://localhost:5000)",
    )
    parser.add_argument(
        "--experiment",
        default="local-mlflow-smoke",
        help="Experiment name (default: local-mlflow-smoke)",
    )
    parser.add_argument(
        "--run-name",
        default="smoke-run",
        help="Run name (default: smoke-run)",
    )
    parser.add_argument(
        "--steps",
        type=int,
        default=5,
        help="Number of metric steps to log (default: 5)",
    )
    return parser.parse_args()


def _loss_series(steps: int) -> Iterable[tuple[int, float]]:
    for step in range(steps):
        # Small noise keeps runs realistic while still trending downward.
        loss = (1.0 / (step + 1)) + random.random() * 0.01
        yield step, loss


def main() -> None:
    args = _parse_args()
    mlflow.set_tracking_uri(args.tracking_uri)
    mlflow.set_experiment(args.experiment)

    with mlflow.start_run(run_name=args.run_name):
        mlflow.log_param("smoke_test", True)
        mlflow.log_param("steps", args.steps)
        for step, loss in _loss_series(args.steps):
            mlflow.log_metric("loss", loss, step=step)
        mlflow.log_metric("accuracy", 0.91)

    print(
        "MLflow smoke run logged successfully "
        f"(experiment={args.experiment}, run_name={args.run_name}, "
        f"tracking_uri={args.tracking_uri})"
    )


if __name__ == "__main__":
    main()
