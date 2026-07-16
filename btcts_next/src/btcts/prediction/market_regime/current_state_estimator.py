# path: ./btcts_next/src/btcts/prediction/market_regime/current_state_estimator.py
# desc: MR-F2 pure current-state estimator from current L4 candle signals only. No forecast-label reuse, reads, writes, UI, broker, scheduler, or AutoTrade.

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Mapping

from .contracts import FeatureGroup
from .features import MarketRegimeFeatureBundle
from .current_state_persistence import build_persisted_current_state
from .feature_scoring import (
    build_market_regime_shadow_label_recommendation,
    score_market_regime_candidates,
    summarize_market_regime_candidate_scores,
)
from .parameter_set import build_default_market_regime_parameter_set
from .transition_policy import evaluate_market_regime_transition

CURRENT_STATE_ESTIMATOR_VERSION = "prediction.market_regime.current_state_estimator.mr_f2.v1"


def _signals(bundle: MarketRegimeFeatureBundle, group: FeatureGroup) -> Mapping[str, Any]:
    return {signal.name: signal for signal in bundle.signals_by_group(group)}


def _value(bundle: MarketRegimeFeatureBundle, group: FeatureGroup, name: str, default: Any = None) -> Any:
    signal = _signals(bundle, group).get(name)
    if signal is None or not signal.available:
        return default
    return signal.value


def _parse_utc(value: Any) -> datetime | None:
    text = str(value or "").strip()
    if not text:
        return None
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(text)
    except Exception:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _window_age_sec(started_at: str, cutoff: str) -> int | None:
    start = _parse_utc(started_at)
    end = _parse_utc(cutoff)
    if start is None or end is None or end < start:
        return None
    return int((end - start).total_seconds())


def _previous_state_age_sec(previous_state: Mapping[str, Any] | None, observed_at: str) -> int | None:
    previous = dict(previous_state or {})
    started_at = str(previous.get("state_started_at") or "")
    return _window_age_sec(started_at, observed_at)


def _as_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except Exception:
        return default


def _transition_settings(parameter_set: Any) -> Mapping[str, Any]:
    thresholds = getattr(parameter_set, "thresholds", {})
    if not isinstance(thresholds, Mapping):
        return {}
    value = thresholds.get("transition_and_persistence", {})
    return value if isinstance(value, Mapping) else {}


def resolve_market_regime_canonical_label(
    *,
    usable: bool,
    legacy_label: str,
    previous_state: Mapping[str, Any] | None,
    shadow_recommendation: Mapping[str, Any],
    transition_result: Mapping[str, Any],
    parameter_set: Any,
) -> dict[str, Any]:
    legacy = str(legacy_label or "UNKNOWN").strip().upper() or "UNKNOWN"
    previous = str(dict(previous_state or {}).get("regime_code") or "UNKNOWN").strip().upper() or "UNKNOWN"
    settings = _transition_settings(parameter_set)
    enabled = bool(settings.get("canonical_application_enabled", False))
    recommendation_ready = bool(shadow_recommendation.get("shadow_recommendation_ready", False))
    decision = str(transition_result.get("decision") or "unknown")
    accepted = str(transition_result.get("accepted_regime") or "UNKNOWN").strip().upper() or "UNKNOWN"

    if not usable:
        selected = "UNKNOWN"
        source = "current_state_estimator_unavailable"
        reason = "current_evidence_unusable"
        applied = False
    elif not enabled:
        selected = legacy
        source = "current_l4_candle_regime_hint"
        reason = "mr_f4_canonical_application_disabled"
        applied = False
    elif recommendation_ready and decision in {"started", "continued", "transitioned"} and accepted != "UNKNOWN":
        selected = accepted
        source = "mr_f4_transition_policy"
        reason = f"mr_f4_transition_policy_{decision}"
        applied = True
    elif previous != "UNKNOWN":
        selected = previous
        source = "mr_f4_transition_policy_hold"
        reason = (
            f"mr_f4_transition_policy_{decision}"
            if recommendation_ready
            else "mr_f4_shadow_recommendation_not_ready_hold_previous"
        )
        applied = True
    else:
        selected = legacy
        source = "current_l4_candle_regime_hint"
        reason = (
            "mr_f4_transition_policy_no_previous_fallback"
            if recommendation_ready
            else "mr_f4_shadow_recommendation_not_ready_no_previous_fallback"
        )
        applied = False

    return {
        "selected_regime": selected,
        "label_source": source,
        "selection_reason": reason,
        "canonical_application_enabled": enabled,
        "transition_policy_applied_to_selected_label": applied,
        "legacy_fallback_used": source == "current_l4_candle_regime_hint",
        "previous_regime_held": source == "mr_f4_transition_policy_hold",
    }


