from __future__ import annotations

import json
from pathlib import Path

from .models import PackageManifest, PromotionRecord

ROOT = Path(".mlops_state")
PACKAGES = ROOT / "packages"
PROMOTIONS = ROOT / "promotions"


def _ensure_dirs() -> None:
    PACKAGES.mkdir(parents=True, exist_ok=True)
    PROMOTIONS.mkdir(parents=True, exist_ok=True)


def save_package(manifest: PackageManifest) -> Path:
    _ensure_dirs()
    target = PACKAGES / f"{manifest.model_version}.json"
    target.write_text(manifest.model_dump_json(indent=2), encoding="utf-8")
    return target


def load_package(version: str) -> PackageManifest:
    target = PACKAGES / f"{version}.json"
    raw = json.loads(target.read_text(encoding="utf-8"))
    return PackageManifest.model_validate(raw)


def save_promotion(record: PromotionRecord) -> Path:
    _ensure_dirs()
    target = PROMOTIONS / f"{record.model_version}-{record.to_environment}.json"
    target.write_text(record.model_dump_json(indent=2), encoding="utf-8")
    return target
