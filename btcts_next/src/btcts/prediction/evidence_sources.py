# path: ./btcts_next/src/btcts/prediction/evidence_sources.py
# desc: Common evidence-source weight profile contract for prediction families. Pure/read-only; no market reads, broker, AutoTrade, or parameter apply.

from __future__ import annotations

from typing import Any, Mapping

PREDICTION_EVIDENCE_SOURCE_WEIGHT_PROFILE_VERSION = "prediction.evidence_source_weight_profile.2026_07_10.v1"

ALLOWED_EVIDENCE_SOURCE_ROLES = frozenset({
    "primary",
    "supporting",
    "reference_only",
    "veto",
    "blocker",
    "confidence_cap",
    "context_only",
})

ALLOWED_EVIDENCE_HORIZON_GROUPS = frozenset({
    "nowcast",
    "short_horizon",
    "mid_horizon",
    "long_horizon",
    "context",
})

ALLOWED_EVIDENCE_DIRECTIONS = frozenset({
    "bullish",
    "bearish",
    "range",
    "wait",
    "unknown",
    "no_edge",
    "conflicting",
    "risk_off",
    "context_only",
})

_FORBIDDEN_RAW_KEYS = frozenset({
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
})

_DEFAULT_FAMILY_ROLES = {
    "market_regime": "primary_context",
    "trend_bias": "directional_bias",
    "reversal_zone": "reversal_warning",
    "breakout_false_break": "breakout_warning",
    "volatility_risk": "risk_cap",
    "liquidity_execution_quality": "liquidity_context",
    "macro_cross_context": "macro_context",
    "trigger_candidate": "trigger_candidate_context",
}

_DEFAULT_HORIZON_CONFIDENCE_CAPS = {
    "nowcast": 99,
    "short_horizon": 92,
    "mid_horizon": 82,
    "long_horizon": 68,
    "context": 60,
}


def _safety() -> dict[str, bool]:
    return {
        "read_only_inputs": True,
        "contract_only": True,
        "parameter_set_tunable": True,
        "weights_apply_only_after_human_gate": True,
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
        "would_send_to_broker": False,
    }


def _as_text_list(value: Any) -> list[str]:
    if isinstance(value, (list, tuple)):
        return [str(item) for item in value if str(item)]
    if value:
        return [str(value)]
    return []


def _default_horizon_confidence_cap_percent(horizon_group: str) -> int:
    return int(_DEFAULT_HORIZON_CONFIDENCE_CAPS.get(str(horizon_group or ""), 60))


def _contains_forbidden_raw_key(value: Any) -> bool:
    if isinstance(value, Mapping):
        for key, child in value.items():
            if str(key) in _FORBIDDEN_RAW_KEYS:
                return True
            if _contains_forbidden_raw_key(child):
                return True
    if isinstance(value, list):
        return any(_contains_forbidden_raw_key(item) for item in value)
    return False


def _clamp_int(value: Any, *, low: int, high: int, default: int) -> int:
    try:
        number = int(value)
    except (TypeError, ValueError):
        number = default
    return max(low, min(high, number))


def _percent(value: Any, *, default: int) -> int:
    return _clamp_int(value, low=0, high=100, default=default)


