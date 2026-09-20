from __future__ import annotations

import argparse
import json
import sys

from .service import approve_model, package_model, promote_model, verify_mlflow_approval


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="MLOps lifecycle CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    pack = sub.add_parser("package")
    pack.add_argument("--version", required=True)
    pack.add_argument("--code-sha", default="local-dev")
    pack.add_argument("--image-uri", default="local/image:latest")
    pack.add_argument("--prompt-bundle-version", default="p1")
    pack.add_argument("--config-version", default="c1")
    pack.add_argument("--created-by", default="local-user")
    pack.add_argument("--mlflow-model-name")
    pack.add_argument("--mlflow-model-version")

    approve = sub.add_parser("approve")
    approve.add_argument("--version", required=True)
    approve.add_argument("--approver", required=True)
    approve.add_argument("--mlflow-stage", default=None)

    promote = sub.add_parser("promote")
    promote.add_argument("--version", required=True)
    promote.add_argument("--from-environment", default="test")
    promote.add_argument("--environment", required=True)
    promote.add_argument("--promoted-by", default="release-bot")
    promote.add_argument("--evidence-uri", default="s3://evidence/local.json")
    promote.add_argument("--model-name", default=None)
    promote.add_argument("--model-registry-version", default=None)
    promote.add_argument(
        "--allowed-stage",
        action="append",
        default=None,
        help="May be passed multiple times",
    )

    verify = sub.add_parser("verify-mlflow")
    verify.add_argument("--model-name", required=True)
    verify.add_argument("--model-version", required=True)
    verify.add_argument(
        "--allowed-stage",
        action="append",
        default=None,
        help="May be passed multiple times",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "package":
        result = package_model(
            version=args.version,
            code_sha=args.code_sha,
            image_uri=args.image_uri,
            prompt_bundle_version=args.prompt_bundle_version,
            config_version=args.config_version,
            created_by=args.created_by,
            mlflow_model_name=args.mlflow_model_name,
            mlflow_model_version=args.mlflow_model_version,
        )
    elif args.command == "approve":
        result = approve_model(
            version=args.version,
            approver=args.approver,
            mlflow_stage=args.mlflow_stage,
        )
    elif args.command == "verify-mlflow":
        allowed_stages = tuple(args.allowed_stage or ["Staging", "Production"])
        result = verify_mlflow_approval(
            model_name=args.model_name,
            model_version=args.model_version,
            allowed_stages=allowed_stages,
        )
        print(json.dumps(result.__dict__, indent=2, default=str))
        if not result.approved:
            sys.exit(2)
        return
    else:
        allowed_stages = tuple(args.allowed_stage or ["Staging", "Production"])
        result = promote_model(
            version=args.version,
            from_environment=args.from_environment,
            to_environment=args.environment,
            promoted_by=args.promoted_by,
            evidence_uri=args.evidence_uri,
            model_name=args.model_name,
            model_registry_version=args.model_registry_version,
            allowed_stages=allowed_stages,
        )

    print(json.dumps(result.model_dump(mode="json"), indent=2, default=str))


if __name__ == "__main__":
    main()
