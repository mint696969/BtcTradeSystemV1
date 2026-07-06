# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/rt_ui/interactive_chart/candle_records.py
# desc: Convert backend candle frames to compact frontend records. Pure transform only.

from __future__ import annotations

from typing import Any

import pandas as pd


def utc_timestamp(value: object) -> pd.Timestamp | None:
    ts = pd.to_datetime(value, utc=True, errors="coerce")
    if pd.isna(ts):
        return None
    return ts


def epoch_seconds(value: object) -> int | None:
    ts = utc_timestamp(value)
    if ts is None:
        return None
    return int(ts.timestamp())


def iso_utc(value: object) -> str | None:
    ts = utc_timestamp(value)
    if ts is None:
        return None
    return ts.isoformat().replace("+00:00", "Z")


def iso_jst(value: object) -> str | None:
    ts = utc_timestamp(value)
    if ts is None:
        return None
    return ts.tz_convert("Asia/Tokyo").isoformat()


def build_interactive_candle_records(candle_frame: pd.DataFrame, *, max_candles: int = 720) -> list[dict[str, Any]]:
    if candle_frame.empty:
        return []
    required = {"ts", "open", "high", "low", "close"}
    if not required.issubset(set(candle_frame.columns)):
        return []
    frame = candle_frame.copy()
    frame["ts"] = pd.to_datetime(frame["ts"], utc=True, errors="coerce")
    for column in ["open", "high", "low", "close"]:
        frame[column] = pd.to_numeric(frame[column], errors="coerce")
    frame = frame.dropna(subset=["ts", "open", "high", "low", "close"]).sort_values("ts").tail(max_candles)
    records: list[dict[str, Any]] = []
    for index, row in enumerate(frame.to_dict("records")):
        epoch = epoch_seconds(row.get("ts"))
        if epoch is None:
            continue
        records.append(
            {
                "time": epoch,
                "time_utc": iso_utc(row.get("ts")),
                "time_jst": iso_jst(row.get("ts")),
                "open": round(float(row["open"]), 6),
                "high": round(float(row["high"]), 6),
                "low": round(float(row["low"]), 6),
                "close": round(float(row["close"]), 6),
                "volume": round(float(row.get("volume") or 0.0), 8),
                "trade_count": int(row.get("trade_count") or row.get("count") or 0),
                "candle_index": index,
                "candle_status": str(row.get("candle_status") or ""),
                "source_role": str(row.get("source_role") or ""),
            }
        )
    return records
