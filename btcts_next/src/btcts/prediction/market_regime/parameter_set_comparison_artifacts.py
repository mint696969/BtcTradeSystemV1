# path: ./btcts_next/src/btcts/prediction/market_regime/parameter_set_comparison_artifacts.py
# desc: Market-regime parameter-set comparison read-model artifact writer. Reads outcome rows and writes only the comparison read model artifact; no raw market read, scheduler, broker, AutoTrade, or parameter mutation.

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from .calibration_summary import read_market_regime_outcome_rows
from .parameter_set_comparison_read_model import (
    MARKET_REGIME_PARAMETER_SET_COMPARISON_READ_MODEL_VERSION,
    build_market_regime_parameter_set_comparison_read_model_from_outcome_rows,
    validate_market_regime_parameter_set_comparison_read_model,
)
from .parameter_set_registry import MARKET_REGIME_DEFAULT_ACTIVE_PARAMETER_SET_ID

MARKET_REGIME_PARAMETER_SET_COMPARISON_ARTIFACT_WRITER_VERSION = "prediction.market_regime.parameter_set_comparison_artifacts.2026_07_09.v1"
PARAMETER_SET_COMPARISON_LATEST_READ_MODEL_RELPATH = "prediction/market_regime/parameter_set_comparison/latest_read_model.json"


def parameter_set_comparison_latest_read_model_relpath() -> str:
    return PARAMETER_SET_COMPARISON_LATEST_READ_MODEL_RELPATH


def parameter_set_comparison_outcome_part_relpath(date: str) -> str:
    return f"prediction/market_regime/outcomes/date={date}/part-00001.jsonl"


