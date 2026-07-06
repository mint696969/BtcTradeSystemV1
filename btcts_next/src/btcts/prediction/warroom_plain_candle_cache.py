# path: ./btcts_next/src/btcts/prediction/warroom_plain_candle_cache.py
# desc: D-hot derived cache writer/reader for WarRoom plain trade-price candles. Read-only for UI consumers.

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd

from btcts.prediction.warroom_plain_candles import (
    DEFAULT_DHOT_ROOT,
    DEFAULT_EXCHANGE,
    DEFAULT_MAX_FILES,
    DEFAULT_MAX_RANGE_MINUTES,
    DEFAULT_MAX_TRADES,
    DEFAULT_SYMBOL,
    DEFAULT_TIMEFRAME_SECONDS,
    ENV_DHOT_DATA_ROOT,
    ENV_DHOT_RUNTIME_ROOT,
    WARROOM_PLAIN_CANDLES_VERSION,
    candle_records,
    load_plain_trade_candles_time_range,
)

WARROOM_PLAIN_CANDLE_CACHE_VERSION = "warroom_plain_candle_cache.2026_07_06.v1_dhot_derived_latest_jsonl"
CACHE_RELATIVE = "data/derived/warroom/plain_candles/exchange={exchange}/symbol={symbol}/timeframe={timeframe_sec}s"
LATEST_CACHE_NAME = "latest.jsonl"
LATEST_META_NAME = "latest_meta.json"
CACHE_COLUMNS = [
    "time",
    "time_utc",
    "candle_index",
    "open",
    "high",
    "low",
    "close",
    "volume",
    "trade_count",
    "timeframe_sec",
    "source_family",
]


@dataclass(frozen=True)
class WarRoomPlainCandleCacheMeta:
    ok: bool
    version: str
    candle_core_version: str
    cache_root: str
    cache_path: str
    meta_path: str
    exchange: str
    symbol: str
    timeframe_sec: int
    start_ts_utc: str
    end_ts_utc: str
    candles_written: int
    source_meta: dict[str, Any]
    error: str | None = None
    read_only: bool = True
    broker_send_enabled: bool = False
    order_intent_submitted: bool = False
    prediction_invoked: bool = False
    classifier_invoked: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "ok": self.ok,
            "version": self.version,
            "candle_core_version": self.candle_core_version,
            "cache_root": self.cache_root,
            "cache_path": self.cache_path,
            "meta_path": self.meta_path,
            "exchange": self.exchange,
            "symbol": self.symbol,
            "timeframe_sec": self.timeframe_sec,
            "start_ts_utc": self.start_ts_utc,
            "end_ts_utc": self.end_ts_utc,
            "candles_written": self.candles_written,
            "source_meta": self.source_meta,
            "error": self.error,
            "read_only": self.read_only,
            "broker_send_enabled": self.broker_send_enabled,
            "order_intent_submitted": self.order_intent_submitted,
            "prediction_invoked": self.prediction_invoked,
            "classifier_invoked": self.classifier_invoked,
        }


def resolve_cache_base_root(root: Path | None = None) -> tuple[Path, str]:
    if root is not None:
        return Path(root), "explicit"
    for env_name in (ENV_DHOT_DATA_ROOT, ENV_DHOT_RUNTIME_ROOT):
        value = os.environ.get(env_name)
        if value and value.strip():
            return Path(value.strip()).expanduser(), f"env:{env_name}"
    return DEFAULT_DHOT_ROOT, "default:D:/btc_ts_hot"


def plain_candle_cache_dir(
    root: Path | None = None,
    *,
    exchange: str = DEFAULT_EXCHANGE,
    symbol: str = DEFAULT_SYMBOL,
    timeframe_sec: int = DEFAULT_TIMEFRAME_SECONDS,
) -> Path:
    base, _reason = resolve_cache_base_root(root)
    return base / CACHE_RELATIVE.format(exchange=exchange, symbol=symbol, timeframe_sec=int(timeframe_sec))


def latest_cache_paths(
    root: Path | None = None,
    *,
    exchange: str = DEFAULT_EXCHANGE,
    symbol: str = DEFAULT_SYMBOL,
    timeframe_sec: int = DEFAULT_TIMEFRAME_SECONDS,
) -> tuple[Path, Path]:
    directory = plain_candle_cache_dir(root, exchange=exchange, symbol=symbol, timeframe_sec=timeframe_sec)
    return directory / LATEST_CACHE_NAME, directory / LATEST_META_NAME


def _iso_utc(ts: Any) -> str:
    value = pd.Timestamp(ts)
    if value.tzinfo is None:
        value = value.tz_localize("UTC")
    value = value.tz_convert("UTC")
    return value.strftime("%Y-%m-%dT%H:%M:%SZ")


def _empty_cache_frame() -> pd.DataFrame:
    return pd.DataFrame(columns=CACHE_COLUMNS)


