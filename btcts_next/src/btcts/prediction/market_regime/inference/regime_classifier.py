# path: ./btcts_next/src/btcts/prediction/market_regime/inference/regime_classifier.py
# desc: Pure market-regime classifier v1 from feature bundle to prediction packet. No reads, writes, UI, scheduler, or execution behavior.

from __future__ import annotations

from typing import Any, Mapping, Tuple

from ..contracts import EvidenceQuality, FeatureGroup, FreshnessState, MarketRegimeCode, MarketRegimePrediction, MarketRegimePredictionPacket, TacticalHint
from ..features import FeatureSignal, MarketRegimeFeatureBundle
from ..horizon_policy import build_default_horizon_policy
from ..current_state_estimator import estimate_current_market_regime
from .current_l4_diagnostic import build_current_l4_candle_evidence_digest

MARKET_REGIME_CLASSIFIER_VERSION = "prediction.market_regime.regime_classifier.ps_q27z.v3"
# MR_A1_STALE_SOURCE_GATE_2026_07_09
# MR_A2_CURRENT_L4_CANDLE_FEATURES_2026_07_09



def _signals(bundle: MarketRegimeFeatureBundle, group: FeatureGroup) -> Mapping[str, FeatureSignal]:
    return {signal.name: signal for signal in bundle.signals_by_group(group)}


def _value(bundle: MarketRegimeFeatureBundle, group: FeatureGroup, name: str, default: Any = None) -> Any:
    signal = _signals(bundle, group).get(name)
    if signal is None or not signal.available:
        return default
    return signal.value


def _bool(bundle: MarketRegimeFeatureBundle, group: FeatureGroup, name: str) -> bool:
    return bool(_value(bundle, group, name, False))


def _float(bundle: MarketRegimeFeatureBundle, group: FeatureGroup, name: str, default: float = 0.0) -> float:
    try:
        return float(_value(bundle, group, name, default))
    except Exception:
        return default


def _labels_by_horizon(bundle: MarketRegimeFeatureBundle) -> Mapping[str, str]:
    value = _value(bundle, FeatureGroup.PRICE_STRUCTURE, "market_regime_labels_by_horizon_sec", {})
    if not isinstance(value, Mapping):
        return {}
    return {str(key): str(val) for key, val in value.items() if val}


def _float_map_by_horizon(bundle: MarketRegimeFeatureBundle, name: str) -> Mapping[str, float]:
    value = _value(bundle, FeatureGroup.PRICE_STRUCTURE, name, {})
    if not isinstance(value, Mapping):
        return {}
    result: dict[str, float] = {}
    for key, val in value.items():
        try:
            result[str(key)] = float(val)
        except Exception:
            continue
    return result


def _selected_forecast_metric(bundle: MarketRegimeFeatureBundle, name: str, selected_horizon_sec: int | None) -> float | None:
    if selected_horizon_sec is None:
        return None
    return _float_map_by_horizon(bundle, name).get(str(int(selected_horizon_sec)))


def _selected_label_for_horizon(bundle: MarketRegimeFeatureBundle, horizon_sec: int, *, current_estimate: Mapping[str, Any] | None = None) -> tuple[Any, int | None, str]:
    if int(horizon_sec) == 0:
        current = current_estimate or estimate_current_market_regime(bundle)
        return (
            current.get("regime_label") if current.get("ok") else None,
            None,
            str(current.get("selection_reason") or "current_state_estimator_unavailable"),
        )
    forecast_current_enough = bool(_value(bundle, FeatureGroup.SOURCE_QUALITY, "forecast_records_current_enough", True))
    current_l4_candle_current_enough = bool(_value(bundle, FeatureGroup.SOURCE_QUALITY, "current_l4_candle_window_current_enough", False))
    if not forecast_current_enough:
        candle_hint = _value(bundle, FeatureGroup.PRICE_STRUCTURE, "current_l4_candle_regime_hint")
        if current_l4_candle_current_enough and candle_hint and int(horizon_sec) <= 3600:
            return candle_hint, None, "current_l4_candle_window_fallback"
        return None, None, "forecast_records_stale_blocked"
    labels = _labels_by_horizon(bundle)
    if str(int(horizon_sec)) in labels:
        return labels[str(int(horizon_sec))], int(horizon_sec), "exact_forecast_horizon"
    return None, None, "forecast_horizon_label_missing"


