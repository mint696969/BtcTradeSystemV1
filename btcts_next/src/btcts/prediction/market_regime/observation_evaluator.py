# path: ./btcts_next/src/btcts/prediction/market_regime/observation_evaluator.py
# desc: Market-regime candle-summary observation evaluator MVP. Reads WarRoom derived closed candles and returns compact outcome observations. No raw market payload duplication, classifier, scheduler, broker, AutoTrade, or parameter promotion.

from __future__ import annotations

import json
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Mapping

MARKET_REGIME_CANDLE_OBSERVATION_EVALUATOR_VERSION = "prediction.market_regime.observation_evaluator.2026_07_08.v1"
WARROOM_CANDLE_STORE_VERSION_HINT = "warroom_candle_store.2026_07_07.v1_rolling_closed_forming"


def _parse_ts(value: object) -> datetime | None:
    text = str(value or "").strip()
    if not text:
        return None
    try:
        return datetime.fromisoformat(text.replace("Z", "+00:00")).astimezone(timezone.utc)
    except Exception:
        return None


def _iso(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _as_float(value: object, default: float = 0.0) -> float:
    try:
        return float(value)
    except Exception:
        return default


def warroom_closed_candle_relpath(*, timeframe_sec: int, exchange: str = "bitflyer", symbol: str = "FX_BTC_JPY") -> str:
    return f"data/derived/warroom/candles/exchange={exchange}/symbol={symbol}/timeframe={int(timeframe_sec)}s/closed.jsonl"


def select_observation_candle_timeframe_sec(horizon_sec: int) -> int:
    horizon = max(0, int(horizon_sec))
    if horizon <= 600:
        return 60
    if horizon <= 3600:
        return 300
    if horizon <= 21600:
        return 900
    return 3600


def _candle_ts(row: Mapping[str, Any]) -> datetime | None:
    return _parse_ts(row.get("time_utc") or row.get("ts") or row.get("timestamp"))


def read_warroom_closed_candles_for_window(
    root: str | Path,
    *,
    start_utc: str,
    end_utc: str,
    timeframe_sec: int,
    exchange: str = "bitflyer",
    symbol: str = "FX_BTC_JPY",
    max_candles: int = 2000,
) -> list[dict[str, Any]]:
    start = _parse_ts(start_utc)
    end = _parse_ts(end_utc)
    if start is None or end is None or end < start:
        return []
    relpath = warroom_closed_candle_relpath(timeframe_sec=timeframe_sec, exchange=exchange, symbol=symbol)
    path = Path(root) / relpath
    if not path.exists():
        return []
    candles: list[dict[str, Any]] = []
    limit = max(1, int(max_candles))
    with path.open("r", encoding="utf-8") as handle:
        for raw in handle:
            if not raw.strip():
                continue
            try:
                row = json.loads(raw)
            except Exception:
                continue
            if not isinstance(row, Mapping):
                continue
            ts = _candle_ts(row)
            if ts is None or ts < start or ts > end:
                continue
            candles.append({
                "time_utc": _iso(ts),
                "open": _as_float(row.get("open")),
                "high": _as_float(row.get("high")),
                "low": _as_float(row.get("low")),
                "close": _as_float(row.get("close")),
                "volume": _as_float(row.get("volume")),
                "trade_count": int(row.get("trade_count") or 0),
                "timeframe_sec": int(row.get("timeframe_sec") or timeframe_sec),
            })
            if len(candles) >= limit:
                break
    return candles


def summarize_candle_window(candles: list[Mapping[str, Any]]) -> dict[str, Any]:
    rows = [dict(row) for row in candles if isinstance(row, Mapping)]
    if not rows:
        return {"ok": False, "reason": "no_candles", "candle_count": 0}
    opens = [_as_float(row.get("open")) for row in rows]
    highs = [_as_float(row.get("high")) for row in rows]
    lows = [_as_float(row.get("low")) for row in rows]
    closes = [_as_float(row.get("close")) for row in rows]
    volumes = [_as_float(row.get("volume")) for row in rows]
    trade_counts = [int(row.get("trade_count") or 0) for row in rows]
    first_open = opens[0]
    last_close = closes[-1]
    high = max(highs)
    low = min(lows)
    denom = first_open if first_open > 0 else 1.0
    net_change_bps = ((last_close - first_open) / denom) * 10000.0
    range_bps = ((high - low) / denom) * 10000.0
    close_position = (last_close - low) / (high - low) if high > low else 0.5
    return {
        "ok": True,
        "candle_count": len(rows),
        "first_ts": str(rows[0].get("time_utc") or ""),
        "last_ts": str(rows[-1].get("time_utc") or ""),
        "first_open": round(first_open, 8),
        "last_close": round(last_close, 8),
        "high": round(high, 8),
        "low": round(low, 8),
        "net_change_bps": round(net_change_bps, 4),
        "range_bps": round(range_bps, 4),
        "close_position": round(close_position, 4),
        "volume_sum": round(sum(volumes), 8),
        "trade_count_sum": int(sum(trade_counts)),
    }


def classify_candle_window_regime(summary: Mapping[str, Any]) -> tuple[str, str]:
    if not bool(summary.get("ok")) or int(summary.get("candle_count") or 0) < 2:
        return "UNKNOWN", "insufficient_candle_window"
    range_bps = _as_float(summary.get("range_bps"))
    net_bps = _as_float(summary.get("net_change_bps"))
    abs_net = abs(net_bps)
    if range_bps >= 250.0 and abs_net <= range_bps * 0.35:
        return "HIGH_VOL_CHOP", "wide_range_without_directional_acceptance"
    if abs_net >= max(35.0, range_bps * 0.45):
        return ("UP_TREND", "positive_net_change_dominates_window") if net_bps > 0 else ("DOWN_TREND", "negative_net_change_dominates_window")
    if range_bps <= 30.0:
        return "LOW_VOL_COMPRESSION", "small_range_compressed_window"
    return "RANGE", "bounded_or_mean_reverting_candle_window"


def build_market_regime_candle_observation(
    root: str | Path,
    *,
    prediction: Mapping[str, Any],
    resolved_at: str | None = None,
    exchange: str = "bitflyer",
    symbol: str = "FX_BTC_JPY",
    timeframe_sec: int | None = None,
    max_candles: int = 2000,
) -> dict[str, Any]:
    generated_at = str(prediction.get("generated_at") or prediction.get("prediction_generated_at") or "")
    generated = _parse_ts(generated_at)
    horizon_sec = int(prediction.get("horizon_sec") or 0)
    if generated is None or horizon_sec <= 0:
        return _unavailable_observation(reason="prediction_time_or_horizon_missing", resolved_at=resolved_at or generated_at)
    expiry = generated + timedelta(seconds=horizon_sec)
    effective_resolved_at = resolved_at or _iso(expiry)
    tf = int(timeframe_sec or select_observation_candle_timeframe_sec(horizon_sec))
    relpath = warroom_closed_candle_relpath(timeframe_sec=tf, exchange=exchange, symbol=symbol)
    candles: list[dict[str, Any]] = []
    last_read_error: OSError | None = None
    for attempt in range(1, 4):
        try:
            candles = read_warroom_closed_candles_for_window(
                root,
                start_utc=generated_at,
                end_utc=_iso(expiry),
                timeframe_sec=tf,
                exchange=exchange,
                symbol=symbol,
                max_candles=max_candles,
            )
            last_read_error = None
            break
        except OSError as exc:
            last_read_error = exc
            if attempt < 3:
                time.sleep(min(0.25, 0.05 * (2 ** (attempt - 1))))
    if last_read_error is not None:
        return _unavailable_observation(
            reason=f"candle_read_error:{type(last_read_error).__name__}",
            resolved_at=effective_resolved_at,
            source_refs=[relpath],
        )
    summary = summarize_candle_window(candles)
    observed, reason = classify_candle_window_regime(summary)
    available = bool(summary.get("ok")) and observed != "UNKNOWN"
    return {
        "observation_at": effective_resolved_at,
        "observation_available": available,
        "observed_regime_code": observed,
        "observation_source": "candle_summary",
        "source_refs": [relpath],
        "summary": (
            f"candle_summary_observation horizon_sec={horizon_sec} timeframe_sec={tf} "
            f"candles={summary.get('candle_count', 0)} regime={observed} reason={reason} "
            f"net_bps={summary.get('net_change_bps')} range_bps={summary.get('range_bps')}"
        ),
        "invalidated": False,
        "partial_match": False,
        "candle_summary": summary,
        "observation_reason": reason,
        "observation_evaluator_version": MARKET_REGIME_CANDLE_OBSERVATION_EVALUATOR_VERSION,
        "safety": _safety(),
    }


def _unavailable_observation(*, reason: str, resolved_at: str, source_refs: list[str] | None = None) -> dict[str, Any]:
    return {
        "observation_at": str(resolved_at or ""),
        "observation_available": False,
        "observed_regime_code": "UNKNOWN",
        "observation_source": "candle_summary",
        "source_refs": list(source_refs or []),
        "summary": reason,
        "invalidated": False,
        "partial_match": False,
        "candle_summary": {"ok": False, "reason": reason, "candle_count": 0},
        "observation_reason": reason,
        "observation_evaluator_version": MARKET_REGIME_CANDLE_OBSERVATION_EVALUATOR_VERSION,
        "safety": _safety(),
    }


def _safety() -> dict[str, Any]:
    return {
        "reads_derived_warroom_candles_only": True,
        "raw_market_data_duplicated": False,
        "raw_orderbook_read": False,
        "raw_trades_read": False,
        "classifier_invoked": False,
        "scheduler_enabled": False,
        "producer_loop_enabled": False,
        "broker_private_api_allowed": False,
        "autotrade_trigger_allowed": False,
        "order_intent_submitted": False,
        "parameter_auto_promotion_allowed": False,
        "would_send_to_broker": False,
    }
