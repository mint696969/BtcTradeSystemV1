# path: ./btcts_next/src/btcts/prediction/scenario_parts.py
# desc: Common family scenario-part and parent scenario-guidance contracts. Pure read-model builders; no D-hot writes, UI inference, broker, AutoTrade, or parameter mutation.

from __future__ import annotations

from typing import Any, Iterable, Mapping

PREDICTION_FAMILY_SCENARIO_PART_CONTRACT_VERSION = "prediction.family_scenario_part.2026_07_10.v1"
PREDICTION_PARENT_SCENARIO_GUIDANCE_CONTRACT_VERSION = "prediction.parent_scenario_guidance.2026_07_10.v1"

_ALLOWED_PART_ROLES = {
    "primary_context",
    "directional_bias",
    "reversal_warning",
    "breakout_warning",
    "risk_cap",
    "liquidity_context",
    "macro_context",
    "trigger_candidate_context",
    "context_only",
}
_ALLOWED_SCENARIO_STATES = {
    "bullish",
    "bearish",
    "range",
    "wait",
    "unknown",
    "no_edge",
    "conflicting",
    "risk_off",
    "context_only",
}
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


def _as_text_list(value: object) -> list[str]:
    if isinstance(value, (list, tuple)):
        return [str(item) for item in value if str(item)]
    if value:
        return [str(value)]
    return []


def _safe_int(value: object, *, default: int = 0) -> int:
    try:
        return int(value)
    except Exception:
        return default


def _bounded_percent(value: object) -> int:
    percent = _safe_int(value)
    if percent < 0:
        return 0
    if percent > 99:
        return 99
    return percent