def _label_to_regime(label: Any, *, source_snapshot_ok: bool) -> MarketRegimeCode:
    if not source_snapshot_ok:
        return MarketRegimeCode.UNKNOWN
    normalized = str(label or "").lower()
    if normalized in ("range_candidate", "range", "neutral_range"):
        return MarketRegimeCode.RANGE
    if normalized in ("low_vol_compression", "low_vol", "compression"):
        return MarketRegimeCode.LOW_VOL_COMPRESSION
    if normalized in ("trend_candidate", "up_trend", "trend_up", "long_bias"):
        return MarketRegimeCode.UP_TREND
    if normalized in ("down_trend", "trend_down", "short_bias"):
        return MarketRegimeCode.DOWN_TREND
    if normalized in ("volatile_or_divergent", "high_vol_chop", "choppy"):
        return MarketRegimeCode.HIGH_VOL_CHOP
    if normalized in ("breakout", "breakout_candidate"):
        return MarketRegimeCode.BREAKOUT
    if normalized in ("reversal_watch", "reaction_zone_watch"):
        return MarketRegimeCode.REVERSAL_WATCH
    return MarketRegimeCode.UNKNOWN


def _tactical_hint(regime: MarketRegimeCode, *, crossed_or_negative_spread: bool, source_snapshot_ok: bool) -> TacticalHint:
    if not source_snapshot_ok:
        return TacticalHint.UNKNOWN_HOLD
    if crossed_or_negative_spread:
        return TacticalHint.NO_NEW_ENTRY
    if regime == MarketRegimeCode.RANGE:
        return TacticalHint.RANGE_TACTIC
    if regime in (MarketRegimeCode.UP_TREND, MarketRegimeCode.DOWN_TREND):
        return TacticalHint.TREND_FOLLOW_WATCH
    if regime == MarketRegimeCode.BREAKOUT:
        return TacticalHint.BREAKOUT_WATCH
    if regime == MarketRegimeCode.REVERSAL_WATCH:
        return TacticalHint.REVERSAL_WATCH
    if regime in (MarketRegimeCode.HIGH_VOL_CHOP, MarketRegimeCode.PANIC_SPIKE):
        return TacticalHint.RISK_REDUCE
    return TacticalHint.UNKNOWN_HOLD


def _evidence_quality(
    bundle: MarketRegimeFeatureBundle,
    *,
    regime: MarketRegimeCode,
    label_selection_reason: str,
    crossed_or_negative_spread: bool,
    forecast_score: float | None = None,
    signal_strength_percent: float | None = None,
    reference_hit_rate_percent: float | None = None,
) -> tuple[EvidenceQuality, str]:
    if not bundle.source_snapshot_ok:
        return EvidenceQuality.MISSING, "source_snapshot_missing"
    if regime == MarketRegimeCode.UNKNOWN:
        return EvidenceQuality.MISSING, "no_current_evidence_for_horizon"
    if label_selection_reason in {"current_l4_candle_window_fallback", "current_state_estimator"}:
        if crossed_or_negative_spread:
            return EvidenceQuality.WEAK, "current_l4_fallback_uncalibrated_with_crossed_or_negative_spread"
        return EvidenceQuality.PARTIAL, "current_l4_fallback_uncalibrated_partial"
    available_count = bundle.available_signal_count()
    source_score = _float(bundle, FeatureGroup.SOURCE_QUALITY, "source_quality_score", 0.0)
    if forecast_score is not None or signal_strength_percent is not None or reference_hit_rate_percent is not None:
        score = max(0.0, min(float(forecast_score or 0.0), 1.0))
        strength = max(0.0, min(float(signal_strength_percent or 0.0), 100.0))
        reference = max(0.0, min(float(reference_hit_rate_percent or 0.0), 100.0))
        metric_quality = (score * 0.45) + (strength / 100.0 * 0.35) + (reference / 100.0 * 0.20)
        if crossed_or_negative_spread:
            return (EvidenceQuality.PARTIAL if metric_quality >= 0.72 and source_score >= 0.70 else EvidenceQuality.WEAK), "forecast_metric_with_crossed_or_negative_spread"
        if metric_quality >= 0.72 and source_score >= 0.80 and available_count >= 10:
            return EvidenceQuality.STRONG, "forecast_metric_strong"
        if metric_quality >= 0.48 and source_score >= 0.60 and available_count >= 6:
            return EvidenceQuality.PARTIAL, "forecast_metric_partial"
        return EvidenceQuality.WEAK, "forecast_metric_weak"
    if crossed_or_negative_spread:
        return (EvidenceQuality.PARTIAL if source_score >= 0.70 and available_count >= 8 else EvidenceQuality.WEAK), "legacy_source_fallback_crossed_or_negative_spread"
    if source_score >= 0.90 and available_count >= 10:
        return EvidenceQuality.STRONG, "legacy_source_fallback_strong"
    if source_score >= 0.65 and available_count >= 6:
        return EvidenceQuality.PARTIAL, "legacy_source_fallback_partial"
    if available_count > 0:
        return EvidenceQuality.WEAK, "legacy_source_fallback_weak"
    return EvidenceQuality.MISSING, "legacy_source_fallback_missing"


