# path: ./btcts_next/src/btcts/prediction/technical.py
# desc: Non-executing human-style technical indicator summaries over already-provided OHLCV candles.

from __future__ import annotations

from dataclasses import asdict, dataclass
from math import sqrt
from typing import Any, Dict, Iterable, Tuple

from .ohlcv import OHLCVCandle

LOGIC_VERSION = "prediction_human_technical.s126.v1"


@dataclass(frozen=True)
class SupportResistanceZone:
    zone_kind: str
    low: float
    high: float
    touches: int
    confidence: float
    source: str = "recent_candle_extremes"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class RangeBoundarySummary:
    range_low: float | None = None
    range_high: float | None = None
    range_width: float | None = None
    close_position: str = "unknown"
    close_percentile: float | None = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class MovingAverageSlopeSummary:
    short_window: int
    long_window: int
    short_ma: float | None = None
    long_ma: float | None = None
    slope: float | None = None
    slope_label: str = "unknown"
    cross_state: str = "unknown"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class VwapRelationSummary:
    latest_close: float | None = None
    latest_vwap: float | None = None
    relation: str = "unknown"
    distance: float | None = None
    distance_pct: float | None = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class VolatilityTechnicalSummary:
    atr: float | None = None
    realized_volatility: float | None = None
    range_width: float | None = None
    state: str = "unknown"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class CandleWickBodySummary:
    latest_body: float | None = None
    latest_upper_wick: float | None = None
    latest_lower_wick: float | None = None
    latest_body_ratio: float | None = None
    wick_signal: str = "unknown"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class HumanTechnicalSummary:
    logic_version: str = LOGIC_VERSION
    timeframe_sec: int | None = None
    candle_count: int = 0
    support_zones: Tuple[SupportResistanceZone, ...] = ()
    resistance_zones: Tuple[SupportResistanceZone, ...] = ()
    range_boundary: RangeBoundarySummary = RangeBoundarySummary()
    moving_average: MovingAverageSlopeSummary = MovingAverageSlopeSummary(short_window=3, long_window=5)
    vwap_relation: VwapRelationSummary = VwapRelationSummary()
    volatility: VolatilityTechnicalSummary = VolatilityTechnicalSummary()
    wick_body: CandleWickBodySummary = CandleWickBodySummary()
    blockers: Tuple[str, ...] = ()
    warnings: Tuple[str, ...] = ()
    read_only: bool = True
    non_executing: bool = True
    would_collect_public_source: bool = False
    would_write_runtime_artifact: bool = False
    would_send_to_broker: bool = False

    @property
    def usable(self) -> bool:
        return not self.blockers

    def to_dict(self) -> Dict[str, Any]:
        return {
            "logic_version": self.logic_version,
            "timeframe_sec": self.timeframe_sec,
            "candle_count": self.candle_count,
            "support_zones": [zone.to_dict() for zone in self.support_zones],
            "resistance_zones": [zone.to_dict() for zone in self.resistance_zones],
            "range_boundary": self.range_boundary.to_dict(),
            "moving_average": self.moving_average.to_dict(),
            "vwap_relation": self.vwap_relation.to_dict(),
            "volatility": self.volatility.to_dict(),
            "wick_body": self.wick_body.to_dict(),
            "blockers": list(self.blockers),
            "warnings": list(self.warnings),
            "usable": self.usable,
            "read_only": self.read_only,
            "non_executing": self.non_executing,
            "would_collect_public_source": self.would_collect_public_source,
            "would_write_runtime_artifact": self.would_write_runtime_artifact,
            "would_send_to_broker": self.would_send_to_broker,
        }


def _sorted_candles(candles: Iterable[OHLCVCandle], timeframe_sec: int | None) -> list[OHLCVCandle]:
    selected = [c for c in candles if timeframe_sec is None or c.timeframe.timeframe_sec == int(timeframe_sec)]
    selected.sort(key=lambda c: c.start_ts)
    return selected


def _mean(values: list[float]) -> float | None:
    return sum(values) / len(values) if values else None


def _zone_from_values(kind: str, values: list[float]) -> SupportResistanceZone | None:
    if not values:
        return None
    anchor = min(values) if kind == "support" else max(values)
    width = max(anchor * 0.0005, 1.0)
    touches = sum(1 for value in values if abs(value - anchor) <= width)
    confidence = min(1.0, 0.35 + touches * 0.15)
    return SupportResistanceZone(kind, anchor - width, anchor + width, touches, round(confidence, 4))


def _range_summary(candles: list[OHLCVCandle]) -> RangeBoundarySummary:
    lows = [c.low for c in candles]
    highs = [c.high for c in candles]
    if not lows or not highs:
        return RangeBoundarySummary()
    low = min(lows)
    high = max(highs)
    width = max(high - low, 0.0)
    close = candles[-1].close
    pct = ((close - low) / width) if width > 0 else None
    if pct is None:
        pos = "flat"
    elif pct >= 0.75:
        pos = "near_range_high"
    elif pct <= 0.25:
        pos = "near_range_low"
    else:
        pos = "mid_range"
    return RangeBoundarySummary(low, high, width, pos, round(pct, 6) if pct is not None else None)


