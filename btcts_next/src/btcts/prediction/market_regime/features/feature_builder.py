# path: ./btcts_next/src/btcts/prediction/market_regime/features/feature_builder.py
# desc: Builds read-only feature bundles from MarketRegimeSourceSnapshot. No external reads or writes.

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Mapping, Tuple

from ..contracts import FeatureGroup, FreshnessState, SourceCoverage
from ..source_snapshot import MarketRegimeSourceSnapshot
from .feature_bundle import FeatureSignal, MarketRegimeFeatureBundle


# MR_A1_STALE_SOURCE_GATE_2026_07_09
FORECAST_RECORDS_LIVE_MAX_AGE_SEC = 6 * 60 * 60


def _parse_utc_ts(value: Any) -> datetime | None:
    if value is None:
        return None
    text = str(value).strip()
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


def _age_sec(generated_at: str, source_ts: str | None) -> float | None:
    generated = _parse_utc_ts(generated_at)
    source = _parse_utc_ts(source_ts)
    if generated is None or source is None:
        return None
    return (generated - source).total_seconds()


def _latest_forecast_generated_at(snapshot: MarketRegimeSourceSnapshot) -> str | None:
    values: list[str] = []
    for record in snapshot.forecast_records.market_regime_records:
        value = record.get("generated_at")
        if value:
            values.append(str(value))
    if values:
        return max(values)
    manifest_generated_at = snapshot.latest_manifest.data.get("generated_at") if isinstance(snapshot.latest_manifest.data, Mapping) else None
    return str(manifest_generated_at) if manifest_generated_at else None


def _forecast_records_currentness(snapshot: MarketRegimeSourceSnapshot, *, generated_at: str) -> tuple[bool, float | None, str | None, tuple[str, ...]]:
    source_ts = _latest_forecast_generated_at(snapshot)
    age = _age_sec(generated_at, source_ts)
    warnings: list[str] = []
    if not snapshot.forecast_records.ok:
        return False, age, source_ts, ("forecast_records_not_ok",)
    if age is None:
        return False, age, source_ts, ("forecast_records_generated_at_missing",)
    if age < 0:
        warnings.append("forecast_records_from_future")
        return False, age, source_ts, tuple(warnings)
    if age > FORECAST_RECORDS_LIVE_MAX_AGE_SEC:
        warnings.append("forecast_records_stale")
        warnings.append(f"forecast_records_age_sec:{int(age)}")
        return False, age, source_ts, tuple(warnings)
    return True, age, source_ts, ()


def _as_float(value: Any) -> float | None:
    try:
        if value is None:
            return None
        return float(value)
    except Exception:
        return None


def _as_int(value: Any) -> int | None:
    try:
        if value is None:
            return None
        return int(value)
    except Exception:
        return None


def _latest_market_regime_record(snapshot: MarketRegimeSourceSnapshot, horizon_sec: int | None = None) -> Mapping[str, Any] | None:
    records = snapshot.forecast_records.market_regime_records
    if horizon_sec is not None:
        for record in records:
            if _as_int(record.get("horizon_sec")) == int(horizon_sec):
                return record
    return records[-1] if records else None




def _record_values(record: Mapping[str, Any] | None) -> Mapping[str, Any]:
    if not isinstance(record, Mapping):
        return {}
    values = record.get("values")
    if isinstance(values, Mapping):
        return values
    values_snapshot = record.get("values_snapshot")
    if isinstance(values_snapshot, Mapping):
        return values_snapshot
    return {}

def _signal(group: FeatureGroup, name: str, value: Any, *, available: bool, source_refs: Tuple[str, ...], warnings: Tuple[str, ...] = (), weight_hint: float = 0.0) -> FeatureSignal:
    return FeatureSignal(
        feature_group=group,
        name=name,
        value=value,
        available=available,
        source_refs=source_refs,
        warnings=warnings,
        weight_hint=weight_hint,
    )