def _confidence_percent(
    bundle: MarketRegimeFeatureBundle,
    regime: MarketRegimeCode,
    *,
    crossed_or_negative_spread: bool,
    forecast_score: float | None = None,
    signal_strength_percent: float | None = None,
    reference_hit_rate_percent: float | None = None,
) -> int:
    if regime == MarketRegimeCode.UNKNOWN or not bundle.source_snapshot_ok:
        return 15
    forecast_current_enough = bool(_value(bundle, FeatureGroup.SOURCE_QUALITY, "forecast_records_current_enough", True))
    current_l4_candle_current_enough = bool(_value(bundle, FeatureGroup.SOURCE_QUALITY, "current_l4_candle_window_current_enough", False))
    source_score = _float(bundle, FeatureGroup.SOURCE_QUALITY, "source_quality_score", 0.0)
    available_count = min(bundle.available_signal_count(), 12)
    if forecast_score is None and signal_strength_percent is None and reference_hit_rate_percent is None:
        base_by_regime = {
            MarketRegimeCode.RANGE: 52,
            MarketRegimeCode.UP_TREND: 56,
            MarketRegimeCode.DOWN_TREND: 56,
            MarketRegimeCode.HIGH_VOL_CHOP: 58,
            MarketRegimeCode.BREAKOUT: 55,
            MarketRegimeCode.REVERSAL_WATCH: 49,
            MarketRegimeCode.LOW_VOL_COMPRESSION: 50,
            MarketRegimeCode.PANIC_SPIKE: 60,
        }.get(regime, 20)
        confidence = base_by_regime + int(source_score * 18) + int(available_count / 12 * 8)
    else:
        base_by_regime = {
            MarketRegimeCode.RANGE: 40,
            MarketRegimeCode.UP_TREND: 43,
            MarketRegimeCode.DOWN_TREND: 43,
            MarketRegimeCode.HIGH_VOL_CHOP: 44,
            MarketRegimeCode.BREAKOUT: 42,
            MarketRegimeCode.REVERSAL_WATCH: 38,
            MarketRegimeCode.LOW_VOL_COMPRESSION: 39,
            MarketRegimeCode.PANIC_SPIKE: 46,
        }.get(regime, 20)
        score_component = int(max(0.0, min(float(forecast_score or 0.0), 1.0)) * 14)
        strength_component = int(max(0.0, min(float(signal_strength_percent or 0.0), 100.0)) * 0.14)
        reference_component = int(max(0.0, min(float(reference_hit_rate_percent or 0.0), 100.0)) * 0.05)
        confidence = base_by_regime + int(source_score * 9) + int(available_count / 12 * 5) + score_component + strength_component + reference_component
    if crossed_or_negative_spread:
        confidence -= 10
    if not forecast_current_enough and current_l4_candle_current_enough:
        confidence = min(confidence, 65)
    elif not forecast_current_enough and not current_l4_candle_current_enough:
        confidence = min(confidence, 35)
    return max(0, min(confidence, 99))


