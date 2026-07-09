# path: ./btcts_next/src/btcts/prediction/scenario_guidance_artifacts.py
# desc: Common parent scenario-guidance latest read-model writer. Writes only the parent guidance read model artifact; no raw market read, UI inference, scheduler, broker, AutoTrade, or parameter mutation.

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable, Mapping

from .scenario_guidance import (
    PARENT_SCENARIO_GUIDANCE_LATEST_READ_MODEL_RELPATH,
    PREDICTION_PARENT_SCENARIO_GUIDANCE_ARTIFACT_VERSION,
    build_parent_scenario_guidance_latest_read_model_artifact,
    validate_parent_scenario_guidance_latest_read_model_artifact,
)

PREDICTION_PARENT_SCENARIO_GUIDANCE_ARTIFACT_WRITER_VERSION = "prediction.parent_scenario_guidance_artifacts.2026_07_10.v1"


def _write_json_atomic(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    tmp.replace(path)


def _writer_safety() -> dict[str, Any]:
    return {
        "read_only_family_scenario_parts": True,
        "writes_parent_scenario_guidance_read_model_only": True,
        "raw_market_data_read": False,
        "raw_market_data_duplicated": False,
        "ui_render_invokes_classifier": False,
        "classifier_invoked": False,
        "prediction_invoked": False,
        "producer_enabled": False,
        "scheduler_enabled": False,
        "broker_private_api_allowed": False,
        "autotrade_trigger_allowed": False,
        "order_intent_submitted": False,
        "parameter_auto_promotion_allowed": False,
        "live_parameter_apply_allowed": False,
        "would_send_to_broker": False,
    }


def build_parent_scenario_guidance_artifact_write_plan(
    root: str | Path,
    *,
    family_scenario_parts: Iterable[Mapping[str, Any]],
    generated_at: str = "",
    source_run_id: str = "",
) -> dict[str, Any]:
    base = Path(root)
    read_model = build_parent_scenario_guidance_latest_read_model_artifact(
        family_scenario_parts,
        generated_at=generated_at,
        source_run_id=source_run_id,
    )
    validation = validate_parent_scenario_guidance_latest_read_model_artifact(read_model)
    if not validation.get("ok"):
        raise ValueError(f"parent scenario guidance latest read model validation failed: {validation}")
    relpath = PARENT_SCENARIO_GUIDANCE_LATEST_READ_MODEL_RELPATH
    return {
        "ok": True,
        "parent_scenario_guidance_artifact_writer_version": PREDICTION_PARENT_SCENARIO_GUIDANCE_ARTIFACT_WRITER_VERSION,
        "parent_scenario_guidance_artifact_version": PREDICTION_PARENT_SCENARIO_GUIDANCE_ARTIFACT_VERSION,
        "preflight_only": True,
        "would_write": False,
        "root": str(base),
        "parent_scenario_guidance_read_model_json": relpath,
        "generated_at": str(generated_at or ""),
        "source_run_id": str(source_run_id or ""),
        "horizon_count": int(read_model.get("horizon_count") or 0),
        "family_part_count": int(read_model.get("family_part_count") or 0),
        "rejected_part_count": int(read_model.get("rejected_part_count") or 0),
        "prediction_family_ids": list(read_model.get("prediction_family_ids") or []),
        "scenario_states": list((read_model.get("summary") or {}).get("scenario_states") or []) if isinstance(read_model.get("summary"), Mapping) else [],
        "dominant_family_ids": list((read_model.get("summary") or {}).get("dominant_family_ids") or []) if isinstance(read_model.get("summary"), Mapping) else [],
        "validation": validation,
        "read_model": read_model,
        "safety": _writer_safety(),
    }


def preflight_parent_scenario_guidance_latest_read_model(
    root: str | Path,
    *,
    family_scenario_parts: Iterable[Mapping[str, Any]],
    generated_at: str = "",
    source_run_id: str = "",
) -> dict[str, Any]:
    plan = build_parent_scenario_guidance_artifact_write_plan(
        root,
        family_scenario_parts=family_scenario_parts,
        generated_at=generated_at,
        source_run_id=source_run_id,
    )
    return {key: value for key, value in plan.items() if key != "read_model"}


def write_parent_scenario_guidance_latest_read_model(
    root: str | Path,
    *,
    family_scenario_parts: Iterable[Mapping[str, Any]],
    generated_at: str = "",
    source_run_id: str = "",
) -> dict[str, Any]:
    base = Path(root)
    plan = build_parent_scenario_guidance_artifact_write_plan(
        base,
        family_scenario_parts=family_scenario_parts,
        generated_at=generated_at,
        source_run_id=source_run_id,
    )
    relpath = str(plan["parent_scenario_guidance_read_model_json"])
    _write_json_atomic(base / relpath, plan["read_model"])
    return {
        "ok": True,
        "parent_scenario_guidance_artifact_writer_version": PREDICTION_PARENT_SCENARIO_GUIDANCE_ARTIFACT_WRITER_VERSION,
        "parent_scenario_guidance_artifact_version": PREDICTION_PARENT_SCENARIO_GUIDANCE_ARTIFACT_VERSION,
        "would_write": True,
        "parent_scenario_guidance_read_model_json": relpath,
        "generated_at": str(generated_at or ""),
        "source_run_id": str(source_run_id or ""),
        "horizon_count": plan["horizon_count"],
        "family_part_count": plan["family_part_count"],
        "rejected_part_count": plan["rejected_part_count"],
        "prediction_family_ids": plan["prediction_family_ids"],
        "scenario_states": plan["scenario_states"],
        "dominant_family_ids": plan["dominant_family_ids"],
        "validation": plan["validation"],
        "safety": _writer_safety(),
    }