def _safety(*, parent: bool = False) -> dict[str, Any]:
    return {
        "read_only_inputs": True,
        "display_read_model_only": True,
        "family_part_only": not parent,
        "parent_guidance_only": parent,
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


def build_prediction_family_scenario_part(
    *,
    prediction_family_id: str,
    horizon_key: str,
    horizon_group: str,
    scenario_state: str,
    scenario_label: str,
    scenario_summary: str,
    confidence_percent: int = 0,
    estimated_signal_strength_percent: int = 0,
    part_role: str = "context_only",
    drivers: Iterable[object] | None = None,
    blockers: Iterable[object] | None = None,
    warnings: Iterable[object] | None = None,
    evidence_refs: Iterable[Mapping[str, Any]] | None = None,
    source_quality_notes: Iterable[object] | None = None,
    trace_refs: Iterable[object] | None = None,
    parameter_set_id: str = "",
    generated_at: str = "",
) -> dict[str, Any]:
    state = str(scenario_state or "unknown")
    role = str(part_role or "context_only")
    part = {
        "schema_version": "prediction_family_scenario_part.2026_07_10.v1",
        "contract_version": PREDICTION_FAMILY_SCENARIO_PART_CONTRACT_VERSION,
        "artifact_family": "prediction/scenario_parts",
        "artifact_kind": "family_scenario_part",
        "prediction_family_id": str(prediction_family_id or ""),
        "horizon_key": str(horizon_key or ""),
        "horizon_group": str(horizon_group or ""),
        "scenario_state": state,
        "scenario_label": str(scenario_label or ""),
        "scenario_summary": str(scenario_summary or ""),
        "confidence_percent": _bounded_percent(confidence_percent),
        "estimated_signal_strength_percent": _bounded_percent(estimated_signal_strength_percent),
        "part_role": role,
        "drivers": _as_text_list(list(drivers or [])),
        "blockers": _as_text_list(list(blockers or [])),
        "warnings": _as_text_list(list(warnings or [])),
        "evidence_refs": [dict(item) for item in (evidence_refs or []) if isinstance(item, Mapping)],
        "source_quality_notes": _as_text_list(list(source_quality_notes or [])),
        "trace_refs": _as_text_list(list(trace_refs or [])),
        "parameter_set_id": str(parameter_set_id or ""),
        "generated_at": str(generated_at or ""),
        "parent_merge": {
            "eligible_for_parent_guidance": True,
            "part_role": role,
            "same_run_recursive_dependency_allowed": False,
            "family_decides_overall_scenario": False,
        },
        "safety": _safety(parent=False),
    }
    validation = validate_prediction_family_scenario_part(part)
    if not validation["ok"]:
        raise ValueError(f"family scenario part validation failed: {validation}")
    return part


def validate_prediction_family_scenario_part(part: Mapping[str, Any]) -> dict[str, Any]:
    failures: list[str] = []
    if part.get("artifact_kind") != "family_scenario_part":
        failures.append("artifact_kind_mismatch")
    if not str(part.get("prediction_family_id") or ""):
        failures.append("prediction_family_id_missing")
    if not str(part.get("horizon_key") or ""):
        failures.append("horizon_key_missing")
    if not str(part.get("horizon_group") or ""):
        failures.append("horizon_group_missing")
    if part.get("scenario_state") not in _ALLOWED_SCENARIO_STATES:
        failures.append("scenario_state_not_allowed")
    if part.get("part_role") not in _ALLOWED_PART_ROLES:
        failures.append("part_role_not_allowed")
    if _safe_int(part.get("estimated_signal_strength_percent")) > 99:
        failures.append("estimated_signal_strength_percent_over_99")
    if _has_forbidden_raw_keys(part):
        failures.append("forbidden_raw_payload_key_present")
    merge = part.get("parent_merge") if isinstance(part.get("parent_merge"), Mapping) else {}
    if merge.get("family_decides_overall_scenario") is not False:
        failures.append("family_decides_overall_scenario_not_false")
    if merge.get("same_run_recursive_dependency_allowed") is not False:
        failures.append("same_run_recursive_dependency_allowed_not_false")
    failures.extend(_safety_failures(part.get("safety"), parent=False))
    return {
        "ok": not failures,
        "contract_version": PREDICTION_FAMILY_SCENARIO_PART_CONTRACT_VERSION,
        "failure_count": len(failures),
        "failures": failures,
    }


def build_parent_scenario_guidance_read_model(
    parts: Iterable[Mapping[str, Any]],
    *,
    horizon_key: str,
    horizon_group: str,
    generated_at: str = "",
) -> dict[str, Any]:
    safe_parts = [dict(part) for part in parts if isinstance(part, Mapping)]
    valid_parts: list[dict[str, Any]] = []
    rejected: list[dict[str, Any]] = []
    for part in safe_parts:
        validation = validate_prediction_family_scenario_part(part)
        if validation["ok"]:
            valid_parts.append(part)
        else:
            rejected.append({
                "prediction_family_id": str(part.get("prediction_family_id") or ""),
                "failures": validation["failures"],
            })
    supporting = [part for part in valid_parts if not part.get("blockers")]
    conflicting = [part for part in valid_parts if part.get("blockers") or part.get("warnings")]
    dominant = _select_dominant_part(valid_parts)
    scenario_state = str(dominant.get("scenario_state") or "unknown") if dominant else "unknown"
    scenario_label = str(dominant.get("scenario_label") or "観測待ち") if dominant else "観測待ち"
    model = {
        "schema_version": "prediction_parent_scenario_guidance.2026_07_10.v1",
        "contract_version": PREDICTION_PARENT_SCENARIO_GUIDANCE_CONTRACT_VERSION,
        "artifact_family": "prediction/scenario_guidance",
        "artifact_kind": "parent_scenario_guidance_read_model",
        "horizon_key": str(horizon_key or ""),
        "horizon_group": str(horizon_group or ""),
        "generated_at": str(generated_at or ""),
        "scenario_state": scenario_state,
        "scenario_label": scenario_label,
        "scenario_summary": _parent_summary(dominant, valid_parts),
        "supporting_parts": [_part_ref(part) for part in supporting],
        "conflicting_parts": [_part_ref(part) for part in conflicting],
        "rejected_parts": rejected,
        "family_part_count": len(valid_parts),
        "dominant_family_id": str(dominant.get("prediction_family_id") or "") if dominant else "",
        "operator_guidance": _operator_guidance(scenario_state, valid_parts, rejected),
        "read_only": True,
        "safety": _safety(parent=True),
    }
    validation = validate_parent_scenario_guidance_read_model(model)
    if not validation["ok"]:
        raise ValueError(f"parent scenario guidance validation failed: {validation}")
    return model


def validate_parent_scenario_guidance_read_model(model: Mapping[str, Any]) -> dict[str, Any]:
    failures: list[str] = []
    if model.get("artifact_kind") != "parent_scenario_guidance_read_model":
        failures.append("artifact_kind_mismatch")
    if not str(model.get("horizon_key") or ""):
        failures.append("horizon_key_missing")
    if not str(model.get("horizon_group") or ""):
        failures.append("horizon_group_missing")
    if model.get("scenario_state") not in _ALLOWED_SCENARIO_STATES:
        failures.append("scenario_state_not_allowed")
    if _has_forbidden_raw_keys(model):
        failures.append("forbidden_raw_payload_key_present")
    if model.get("read_only") is not True:
        failures.append("read_only_not_true")
    failures.extend(_safety_failures(model.get("safety"), parent=True))
    return {
        "ok": not failures,
        "contract_version": PREDICTION_PARENT_SCENARIO_GUIDANCE_CONTRACT_VERSION,
        "failure_count": len(failures),
        "failures": failures,
    }


def _safety_failures(value: object, *, parent: bool) -> list[str]:
    failures: list[str] = []
    safety = value if isinstance(value, Mapping) else {}
    for key in ("read_only_inputs", "display_read_model_only"):
        if safety.get(key) is not True:
            failures.append(f"safety_{key}_not_true")
    if safety.get("parent_guidance_only") is not parent:
        failures.append("safety_parent_guidance_only_mismatch")
    if safety.get("family_part_only") is not (not parent):
        failures.append("safety_family_part_only_mismatch")
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
    return failures


def _select_dominant_part(parts: list[Mapping[str, Any]]) -> Mapping[str, Any]:
    if not parts:
        return {}
    role_priority = {
        "primary_context": 6,
        "directional_bias": 5,
        "reversal_warning": 4,
        "breakout_warning": 4,
        "risk_cap": 3,
        "liquidity_context": 2,
        "macro_context": 2,
        "trigger_candidate_context": 1,
        "context_only": 0,
    }
    return max(
        parts,
        key=lambda part: (
            role_priority.get(str(part.get("part_role") or "context_only"), 0),
            _safe_int(part.get("estimated_signal_strength_percent")),
            _safe_int(part.get("confidence_percent")),
        ),
    )


def _part_ref(part: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "prediction_family_id": str(part.get("prediction_family_id") or ""),
        "horizon_key": str(part.get("horizon_key") or ""),
        "horizon_group": str(part.get("horizon_group") or ""),
        "scenario_state": str(part.get("scenario_state") or ""),
        "scenario_label": str(part.get("scenario_label") or ""),
        "part_role": str(part.get("part_role") or ""),
        "confidence_percent": _safe_int(part.get("confidence_percent")),
        "estimated_signal_strength_percent": _safe_int(part.get("estimated_signal_strength_percent")),
        "blockers": _as_text_list(part.get("blockers")),
        "warnings": _as_text_list(part.get("warnings")),
        "parameter_set_id": str(part.get("parameter_set_id") or ""),
    }


def _parent_summary(dominant: Mapping[str, Any], parts: list[Mapping[str, Any]]) -> str:
    if not parts:
        return "family scenario parts are not available; parent guidance is observation-only."
    label = str(dominant.get("scenario_label") or "観測待ち")
    family = str(dominant.get("prediction_family_id") or "unknown_family")
    return f"dominant_family={family} / scenario={label} / parts={len(parts)} / read_only=true"


def _operator_guidance(scenario_state: str, parts: list[Mapping[str, Any]], rejected: list[Mapping[str, Any]]) -> dict[str, Any]:
    blockers = [blocker for part in parts for blocker in _as_text_list(part.get("blockers"))]
    warnings = [warning for part in parts for warning in _as_text_list(part.get("warnings"))]
    return {
        "guidance_mode": "observational_scenario_only",
        "scenario_state": scenario_state,
        "operator_action": "read_context_only",
        "blockers": blockers,
        "warnings": warnings,
        "rejected_part_count": len(rejected),
        "prediction_invoked": False,
        "classifier_invoked": False,
        "broker_action_allowed": False,
        "autotrade_trigger_allowed": False,
    }
