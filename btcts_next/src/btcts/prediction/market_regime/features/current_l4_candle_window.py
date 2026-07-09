# path: ./btcts_next/src/btcts/prediction/market_regime/features/current_l4_candle_window.py
# desc: Current WarRoom L4 candle-window summary helpers for MarketRegime features. Pure calculation only; no reads, writes, UI, broker, scheduler, or AutoTrade.

from __future__ import annotations

from math import sqrt
from typing import Any, Mapping

from ..source_snapshot import MarketRegimeSourceSnapshot

# MR_A2_SPLIT_CURRENT_L4_CANDLE_WINDOW_2026_07_09
CURRENT_L4_CANDLE_WINDOW_MAX_ROWS = 60


def _as_float(value: Any) -> float | None:
    try:
        if value is None:
            return None
        return float(value)
    except Exception:
        return None


def current_l4_candle_rows(snapshot: MarketRegimeSourceSnapshot) -> tuple[Mapping[str, Any], ...]:
    rows = tuple(dict(row) for row in snapshot.warroom_candles.closed_candles[-CURRENT_L4_CANDLE_WINDOW_MAX_ROWS:])
    return rows


def summarize_current_l4_candle_rows(rows: tuple[Mapping[str, Any], ...]) -> Mapping[str, Any]:
    if len(rows) < 2:
        return {"ok": False, "reason": "insufficient_current_l4_candles", "candle_count": len(rows)}
    opens = [_as_float(row.get("open")) for row in rows]
    highs = [_as_float(row.get("high")) for row in rows]
    lows = [_as_float(row.get("low")) for row in rows]
    closes = [_as_float(row.get("close")) for row in rows]
    valid = all(value is not None for value in opens + highs + lows + closes)
    if not valid:
        return {"ok": False, "reason": "invalid_current_l4_candle_ohlc", "candle_count": len(rows)}
    first_open = float(opens[0] or 0.0)
    last_close = float(closes[-1] or 0.0)
    high = max(float(value or 0.0) for value in highs)
    low = min(float(value or 0.0) for value in lows)
    denom = first_open if first_open > 0 else 1.0
    net_bps = ((last_close - first_open) / denom) * 10000.0
    range_bps = ((high - low) / denom) * 10000.0
    close_position = (last_close - low) / (high - low) if high > low else 0.5
    close_returns: list[float] = []
    for prev, curr in zip(closes, closes[1:]):
        prev_f = float(prev or 0.0)
        curr_f = float(curr or 0.0)
        if prev_f > 0:
            close_returns.append(((curr_f - prev_f) / prev_f) * 10000.0)
    mean = sum(close_returns) / len(close_returns) if close_returns else 0.0
    variance = sum((value - mean) ** 2 for value in close_returns) / len(close_returns) if close_returns else 0.0
    realized_vol_bps = sqrt(variance) if variance >= 0 else 0.0
    per_candle_ranges = []
    for high_v, low_v, open_v in zip(highs, lows, opens):
        base = float(open_v or 0.0) or denom
        if base > 0:
            per_candle_ranges.append(((float(high_v or 0.0) - float(low_v or 0.0)) / base) * 10000.0)
    avg_range_bps = sum(per_candle_ranges) / len(per_candle_ranges) if per_candle_ranges else 0.0
    return {
        "ok": True,
        "candle_count": len(rows),
        "first_ts": str(rows[0].get("time_utc") or ""),
        "last_ts": str(rows[-1].get("time_utc") or ""),
        "first_open": round(first_open, 8),
        "last_close": round(last_close, 8),
        "high": round(high, 8),
        "low": round(low, 8),
        "net_change_bps": round(net_bps, 4),
        "range_bps": round(range_bps, 4),
        "close_position": round(close_position, 4),
        "realized_volatility_bps": round(realized_vol_bps, 4),
        "average_candle_range_bps": round(avg_range_bps, 4),
    }


def current_l4_candle_regime_hint(summary: Mapping[str, Any]) -> tuple[str, str]:
    if not bool(summary.get("ok")) or int(summary.get("candle_count") or 0) < 2:
        return "UNKNOWN", "insufficient_current_l4_candle_window"
    range_bps = _as_float(summary.get("range_bps")) or 0.0
    net_bps = _as_float(summary.get("net_change_bps")) or 0.0
    abs_net = abs(net_bps)
    if range_bps >= 180.0 and abs_net <= range_bps * 0.35:
        return "HIGH_VOL_CHOP", "current_l4_wide_range_without_directional_acceptance"
    if abs_net >= max(25.0, range_bps * 0.45):
        return ("UP_TREND", "current_l4_positive_net_change_dominates_window") if net_bps > 0 else ("DOWN_TREND", "current_l4_negative_net_change_dominates_window")
    if range_bps <= 20.0:
        return "LOW_VOL_COMPRESSION", "current_l4_small_range_compressed_window"
    return "RANGE", "current_l4_bounded_or_mean_reverting_window"
