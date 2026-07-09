# path: ./btcts_next/src/btcts/prediction/market_regime/parameter_set_review_packet.py
# desc: Pure MarketRegime parameter-set review packet builder. Converts comparison read models into human/GPT review evidence without D-hot writes, broker, AutoTrade, or parameter mutation.

from __future__ import annotations

from typing import Any, Mapping

MARKET_REGIME_PARAMETER_SET_REVIEW_PACKET_VERSION = "prediction.market_regime.parameter_set_review_packet.2026_07_10.v1"

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


def _safe_int(value: object) -> int:
    try:
        return int(value)
    except Exception:
        return 0


def _safe_float(value: object) -> float | None:
    if value is None:
        return None
    try:
        return round(float(value), 4)
    except Exception:
        return None


def _as_list(value: object) -> list[object]:
    return list(value) if isinstance(value, list) else []


def _mapping(value: object) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _safety() -> dict[str, Any]:
    return {
        "read_only_inputs": True,
        "display_review_packet_only": True,
        "writes_dhot": False,
        "raw_market_data_read": False,
        "raw_market_data_duplicated": False,
        "classifier_invoked": False,
        "prediction_invoked": False,
        "producer_enabled": False,
        "scheduler_enabled": False,
        "broker_private_api_allowed": False,
        "autotrade_trigger_allowed": False,
        "order_intent_submitted": False,
        "parameter_auto_promotion_allowed": False,
        "live_parameter_apply_allowed": False,
        "human_gate_required_for_parameter_change": True,
        "would_send_to_broker": False,
    }


def _review_state(comparison_ready: bool, blockers: list[str]) -> str:
    if comparison_ready:
        return "comparison_ready_for_human_review"
    if "fewer_than_two_parameter_sets_with_minimum_trusted_samples" in blockers:
        return "not_comparable_single_trusted_parameter_set"
    if blockers:
        return "not_comparable_blocked"
    return "not_comparable_waiting_for_evidence"


def _review_decision_options(review_state: str) -> list[dict[str, Any]]:
    base = [
        {
            "decision": "keep_testing",
            "enabled": True,
            "reason": "safe_default_no_parameter_change",
            "requires_human_confirmation": True,
            "auto_apply_allowed": False,
        },
        {
            "decision": "request_more_shadow_evidence",
            "enabled": True,
            "reason": "increase_comparable_trusted_samples_before_change",
            "requires_human_confirmation": True,
            "auto_apply_allowed": False,
        },
    ]
    if review_state == "comparison_ready_for_human_review":
        base.append({
            "decision": "open_promotion_or_rollback_review",
            "enabled": True,
            "reason": "comparison_ready_but_no_auto_promotion",
            "requires_human_confirmation": True,
            "auto_apply_allowed": False,
        })
    else:
        base.append({
            "decision": "open_promotion_or_rollback_review",
            "enabled": False,
            "reason": "comparison_not_ready",
            "requires_human_confirmation": True,
            "auto_apply_allowed": False,
        })
    return base