def _source_quality_signals(snapshot: MarketRegimeSourceSnapshot, *, generated_at: str) -> Tuple[FeatureSignal, ...]:
    refs = ("latest_manifest", "forecast_records", "collector_market_state", "collector_health")
    missing_count = len(snapshot.missing_sources)
    forecast_current_enough, forecast_age_sec, forecast_source_ts, currentness_warnings = _forecast_records_currentness(snapshot, generated_at=generated_at)
    currentness_penalty = 1 if not forecast_current_enough else 0
    ok_score = max(0.0, 1.0 - min(missing_count + currentness_penalty, 6) / 6.0)
    combined_warnings = tuple(dict.fromkeys(tuple(snapshot.warnings) + currentness_warnings))
    return (
        _signal(FeatureGroup.SOURCE_QUALITY, "source_snapshot_ok", bool(snapshot.ok), available=True, source_refs=refs, weight_hint=0.20),
        _signal(FeatureGroup.SOURCE_QUALITY, "missing_source_count", missing_count, available=True, source_refs=refs, warnings=tuple(snapshot.missing_sources), weight_hint=0.20),
        _signal(FeatureGroup.SOURCE_QUALITY, "forecast_records_current_enough", forecast_current_enough, available=True, source_refs=(snapshot.forecast_records.relative_path,), warnings=currentness_warnings, weight_hint=0.20),
        _signal(FeatureGroup.SOURCE_QUALITY, "forecast_records_age_sec", int(forecast_age_sec) if forecast_age_sec is not None else None, available=forecast_age_sec is not None, source_refs=(snapshot.forecast_records.relative_path,), warnings=currentness_warnings, weight_hint=0.10),
        _signal(FeatureGroup.SOURCE_QUALITY, "forecast_records_generated_at", forecast_source_ts, available=forecast_source_ts is not None, source_refs=(snapshot.forecast_records.relative_path,), warnings=currentness_warnings, weight_hint=0.05),
        _signal(FeatureGroup.SOURCE_QUALITY, "source_quality_score", round(ok_score, 4), available=True, source_refs=refs, warnings=combined_warnings, weight_hint=0.25),
    )


def _first_float(data: Mapping[str, Any], *keys: str) -> float | None:
    for key in keys:
        value = _as_float(data.get(key))
        if value is not None:
            return value
    return None


def _safe_ratio(numerator: float | None, denominator: float | None) -> float | None:
    if numerator is None or denominator in (None, 0.0):
        return None
    return numerator / denominator