def _drivers(
    bundle: MarketRegimeFeatureBundle,
    regime: MarketRegimeCode,
    *,
    selected_label: Any,
    selected_horizon_sec: int | None,
    label_selection_reason: str,
) -> Tuple[str, ...]:
    drivers: list[str] = []
    horizons = _value(bundle, FeatureGroup.PRICE_STRUCTURE, "market_regime_horizons_sec", [])
    volatility_state = _value(bundle, FeatureGroup.VOLATILITY, "volatility_state")
    cross_venue = _value(bundle, FeatureGroup.CROSS_VENUE, "cross_venue_agreement")
    if selected_label:
        if label_selection_reason in {"current_l4_candle_window_fallback", "current_state_estimator"}:
            drivers.append(f"current_l4_candle_regime_hint:{selected_label}")
        else:
            drivers.append(f"forecast_label:{selected_label}")
    if selected_horizon_sec is not None:
        drivers.append(f"forecast_horizon_sec:{selected_horizon_sec}")
    drivers.append(f"forecast_label_selection:{label_selection_reason}")
    if horizons:
        drivers.append(f"forecast_horizons:{','.join(str(item) for item in horizons)}")
    if volatility_state:
        drivers.append(f"volatility_state:{volatility_state}")
    if cross_venue:
        drivers.append(f"cross_venue_agreement:{cross_venue}")
    drivers.append(f"classified_regime:{regime.value}")
    return tuple(dict.fromkeys(drivers))


def _warnings(
    bundle: MarketRegimeFeatureBundle,
    *,
    horizon_sec: int,
    label_selection_reason: str,
    crossed_or_negative_spread: bool,
) -> Tuple[str, ...]:
    warnings = list(bundle.warnings)
    if crossed_or_negative_spread:
        warnings.append("negative_spread_seen")
        warnings.append("tactical_hint_forced_no_new_entry")
    forecast_current_enough = bool(_value(bundle, FeatureGroup.SOURCE_QUALITY, "forecast_records_current_enough", True))
    current_l4_candle_current_enough = bool(_value(bundle, FeatureGroup.SOURCE_QUALITY, "current_l4_candle_window_current_enough", False))
    if not forecast_current_enough:
        warnings.append("forecast_records_stale")
        warnings.append("forecast_label_blocked_by_currentness_gate")
        if label_selection_reason == "current_l4_candle_window_fallback":
            warnings.append("current_l4_candle_window_fallback_used")
        elif label_selection_reason == "current_state_estimator":
            warnings.append("current_state_estimator_used")
        elif current_l4_candle_current_enough and int(horizon_sec) > 3600:
            warnings.append("current_l4_candle_window_not_applicable_to_horizon")
    if not bundle.source_snapshot_ok:
        warnings.append("source_snapshot_not_ok")
    return tuple(dict.fromkeys(warnings))


def _freshness_state_for_horizon(
    bundle: MarketRegimeFeatureBundle,
    *,
    regime: MarketRegimeCode,
    label_selection_reason: str,
) -> FreshnessState:
    if not bundle.source_snapshot_ok:
        return FreshnessState.MISSING
    if regime == MarketRegimeCode.UNKNOWN:
        return FreshnessState.STALE
    if label_selection_reason in {
        "exact_forecast_horizon",
        "current_l4_candle_window_fallback",
        "current_state_estimator",
    }:
        return FreshnessState.LIVE
    return FreshnessState.STALE


def _missing_sources(bundle: MarketRegimeFeatureBundle) -> Tuple[str, ...]:
    return tuple(dict.fromkeys(bundle.missing_sources))


