# path: ./btcts_next/src/btcts/prediction/scenario_guidance.py
# desc: Common parent scenario-guidance latest read-model artifact builders. Pure in-memory builders; no D-hot writes, UI inference, broker, AutoTrade, or parameter mutation.

from __future__ import annotations

from collections import defaultdict
from typing import Any, Iterable, Mapping

from .scenario_parts import (
    build_parent_scenario_guidance_read_model,
    validate_parent_scenario_guidance_read_model,
    validate_prediction_family_scenario_part,
)

PREDICTION_PARENT_SCENARIO_GUIDANCE_ARTIFACT_VERSION = "prediction.parent_scenario_guidance_artifact.2026_07_10.v1"
PARENT_SCENARIO_GUIDANCE_LATEST_READ_MODEL_RELPATH = "prediction/scenario_guidance/latest_read_model.json"

_FORBIDDEN_RAW_KEYS = {
    "raw_candles",
    "raw_orderbook",
    "raw_trades",
    "raw_executions",
    "raw_market_payload",
    "raw_source_payload",
    "bids",
    "asks",
    "trades",
    "executions",
}


def _has_forbidden_raw_keys(value: Any) -> bool:
    if isinstance(value, Mapping):
        for key, nested in value.items():
            if str(key) in _FORBIDDEN_RAW_KEYS:
                return True
            if _has_forbidden_raw_keys(nested):
                return True
    elif isinstance(value, list):
        return any(_has_forbidden_raw_keys(item) for item in value)
    return False