def _liquidity_signals(snapshot: MarketRegimeSourceSnapshot) -> Tuple[FeatureSignal, ...]:
    data = snapshot.nowcast.market_state.data
    rel = snapshot.nowcast.market_state.relative_path
    spread = _first_float(data, "last_spread", "spread")
    bid = _first_float(data, "last_best_bid", "best_bid")
    ask = _first_float(data, "last_best_ask", "best_ask")
    bid_depth = _first_float(data, "bid_depth_size", "best_bid_depth", "bid_depth", "sum_bid_size", "bid_size_total")
    ask_depth = _first_float(data, "ask_depth_size", "best_ask_depth", "ask_depth", "sum_ask_size", "ask_size_total")
    mid_price = (bid + ask) / 2.0 if bid is not None and ask is not None else None
    microprice = _first_float(data, "microprice", "last_microprice")
    abs_spread = abs(spread) if spread is not None else None
    crossed_or_negative = spread is not None and spread < 0
    spread_bps = abs_spread / mid_price * 10000.0 if abs_spread is not None and mid_price not in (None, 0.0) else None
    depth_total = (bid_depth or 0.0) + (ask_depth or 0.0) if bid_depth is not None or ask_depth is not None else None
    depth_imbalance = (bid_depth - ask_depth) / depth_total if bid_depth is not None and ask_depth is not None and depth_total not in (None, 0.0) else None
    microprice_bias_bps = (microprice - mid_price) / mid_price * 10000.0 if microprice is not None and mid_price not in (None, 0.0) else None
    replenishment = _first_float(data, "liquidity_replenishment_score", "replenishment_score", "depth_replenishment_score")
    disappearance = _first_float(data, "liquidity_disappearance_score", "disappearance_score", "depth_disappearance_score")
    absorption = _first_float(data, "absorption_score", "liquidity_absorption_score", "orderflow_absorption_score")
    spread_change_1m = _first_float(data, "spread_change_bps_1m", "spread_change_1m_bps")
    return (
        _signal(FeatureGroup.LIQUIDITY, "best_bid", bid, available=bid is not None, source_refs=(rel,), weight_hint=0.10),
        _signal(FeatureGroup.LIQUIDITY, "best_ask", ask, available=ask is not None, source_refs=(rel,), weight_hint=0.10),
        _signal(FeatureGroup.LIQUIDITY, "mid_price", mid_price, available=mid_price is not None, source_refs=(rel,), weight_hint=0.08),
        _signal(FeatureGroup.LIQUIDITY, "absolute_spread", abs_spread, available=abs_spread is not None, source_refs=(rel,), warnings=("negative_spread_seen",) if crossed_or_negative else (), weight_hint=0.18),
        _signal(FeatureGroup.LIQUIDITY, "spread_bps", spread_bps, available=spread_bps is not None, source_refs=(rel,), warnings=("negative_spread_seen",) if crossed_or_negative else (), weight_hint=0.14),
        _signal(FeatureGroup.LIQUIDITY, "crossed_or_negative_spread", crossed_or_negative, available=spread is not None, source_refs=(rel,), weight_hint=0.12),
        _signal(FeatureGroup.LIQUIDITY, "bid_depth_size", bid_depth, available=bid_depth is not None, source_refs=(rel,), weight_hint=0.08),
        _signal(FeatureGroup.LIQUIDITY, "ask_depth_size", ask_depth, available=ask_depth is not None, source_refs=(rel,), weight_hint=0.08),
        _signal(FeatureGroup.LIQUIDITY, "depth_imbalance", round(depth_imbalance, 4) if depth_imbalance is not None else None, available=depth_imbalance is not None, source_refs=(rel,), weight_hint=0.18),
        _signal(FeatureGroup.LIQUIDITY, "microprice", microprice, available=microprice is not None, source_refs=(rel,), weight_hint=0.12),
        _signal(FeatureGroup.LIQUIDITY, "microprice_bias_bps", microprice_bias_bps, available=microprice_bias_bps is not None, source_refs=(rel,), weight_hint=0.14),
        _signal(FeatureGroup.LIQUIDITY, "liquidity_replenishment_score", replenishment, available=replenishment is not None, source_refs=(rel,), weight_hint=0.16),
        _signal(FeatureGroup.LIQUIDITY, "liquidity_disappearance_score", disappearance, available=disappearance is not None, source_refs=(rel,), weight_hint=0.16),
        _signal(FeatureGroup.LIQUIDITY, "absorption_score", absorption, available=absorption is not None, source_refs=(rel,), weight_hint=0.18),
        _signal(FeatureGroup.LIQUIDITY, "spread_change_bps_1m", spread_change_1m, available=spread_change_1m is not None, source_refs=(rel,), weight_hint=0.10),
    )


def _orderflow_signals(snapshot: MarketRegimeSourceSnapshot) -> Tuple[FeatureSignal, ...]:
    data = snapshot.nowcast.executions.data
    rel = snapshot.nowcast.executions.relative_path
    trade_count = _as_int(data.get("trade_count") or data.get("execution_count"))
    ws_state = data.get("ws_state") or data.get("state")
    live = str(ws_state).upper() == "LIVE" if ws_state is not None else False
    buy_volume = _first_float(data, "aggressive_buy_volume", "buy_aggressor_volume", "taker_buy_volume")
    sell_volume = _first_float(data, "aggressive_sell_volume", "sell_aggressor_volume", "taker_sell_volume")
    volume_total = (buy_volume or 0.0) + (sell_volume or 0.0) if buy_volume is not None or sell_volume is not None else None
    imbalance = (buy_volume - sell_volume) / volume_total if buy_volume is not None and sell_volume is not None and volume_total not in (None, 0.0) else None
    cvd = _first_float(data, "cvd", "cumulative_volume_delta", "cvd_proxy")
    large_trade_count = _as_int(data.get("large_trade_count") or data.get("large_execution_count"))
    volume_acceleration = _first_float(data, "volume_acceleration", "trade_volume_acceleration")
    return (
        _signal(FeatureGroup.ORDERFLOW, "execution_trade_count", trade_count, available=trade_count is not None, source_refs=(rel,), weight_hint=0.22),
        _signal(FeatureGroup.ORDERFLOW, "executions_ws_live", live, available=ws_state is not None, source_refs=(rel,), weight_hint=0.18),
        _signal(FeatureGroup.ORDERFLOW, "aggressive_buy_volume", buy_volume, available=buy_volume is not None, source_refs=(rel,), weight_hint=0.18),
        _signal(FeatureGroup.ORDERFLOW, "aggressive_sell_volume", sell_volume, available=sell_volume is not None, source_refs=(rel,), weight_hint=0.18),
        _signal(FeatureGroup.ORDERFLOW, "orderflow_imbalance", round(imbalance, 4) if imbalance is not None else None, available=imbalance is not None, source_refs=(rel,), weight_hint=0.20),
        _signal(FeatureGroup.ORDERFLOW, "cvd", cvd, available=cvd is not None, source_refs=(rel,), weight_hint=0.16),
        _signal(FeatureGroup.ORDERFLOW, "large_trade_count", large_trade_count, available=large_trade_count is not None, source_refs=(rel,), weight_hint=0.10),
        _signal(FeatureGroup.ORDERFLOW, "volume_acceleration", volume_acceleration, available=volume_acceleration is not None, source_refs=(rel,), weight_hint=0.12),
    )


