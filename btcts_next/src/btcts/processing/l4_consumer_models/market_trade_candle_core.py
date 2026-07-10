# path: ./btcts_next/src/btcts/processing/l4_consumer_models/market_trade_candle_core.py
# desc: Shared L4 market.trade parsing and OHLC helpers. No prediction, UI, broker, scheduler, or runtime write dependency.

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Iterable, Mapping

import pandas as pd

DEFAULT_EXCHANGE = "bitflyer"
DEFAULT_SYMBOL = "FX_BTC_JPY"
DEFAULT_DHOT_ROOT = Path("D:/btc_ts_hot")
ENV_DHOT_DATA_ROOT = "BTCTS_HOT_DATA_ROOT"
ENV_DHOT_RUNTIME_ROOT = "BTC_TS_AUTOTRADE_RUNTIME_ROOT"
MARKET_TRADE_RELATIVE = "data/market_data/exchange={exchange}/symbol={symbol}/type=market.trade"
DEFAULT_TIMEFRAME_SECONDS = 60
PLAIN_CANDLE_COLUMNS = [
    "ts", "open", "high", "low", "close", "volume", "trade_count",
    "timeframe_sec", "source_family",
]
TRADE_ROW_COLUMNS = ["ts", "price", "size", "side", "trade_id", "source_file"]


def resolve_dhot_root() -> tuple[Path, str]:
    for env_name in (ENV_DHOT_DATA_ROOT, ENV_DHOT_RUNTIME_ROOT):
        value = os.environ.get(env_name)
        if value and value.strip():
            return Path(value.strip()).expanduser(), f"env:{env_name}"
    return DEFAULT_DHOT_ROOT, "default:D:/btc_ts_hot"


def _empty_candle_frame() -> pd.DataFrame:
    return pd.DataFrame(columns=PLAIN_CANDLE_COLUMNS)


def _parse_ts(value: Any) -> pd.Timestamp | None:
    ts = pd.to_datetime(value, utc=True, errors="coerce")
    if pd.isna(ts):
        return None
    return pd.Timestamp(ts)


def _first_present(mapping: Mapping[str, Any], keys: Iterable[str]) -> Any:
    for key in keys:
        if key in mapping and mapping[key] not in (None, ""):
            return mapping[key]
    return None


def _json_record_from_line(line: bytes | str) -> Mapping[str, Any] | None:
    if isinstance(line, bytes):
        line = line.decode("utf-8", errors="ignore")
    line = line.strip()
    if not line:
        return None
    try:
        item = json.loads(line)
    except json.JSONDecodeError:
        return None
    return item if isinstance(item, Mapping) else None


def _first_json_record(path: Path) -> Mapping[str, Any] | None:
    with path.open("rb") as handle:
        for line in handle:
            record = _json_record_from_line(line)
            if record is not None:
                return record
    return None


def _last_json_record(path: Path, *, block_size: int = 65536) -> Mapping[str, Any] | None:
    file_size = path.stat().st_size
    if file_size <= 0:
        return None
    with path.open("rb") as handle:
        pos = file_size
        buffer = b""
        while pos > 0:
            read_size = min(block_size, pos)
            pos -= read_size
            handle.seek(pos)
            buffer = handle.read(read_size) + buffer
            for line in reversed(buffer.splitlines()):
                record = _json_record_from_line(line)
                if record is not None:
                    return record
    return None


def _record_event_ts(record: Mapping[str, Any]) -> pd.Timestamp | None:
    payload = record.get("payload") if isinstance(record.get("payload"), Mapping) else {}
    return _parse_ts(
        _first_present(record, ("event_ts", "exchange_ts", "ingest_ts", "collector_ts", "ts", "timestamp"))
        or _first_present(payload, ("trade_ts", "event_ts", "timestamp", "ts"))
    )


def market_trade_record_to_trade_row(
    record: Mapping[str, Any], *, source_file: str = ""
) -> dict[str, Any] | None:
    payload = record.get("payload") if isinstance(record.get("payload"), Mapping) else {}
    ts = _record_event_ts(record)
    price = _first_present(payload, ("price", "last_price")) or _first_present(
        record, ("price", "last_price")
    )
    size = _first_present(payload, ("size", "volume")) or _first_present(
        record, ("size", "volume")
    ) or 0.0
    side = str(
        _first_present(payload, ("side",))
        or _first_present(record, ("side",))
        or ""
    )
    trade_id = (
        _first_present(payload, ("trade_id", "id"))
        or _first_present(record, ("source_event_id", "record_id"))
        or ""
    )
    value = pd.to_numeric(pd.Series([price]), errors="coerce").iloc[0]
    if ts is None or pd.isna(value):
        return None
    try:
        size_value = float(size or 0.0)
    except (TypeError, ValueError):
        size_value = 0.0
    return {
        "ts": ts,
        "price": float(value),
        "size": size_value,
        "side": side.upper() if side else "",
        "trade_id": str(trade_id or ""),
        "source_file": source_file,
    }