def classify_market_regime_feature_bundle(
    bundle: MarketRegimeFeatureBundle,
    *,
    generated_at: str,
    previous_current_state: Mapping[str, Any] | None = None,
) -> MarketRegimePredictionPacket:
    crossed_or_negative_spread = _bool(bundle, FeatureGroup.LIQUIDITY, "crossed_or_negative_spread")
    forecast_current_enough = bool(_value(bundle, FeatureGroup.SOURCE_QUALITY, "forecast_records_current_enough", True))
    current_l4_candle_current_enough = bool(_value(bundle, FeatureGroup.SOURCE_QUALITY, "current_l4_candle_window_current_enough", False))
    missing_sources = _missing_sources(bundle)
    packet_warnings: list[str] = []

    prediction_rows: list[MarketRegimePrediction] = []
    current_estimate = estimate_current_market_regime(
        bundle,
        previous_state=previous_current_state,
        observed_at=generated_at,
    )
    for horizon in build_default_horizon_policy().horizons:
        selected_label, selected_horizon_sec, label_selection_reason = _selected_label_for_horizon(
            bundle,
            horizon.horizon_sec,
            current_estimate=current_estimate,
        )
        regime = _label_to_regime(
            selected_label,
            source_snapshot_ok=bundle.source_snapshot_ok,
        )
        forecast_score = _selected_forecast_metric(bundle, "market_regime_scores_by_horizon_sec", selected_horizon_sec)
        signal_strength_percent = _selected_forecast_metric(bundle, "market_regime_signal_strength_percent_by_horizon_sec", selected_horizon_sec)
        reference_hit_rate_percent = _selected_forecast_metric(bundle, "market_regime_reference_hit_rate_percent_by_horizon_sec", selected_horizon_sec)
        confidence = _confidence_percent(
            bundle,
            regime,
            crossed_or_negative_spread=crossed_or_negative_spread,
            forecast_score=forecast_score,
            signal_strength_percent=signal_strength_percent,
            reference_hit_rate_percent=reference_hit_rate_percent,
        )
        evidence, evidence_quality_reason = _evidence_quality(
            bundle,
            regime=regime,
            label_selection_reason=label_selection_reason,
            crossed_or_negative_spread=crossed_or_negative_spread,
            forecast_score=forecast_score,
            signal_strength_percent=signal_strength_percent,
            reference_hit_rate_percent=reference_hit_rate_percent,
        )
        horizon_warnings = _warnings(
            bundle,
            horizon_sec=horizon.horizon_sec,
            label_selection_reason=label_selection_reason,
            crossed_or_negative_spread=crossed_or_negative_spread,
        )
        packet_warnings.extend(horizon_warnings)
        freshness_state = _freshness_state_for_horizon(
            bundle,
            regime=regime,
            label_selection_reason=label_selection_reason,
        )
        tactical_hint = _tactical_hint(
            regime,
            crossed_or_negative_spread=crossed_or_negative_spread,
            source_snapshot_ok=bundle.source_snapshot_ok,
        )
        drivers = _drivers(
            bundle,
            regime,
            selected_label=selected_label,
            selected_horizon_sec=selected_horizon_sec,
            label_selection_reason=label_selection_reason,
        )
        prediction_rows.append(
            MarketRegimePrediction(
                horizon_label=horizon.label,
                horizon_sec=horizon.horizon_sec,
                regime_code=regime,
                confidence_percent=confidence,
                evidence_quality=evidence,
                freshness_state=freshness_state,
                tactical_hint=tactical_hint,
                drivers=drivers,
                warnings=horizon_warnings,
                missing_sources=missing_sources,
                invalidation_hints=("source_quality_drops", "spread_widens_or_crosses", "forecast_label_changes"),
                parameter_set_id="market_regime_engine_parameter_set.v1",
                source_priority_policy_id="market_regime_source_priority.v1",
                diagnostic_record={
                    "classifier_version": MARKET_REGIME_CLASSIFIER_VERSION,
                    "source_snapshot_ok": bundle.source_snapshot_ok,
                    "available_signal_count": bundle.available_signal_count(),
                    # MR_A2_DIAGNOSTIC_LABEL_SOURCE_2026_07_09
                    "selected_label": str(selected_label or ""),
                    "selected_label_source": "current_state_estimator" if label_selection_reason == "current_state_estimator" else ("current_l4_candle_window" if label_selection_reason == "current_l4_candle_window_fallback" else ("forecast_records" if selected_label else "none")),
                    "selected_forecast_label": "" if label_selection_reason in {"current_l4_candle_window_fallback", "current_state_estimator"} else str(selected_label or ""),
                    "selected_l4_candle_regime_hint": str(selected_label or "") if label_selection_reason in {"current_l4_candle_window_fallback", "current_state_estimator"} else "",
                    "selected_forecast_horizon_sec": selected_horizon_sec,
                    "forecast_records_current_enough": forecast_current_enough,
                    "forecast_records_currentness_gate_applied": not forecast_current_enough,
                    "current_l4_candle_window_current_enough": current_l4_candle_current_enough,
                    "current_l4_candle_window_fallback_used": label_selection_reason == "current_l4_candle_window_fallback",
                    "current_state_estimator_used": label_selection_reason == "current_state_estimator",
                    "current_state_estimator_version": current_estimate.get("estimator_version") if int(horizon.horizon_sec) == 0 else "",
                    "current_state_source_cutoff_time": current_estimate.get("source_cutoff_time") if int(horizon.horizon_sec) == 0 else "",
                    "current_state_started_at": current_estimate.get("state_started_at") if int(horizon.horizon_sec) == 0 else "",
                    "current_state_age_sec": current_estimate.get("state_age_sec") if int(horizon.horizon_sec) == 0 else None,
                    "current_state_start_estimation_status": current_estimate.get("state_start_estimation_status") if int(horizon.horizon_sec) == 0 else "",
                    "current_state_transition_detected": current_estimate.get("state_transition_detected") if int(horizon.horizon_sec) == 0 else False,
                    "current_state_previous_regime_code": current_estimate.get("previous_regime_code") if int(horizon.horizon_sec) == 0 else "",
                    "current_state_window_started_at": current_estimate.get("state_window_started_at") if int(horizon.horizon_sec) == 0 else "",
                    "current_state_window_age_sec": current_estimate.get("state_window_age_sec") if int(horizon.horizon_sec) == 0 else None,
                    "current_state_change_point_probability": current_estimate.get("change_point_probability") if int(horizon.horizon_sec) == 0 else None,
                    "current_state_change_point_probability_calibrated": current_estimate.get("change_point_probability_calibrated") if int(horizon.horizon_sec) == 0 else False,
                    "current_state_change_point_evidence_score": current_estimate.get("change_point_evidence_score") if int(horizon.horizon_sec) == 0 else None,
                    "current_state_transition_candidate": current_estimate.get("transition_candidate") if int(horizon.horizon_sec) == 0 else None,
                    "current_state_transition_candidate_basis": current_estimate.get("transition_candidate_basis") if int(horizon.horizon_sec) == 0 else "",
                    "current_state_supporting_evidence": current_estimate.get("supporting_evidence") if int(horizon.horizon_sec) == 0 else {},
                    "current_state_label_source": current_estimate.get("label_source") if int(horizon.horizon_sec) == 0 else "",
                    "current_state_candidate_scoring_version": current_estimate.get("candidate_scoring_version") if int(horizon.horizon_sec) == 0 else "",
                    "current_state_candidate_scores": current_estimate.get("candidate_scores") if int(horizon.horizon_sec) == 0 else {},
                    "current_state_top_candidate": current_estimate.get("top_candidate") if int(horizon.horizon_sec) == 0 else "",
                    "current_state_top_candidate_score": current_estimate.get("top_candidate_score") if int(horizon.horizon_sec) == 0 else None,
                    "current_state_runner_up_candidate": current_estimate.get("runner_up_candidate") if int(horizon.horizon_sec) == 0 else "",
                    "current_state_candidate_score_margin": current_estimate.get("candidate_score_margin") if int(horizon.horizon_sec) == 0 else None,
                    "current_state_eligible_top_candidate": current_estimate.get("eligible_top_candidate") if int(horizon.horizon_sec) == 0 else "",
                    "current_state_eligible_top_candidate_score": current_estimate.get("eligible_top_candidate_score") if int(horizon.horizon_sec) == 0 else None,
                    "current_state_eligible_runner_up_candidate": current_estimate.get("eligible_runner_up_candidate") if int(horizon.horizon_sec) == 0 else "",
                    "current_state_eligible_runner_up_score": current_estimate.get("eligible_runner_up_score") if int(horizon.horizon_sec) == 0 else None,
                    "current_state_eligible_candidate_score_margin": current_estimate.get("eligible_candidate_score_margin") if int(horizon.horizon_sec) == 0 else None,
                    "current_state_label_selection_eligible_candidates": current_estimate.get("label_selection_eligible_candidates") if int(horizon.horizon_sec) == 0 else [],
                    "current_state_label_selection_ineligible_candidates": current_estimate.get("label_selection_ineligible_candidates") if int(horizon.horizon_sec) == 0 else {},
                    "current_state_label_selection_readiness_blockers": current_estimate.get("label_selection_readiness_blockers") if int(horizon.horizon_sec) == 0 else [],
                    "current_state_top_candidate_contributions": current_estimate.get("top_candidate_contributions") if int(horizon.horizon_sec) == 0 else [],
                    "current_state_scoring_ready_for_label_selection": current_estimate.get("scoring_ready_for_label_selection") if int(horizon.horizon_sec) == 0 else False,
                    "current_state_scoring_label_selection_enabled": current_estimate.get("scoring_label_selection_enabled") if int(horizon.horizon_sec) == 0 else False,
                    "current_state_scoring_label_selection_deferred_reason": current_estimate.get("scoring_label_selection_deferred_reason") if int(horizon.horizon_sec) == 0 else "",
                    "current_state_shadow_recommended_regime_code": current_estimate.get("shadow_recommended_regime_code") if int(horizon.horizon_sec) == 0 else "UNKNOWN",
                    "current_state_shadow_recommendation_candidate": current_estimate.get("shadow_recommendation_candidate") if int(horizon.horizon_sec) == 0 else "",
                    "current_state_shadow_recommendation_candidate_score": current_estimate.get("shadow_recommendation_candidate_score") if int(horizon.horizon_sec) == 0 else None,
                    "current_state_shadow_recommendation_ready": current_estimate.get("shadow_recommendation_ready") if int(horizon.horizon_sec) == 0 else False,
                    "current_state_shadow_recommendation_direction_basis": current_estimate.get("shadow_recommendation_direction_basis") if int(horizon.horizon_sec) == 0 else "",
                    "current_state_shadow_recommendation_agrees_with_selected_label": current_estimate.get("shadow_recommendation_agrees_with_selected_label") if int(horizon.horizon_sec) == 0 else False,
                    "current_state_shadow_recommendation_mismatch_reason": current_estimate.get("shadow_recommendation_mismatch_reason") if int(horizon.horizon_sec) == 0 else "",
                    "current_state_shadow_recommendation_enabled": current_estimate.get("shadow_recommendation_enabled") if int(horizon.horizon_sec) == 0 else False,
                    "current_state_shadow_recommendation_applied_to_selected_label": current_estimate.get("shadow_recommendation_applied_to_selected_label") if int(horizon.horizon_sec) == 0 else False,
                    "current_state_conflicting_evidence": current_estimate.get("conflicting_evidence") if int(horizon.horizon_sec) == 0 else [],
                    "current_state_outcome_rule_version": current_estimate.get("current_state_outcome_rule_version") if int(horizon.horizon_sec) == 0 else "",
                    "current_state_outcome_rule_defined": current_estimate.get("current_state_outcome_rule_defined") if int(horizon.horizon_sec) == 0 else False,
                    "current_state_outcome_rule_gap": current_estimate.get("current_state_outcome_rule_gap") if int(horizon.horizon_sec) == 0 else "",
                    "future_forecast_label_used_for_current": False if int(horizon.horizon_sec) == 0 else None,
                    # MR_A3_CURRENT_L4_EVIDENCE_DIAGNOSTIC_2026_07_09
                    "current_l4_candle_evidence": build_current_l4_candle_evidence_digest(bundle),
                    "selected_forecast_score": forecast_score,
                    "selected_signal_strength_percent": signal_strength_percent,
                    "selected_reference_hit_rate_percent": reference_hit_rate_percent,
                    "confidence_calibrated_from_forecast_metric": forecast_score is not None or signal_strength_percent is not None or reference_hit_rate_percent is not None,
                    "selected_evidence_quality_reason": evidence_quality_reason,
                    "evidence_quality_calibrated_from_forecast_metric": evidence_quality_reason.startswith("forecast_metric_"),
                    "label_selection_reason": label_selection_reason,
                    "horizon_specific_classifier": True,
                    "source_snapshot_input_only": True,
                    "execution_enabled": False,
                    "runtime_write_requested": False,
                },
            )
        )

    predictions = tuple(prediction_rows)
    return MarketRegimePredictionPacket(
        generated_at=generated_at,
        predictions=predictions,
        source_coverage=bundle.coverage,
        missing_sources=missing_sources,
        warnings=tuple(dict.fromkeys(packet_warnings)),
        logic_version=MARKET_REGIME_CLASSIFIER_VERSION,
    )