def _atomic_write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_suffix(path.suffix + ".tmp")
    tmp_path.write_text(text, encoding="utf-8")
    tmp_path.replace(path)


def _records_to_jsonl(records: list[dict[str, Any]]) -> str:
    return "".join(json.dumps(record, ensure_ascii=False, separators=(",", ":")) + "\n" for record in records)


def write_plain_candle_cache_time_range(
    *,
    raw_root: Path | None = None,
    cache_root: Path | None = None,
    start_ts: Any,
    end_ts: Any,
    exchange: str = DEFAULT_EXCHANGE,
    symbol: str = DEFAULT_SYMBOL,
    timeframe_sec: int = DEFAULT_TIMEFRAME_SECONDS,
    max_range_minutes: int = DEFAULT_MAX_RANGE_MINUTES,
    max_files: int = DEFAULT_MAX_FILES,
    max_trades: int = DEFAULT_MAX_TRADES,
) -> WarRoomPlainCandleCacheMeta:
    candles, source_meta = load_plain_trade_candles_time_range(
        root=raw_root,
        start_ts=start_ts,
        end_ts=end_ts,
        exchange=exchange,
        symbol=symbol,
        timeframe_sec=timeframe_sec,
        max_range_minutes=max_range_minutes,
        max_files=max_files,
        max_trades=max_trades,
    )
    cache_path, meta_path = latest_cache_paths(cache_root, exchange=exchange, symbol=symbol, timeframe_sec=timeframe_sec)
    records = candle_records(candles)
    if records:
        start_value = str(records[0]["time_utc"])
        end_value = str(records[-1]["time_utc"])
    else:
        start_value = _iso_utc(start_ts)
        end_value = _iso_utc(end_ts)
    cache_meta = WarRoomPlainCandleCacheMeta(
        ok=bool(records),
        version=WARROOM_PLAIN_CANDLE_CACHE_VERSION,
        candle_core_version=WARROOM_PLAIN_CANDLES_VERSION,
        cache_root=str(cache_path.parent),
        cache_path=str(cache_path),
        meta_path=str(meta_path),
        exchange=exchange,
        symbol=symbol,
        timeframe_sec=int(timeframe_sec),
        start_ts_utc=start_value,
        end_ts_utc=end_value,
        candles_written=len(records),
        source_meta=source_meta.to_dict(),
        error=None if records else source_meta.error or "no_candles_to_cache",
    )
    if not records:
        return cache_meta
    _atomic_write_text(cache_path, _records_to_jsonl(records))
    _atomic_write_text(meta_path, json.dumps(cache_meta.to_dict(), ensure_ascii=False, indent=2) + "\n")
    return cache_meta


def read_plain_candle_cache(
    root: Path | None = None,
    *,
    exchange: str = DEFAULT_EXCHANGE,
    symbol: str = DEFAULT_SYMBOL,
    timeframe_sec: int = DEFAULT_TIMEFRAME_SECONDS,
    max_candles: int | None = None,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    cache_path, meta_path = latest_cache_paths(root, exchange=exchange, symbol=symbol, timeframe_sec=timeframe_sec)
    if not cache_path.exists():
        return _empty_cache_frame(), {
            "ok": False,
            "version": WARROOM_PLAIN_CANDLE_CACHE_VERSION,
            "cache_path": str(cache_path),
            "meta_path": str(meta_path),
            "error": "cache_missing",
            "read_only": True,
            "broker_send_enabled": False,
            "order_intent_submitted": False,
            "prediction_invoked": False,
            "classifier_invoked": False,
        }
    rows: list[dict[str, Any]] = []
    with cache_path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            try:
                item = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(item, dict):
                rows.append(item)
    if max_candles is not None and max_candles >= 0:
        rows = rows[-int(max_candles) :]
    frame = pd.DataFrame(rows, columns=CACHE_COLUMNS) if rows else _empty_cache_frame()
    if not frame.empty:
        frame["time"] = pd.to_numeric(frame["time"], errors="coerce").astype("Int64")
        for column in ("open", "high", "low", "close", "volume"):
            frame[column] = pd.to_numeric(frame[column], errors="coerce")
        frame["trade_count"] = pd.to_numeric(frame["trade_count"], errors="coerce").fillna(0).astype(int)
        frame["timeframe_sec"] = pd.to_numeric(frame["timeframe_sec"], errors="coerce").fillna(timeframe_sec).astype(int)
    meta: dict[str, Any]
    if meta_path.exists():
        try:
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            meta = {"ok": False, "error": "meta_json_invalid"}
    else:
        meta = {"ok": False, "error": "meta_missing"}
    meta.update(
        {
            "read_ok": not frame.empty,
            "rows_returned": len(frame),
            "cache_path": str(cache_path),
            "read_only": True,
            "broker_send_enabled": False,
            "order_intent_submitted": False,
            "prediction_invoked": False,
            "classifier_invoked": False,
        }
    )
    return frame, meta