def _labels_by_horizon_sec(records: Tuple[Mapping[str, Any], ...]) -> dict[str, str]:
    labels: dict[str, str] = {}
    for record in records:
        horizon = _as_int(record.get("horizon_sec"))
        label = record.get("primary_label")
        if horizon is not None and label:
            labels[str(horizon)] = str(label)
    return labels


def _numeric_by_horizon_sec(records: Tuple[Mapping[str, Any], ...], field: str, *, values_field: str | None = None) -> dict[str, float]:
    values_by_horizon: dict[str, float] = {}
    for record in records:
        horizon = _as_int(record.get("horizon_sec"))
        raw = _record_values(record).get(values_field) if values_field else record.get(field)
        value = _as_float(raw)
        if horizon is not None and value is not None:
            values_by_horizon[str(horizon)] = value
    return values_by_horizon


def _price_structure_signals(snapshot: MarketRegimeSourceSnapshot, *, generated_at: str) -> Tuple[FeatureSignal, ...]:
    records = snapshot.forecast_records.market_regime_records
    forecast_current_enough, _, _, currentness_warnings = _forecast_records_currentness(snapshot, generated_at=generated_at)
    latest = _latest_market_regime_record(snapshot) if forecast_current_enough else None
    label = latest.get("primary_label") if latest else None
    horizons = tuple(snapshot.forecast_records.market_regime_horizons_sec) if forecast_current_enough else ()
    labels_by_horizon = _labels_by_horizon_sec(records) if forecast_current_enough else {}
    scores_by_horizon = _numeric_by_horizon_sec(records, "score") if forecast_current_enough else {}
    signal_strength_by_horizon = _numeric_by_horizon_sec(records, "estimated_signal_strength_percent", values_field="estimated_signal_strength_percent") if forecast_current_enough else {}
    reference_hit_rate_by_horizon = _numeric_by_horizon_sec(records, "estimated_reference_hit_rate_percent", values_field="estimated_reference_hit_rate_percent") if forecast_current_enough else {}
    values = _record_values(latest) if forecast_current_enough else {}
    range_high = _first_float(values, "range_high", "recent_range_high", "resistance")
    range_low = _first_float(values, "range_low", "recent_range_low", "support")
    vwap = _first_float(values, "vwap", "session_vwap")
    ma_slope = _first_float(values, "ma_slope", "moving_average_slope")
    price_position = _first_float(values, "price_position_in_range", "range_position")
    break_hold_count = _as_int(values.get("break_hold_count") or values.get("confirmed_break_hold_count"))
    false_break_count = _as_int(values.get("false_break_count") or values.get("failed_break_count"))
    technical_available = any(value is not None for value in (range_high, range_low, vwap, ma_slope, price_position, break_hold_count, false_break_count))
    return (
        _signal(FeatureGroup.PRICE_STRUCTURE, "market_regime_record_count", len(records), available=True, source_refs=(snapshot.forecast_records.relative_path,), warnings=currentness_warnings, weight_hint=0.12),
        _signal(FeatureGroup.PRICE_STRUCTURE, "market_regime_horizons_sec", list(horizons), available=bool(horizons), source_refs=(snapshot.forecast_records.relative_path,), warnings=currentness_warnings, weight_hint=0.12),
        _signal(FeatureGroup.PRICE_STRUCTURE, "latest_market_regime_label", label, available=label is not None, source_refs=(snapshot.forecast_records.relative_path,), warnings=currentness_warnings, weight_hint=0.12),
        _signal(FeatureGroup.PRICE_STRUCTURE, "market_regime_labels_by_horizon_sec", labels_by_horizon, available=bool(labels_by_horizon), source_refs=(snapshot.forecast_records.relative_path,), warnings=currentness_warnings, weight_hint=0.12),
        _signal(FeatureGroup.PRICE_STRUCTURE, "market_regime_scores_by_horizon_sec", scores_by_horizon, available=bool(scores_by_horizon), source_refs=(snapshot.forecast_records.relative_path,), warnings=currentness_warnings, weight_hint=0.08),
        _signal(FeatureGroup.PRICE_STRUCTURE, "market_regime_signal_strength_percent_by_horizon_sec", signal_strength_by_horizon, available=bool(signal_strength_by_horizon), source_refs=(snapshot.forecast_records.relative_path,), warnings=currentness_warnings, weight_hint=0.08),
        _signal(FeatureGroup.PRICE_STRUCTURE, "market_regime_reference_hit_rate_percent_by_horizon_sec", reference_hit_rate_by_horizon, available=bool(reference_hit_rate_by_horizon), source_refs=(snapshot.forecast_records.relative_path,), warnings=currentness_warnings, weight_hint=0.08),
        _signal(FeatureGroup.PRICE_STRUCTURE, "range_high", range_high, available=range_high is not None, source_refs=(snapshot.forecast_records.relative_path,), weight_hint=0.10),
        _signal(FeatureGroup.PRICE_STRUCTURE, "range_low", range_low, available=range_low is not None, source_refs=(snapshot.forecast_records.relative_path,), weight_hint=0.10),
        _signal(FeatureGroup.PRICE_STRUCTURE, "vwap", vwap, available=vwap is not None, source_refs=(snapshot.forecast_records.relative_path,), weight_hint=0.10),
        _signal(FeatureGroup.PRICE_STRUCTURE, "ma_slope", ma_slope, available=ma_slope is not None, source_refs=(snapshot.forecast_records.relative_path,), weight_hint=0.08),
        _signal(FeatureGroup.PRICE_STRUCTURE, "price_position_in_range", price_position, available=price_position is not None, source_refs=(snapshot.forecast_records.relative_path,), weight_hint=0.08),
        _signal(FeatureGroup.PRICE_STRUCTURE, "break_hold_count", break_hold_count, available=break_hold_count is not None, source_refs=(snapshot.forecast_records.relative_path,), weight_hint=0.08),
        _signal(FeatureGroup.PRICE_STRUCTURE, "false_break_count", false_break_count, available=false_break_count is not None, source_refs=(snapshot.forecast_records.relative_path,), weight_hint=0.08),
        _signal(FeatureGroup.PRICE_STRUCTURE, "confirmed_technical_structure_available", technical_available, available=True, source_refs=(snapshot.forecast_records.relative_path,), weight_hint=0.08),
    )