def build_prediction_evidence_source_descriptor(
    *,
    source_id: str,
    role: str,
    source_kind: str = "derived_read_model",
    weight_percent: int = 0,
    priority_rank: int = 100,
    confidence_cap_percent: int | None = None,
    default_reliability_percent: int = 50,
    default_signal_strength_percent: int = 50,
    default_freshness_percent: int = 100,
    default_quality_percent: int = 100,
    default_direction: str = "unknown",
    learned_from_outcomes: bool = False,
    min_required: bool = False,
    missing_policy: str = "degrade_confidence",
    tunable: bool = True,
    source_ref: str = "",
    rationale: str = "",
) -> dict[str, Any]:
    """Build a compact source descriptor. This stores references/weights only, never raw payload."""

    descriptor = {
        "source_id": str(source_id),
        "role": str(role),
        "source_kind": str(source_kind or "derived_read_model"),
        "weight_percent": _clamp_int(weight_percent, low=0, high=100, default=0),
        "priority_rank": _clamp_int(priority_rank, low=1, high=999, default=100),
        "confidence_cap_percent": None if confidence_cap_percent is None else _percent(confidence_cap_percent, default=100),
        "default_reliability_percent": _percent(default_reliability_percent, default=50),
        "default_signal_strength_percent": _percent(default_signal_strength_percent, default=50),
        "default_freshness_percent": _percent(default_freshness_percent, default=100),
        "default_quality_percent": _percent(default_quality_percent, default=100),
        "default_direction": str(default_direction or "unknown"),
        "learned_from_outcomes": bool(learned_from_outcomes),
        "min_required": bool(min_required),
        "missing_policy": str(missing_policy or "degrade_confidence"),
        "tunable": bool(tunable),
        "source_ref": str(source_ref or ""),
        "rationale": str(rationale or ""),
        "safety": _safety(),
    }
    return descriptor


def _normalize_sources(sources: list[Mapping[str, Any]] | tuple[Mapping[str, Any], ...]) -> list[dict[str, Any]]:
    normalized: list[dict[str, Any]] = []
    for index, source in enumerate(sources):
        if not isinstance(source, Mapping):
            continue
        normalized.append(build_prediction_evidence_source_descriptor(
            source_id=str(source.get("source_id") or f"source_{index}"),
            role=str(source.get("role") or "supporting"),
            source_kind=str(source.get("source_kind") or "derived_read_model"),
            weight_percent=int(source.get("weight_percent") or 0),
            priority_rank=int(source.get("priority_rank") or (index + 1)),
            confidence_cap_percent=source.get("confidence_cap_percent") if source.get("confidence_cap_percent") is not None else None,
            default_reliability_percent=int(source.get("default_reliability_percent") or 50),
            default_signal_strength_percent=int(source.get("default_signal_strength_percent") or 50),
            default_freshness_percent=int(source.get("default_freshness_percent") or 100),
            default_quality_percent=int(source.get("default_quality_percent") or 100),
            default_direction=str(source.get("default_direction") or "unknown"),
            learned_from_outcomes=bool(source.get("learned_from_outcomes")),
            min_required=bool(source.get("min_required")),
            missing_policy=str(source.get("missing_policy") or "degrade_confidence"),
            tunable=bool(source.get("tunable", True)),
            source_ref=str(source.get("source_ref") or ""),
            rationale=str(source.get("rationale") or ""),
        ))
    return sorted(normalized, key=lambda item: (int(item.get("priority_rank") or 999), str(item.get("source_id") or "")))