def _change_point_evidence_score(*, net_bps: float, range_bps: float, close_position: float) -> float:
    if range_bps <= 0:
        return 0.0
    directional_ratio = min(1.0, abs(net_bps) / range_bps)
    edge_distance = min(1.0, abs(close_position - 0.5) * 2.0)
    return round(min(1.0, 0.65 * directional_ratio + 0.35 * edge_distance), 4)


def estimate_current_market_regime(bundle: MarketRegimeFeatureBundle, *, previous_state: Mapping[str, Any] | None = None, observed_at: str | None = None) -> dict[str, Any]:
    current_enough = bool(
        _value(
            bundle,
            FeatureGroup.SOURCE_QUALITY,
            "current_l4_candle_window_current_enough",
            False,
        )
    )
    label = str(
        _value(
            bundle,
            FeatureGroup.PRICE_STRUCTURE,
            "current_l4_candle_regime_hint",
            "UNKNOWN",
        )
        or "UNKNOWN"
    )
    reason = str(
        _value(
            bundle,
            FeatureGroup.PRICE_STRUCTURE,
            "current_l4_candle_regime_reason",
            "current_l4_candle_regime_reason_missing",
        )
        or "current_l4_candle_regime_reason_missing"
    )
    cutoff = str(
        _value(
            bundle,
            FeatureGroup.SOURCE_QUALITY,
            "current_l4_candle_window_generated_at",
            "",
        )
        or ""
    )
    threshold_set_id = str(
        _value(
            bundle,
            FeatureGroup.PRICE_STRUCTURE,
            "current_l4_candle_threshold_set_id",
            "",
        )
        or ""
    )
    state_window_started_at = str(
        _value(
            bundle,
            FeatureGroup.PRICE_STRUCTURE,
            "current_l4_candle_window_first_ts",
            "",
        )
        or ""
    )
    net_bps = _as_float(
        _value(bundle, FeatureGroup.PRICE_STRUCTURE, "current_l4_candle_net_change_bps", 0.0)
    )
    range_bps = _as_float(
        _value(bundle, FeatureGroup.PRICE_STRUCTURE, "current_l4_candle_range_bps", 0.0)
    )
    close_position = _as_float(
        _value(bundle, FeatureGroup.PRICE_STRUCTURE, "current_l4_candle_close_position", 0.5),
        0.5,
    )
    realized_volatility_bps = _as_float(
        _value(bundle, FeatureGroup.VOLATILITY, "current_l4_candle_realized_volatility_bps", 0.0)
    )
    change_point_evidence_score = _change_point_evidence_score(
        net_bps=net_bps,
        range_bps=range_bps,
        close_position=close_position,
    )
    transition_candidate = change_point_evidence_score >= 0.65
    state_window_age_sec = _window_age_sec(state_window_started_at, cutoff)
    source_currentness_verified = current_enough and bool(cutoff)
    usable = (
        current_enough
        and label != "UNKNOWN"
        and bool(cutoff)
        and bool(state_window_started_at)
        and state_window_age_sec is not None
    )
    evidence = {
        "net_change_bps": round(net_bps, 4),
        "range_bps": round(range_bps, 4),
        "close_position": round(close_position, 4),
        "realized_volatility_bps": round(realized_volatility_bps, 4),
        "threshold_set_id": threshold_set_id,
        "source_refs": ["warroom_candles", "active_parameter_set"],
    }
    candidate_scoring = score_market_regime_candidates(bundle)
    candidate_summary = summarize_market_regime_candidate_scores(candidate_scoring)
    shadow_recommendation = build_market_regime_shadow_label_recommendation(
        bundle,
        candidate_summary,
        selected_label=label if usable else "UNKNOWN",
    )
    observation_time = str(observed_at or bundle.generated_at)
    parameter_set = build_default_market_regime_parameter_set()
    shadow_transition = evaluate_market_regime_transition(
        previous_regime=str(dict(previous_state or {}).get("regime_code") or "UNKNOWN"),
        candidate_regime=str(
            shadow_recommendation.get("shadow_recommended_regime_code") or "UNKNOWN"
        ),
        previous_state_age_sec=_previous_state_age_sec(previous_state, observation_time),
        candidate_score=candidate_summary.get("eligible_top_candidate_score"),
        runner_up_score=candidate_summary.get("eligible_runner_up_score"),
        change_point_evidence_score=change_point_evidence_score if usable else 0.0,
        parameter_set=parameter_set,
    )
    canonical_selection = resolve_market_regime_canonical_label(
        usable=usable,
        legacy_label=label if usable else "UNKNOWN",
        previous_state=previous_state,
        shadow_recommendation=shadow_recommendation,
        transition_result=shadow_transition,
        parameter_set=parameter_set,
    )
    selected_regime = str(canonical_selection["selected_regime"])
    persistence = build_persisted_current_state(
        previous=previous_state,
        regime_code=selected_regime,
        observed_at=observation_time,
        estimator_version=CURRENT_STATE_ESTIMATOR_VERSION,
        source_cutoff_time=cutoff,
    )
    return {
        "ok": usable,
        "regime_label": selected_regime,
        "selection_reason": (
            "current_state_estimator_unavailable"
            if not usable
            else (
                "mr_f4_transition_policy"
                if canonical_selection["transition_policy_applied_to_selected_label"]
                else "current_state_estimator"
            )
        ),
        "canonical_selection_reason": canonical_selection["selection_reason"],
        "estimator_version": CURRENT_STATE_ESTIMATOR_VERSION,
        "source_cutoff_time": cutoff,
        "source_currentness_verified": source_currentness_verified,
        "state_started_at": persistence.get("state_started_at", ""),
        "state_age_sec": persistence.get("state_age_sec"),
        "state_start_estimation_status": persistence.get("persistence_status", "unavailable"),
        "state_transition_detected": persistence.get("transition_detected", False),
        "previous_regime_code": persistence.get("previous_regime_code", "UNKNOWN"),
        "state_window_started_at": state_window_started_at if usable else "",
        "state_window_age_sec": state_window_age_sec if usable else None,
        "change_point_probability": None,
        "change_point_probability_calibrated": False,
        "change_point_evidence_score": change_point_evidence_score if usable else 0.0,
        "transition_candidate": transition_candidate if usable else False,
        "transition_candidate_basis": "heuristic_change_point_evidence_score" if usable else "unavailable",
        "threshold_set_id": threshold_set_id,
        "evidence_reason": reason,
        "supporting_evidence": evidence if usable else {},
        "conflicting_evidence": [],
        "label_source": canonical_selection["label_source"],
        "legacy_current_l4_regime_label": label if usable else "UNKNOWN",
        "transition_policy_canonical_application_enabled": canonical_selection["canonical_application_enabled"],
        "transition_policy_applied_to_selected_label": canonical_selection["transition_policy_applied_to_selected_label"],
        "transition_policy_legacy_fallback_used": canonical_selection["legacy_fallback_used"],
        "transition_policy_previous_regime_held": canonical_selection["previous_regime_held"],
        "candidate_scoring_version": candidate_scoring.get("logic_version", ""),
        "candidate_scores": candidate_scoring.get("candidate_scores", {}),
        "candidate_scoring_blockers": candidate_summary.get("scoring_blockers", []),
        "top_candidate": candidate_summary.get("top_candidate", ""),
        "top_candidate_score": candidate_summary.get("top_candidate_score"),
        "runner_up_candidate": candidate_summary.get("runner_up_candidate", ""),
        "runner_up_score": candidate_summary.get("runner_up_score"),
        "candidate_score_margin": candidate_summary.get("score_margin"),
        "eligible_top_candidate": candidate_summary.get("eligible_top_candidate", ""),
        "eligible_top_candidate_score": candidate_summary.get("eligible_top_candidate_score"),
        "eligible_runner_up_candidate": candidate_summary.get("eligible_runner_up_candidate", ""),
        "eligible_runner_up_score": candidate_summary.get("eligible_runner_up_score"),
        "eligible_candidate_score_margin": candidate_summary.get("eligible_score_margin"),
        "eligible_top_candidate_available_weight": candidate_summary.get("eligible_top_candidate_available_weight", 0.0),
        "label_selection_eligible_candidates": candidate_summary.get("label_selection_eligible_candidates", []),
        "label_selection_ineligible_candidates": candidate_summary.get("label_selection_ineligible_candidates", {}),
        "label_selection_readiness_blockers": candidate_summary.get("label_selection_readiness_blockers", []),
        "top_candidate_available_weight": candidate_summary.get("top_candidate_available_weight", 0.0),
        "top_candidate_missing_feature_groups": candidate_summary.get("top_candidate_missing_feature_groups", []),
        "top_candidate_contradictory_feature_groups": candidate_summary.get("top_candidate_contradictory_feature_groups", []),
        "top_candidate_contributions": candidate_summary.get("top_candidate_contributions", []),
        "scoring_ready_for_label_selection": candidate_summary.get("scoring_ready_for_label_selection", False),
        "scoring_label_selection_enabled": candidate_summary.get("label_selection_enabled", False),
        "scoring_label_selection_deferred_reason": candidate_summary.get("label_selection_deferred_reason", ""),
        "scoring_readiness_thresholds": candidate_summary.get("readiness_thresholds", {}),
        "shadow_recommended_regime_code": shadow_recommendation.get("shadow_recommended_regime_code", "UNKNOWN"),
        "shadow_recommendation_candidate": shadow_recommendation.get("shadow_recommendation_candidate", ""),
        "shadow_recommendation_candidate_score": shadow_recommendation.get("shadow_recommendation_candidate_score"),
        "shadow_recommendation_ready": shadow_recommendation.get("shadow_recommendation_ready", False),
        "shadow_recommendation_direction_basis": shadow_recommendation.get("shadow_recommendation_direction_basis", ""),
        "shadow_recommendation_agrees_with_selected_label": shadow_recommendation.get("shadow_recommendation_agrees_with_selected_label", False),
        "shadow_recommendation_mismatch_reason": shadow_recommendation.get("shadow_recommendation_mismatch_reason", ""),
        "shadow_recommendation_enabled": shadow_recommendation.get("shadow_recommendation_enabled", False),
        "shadow_recommendation_applied_to_selected_label": shadow_recommendation.get("shadow_recommendation_applied_to_selected_label", False),
        "shadow_transition_policy_version": shadow_transition.get("logic_version", ""),
        "shadow_transition_previous_regime": shadow_transition.get("previous_regime", "UNKNOWN"),
        "shadow_transition_candidate_regime": shadow_transition.get("candidate_regime", "UNKNOWN"),
        "shadow_transition_accepted_regime": shadow_transition.get("accepted_regime", "UNKNOWN"),
        "shadow_transition_decision": shadow_transition.get("decision", "unknown"),
        "shadow_transition_blockers": shadow_transition.get("blockers", []),
        "shadow_transition_allowed": shadow_transition.get("transition_allowed", False),
        "shadow_transition_dwell_satisfied": shadow_transition.get("dwell_satisfied", False),
        "shadow_transition_hysteresis_satisfied": shadow_transition.get("hysteresis_satisfied", False),
        "shadow_transition_change_point_override_applied": shadow_transition.get("change_point_override_applied", False),
        "shadow_transition_candidate_margin": shadow_transition.get("candidate_margin"),
        "shadow_transition_penalty": shadow_transition.get("transition_penalty"),
        "shadow_persistence_probability": shadow_transition.get("persistence_probability"),
        "shadow_persistence_probability_calibrated": shadow_transition.get("persistence_probability_calibrated", False),
        "shadow_transition_observation_only": not canonical_selection["transition_policy_applied_to_selected_label"],
        "shadow_transition_applied_to_selected_label": canonical_selection["transition_policy_applied_to_selected_label"],
        "current_state_outcome_rule_version": "market_regime_current_state_outcome_rule.mr_f2.v1",
        "current_state_outcome_rule_defined": True,
        "current_state_outcome_rule_gap": "",
        "future_forecast_label_used": False,
        "read_only": True,
        "non_executing": True,
        "prediction_artifact_write_allowed": False,
        "broker_private_api_allowed": False,
        "autotrade_trigger_allowed": False,
        "would_send_to_broker": False,
    }
