# path: ./btcts_next/src/btcts/prediction/market_regime/inference/regime_classifier.py
# desc: Pure market-regime classifier v1 from feature bundle to prediction packet. No reads, writes, UI, scheduler, or execution behavior.

from __future__ import annotations

from typing import Any, Mapping, Tuple

from ..contracts import EvidenceQuality, FeatureGroup, FreshnessState, MarketRegimeCode, MarketRegimePrediction, MarketRegimePredictionPacket, TacticalHint
from ..features import FeatureSignal, MarketRegimeFeatureBundle
from ..horizon_policy import build_default_horizon_policy

MARKET_REGIME_CLASSIFIER_VERSION = "prediction.market_regime.regime_classifier.ps_q27y.v1"


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


def _selected_label_for_horizon(bundle: MarketRegimeFeatureBundle, horizon_sec: int) -> tuple[Any, int | None, str]:
    labels = _labels_by_horizon(bundle)
    fallback = _value(bundle, FeatureGroup.PRICE_STRUCTURE, "latest_market_regime_label")
    if labels:
        if int(horizon_sec) == 0:
            shortest = min(int(key) for key in labels.keys() if str(key).lstrip('-').isdigit())
            return labels.get(str(shortest), fallback), shortest, "shortest_forecast_for_current"
        if str(int(horizon_sec)) in labels:
            return labels[str(int(horizon_sec))], int(horizon_sec), "exact_forecast_horizon"
    return fallback, None, "latest_label_fallback"


def _label_to_regime(label: Any, *, crossed_or_negative_spread: bool, source_snapshot_ok: bool) -> MarketRegimeCode:
    if not source_snapshot_ok:
        return MarketRegimeCode.UNKNOWN
    normalized = str(label or "").lower()
    if normalized in ("range_candidate", "range", "neutral_range"):
        return MarketRegimeCode.RANGE
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
    if crossed_or_negative_spread:
        return MarketRegimeCode.HIGH_VOL_CHOP
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


def _evidence_quality(bundle: MarketRegimeFeatureBundle, *, crossed_or_negative_spread: bool) -> EvidenceQuality:
    if not bundle.source_snapshot_ok:
        return EvidenceQuality.MISSING
    available_count = bundle.available_signal_count()
    source_score = _float(bundle, FeatureGroup.SOURCE_QUALITY, "source_quality_score", 0.0)
    if crossed_or_negative_spread:
        return EvidenceQuality.PARTIAL if source_score >= 0.70 and available_count >= 8 else EvidenceQuality.WEAK
    if source_score >= 0.90 and available_count >= 10:
        return EvidenceQuality.STRONG
    if source_score >= 0.65 and available_count >= 6:
        return EvidenceQuality.PARTIAL
    if available_count > 0:
        return EvidenceQuality.WEAK
    return EvidenceQuality.MISSING


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


def _warnings(bundle: MarketRegimeFeatureBundle, *, crossed_or_negative_spread: bool) -> Tuple[str, ...]:
    warnings = list(bundle.warnings)
    if crossed_or_negative_spread:
        warnings.append("negative_spread_seen")
        warnings.append("tactical_hint_forced_no_new_entry")
    if not bundle.source_snapshot_ok:
        warnings.append("source_snapshot_not_ok")
    return tuple(dict.fromkeys(warnings))


def _missing_sources(bundle: MarketRegimeFeatureBundle) -> Tuple[str, ...]:
    return tuple(dict.fromkeys(bundle.missing_sources))


def classify_market_regime_feature_bundle(bundle: MarketRegimeFeatureBundle, *, generated_at: str) -> MarketRegimePredictionPacket:
    crossed_or_negative_spread = _bool(bundle, FeatureGroup.LIQUIDITY, "crossed_or_negative_spread")
    evidence = _evidence_quality(bundle, crossed_or_negative_spread=crossed_or_negative_spread)
    warnings = _warnings(bundle, crossed_or_negative_spread=crossed_or_negative_spread)
    missing_sources = _missing_sources(bundle)

    prediction_rows: list[MarketRegimePrediction] = []
    for horizon in build_default_horizon_policy().horizons:
        selected_label, selected_horizon_sec, label_selection_reason = _selected_label_for_horizon(bundle, horizon.horizon_sec)
        regime = _label_to_regime(
            selected_label,
            crossed_or_negative_spread=crossed_or_negative_spread,
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
                freshness_state=FreshnessState.LIVE if bundle.source_snapshot_ok else FreshnessState.MISSING,
                tactical_hint=tactical_hint,
                drivers=drivers,
                warnings=warnings,
                missing_sources=missing_sources,
                invalidation_hints=("source_quality_drops", "spread_widens_or_crosses", "forecast_label_changes"),
                parameter_set_id="market_regime_engine_parameter_set.v1",
                source_priority_policy_id="market_regime_source_priority.v1",
                diagnostic_record={
                    "classifier_version": MARKET_REGIME_CLASSIFIER_VERSION,
                    "source_snapshot_ok": bundle.source_snapshot_ok,
                    "available_signal_count": bundle.available_signal_count(),
                    "selected_forecast_label": str(selected_label or ""),
                    "selected_forecast_horizon_sec": selected_horizon_sec,
                    "selected_forecast_score": forecast_score,
                    "selected_signal_strength_percent": signal_strength_percent,
                    "selected_reference_hit_rate_percent": reference_hit_rate_percent,
                    "confidence_calibrated_from_forecast_metric": forecast_score is not None or signal_strength_percent is not None or reference_hit_rate_percent is not None,
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
        warnings=warnings,
        logic_version=MARKET_REGIME_CLASSIFIER_VERSION,
    )