def build_prediction_evidence_source_weight_profile(
    *,
    prediction_family_id: str,
    horizon_key: str,
    horizon_group: str,
    parameter_set_id: str,
    sources: list[Mapping[str, Any]] | tuple[Mapping[str, Any], ...],
    generated_at: str = "",
    profile_id: str = "",
    family_part_role: str = "",
    target_weight_total_percent: int = 100,
    confidence_floor_percent: int = 0,
    confidence_ceiling_percent: int = 100,
    horizon_confidence_cap_percent: int | None = None,
    notes: list[str] | tuple[str, ...] = (),
) -> dict[str, Any]:
    normalized_sources = _normalize_sources(sources)
    weight_total = sum(int(source.get("weight_percent") or 0) for source in normalized_sources)
    horizon_cap = _percent(
        horizon_confidence_cap_percent
        if horizon_confidence_cap_percent is not None
        else _default_horizon_confidence_cap_percent(str(horizon_group)),
        default=_default_horizon_confidence_cap_percent(str(horizon_group)),
    )
    profile = {
        "artifact_kind": "prediction_evidence_source_weight_profile",
        "contract_version": PREDICTION_EVIDENCE_SOURCE_WEIGHT_PROFILE_VERSION,
        "profile_id": profile_id or f"{prediction_family_id}:{horizon_key}:{parameter_set_id}:evidence_weight_profile",
        "generated_at": str(generated_at or ""),
        "prediction_family_id": str(prediction_family_id),
        "family_part_role": str(family_part_role or _DEFAULT_FAMILY_ROLES.get(str(prediction_family_id), "context_only")),
        "horizon_key": str(horizon_key),
        "horizon_group": str(horizon_group),
        "parameter_set_id": str(parameter_set_id),
        "target_weight_total_percent": _clamp_int(target_weight_total_percent, low=0, high=100, default=100),
        "weight_total_percent": weight_total,
        "confidence_floor_percent": _clamp_int(confidence_floor_percent, low=0, high=100, default=0),
        "confidence_ceiling_percent": _clamp_int(confidence_ceiling_percent, low=0, high=100, default=100),
        "horizon_confidence_cap_percent": horizon_cap,
        "card_interval_calibration_policy": {
            "validity_scope": "until_next_same_family_same_horizon_card",
            "calibration_target_window": "current_card_to_next_same_family_same_horizon_card",
            "confidence_is_prophecy": False,
            "prediction_may_change_before_next_card": True,
            "source_invalidation_can_end_validity_early": True,
            "nearer_horizons_default_to_higher_confidence_caps": True,
            "farther_horizons_default_to_lower_confidence_caps": True,
            "recommended_outcome_alignment": "score each card against realized/next-card outcome for its own interval only",
        },
        "source_count": len(normalized_sources),
        "sources": normalized_sources,
        "confidence_model_owner": "parent_common_prediction_layer",
        "family_vs_common_responsibility": {
            "family_specific_logic_owns": [
                "source_selection",
                "source_direction",
                "signal_strength_percent",
                "family_specific_blockers",
                "family_scenario_part_state",
            ],
            "common_parent_logic_owns": [
                "source_weight_contract",
                "source_reliability_percent",
                "source_agreement",
                "freshness_quality_adjustment",
                "horizon_confidence_cap",
                "display_confidence_percent",
                "calibration_to_next_same_family_same_horizon_card",
            ],
            "reason": "family results may differ, but displayed confidence percent must have the same meaning across all prediction families",
        },
        "confidence_formula": {
            "formula_version": "display_confidence.weighted_reliability_signal_agreement.v1",
            "display_confidence_percent": "clamp(weighted_source_quality_percent * agreement_multiplier, floor, ceiling, horizon_cap, source_confidence_caps)",
            "weighted_source_quality_percent": "sum(weight * reliability * signal_strength * freshness * quality) / sum(weight)",
            "agreement_multiplier": "0.55 + 0.45 * aligned_weighted_quality_ratio",
            "source_reliability_percent": "learned from outcome/calibration; higher for sources with more correct historical calls",
            "signal_strength_percent": "runtime signal strength for the current card/horizon",
            "all_sources_aligned_high_quality": "can approach 99 when reliability, signal, freshness, and quality are all near 100",
            "conflict_or_stale_evidence": "reduces confidence or applies caps/blockers",
        },
        "tunable_fields": [
            "sources[].weight_percent",
            "sources[].priority_rank",
            "sources[].confidence_cap_percent",
            "sources[].default_reliability_percent",
            "sources[].default_signal_strength_percent",
            "sources[].default_freshness_percent",
            "sources[].default_quality_percent",
            "sources[].min_required",
            "sources[].missing_policy",
            "confidence_floor_percent",
            "confidence_ceiling_percent",
            "horizon_confidence_cap_percent",
        ],
        "adjustment_loop": {
            "analysis_source": "outcome_and_calibration_read_models",
            "human_review_required": True,
            "auto_apply_allowed": False,
            "auto_promotion_allowed": False,
            "recommended_use": "compare parameter_set profiles by outcome/calibration before changing live weights",
        },
        "notes": _as_text_list(notes),
        "safety": _safety(),
    }
    profile["validation"] = validate_prediction_evidence_source_weight_profile(profile)
    return profile


