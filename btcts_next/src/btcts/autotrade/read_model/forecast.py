# path: ./btcts_next/src/btcts/autotrade/read_model/forecast.py
# desc: Rule-based 5-minute forecast contract builder for AutoTrade read model.

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Tuple

from btcts.autotrade.config.models import ParameterSet

from .ids import build_forecast_id
from .models import (
    AutoTradeSnapshot,
    Confidence,
    Forecast5m,
    ForecastDirection,
    ForecastExpectedChange,
    ForecastOutcome,
    ForecastOutcomeResult,
    ForecastScore,
    GroundDirection,
)


def _parse_ts(value: str) -> datetime:
    normalized = value.replace("Z", "+00:00")
    dt = datetime.fromisoformat(normalized)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def target_ts_for(created_at: str, horizon_sec: int) -> str:
    return (_parse_ts(created_at) + timedelta(seconds=int(horizon_sec))).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _downgrade_confidence_for_stale(snapshot: AutoTradeSnapshot, confidence: Confidence, blocked: list[str]) -> Confidence:
    if snapshot.stale_reasons:
        blocked.extend(snapshot.stale_reasons)
    if not snapshot.usability.temporal:
        blocked.append("temporal_flow_unusable")
    if not snapshot.usability.liquidity:
        blocked.append("liquidity_unusable")
    if not snapshot.usability.trade:
        blocked.append("trade_unusable")
    if blocked:
        return Confidence.LOW
    return confidence


def build_rule_based_forecast_5m(snapshot: AutoTradeSnapshot, parameter_set: ParameterSet) -> Forecast5m:
    drivers: list[str] = []
    blocked_by: list[str] = []
    direction = ForecastDirection.UNKNOWN
    expected = ForecastExpectedChange.UNKNOWN
    confidence = Confidence.LOW

    pressure = snapshot.temporal_flow.temporal_pressure_flow
    price = snapshot.temporal_flow.temporal_price_flow
    patterns = snapshot.temporal_flow.temporal_pattern_flags

    pressure_accel = pressure.get("pressure_acceleration")
    price_300 = price.get("mid_return_300s")

    if patterns.get("liquidity_vacuum_candidate"):
        direction = ForecastDirection.VOLATILE
        expected = ForecastExpectedChange.BREAKOUT_RISK
        drivers.append("liquidity_vacuum_candidate")
        confidence = Confidence.MEDIUM
    elif pressure_accel == "buy" or snapshot.ground.direction == GroundDirection.BUY_LEANING:
        direction = ForecastDirection.UP
        expected = ForecastExpectedChange.STRENGTHEN_BUY
        drivers.append("buy_pressure_or_ground")
        confidence = Confidence.MEDIUM
    elif pressure_accel == "sell" or snapshot.ground.direction == GroundDirection.SELL_LEANING:
        direction = ForecastDirection.DOWN
        expected = ForecastExpectedChange.STRENGTHEN_SELL
        drivers.append("sell_pressure_or_ground")
        confidence = Confidence.MEDIUM
    elif isinstance(price_300, (int, float)) and abs(float(price_300)) < 0.0005:
        direction = ForecastDirection.RANGE
        expected = ForecastExpectedChange.MEAN_REVERT
        drivers.append("low_300s_mid_return")
        confidence = Confidence.LOW

    confidence = _downgrade_confidence_for_stale(snapshot, confidence, blocked_by)

    target_ts = target_ts_for(snapshot.created_at, parameter_set.forecast.horizon_sec)
    forecast_id = build_forecast_id(
        snapshot_id=snapshot.snapshot_id,
        target_ts=target_ts,
        parameter_set_id=parameter_set.parameter_set_id,
        logic_version=parameter_set.logic_version,
    )
    return Forecast5m(
        forecast_id=forecast_id,
        created_at=snapshot.created_at,
        target_ts=target_ts,
        horizon_sec=parameter_set.forecast.horizon_sec,
        source_snapshot_id=snapshot.snapshot_id,
        parameter_set_id=parameter_set.parameter_set_id,
        logic_version=parameter_set.logic_version,
        base_ground_at_forecast=snapshot.ground,
        forecast_direction=direction,
        expected_change=expected,
        confidence=confidence,
        drivers=tuple(drivers),
        blocked_by=tuple(dict.fromkeys(blocked_by)),
    )


def score_forecast_outcome(forecast: Forecast5m, actual_direction: GroundDirection, *, actual_snapshot_id: str | None, resolved_at: str) -> ForecastOutcome:
    expected_map = {
        ForecastDirection.UP: GroundDirection.BUY_LEANING,
        ForecastDirection.DOWN: GroundDirection.SELL_LEANING,
        ForecastDirection.RANGE: GroundDirection.MIXED,
    }
    expected_ground = expected_map.get(forecast.forecast_direction)
    if actual_snapshot_id is None:
        result = ForecastOutcomeResult.UNSCORABLE
        direction_hit = False
    elif expected_ground is None:
        result = ForecastOutcomeResult.UNSCORABLE if forecast.forecast_direction == ForecastDirection.UNKNOWN else ForecastOutcomeResult.PARTIAL
        direction_hit = False
    else:
        direction_hit = actual_direction == expected_ground
        result = ForecastOutcomeResult.HIT if direction_hit else ForecastOutcomeResult.MISS

    actual_ground = forecast.base_ground_at_forecast.__class__(direction=actual_direction, confidence=Confidence.LOW)
    return ForecastOutcome(
        forecast_id=forecast.forecast_id,
        resolved_at=resolved_at,
        target_ts=forecast.target_ts,
        actual_snapshot_id=actual_snapshot_id,
        actual_ground=actual_ground,
        actual_change=__import__("btcts.autotrade.read_model.models", fromlist=["ActualFiveMinuteChange"]).ActualFiveMinuteChange(),
        score=ForecastScore(result=result, direction_hit=direction_hit, change_type_hit=direction_hit),
        divergence_reasons=() if direction_hit else ("direction_mismatch",),
    )
