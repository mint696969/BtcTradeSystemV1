# path: ./btcts_next/src/btcts/prediction/market_regime/features/feature_builder.py
# desc: Builds read-only feature bundles from MarketRegimeSourceSnapshot. No external reads or writes.

from __future__ import annotations

from typing import Any, Mapping, Tuple

from ..contracts import FeatureGroup, FreshnessState, SourceCoverage
from ..source_snapshot import MarketRegimeSourceSnapshot
from .feature_bundle import FeatureSignal, MarketRegimeFeatureBundle


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


def _source_quality_signals(snapshot: MarketRegimeSourceSnapshot) -> Tuple[FeatureSignal, ...]:
    refs = ("latest_manifest", "forecast_records", "collector_market_state", "collector_health")
    missing_count = len(snapshot.missing_sources)
    ok_score = max(0.0, 1.0 - min(missing_count, 6) / 6.0)
    return (
        _signal(FeatureGroup.SOURCE_QUALITY, "source_snapshot_ok", bool(snapshot.ok), available=True, source_refs=refs, weight_hint=0.25),
        _signal(FeatureGroup.SOURCE_QUALITY, "missing_source_count", missing_count, available=True, source_refs=refs, warnings=tuple(snapshot.missing_sources), weight_hint=0.25),
        _signal(FeatureGroup.SOURCE_QUALITY, "source_quality_score", round(ok_score, 4), available=True, source_refs=refs, warnings=tuple(snapshot.warnings), weight_hint=0.50),
    )


def _liquidity_signals(snapshot: MarketRegimeSourceSnapshot) -> Tuple[FeatureSignal, ...]:
    data = snapshot.nowcast.market_state.data
    spread = _as_float(data.get("last_spread") or data.get("spread"))
    bid = _as_float(data.get("last_best_bid") or data.get("best_bid"))
    ask = _as_float(data.get("last_best_ask") or data.get("best_ask"))
    abs_spread = abs(spread) if spread is not None else None
    crossed_or_negative = spread is not None and spread < 0
    return (
        _signal(FeatureGroup.LIQUIDITY, "best_bid", bid, available=bid is not None, source_refs=(snapshot.nowcast.market_state.relative_path,), weight_hint=0.15),
        _signal(FeatureGroup.LIQUIDITY, "best_ask", ask, available=ask is not None, source_refs=(snapshot.nowcast.market_state.relative_path,), weight_hint=0.15),
        _signal(FeatureGroup.LIQUIDITY, "absolute_spread", abs_spread, available=abs_spread is not None, source_refs=(snapshot.nowcast.market_state.relative_path,), warnings=("negative_spread_seen",) if crossed_or_negative else (), weight_hint=0.45),
        _signal(FeatureGroup.LIQUIDITY, "crossed_or_negative_spread", crossed_or_negative, available=spread is not None, source_refs=(snapshot.nowcast.market_state.relative_path,), weight_hint=0.25),
    )


def _orderflow_signals(snapshot: MarketRegimeSourceSnapshot) -> Tuple[FeatureSignal, ...]:
    data = snapshot.nowcast.executions.data
    trade_count = _as_int(data.get("trade_count") or data.get("execution_count"))
    ws_state = data.get("ws_state") or data.get("state")
    live = str(ws_state).upper() == "LIVE" if ws_state is not None else False
    return (
        _signal(FeatureGroup.ORDERFLOW, "execution_trade_count", trade_count, available=trade_count is not None, source_refs=(snapshot.nowcast.executions.relative_path,), weight_hint=0.50),
        _signal(FeatureGroup.ORDERFLOW, "executions_ws_live", live, available=ws_state is not None, source_refs=(snapshot.nowcast.executions.relative_path,), weight_hint=0.50),
    )