def _safety() -> dict[str, Any]:
    return {
        "read_only_inputs": True,
        "display_read_model_only": True,
        "parent_guidance_artifact_only": True,
        "writes_dhot": False,
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


def parent_scenario_guidance_latest_read_model_relpath() -> str:
    return PARENT_SCENARIO_GUIDANCE_LATEST_READ_MODEL_RELPATH


def build_parent_scenario_guidance_latest_read_model_artifact(
    family_scenario_parts: Iterable[Mapping[str, Any]],
    *,
    generated_at: str = "",
    source_run_id: str = "",
) -> dict[str, Any]:
    valid_parts: list[dict[str, Any]] = []
    rejected_parts: list[dict[str, Any]] = []
    for part in family_scenario_parts:
        if not isinstance(part, Mapping):
            rejected_parts.append({"prediction_family_id": "", "horizon_key": "", "failures": ["part_not_mapping"]})
            continue
        validation = validate_prediction_family_scenario_part(part)
        if validation["ok"]:
            valid_parts.append(dict(part))
        else:
            rejected_parts.append({
                "prediction_family_id": str(part.get("prediction_family_id") or ""),
                "horizon_key": str(part.get("horizon_key") or ""),
                "failures": list(validation.get("failures") or []),
            })

    grouped: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for part in valid_parts:
        grouped[(str(part.get("horizon_key") or ""), str(part.get("horizon_group") or ""))].append(part)

    horizons: list[dict[str, Any]] = []
    for (horizon_key, horizon_group), parts in sorted(grouped.items(), key=lambda item: _horizon_sort_key(item[0][0])):
        horizons.append(build_parent_scenario_guidance_read_model(
            parts,
            horizon_key=horizon_key,
            horizon_group=horizon_group,
            generated_at=generated_at,
        ))

    artifact = {
        "schema_version": "prediction_parent_scenario_guidance_latest_read_model.2026_07_10.v1",
        "artifact_family": "prediction/scenario_guidance",
        "artifact_kind": "parent_scenario_guidance_latest_read_model",
        "contract_version": PREDICTION_PARENT_SCENARIO_GUIDANCE_ARTIFACT_VERSION,
        "relpath": PARENT_SCENARIO_GUIDANCE_LATEST_READ_MODEL_RELPATH,
        "generated_at": str(generated_at or ""),
        "source_run_id": str(source_run_id or ""),
        "horizon_count": len(horizons),
        "family_part_count": len(valid_parts),
        "rejected_part_count": len(rejected_parts),
        "prediction_family_ids": sorted({str(part.get("prediction_family_id") or "") for part in valid_parts if str(part.get("prediction_family_id") or "")}),
        "horizons": horizons,
        "rejected_parts": rejected_parts,
        "summary": {
            "scenario_states": sorted({str(item.get("scenario_state") or "") for item in horizons}),
            "dominant_family_ids": sorted({str(item.get("dominant_family_id") or "") for item in horizons if str(item.get("dominant_family_id") or "")}),
            "read_only": True,
            "display_only": True,
            "parent_guidance_artifact_only": True,
        },
        "safety": _safety(),
    }
    validation = validate_parent_scenario_guidance_latest_read_model_artifact(artifact)
    if not validation["ok"]:
        raise ValueError(f"parent scenario guidance artifact validation failed: {validation}")
    return artifact


def validate_parent_scenario_guidance_latest_read_model_artifact(artifact: Mapping[str, Any]) -> dict[str, Any]:
    failures: list[str] = []
    if artifact.get("artifact_kind") != "parent_scenario_guidance_latest_read_model":
        failures.append("artifact_kind_mismatch")
    if artifact.get("artifact_family") != "prediction/scenario_guidance":
        failures.append("artifact_family_mismatch")
    if artifact.get("contract_version") != PREDICTION_PARENT_SCENARIO_GUIDANCE_ARTIFACT_VERSION:
        failures.append("contract_version_mismatch")
    if artifact.get("relpath") != PARENT_SCENARIO_GUIDANCE_LATEST_READ_MODEL_RELPATH:
        failures.append("relpath_mismatch")
    horizons = artifact.get("horizons")
    if not isinstance(horizons, list):
        failures.append("horizons_not_list")
        horizons = []
    if int(artifact.get("horizon_count") or -1) != len(horizons):
        failures.append("horizon_count_mismatch")
    for index, horizon in enumerate(horizons):
        if not isinstance(horizon, Mapping):
            failures.append(f"horizon_{index}_not_mapping")
            continue
        validation = validate_parent_scenario_guidance_read_model(horizon)
        if not validation["ok"]:
            failures.append(f"horizon_{index}_invalid")
            failures.extend([f"horizon_{index}_{failure}" for failure in validation.get("failures", [])])
    if _has_forbidden_raw_keys(artifact):
        failures.append("forbidden_raw_payload_key_present")
    safety = artifact.get("safety") if isinstance(artifact.get("safety"), Mapping) else {}
    for key in ("read_only_inputs", "display_read_model_only", "parent_guidance_artifact_only"):
        if safety.get(key) is not True:
            failures.append(f"safety_{key}_not_true")
    for key in (
        "writes_dhot",
        "raw_market_data_read",
        "raw_market_data_duplicated",
        "ui_render_invokes_classifier",
        "classifier_invoked",
        "prediction_invoked",
        "producer_enabled",
        "scheduler_enabled",
        "broker_private_api_allowed",
        "autotrade_trigger_allowed",
        "order_intent_submitted",
        "parameter_auto_promotion_allowed",
        "live_parameter_apply_allowed",
        "would_send_to_broker",
    ):
        if safety.get(key) is not False:
            failures.append(f"safety_{key}_not_false")
    return {
        "ok": not failures,
        "contract_version": PREDICTION_PARENT_SCENARIO_GUIDANCE_ARTIFACT_VERSION,
        "failure_count": len(failures),
        "failures": failures,
        "horizon_count": len(horizons),
        "family_part_count": int(artifact.get("family_part_count") or 0),
    }


def _horizon_sort_key(horizon_key: str) -> tuple[int, str]:
    key = str(horizon_key or "")
    if key == "current":
        return (0, key)
    if key.endswith("s"):
        try:
            return (int(key[:-1]), key)
        except Exception:
            return (999999999, key)
    return (999999999, key)