def _volatility_signals(snapshot: MarketRegimeSourceSnapshot, *, generated_at: str) -> Tuple[FeatureSignal, ...]:
    forecast_current_enough, _, _, currentness_warnings = _forecast_records_currentness(snapshot, generated_at=generated_at)
    latest = _latest_market_regime_record(snapshot) if forecast_current_enough else None
    values = _record_values(latest) if forecast_current_enough else {}
    volatility_state = values.get("volatility_state")
    atr = _first_float(values, "atr", "average_true_range")
    realized_volatility = _first_float(values, "realized_volatility", "rv")
    compression_score = _first_float(values, "volatility_compression_score", "atr_compression_score")
    expansion_score = _first_float(values, "volatility_expansion_score", "atr_expansion_score")
    return (
        _signal(FeatureGroup.VOLATILITY, "volatility_state", volatility_state, available=volatility_state is not None, source_refs=(snapshot.forecast_records.relative_path,), warnings=currentness_warnings, weight_hint=0.40),
        _signal(FeatureGroup.VOLATILITY, "atr", atr, available=atr is not None, source_refs=(snapshot.forecast_records.relative_path,), warnings=currentness_warnings, weight_hint=0.20),
        _signal(FeatureGroup.VOLATILITY, "realized_volatility", realized_volatility, available=realized_volatility is not None, source_refs=(snapshot.forecast_records.relative_path,), warnings=currentness_warnings, weight_hint=0.20),
        _signal(FeatureGroup.VOLATILITY, "volatility_compression_score", compression_score, available=compression_score is not None, source_refs=(snapshot.forecast_records.relative_path,), warnings=currentness_warnings, weight_hint=0.10),
        _signal(FeatureGroup.VOLATILITY, "volatility_expansion_score", expansion_score, available=expansion_score is not None, source_refs=(snapshot.forecast_records.relative_path,), warnings=currentness_warnings, weight_hint=0.10),
    )