def _labels_by_horizon_sec(records: Tuple[Mapping[str, Any], ...]) -> dict[str, str]:
    labels: dict[str, str] = {}
    for record in records:
        horizon = _as_int(record.get("horizon_sec"))
        label = record.get("primary_label")
        if horizon is not None and label:
            labels[str(horizon)] = str(label)
    return labels


def _price_structure_signals(snapshot: MarketRegimeSourceSnapshot) -> Tuple[FeatureSignal, ...]:
    records = snapshot.forecast_records.market_regime_records
    latest = _latest_market_regime_record(snapshot)
    label = latest.get("primary_label") if latest else None
    horizons = tuple(snapshot.forecast_records.market_regime_horizons_sec)
    labels_by_horizon = _labels_by_horizon_sec(records)
    return (
        _signal(FeatureGroup.PRICE_STRUCTURE, "market_regime_record_count", len(records), available=True, source_refs=(snapshot.forecast_records.relative_path,), weight_hint=0.25),
        _signal(FeatureGroup.PRICE_STRUCTURE, "market_regime_horizons_sec", list(horizons), available=bool(horizons), source_refs=(snapshot.forecast_records.relative_path,), weight_hint=0.25),
        _signal(FeatureGroup.PRICE_STRUCTURE, "latest_market_regime_label", label, available=label is not None, source_refs=(snapshot.forecast_records.relative_path,), weight_hint=0.25),
        _signal(FeatureGroup.PRICE_STRUCTURE, "market_regime_labels_by_horizon_sec", labels_by_horizon, available=bool(labels_by_horizon), source_refs=(snapshot.forecast_records.relative_path,), weight_hint=0.25),
    )


def _volatility_signals(snapshot: MarketRegimeSourceSnapshot) -> Tuple[FeatureSignal, ...]:
    latest = _latest_market_regime_record(snapshot)
    values = _record_values(latest)
    volatility_state = values.get("volatility_state")
    return (
        _signal(FeatureGroup.VOLATILITY, "volatility_state", volatility_state, available=volatility_state is not None, source_refs=(snapshot.forecast_records.relative_path,), weight_hint=1.0),
    )


def _cross_venue_signals(snapshot: MarketRegimeSourceSnapshot) -> Tuple[FeatureSignal, ...]:
    latest = _latest_market_regime_record(snapshot)
    values = _record_values(latest)
    agreement = values.get("cross_venue_agreement")
    latest_prediction_ok = snapshot.latest_prediction.ok
    return (
        _signal(FeatureGroup.CROSS_VENUE, "cross_venue_agreement", agreement, available=agreement is not None, source_refs=(snapshot.forecast_records.relative_path,), weight_hint=0.60),
        _signal(FeatureGroup.CROSS_VENUE, "latest_prediction_artifact_ok", latest_prediction_ok, available=True, source_refs=(snapshot.latest_prediction.relative_path,), weight_hint=0.40),
    )


def _coverage_for_group(group: FeatureGroup, signals: Tuple[FeatureSignal, ...]) -> SourceCoverage:
    group_signals = tuple(signal for signal in signals if signal.feature_group == group)
    available = any(signal.available for signal in group_signals)
    used = tuple(dict.fromkeys(ref for signal in group_signals for ref in signal.source_refs if ref))
    warnings = tuple(dict.fromkeys(warn for signal in group_signals for warn in signal.warnings if warn))
    return SourceCoverage(
        feature_group=group,
        available=available,
        freshness_state=FreshnessState.LIVE if available else FreshnessState.MISSING,
        used_sources=used,
        missing_sources=() if available else (group.value,),
        warnings=warnings,
    )


def build_market_regime_feature_bundle(snapshot: MarketRegimeSourceSnapshot, *, generated_at: str) -> MarketRegimeFeatureBundle:
    signals = (
        *_source_quality_signals(snapshot),
        *_liquidity_signals(snapshot),
        *_orderflow_signals(snapshot),
        *_price_structure_signals(snapshot),
        *_volatility_signals(snapshot),
        *_cross_venue_signals(snapshot),
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