def validate_prediction_evidence_source_weight_profile(profile: Mapping[str, Any]) -> dict[str, Any]:
    failures: list[str] = []
    if not isinstance(profile, Mapping):
        return {"ok": False, "failure_count": 1, "failures": ["profile_not_mapping"]}
    if _contains_forbidden_raw_key(profile):
        failures.append("forbidden_raw_payload_key_present")
    if profile.get("artifact_kind") != "prediction_evidence_source_weight_profile":
        failures.append("artifact_kind_invalid")
    if profile.get("contract_version") != PREDICTION_EVIDENCE_SOURCE_WEIGHT_PROFILE_VERSION:
        failures.append("contract_version_invalid")
    for key in ("prediction_family_id", "horizon_key", "horizon_group", "parameter_set_id"):
        if not str(profile.get(key) or ""):
            failures.append(f"{key}_missing")
    if str(profile.get("horizon_group") or "") not in ALLOWED_EVIDENCE_HORIZON_GROUPS:
        failures.append("horizon_group_invalid")
    sources = profile.get("sources")
    if not isinstance(sources, list) or not sources:
        failures.append("sources_missing")
        sources = []
    source_ids: set[str] = set()
    weight_total = 0
    for index, source in enumerate(sources):
        if not isinstance(source, Mapping):
            failures.append(f"source_{index}_not_mapping")
            continue
        source_id = str(source.get("source_id") or "")
        if not source_id:
            failures.append(f"source_{index}_source_id_missing")
        if source_id in source_ids:
            failures.append(f"source_id_duplicate:{source_id}")
        source_ids.add(source_id)
        role = str(source.get("role") or "")
        if role not in ALLOWED_EVIDENCE_SOURCE_ROLES:
            failures.append(f"source_{source_id or index}_role_invalid")
        direction = str(source.get("default_direction") or "unknown")
        if direction not in ALLOWED_EVIDENCE_DIRECTIONS:
            failures.append(f"source_{source_id or index}_default_direction_invalid")
        try:
            weight = int(source.get("weight_percent"))
        except (TypeError, ValueError):
            failures.append(f"source_{source_id or index}_weight_not_int")
            weight = -1
        if weight < 0 or weight > 100:
            failures.append(f"source_{source_id or index}_weight_out_of_range")
        weight_total += max(0, weight)
        cap = source.get("confidence_cap_percent")
        if cap is not None:
            try:
                cap_int = int(cap)
            except (TypeError, ValueError):
                failures.append(f"source_{source_id or index}_confidence_cap_not_int")
            else:
                if cap_int < 0 or cap_int > 100:
                    failures.append(f"source_{source_id or index}_confidence_cap_out_of_range")
        for percent_key in ("default_reliability_percent", "default_signal_strength_percent", "default_freshness_percent", "default_quality_percent"):
            try:
                percent_value = int(source.get(percent_key))
            except (TypeError, ValueError):
                failures.append(f"source_{source_id or index}_{percent_key}_not_int")
                continue
            if percent_value < 0 or percent_value > 100:
                failures.append(f"source_{source_id or index}_{percent_key}_out_of_range")
        safety = source.get("safety") if isinstance(source.get("safety"), Mapping) else {}
        for flag in ("broker_private_api_allowed", "autotrade_trigger_allowed", "order_intent_submitted", "parameter_auto_promotion_allowed", "live_parameter_apply_allowed", "would_send_to_broker", "raw_market_data_read", "raw_market_data_duplicated", "classifier_invoked", "prediction_invoked"):
            if safety.get(flag) is not False:
                failures.append(f"source_{source_id or index}_safety_{flag}_not_false")
    if int(profile.get("weight_total_percent") or -1) != weight_total:
        failures.append("weight_total_percent_mismatch")
    target = int(profile.get("target_weight_total_percent") or -1)
    if target != weight_total:
        failures.append("weight_total_not_target")
    floor = int(profile.get("confidence_floor_percent") or 0)
    ceiling = int(profile.get("confidence_ceiling_percent") or 0)
    horizon_cap = int(profile.get("horizon_confidence_cap_percent") or -1)
    if floor < 0 or floor > 100 or ceiling < 0 or ceiling > 100 or floor > ceiling:
        failures.append("confidence_floor_ceiling_invalid")
    if horizon_cap < 0 or horizon_cap > 100:
        failures.append("horizon_confidence_cap_percent_invalid")
    policy = profile.get("card_interval_calibration_policy") if isinstance(profile.get("card_interval_calibration_policy"), Mapping) else {}
    if policy.get("validity_scope") != "until_next_same_family_same_horizon_card":
        failures.append("card_interval_validity_scope_invalid")
    if policy.get("calibration_target_window") != "current_card_to_next_same_family_same_horizon_card":
        failures.append("card_interval_calibration_target_invalid")
    if policy.get("confidence_is_prophecy") is not False:
        failures.append("card_interval_confidence_is_prophecy_not_false")
    if policy.get("prediction_may_change_before_next_card") is not True:
        failures.append("card_interval_prediction_may_change_not_true")
    if profile.get("confidence_model_owner") != "parent_common_prediction_layer":
        failures.append("confidence_model_owner_invalid")
    responsibility = profile.get("family_vs_common_responsibility") if isinstance(profile.get("family_vs_common_responsibility"), Mapping) else {}
    if "source_direction" not in _as_text_list(responsibility.get("family_specific_logic_owns")):
        failures.append("family_specific_source_direction_responsibility_missing")
    if "display_confidence_percent" not in _as_text_list(responsibility.get("common_parent_logic_owns")):
        failures.append("common_parent_display_confidence_responsibility_missing")
    safety = profile.get("safety") if isinstance(profile.get("safety"), Mapping) else {}
    for flag in ("broker_private_api_allowed", "autotrade_trigger_allowed", "order_intent_submitted", "parameter_auto_promotion_allowed", "live_parameter_apply_allowed", "would_send_to_broker", "raw_market_data_read", "raw_market_data_duplicated", "classifier_invoked", "prediction_invoked", "producer_enabled", "scheduler_enabled"):
        if safety.get(flag) is not False:
            failures.append(f"safety_{flag}_not_false")
    if safety.get("parameter_set_tunable") is not True:
        failures.append("safety_parameter_set_tunable_not_true")
    if safety.get("weights_apply_only_after_human_gate") is not True:
        failures.append("safety_weights_apply_only_after_human_gate_not_true")
    adjustment = profile.get("adjustment_loop") if isinstance(profile.get("adjustment_loop"), Mapping) else {}
    if adjustment.get("human_review_required") is not True:
        failures.append("adjustment_human_review_required_not_true")
    if adjustment.get("auto_apply_allowed") is not False:
        failures.append("adjustment_auto_apply_allowed_not_false")
    if adjustment.get("auto_promotion_allowed") is not False:
        failures.append("adjustment_auto_promotion_allowed_not_false")
    return {
        "ok": not failures,
        "validator_version": PREDICTION_EVIDENCE_SOURCE_WEIGHT_PROFILE_VERSION,
        "failure_count": len(failures),
        "failures": failures,
        "source_count": len(sources),
        "weight_total_percent": weight_total,
    }