def build_trade_ohlc(
    trades: pd.DataFrame, *, timeframe_sec: int = DEFAULT_TIMEFRAME_SECONDS
) -> pd.DataFrame:
    if trades.empty:
        return _empty_candle_frame()
    work = trades.copy()
    work["ts"] = pd.to_datetime(work["ts"], utc=True, errors="coerce")
    work["price"] = pd.to_numeric(work["price"], errors="coerce")
    if "size" not in work.columns:
        work["size"] = 0.0
    work["size"] = pd.to_numeric(work["size"], errors="coerce").fillna(0.0)
    work = work.dropna(subset=["ts", "price"]).sort_values("ts")
    if work.empty:
        return _empty_candle_frame()
    work["bucket"] = work["ts"].dt.floor(f"{int(timeframe_sec)}s")
    candles = (
        work.groupby("bucket", sort=True)
        .agg(
            open=("price", "first"),
            high=("price", "max"),
            low=("price", "min"),
            close=("price", "last"),
            volume=("size", "sum"),
            trade_count=("price", "count"),
        )
        .reset_index()
        .rename(columns={"bucket": "ts"})
    )
    candles["timeframe_sec"] = int(timeframe_sec)
    candles["source_family"] = "warroom_market_trade_plain_ohlc"
    return candles[PLAIN_CANDLE_COLUMNS].sort_values("ts").reset_index(drop=True)


def market_trade_root(
    root: Path | None = None,
    *,
    exchange: str = DEFAULT_EXCHANGE,
    symbol: str = DEFAULT_SYMBOL,
) -> tuple[Path, str]:
    resolved_root, reason = (
        resolve_dhot_root() if root is None else (Path(root), "explicit")
    )
    return (
        resolved_root / MARKET_TRADE_RELATIVE.format(exchange=exchange, symbol=symbol),
        reason,
    )


def _date_dirs_desc(trade_root: Path, *, max_days: int) -> list[Path]:
    if not trade_root.exists():
        return []
    date_dirs = [path for path in trade_root.glob("date=*") if path.is_dir()]
    return sorted(date_dirs, key=lambda path: path.name, reverse=True)[
        : max(0, int(max_days))
    ]

LEGACY_CACHE_RELATIVE = "data/derived/warroom/plain_candles/exchange={exchange}/symbol={symbol}/timeframe={timeframe_sec}s"
LEGACY_LATEST_CACHE_NAME = "latest.jsonl"
LEGACY_LATEST_META_NAME = "latest_meta.json"
LEGACY_CACHE_COLUMNS = [
    "time", "time_utc", "candle_index", "open", "high", "low", "close",
    "volume", "trade_count", "timeframe_sec", "source_family",
]


def read_legacy_plain_candle_cache(
    root: Path | None = None,
    *,
    exchange: str = DEFAULT_EXCHANGE,
    symbol: str = DEFAULT_SYMBOL,
    timeframe_sec: int = DEFAULT_TIMEFRAME_SECONDS,
    max_candles: int | None = None,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    base, _reason = resolve_dhot_root() if root is None else (Path(root), "explicit")
    directory = base / LEGACY_CACHE_RELATIVE.format(
        exchange=exchange, symbol=symbol, timeframe_sec=int(timeframe_sec)
    )
    cache_path = directory / LEGACY_LATEST_CACHE_NAME
    meta_path = directory / LEGACY_LATEST_META_NAME
    if not cache_path.exists():
        return pd.DataFrame(columns=LEGACY_CACHE_COLUMNS), {
            "ok": False,
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
            item = _json_record_from_line(line)
            if isinstance(item, Mapping):
                rows.append(dict(item))
    if max_candles is not None and max_candles >= 0:
        rows = rows[-int(max_candles):]

    frame = (
        pd.DataFrame(rows, columns=LEGACY_CACHE_COLUMNS)
        if rows
        else pd.DataFrame(columns=LEGACY_CACHE_COLUMNS)
    )
    if not frame.empty:
        frame["time"] = pd.to_numeric(frame["time"], errors="coerce").astype("Int64")
        for column in ("open", "high", "low", "close", "volume"):
            frame[column] = pd.to_numeric(frame[column], errors="coerce")
        frame["trade_count"] = pd.to_numeric(
            frame["trade_count"], errors="coerce"
        ).fillna(0).astype(int)
        frame["timeframe_sec"] = pd.to_numeric(
            frame["timeframe_sec"], errors="coerce"
        ).fillna(timeframe_sec).astype(int)

    if meta_path.exists():
        try:
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            meta = {"ok": False, "error": "meta_json_invalid"}
    else:
        meta = {"ok": False, "error": "meta_missing"}
    meta.update({
        "read_ok": not frame.empty,
        "rows_returned": len(frame),
        "cache_path": str(cache_path),
        "read_only": True,
        "broker_send_enabled": False,
        "order_intent_submitted": False,
        "prediction_invoked": False,
        "classifier_invoked": False,
    })
    return frame, meta