def _write_json_atomic(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    tmp.replace(path)


def _writer_safety() -> dict[str, Any]:
    return {
        "read_only_outcome_rows": True,
        "writes_parameter_set_comparison_read_model_only": True,
        "raw_market_data_read": False,
        "raw_market_data_duplicated": False,
        "scheduler_enabled": False,
        "producer_enabled": False,
        "broker_private_api_allowed": False,
        "autotrade_trigger_allowed": False,
        "order_intent_submitted": False,
        "parameter_auto_promotion_allowed": False,
        "live_parameter_apply_allowed": False,
        "human_gate_required_for_parameter_change": True,
        "would_send_to_broker": False,
    }


def build_market_regime_parameter_set_comparison_artifact_write_plan(
    root: str | Path,
    *,
    date: str,
    active_parameter_set_id: str = MARKET_REGIME_DEFAULT_ACTIVE_PARAMETER_SET_ID,
    min_trusted_samples: int = 20,
) -> dict[str, Any]:
    base = Path(root)
    outcome_relpath = parameter_set_comparison_outcome_part_relpath(date)
    rows = read_market_regime_outcome_rows(base, date=date)
    read_model = build_market_regime_parameter_set_comparison_read_model_from_outcome_rows(
        rows=rows,
        date_range={"date": date, "source_path": outcome_relpath},
        active_parameter_set_id=active_parameter_set_id,
        min_trusted_samples=min_trusted_samples,
    )
    validation = validate_market_regime_parameter_set_comparison_read_model(read_model)
    if not validation.get("ok"):
        raise ValueError(f"market-regime parameter-set comparison read model validation failed: {validation}")
    relpath = parameter_set_comparison_latest_read_model_relpath()
    trust = read_model.get("calibration_trust") if isinstance(read_model.get("calibration_trust"), Mapping) else {}
    identity = read_model.get("outcome_identity_audit") if isinstance(read_model.get("outcome_identity_audit"), Mapping) else {}
    return {
        "ok": True,
        "parameter_set_comparison_artifact_writer_version": MARKET_REGIME_PARAMETER_SET_COMPARISON_ARTIFACT_WRITER_VERSION,
        "comparison_read_model_version": MARKET_REGIME_PARAMETER_SET_COMPARISON_READ_MODEL_VERSION,
        "preflight_only": True,
        "would_write": False,
        "date": date,
        "active_parameter_set_id": active_parameter_set_id,
        "min_trusted_samples": int(min_trusted_samples),
        "outcome_rows_jsonl": outcome_relpath,
        "outcome_row_count": len(rows),
        "parameter_set_comparison_read_model_json": relpath,
        "comparison_ready": bool(read_model.get("comparison_ready")),
        "comparison_blockers": list(read_model.get("comparison_blockers") or []),
        "trusted_row_count": int(trust.get("trusted_row_count") or 0),
        "reference_only_row_count": int(trust.get("reference_only_row_count") or 0),
        "trusted_parameter_set_count": int(trust.get("trusted_parameter_set_count") or 0),
        "comparable_parameter_set_count": int(trust.get("comparable_parameter_set_count") or 0),
        "legacy_outcome_id_without_parameter_set_count": int(identity.get("legacy_outcome_id_without_parameter_set_count") or 0),
        "legacy_outcome_id_without_parameter_set_present": bool(identity.get("legacy_outcome_id_without_parameter_set_present")),
        "promotion_candidate_count": len(read_model.get("promotion_candidates") or []),
        "recommendation_count": len(read_model.get("recommendations") or []),
        "validation": validation,
        "read_model": read_model,
        "safety": _writer_safety(),
    }


def preflight_market_regime_parameter_set_comparison_read_model(
    root: str | Path,
    *,
    date: str,
    active_parameter_set_id: str = MARKET_REGIME_DEFAULT_ACTIVE_PARAMETER_SET_ID,
    min_trusted_samples: int = 20,
) -> dict[str, Any]:
    plan = build_market_regime_parameter_set_comparison_artifact_write_plan(
        root,
        date=date,
        active_parameter_set_id=active_parameter_set_id,
        min_trusted_samples=min_trusted_samples,
    )
    return {key: value for key, value in plan.items() if key != "read_model"}


def write_market_regime_parameter_set_comparison_read_model(
    root: str | Path,
    *,
    date: str,
    active_parameter_set_id: str = MARKET_REGIME_DEFAULT_ACTIVE_PARAMETER_SET_ID,
    min_trusted_samples: int = 20,
) -> dict[str, Any]:
    base = Path(root)
    plan = build_market_regime_parameter_set_comparison_artifact_write_plan(
        base,
        date=date,
        active_parameter_set_id=active_parameter_set_id,
        min_trusted_samples=min_trusted_samples,
    )
    relpath = str(plan["parameter_set_comparison_read_model_json"])
    _write_json_atomic(base / relpath, plan["read_model"])
    return {
        "ok": True,
        "parameter_set_comparison_artifact_writer_version": MARKET_REGIME_PARAMETER_SET_COMPARISON_ARTIFACT_WRITER_VERSION,
        "comparison_read_model_version": MARKET_REGIME_PARAMETER_SET_COMPARISON_READ_MODEL_VERSION,
        "date": date,
        "active_parameter_set_id": active_parameter_set_id,
        "min_trusted_samples": int(min_trusted_samples),
        "outcome_rows_jsonl": plan["outcome_rows_jsonl"],
        "outcome_row_count": plan["outcome_row_count"],
        "parameter_set_comparison_read_model_json": relpath,
        "comparison_ready": plan["comparison_ready"],
        "comparison_blockers": plan["comparison_blockers"],
        "trusted_row_count": plan["trusted_row_count"],
        "reference_only_row_count": plan["reference_only_row_count"],
        "trusted_parameter_set_count": plan["trusted_parameter_set_count"],
        "comparable_parameter_set_count": plan["comparable_parameter_set_count"],
        "legacy_outcome_id_without_parameter_set_count": plan["legacy_outcome_id_without_parameter_set_count"],
        "legacy_outcome_id_without_parameter_set_present": plan["legacy_outcome_id_without_parameter_set_present"],
        "promotion_candidate_count": plan["promotion_candidate_count"],
        "recommendation_count": plan["recommendation_count"],
        "validation": plan["validation"],
        "safety": _writer_safety(),
    }