def estimate_prediction_display_confidence_from_evidence_profile(
    profile: Mapping[str, Any],
    *,
    predicted_direction: str,
    source_signals: Mapping[str, Mapping[str, Any]] | None = None,
) -> dict[str, Any]:
    """Estimate card display confidence from source weights, learned reliability, current signal strength, and agreement.

    This is a pure aggregation helper. It does not read market data, invoke prediction/classification,
    write artifacts, or apply parameter changes. Runtime family logic may supply source_signals later.
    """

    validation = validate_prediction_evidence_source_weight_profile(profile)
    signals = source_signals if isinstance(source_signals, Mapping) else {}
    sources = profile.get("sources") if isinstance(profile.get("sources"), list) else []
    direction = str(predicted_direction or "unknown")
    floor = _percent(profile.get("confidence_floor_percent"), default=0)
    ceiling = _percent(profile.get("confidence_ceiling_percent"), default=100)
    weighted_quality_sum = 0.0
    weighted_quality_denominator = 0.0
    aligned_quality_sum = 0.0
    source_rows: list[dict[str, Any]] = []
    horizon_cap = _percent(profile.get("horizon_confidence_cap_percent"), default=_default_horizon_confidence_cap_percent(str(profile.get("horizon_group") or "")))
    caps: list[int] = [ceiling, horizon_cap]
    blockers: list[str] = []
    for source in sources:
        if not isinstance(source, Mapping):
            continue
        source_id = str(source.get("source_id") or "")
        signal = signals.get(source_id) if isinstance(signals.get(source_id), Mapping) else {}
        weight = _percent(signal.get("weight_percent", source.get("weight_percent")), default=0)
        reliability = _percent(signal.get("reliability_percent", source.get("default_reliability_percent")), default=50)
        strength = _percent(signal.get("signal_strength_percent", source.get("default_signal_strength_percent")), default=50)
        freshness = _percent(signal.get("freshness_percent", source.get("default_freshness_percent")), default=100)
        quality = _percent(signal.get("quality_percent", source.get("default_quality_percent")), default=100)
        source_direction = str(signal.get("direction", source.get("default_direction") or "unknown"))
        role = str(source.get("role") or "supporting")
        cap = signal.get("confidence_cap_percent", source.get("confidence_cap_percent"))
        if cap is not None:
            caps.append(_percent(cap, default=100))
        blocked = bool(signal.get("blocked", False)) or (role in {"veto", "blocker"} and source_direction not in {"unknown", direction, "context_only"} and strength >= 70)
        missing_required = bool(source.get("min_required")) and source_direction == "unknown" and str(source.get("missing_policy") or "") in {"force_unknown", "block_signal"}
        if blocked:
            blockers.append(f"source_blocked:{source_id}")
        if missing_required:
            blockers.append(f"required_source_missing:{source_id}")
        source_quality = reliability * strength * freshness * quality / 1_000_000.0
        contribution = weight * source_quality
        included = role not in {"reference_only", "context_only"} and weight > 0
        aligned = included and source_direction == direction
        if included:
            weighted_quality_sum += contribution
            weighted_quality_denominator += weight
            if aligned:
                aligned_quality_sum += contribution
        source_rows.append({
            "source_id": source_id,
            "role": role,
            "weight_percent": weight,
            "reliability_percent": reliability,
            "signal_strength_percent": strength,
            "freshness_percent": freshness,
            "quality_percent": quality,
            "direction": source_direction,
            "aligned_with_prediction": bool(aligned),
            "included_in_confidence": bool(included),
            "quality_score_percent": round(source_quality, 4),
            "weighted_contribution": round(contribution, 4),
        })
    weighted_source_quality = 0.0 if weighted_quality_denominator <= 0 else weighted_quality_sum / weighted_quality_denominator
    aligned_ratio = 0.0 if weighted_quality_sum <= 0 else aligned_quality_sum / weighted_quality_sum
    agreement_multiplier = 0.55 + 0.45 * aligned_ratio
    estimated = weighted_source_quality * agreement_multiplier
    capped = max(floor, min(min(caps), int(round(estimated))))
    if blockers:
        capped = min(capped, 25)
    return {
        "ok": bool(validation.get("ok")) and not blockers,
        "estimator_version": "display_confidence.weighted_reliability_signal_agreement.v1",
        "predicted_direction": direction,
        "display_confidence_percent": capped,
        "weighted_source_quality_percent": round(weighted_source_quality, 4),
        "aligned_weighted_quality_ratio": round(aligned_ratio, 4),
        "agreement_multiplier": round(agreement_multiplier, 4),
        "confidence_floor_percent": floor,
        "confidence_ceiling_percent": ceiling,
        "horizon_confidence_cap_percent": horizon_cap,
        "applied_confidence_cap_percent": min(caps),
        "blockers": blockers,
        "source_count": len(source_rows),
        "source_rows": source_rows,
        "validation": validation,
        "safety": _safety(),
    }