def _parameter_set_evidence_rows(comparison_read_model: Mapping[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    active_parameter_set_id = str(comparison_read_model.get("active_parameter_set_id") or "")
    for item in _as_list(comparison_read_model.get("parameter_sets")):
        if not isinstance(item, Mapping):
            continue
        parameter_set_id = str(item.get("parameter_set_id") or item.get("key") or "")
        rows.append({
            "parameter_set_id": parameter_set_id,
            "is_active_parameter_set": bool(item.get("is_active_parameter_set")) or bool(active_parameter_set_id and parameter_set_id == active_parameter_set_id),
            "trusted_sample_count": _safe_int(item.get("trusted_sample_count") or item.get("known_total")),
            "known_total": _safe_int(item.get("known_total")),
            "calibration_score": _safe_float(item.get("calibration_score")),
            "hit_rate": _safe_float(item.get("hit_rate")),
            "partial_rate": _safe_float(item.get("partial_rate")),
            "miss_rate": _safe_float(item.get("miss_rate")),
            "insufficient_sample": bool(item.get("insufficient_sample")),
            "sample_outcome_ids": [str(value) for value in _as_list(item.get("sample_outcome_ids"))[:5]],
            "sample_trace_refs": [str(value) for value in _as_list(item.get("sample_trace_refs"))[:5]],
        })
    return rows


def _recommendation_rows(comparison_read_model: Mapping[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for item in _as_list(comparison_read_model.get("recommendations")):
        if not isinstance(item, Mapping):
            continue
        rows.append({
            "parameter_set_id": str(item.get("parameter_set_id") or ""),
            "recommendation": str(item.get("recommendation") or ""),
            "reason": str(item.get("reason") or ""),
            "trusted_sample_count": _safe_int(item.get("trusted_sample_count")),
            "calibration_score": _safe_float(item.get("calibration_score")),
            "human_gate_required": True,
            "auto_apply_allowed": False,
            "auto_promotion_allowed": False,
            "recommendation_shape_only": True,
        })
    return rows


def build_market_regime_parameter_set_review_packet(
    comparison_read_model: Mapping[str, Any],
    *,
    reviewer_lane: str = "human_gpt_review_loop",
) -> dict[str, Any]:
    trust = _mapping(comparison_read_model.get("calibration_trust"))
    blockers = [str(item) for item in _as_list(comparison_read_model.get("comparison_blockers")) if str(item)]
    comparison_ready = bool(comparison_read_model.get("comparison_ready"))
    review_state = _review_state(comparison_ready, blockers)
    evidence_rows = _parameter_set_evidence_rows(comparison_read_model)
    recommendations = _recommendation_rows(comparison_read_model)
    active_parameter_set_id = str(comparison_read_model.get("active_parameter_set_id") or "")
    active_evidence = next((row for row in evidence_rows if row.get("is_active_parameter_set")), {})
    best_evidence = max(
        evidence_rows,
        key=lambda row: (
            row.get("calibration_score") is not None,
            row.get("calibration_score") if row.get("calibration_score") is not None else -1.0,
            _safe_int(row.get("trusted_sample_count")),
        ),
        default={},
    )
    packet = {
        "schema_version": "market_regime_parameter_set_review_packet.2026_07_10.v1",
        "review_packet_version": MARKET_REGIME_PARAMETER_SET_REVIEW_PACKET_VERSION,
        "artifact_family": "prediction/market_regime",
        "artifact_kind": "parameter_set_review_packet",
        "prediction_family_id": "market_regime",
        "source_artifact_kind": str(comparison_read_model.get("artifact_kind") or ""),
        "source_comparison_read_model_version": str(comparison_read_model.get("comparison_read_model_version") or ""),
        "reviewer_lane": str(reviewer_lane or "human_gpt_review_loop"),
        "review_state": review_state,
        "review_required": True,
        "comparison_ready": comparison_ready,
        "comparison_blockers": blockers,
        "active_parameter_set_id": active_parameter_set_id,
        "evidence_summary": {
            "comparison_scope": str(comparison_read_model.get("comparison_scope") or ""),
            "trusted_observation_source": str(trust.get("trusted_observation_source") or ""),
            "reference_only_observation_source": str(trust.get("reference_only_observation_source") or ""),
            "latest_cards_current_is_reference_only": bool(trust.get("latest_cards_current_is_reference_only")),
            "trusted_row_count": _safe_int(trust.get("trusted_row_count")),
            "reference_only_row_count": _safe_int(trust.get("reference_only_row_count")),
            "trusted_parameter_set_count": _safe_int(trust.get("trusted_parameter_set_count")),
            "comparable_parameter_set_count": _safe_int(trust.get("comparable_parameter_set_count")),
            "minimum_trusted_sample_count": _safe_int(trust.get("minimum_trusted_sample_count")),
            "promotion_candidate_count": len(_as_list(comparison_read_model.get("promotion_candidates"))),
            "recommendation_count": len(recommendations),
            "active_parameter_set": active_evidence,
            "best_visible_parameter_set": best_evidence,
        },
        "parameter_set_evidence": evidence_rows,
        "recommendations": recommendations,
        "promotion_candidates": [],
        "decision_options": _review_decision_options(review_state),
        "operator_notes": [
            "Review packet is evidence-only and does not apply parameters.",
            "Promotion candidates remain empty until comparable trusted evidence exists.",
            "Human/GPT review may recommend keep-testing, shadow-only, or rollback review, but cannot auto-apply.",
        ],
        "safety": _safety(),
    }
    validation = validate_market_regime_parameter_set_review_packet(packet)
    if not validation["ok"]:
        raise ValueError(f"market-regime parameter-set review packet validation failed: {validation}")
    return packet


def validate_market_regime_parameter_set_review_packet(packet: Mapping[str, Any]) -> dict[str, Any]:
    failures: list[str] = []
    if packet.get("artifact_kind") != "parameter_set_review_packet":
        failures.append("artifact_kind_mismatch")
    if packet.get("prediction_family_id") != "market_regime":
        failures.append("prediction_family_id_mismatch")
    if packet.get("reviewer_lane") != "human_gpt_review_loop":
        failures.append("reviewer_lane_not_human_gpt_review_loop")
    if packet.get("review_required") is not True:
        failures.append("review_required_not_true")
    if _has_forbidden_raw_keys(packet):
        failures.append("forbidden_raw_payload_key_present")
    if packet.get("promotion_candidates") != []:
        failures.append("promotion_candidates_not_empty")
    for item in _as_list(packet.get("recommendations")):
        if not isinstance(item, Mapping):
            failures.append("recommendation_not_mapping")
            continue
        if item.get("human_gate_required") is not True:
            failures.append("recommendation_human_gate_required_not_true")
        if item.get("auto_apply_allowed") is not False:
            failures.append("recommendation_auto_apply_not_false")
        if item.get("auto_promotion_allowed") is not False:
            failures.append("recommendation_auto_promotion_not_false")
    for item in _as_list(packet.get("decision_options")):
        if not isinstance(item, Mapping):
            failures.append("decision_option_not_mapping")
            continue
        if item.get("auto_apply_allowed") is not False:
            failures.append("decision_option_auto_apply_not_false")
        if item.get("requires_human_confirmation") is not True:
            failures.append("decision_option_human_confirmation_not_true")
    safety = _mapping(packet.get("safety"))
    for key in (
        "read_only_inputs",
        "display_review_packet_only",
        "human_gate_required_for_parameter_change",
    ):
        if safety.get(key) is not True:
            failures.append(f"safety_{key}_not_true")
    for key in (
        "writes_dhot",
        "raw_market_data_read",
        "raw_market_data_duplicated",
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
        "review_packet_version": MARKET_REGIME_PARAMETER_SET_REVIEW_PACKET_VERSION,
        "failure_count": len(failures),
        "failures": failures,
        "review_state": str(packet.get("review_state") or ""),
        "comparison_ready": bool(packet.get("comparison_ready")),
    }
