from __future__ import annotations

import argparse
import json

from .controller import DeploymentController
from .strategies import DeploymentStrategy


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="MLOps deployment controller")
    parser.add_argument("--current-version", default="0.0.0")
    sub = parser.add_subparsers(dest="command", required=True)

    deploy = sub.add_parser("deploy")
    deploy.add_argument("--target-version", required=True)
    deploy.add_argument(
        "--strategy",
        required=True,
        choices=[s.value for s in DeploymentStrategy],
    )

    shift = sub.add_parser("shift")
    shift.add_argument("--percent", required=True, type=int)

    sub.add_parser("rollback")
    return parser


def _to_json(result: object) -> str:
    return json.dumps(result.__dict__, indent=2, default=str)


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    controller = DeploymentController(current_version=args.current_version)

    if args.command == "deploy":
        result = controller.deploy(
            target_version=args.target_version,
            strategy=DeploymentStrategy(args.strategy),
        )
    elif args.command == "shift":
        result = controller.advance_traffic(args.percent)
    else:
        result = controller.rollback()
    print(_to_json(result))


if __name__ == "__main__":
    main()