def _cross_venue_signals(snapshot: MarketRegimeSourceSnapshot, *, generated_at: str) -> Tuple[FeatureSignal, ...]:
    forecast_current_enough, _, _, currentness_warnings = _forecast_records_currentness(snapshot, generated_at=generated_at)
    latest = _latest_market_regime_record(snapshot) if forecast_current_enough else None
    values = _record_values(latest) if forecast_current_enough else {}
    agreement = values.get("cross_venue_agreement")
    latest_prediction_ok = snapshot.latest_prediction.ok
    return (
        _signal(FeatureGroup.CROSS_VENUE, "cross_venue_agreement", agreement, available=agreement is not None, source_refs=(snapshot.forecast_records.relative_path,), warnings=currentness_warnings, weight_hint=0.60),
        _signal(FeatureGroup.CROSS_VENUE, "latest_prediction_artifact_ok", latest_prediction_ok, available=True, source_refs=(snapshot.latest_prediction.relative_path,), warnings=currentness_warnings, weight_hint=0.40),
    )


def _coverage_for_group(group: FeatureGroup, signals: Tuple[FeatureSignal, ...]) -> SourceCoverage:
    # MR_A1_SOURCE_COVERAGE_STALE_FRESHNESS_2026_07_09
    group_signals = tuple(signal for signal in signals if signal.feature_group == group)
    available = any(signal.available for signal in group_signals)
    used = tuple(dict.fromkeys(ref for signal in group_signals for ref in signal.source_refs if ref))
    warnings = tuple(dict.fromkeys(warn for signal in group_signals for warn in signal.warnings if warn))
    if "forecast_records_stale" in warnings or "forecast_records_from_future" in warnings or "forecast_records_generated_at_missing" in warnings:
        freshness = FreshnessState.STALE
    elif not available:
        freshness = FreshnessState.MISSING
    else:
        freshness = FreshnessState.LIVE
    return SourceCoverage(
        feature_group=group,
        available=available,
        freshness_state=freshness,
        used_sources=used,
        missing_sources=() if available else (group.value,),
        warnings=warnings,
    )


def build_market_regime_feature_bundle(snapshot: MarketRegimeSourceSnapshot, *, generated_at: str) -> MarketRegimeFeatureBundle:
    signals = (
        *_source_quality_signals(snapshot, generated_at=generated_at),
        *_liquidity_signals(snapshot),
        *_orderflow_signals(snapshot),
        *_price_structure_signals(snapshot, generated_at=generated_at),
        *_volatility_signals(snapshot, generated_at=generated_at),
        *_cross_venue_signals(snapshot, generated_at=generated_at),
    )
    groups = (
        FeatureGroup.PRICE_STRUCTURE,
        FeatureGroup.VOLATILITY,
        FeatureGroup.LIQUIDITY,
        FeatureGroup.ORDERFLOW,
        FeatureGroup.CROSS_VENUE,
        FeatureGroup.SOURCE_QUALITY,
    )
    coverage = tuple(_coverage_for_group(group, signals) for group in groups)
    warnings = tuple(dict.fromkeys(tuple(snapshot.warnings) + tuple(warn for signal in signals for warn in signal.warnings)))
    return MarketRegimeFeatureBundle(
        generated_at=generated_at,
        signals=signals,
        coverage=coverage,
        source_snapshot_ok=snapshot.ok,
        missing_sources=tuple(snapshot.missing_sources),
        warnings=warnings,
    )
