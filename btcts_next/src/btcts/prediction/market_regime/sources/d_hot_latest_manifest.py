# path: ./btcts_next/src/btcts/prediction/market_regime/sources/d_hot_latest_manifest.py
# desc: Read-only latest prediction manifest resolver for market-regime source snapshots.

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

from ..source_snapshot import JsonSourceArtifact
from .json_io import read_json_artifact

LATEST_MANIFEST_RELATIVE_PATH = "prediction/latest_manifest.json"
LATEST_PREDICTION_FALLBACK_RELATIVE_PATH = "prediction/latest_prediction_system_result.json"


def load_latest_manifest(hot_root: str | Path) -> JsonSourceArtifact:
    return read_json_artifact(hot_root, LATEST_MANIFEST_RELATIVE_PATH)


def resolve_latest_prediction_relative_path(manifest: Mapping[str, Any]) -> str:
    value = manifest.get("legacy_latest_path") or manifest.get("legacy_latest_relative_path")
    return str(value or LATEST_PREDICTION_FALLBACK_RELATIVE_PATH).replace("\\", "/")


def resolve_forecast_records_relative_path(manifest: Mapping[str, Any]) -> str | None:
    sidecars = manifest.get("sidecars")
    if isinstance(sidecars, Mapping):
        value = sidecars.get("forecast_records")
        if value:
            return str(value).replace("\\", "/")
    value = manifest.get("forecast_records") or manifest.get("source_records_path")
    if value:
        return str(value).replace("\\", "/")
    return None