def _ma_summary(candles: list[OHLCVCandle], short_window: int, long_window: int) -> MovingAverageSlopeSummary:
    closes = [c.close for c in candles]
    if len(closes) < max(short_window, long_window):
        return MovingAverageSlopeSummary(short_window, long_window)
    short_ma = _mean(closes[-short_window:])
    long_ma = _mean(closes[-long_window:])
    prev_short = _mean(closes[-short_window - 1:-1]) if len(closes) > short_window else short_ma
    slope = (short_ma - prev_short) if short_ma is not None and prev_short is not None else None
    if slope is None:
        label = "unknown"
    elif slope > 0:
        label = "rising"
    elif slope < 0:
        label = "falling"
    else:
        label = "flat"
    if short_ma is None or long_ma is None:
        cross = "unknown"
    elif short_ma > long_ma:
        cross = "short_above_long"
    elif short_ma < long_ma:
        cross = "short_below_long"
    else:
        cross = "aligned"
    return MovingAverageSlopeSummary(short_window, long_window, short_ma, long_ma, slope, label, cross)


def _vwap_summary(candles: list[OHLCVCandle]) -> VwapRelationSummary:
    if not candles:
        return VwapRelationSummary()
    latest = candles[-1]
    if latest.vwap is None or latest.vwap == 0:
        return VwapRelationSummary(latest_close=latest.close)
    distance = latest.close - latest.vwap
    distance_pct = distance / latest.vwap
    if distance_pct > 0.001:
        relation = "above_vwap"
    elif distance_pct < -0.001:
        relation = "below_vwap"
    else:
        relation = "near_vwap"
    return VwapRelationSummary(latest.close, latest.vwap, relation, distance, round(distance_pct, 8))


def _vol_summary(candles: list[OHLCVCandle]) -> VolatilityTechnicalSummary:
    if not candles:
        return VolatilityTechnicalSummary()
    true_ranges: list[float] = []
    closes = [c.close for c in candles]
    prev_close: float | None = None
    for candle in candles:
        tr = candle.high - candle.low
        if prev_close is not None:
            tr = max(tr, abs(candle.high - prev_close), abs(candle.low - prev_close))
        true_ranges.append(tr)
        prev_close = candle.close
    atr = _mean(true_ranges[-min(14, len(true_ranges)):])
    returns = [(closes[i] - closes[i - 1]) / closes[i - 1] for i in range(1, len(closes)) if closes[i - 1] != 0]
    rv = None
    if returns:
        mean_ret = sum(returns) / len(returns)
        variance = sum((value - mean_ret) ** 2 for value in returns) / len(returns)
        rv = sqrt(variance)
    range_width = max(c.high for c in candles) - min(c.low for c in candles)
    if atr is None:
        state = "unknown"
    elif rv is not None and rv >= 0.01:
        state = "expanding"
    elif range_width <= max(candles[-1].close * 0.002, 1.0):
        state = "compressed"
    else:
        state = "normal"
    return VolatilityTechnicalSummary(atr, rv, range_width, state)


def _wick_body_summary(candles: list[OHLCVCandle]) -> CandleWickBodySummary:
    if not candles:
        return CandleWickBodySummary()
    latest = candles[-1]
    body = abs(latest.close - latest.open)
    upper = latest.high - max(latest.open, latest.close)
    lower = min(latest.open, latest.close) - latest.low
    full_range = max(latest.high - latest.low, 0.0)
    body_ratio = (body / full_range) if full_range > 0 else None
    if body_ratio is None:
        signal = "flat_candle"
    elif upper > body * 1.5 and upper > lower:
        signal = "upper_wick_rejection"
    elif lower > body * 1.5 and lower > upper:
        signal = "lower_wick_rejection"
    elif body_ratio >= 0.65:
        signal = "strong_body"
    else:
        signal = "mixed_wick_body"
    return CandleWickBodySummary(body, upper, lower, round(body_ratio, 6) if body_ratio is not None else None, signal)


def build_human_technical_summary(
    candles: Iterable[OHLCVCandle],
    *,
    timeframe_sec: int | None = None,
    short_ma_window: int = 3,
    long_ma_window: int = 5,
) -> HumanTechnicalSummary:
    selected = _sorted_candles(candles, timeframe_sec)
    blockers: list[str] = []
    warnings: list[str] = []
    if not selected:
        blockers.append("ohlcv_candles_missing")
        return HumanTechnicalSummary(timeframe_sec=timeframe_sec, candle_count=0, blockers=tuple(blockers))
    if len(selected) < long_ma_window:
        warnings.append("insufficient_candles_for_long_ma")
    lows = [c.low for c in selected]
    highs = [c.high for c in selected]
    support = _zone_from_values("support", lows)
    resistance = _zone_from_values("resistance", highs)
    return HumanTechnicalSummary(
        timeframe_sec=selected[-1].timeframe.timeframe_sec if timeframe_sec is None else int(timeframe_sec),
        candle_count=len(selected),
        support_zones=tuple(zone for zone in (support,) if zone is not None),
        resistance_zones=tuple(zone for zone in (resistance,) if zone is not None),
        range_boundary=_range_summary(selected),
        moving_average=_ma_summary(selected, short_ma_window, long_ma_window),
        vwap_relation=_vwap_summary(selected),
        volatility=_vol_summary(selected),
        wick_body=_wick_body_summary(selected),
        blockers=tuple(dict.fromkeys(blockers)),
        warnings=tuple(dict.fromkeys(warnings)),
    )
