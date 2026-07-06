# path: ./btcts_next/src/btcts/prediction/warroom_plain_candles.py
# desc: Bounded plain trade-price candlestick core for WarRoom. Read-only, no UI/broker/order/prediction invocation.

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping

import pandas as pd

WARROOM_PLAIN_CANDLES_VERSION = "warroom_plain_candles.2026_07_06.v1_time_range_trade_ohlc"
DEFAULT_EXCHANGE = "bitflyer"
DEFAULT_SYMBOL = "FX_BTC_JPY"
DEFAULT_DHOT_ROOT = Path("D:/btc_ts_hot")
ENV_DHOT_DATA_ROOT = "BTCTS_HOT_DATA_ROOT"
ENV_DHOT_RUNTIME_ROOT = "BTC_TS_AUTOTRADE_RUNTIME_ROOT"
MARKET_TRADE_RELATIVE = "data/market_data/exchange={exchange}/symbol={symbol}/type=market.trade"
DEFAULT_TIMEFRAME_SECONDS = 60
DEFAULT_MAX_RANGE_MINUTES = 360
DEFAULT_MAX_FILES = 8
DEFAULT_MAX_TRADES = 500_000
PLAIN_CANDLE_COLUMNS = ["ts", "open", "high", "low", "close", "volume", "trade_count", "timeframe_sec", "source_family"]
TRADE_ROW_COLUMNS = ["ts", "price", "size", "side", "trade_id", "source_file"]


@dataclass(frozen=True)
class WarRoomPlainCandleReadMeta:
    ok: bool
    version: str
    source_root: str
    source_root_reason: str
    exchange: str
    symbol: str
    start_ts_utc: str
    end_ts_utc: str
    requested_start_ts_utc: str
    requested_end_ts_utc: str
    max_range_minutes: int
    range_clamped: bool
    timeframe_sec: int
    candidate_file_count: int
    scanned_file_count: int
    max_files: int
    max_trades: int
    trades_read: int
    candles_returned: int
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
            "source_root": self.source_root,
            "source_root_reason": self.source_root_reason,
            "exchange": self.exchange,
            "symbol": self.symbol,
            "start_ts_utc": self.start_ts_utc,
            "end_ts_utc": self.end_ts_utc,
            "requested_start_ts_utc": self.requested_start_ts_utc,
            "requested_end_ts_utc": self.requested_end_ts_utc,
            "max_range_minutes": self.max_range_minutes,
            "range_clamped": self.range_clamped,
            "timeframe_sec": self.timeframe_sec,
            "candidate_file_count": self.candidate_file_count,
            "scanned_file_count": self.scanned_file_count,
            "max_files": self.max_files,
            "max_trades": self.max_trades,
            "trades_read": self.trades_read,
            "candles_returned": self.candles_returned,
            "error": self.error,
            "read_only": self.read_only,
            "broker_send_enabled": self.broker_send_enabled,
            "order_intent_submitted": self.order_intent_submitted,
            "prediction_invoked": self.prediction_invoked,
            "classifier_invoked": self.classifier_invoked,
        }


def resolve_dhot_root() -> tuple[Path, str]:
    for env_name in (ENV_DHOT_DATA_ROOT, ENV_DHOT_RUNTIME_ROOT):
        value = os.environ.get(env_name)
        if value and value.strip():
            return Path(value.strip()).expanduser(), f"env:{env_name}"
    return DEFAULT_DHOT_ROOT, "default:D:/btc_ts_hot"


def _empty_trade_frame() -> pd.DataFrame:
    return pd.DataFrame(columns=TRADE_ROW_COLUMNS)


def _empty_candle_frame() -> pd.DataFrame:
    return pd.DataFrame(columns=PLAIN_CANDLE_COLUMNS)


def _iso_utc(ts: pd.Timestamp) -> str:
    value = pd.Timestamp(ts)
    if value.tzinfo is None:
        value = value.tz_localize("UTC")
    value = value.tz_convert("UTC")
    return value.strftime("%Y-%m-%dT%H:%M:%SZ")


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


def _part_file_span(path: Path) -> tuple[pd.Timestamp | None, pd.Timestamp | None]:
    first = _first_json_record(path)
    last = _last_json_record(path)
    return _record_event_ts(first or {}), _record_event_ts(last or {})


def _part_file_overlaps_range(path: Path, *, start_ts: pd.Timestamp, end_ts: pd.Timestamp) -> bool:
    first_ts, last_ts = _part_file_span(path)
    if last_ts is not None and last_ts < start_ts:
        return False
    if first_ts is not None and first_ts > end_ts:
        return False
    return True


def _record_event_ts(record: Mapping[str, Any]) -> pd.Timestamp | None:
    payload = record.get("payload") if isinstance(record.get("payload"), Mapping) else {}
    return _parse_ts(
        _first_present(record, ("event_ts", "exchange_ts", "ingest_ts", "collector_ts"))
        or _first_present(payload, ("trade_ts", "event_ts", "timestamp"))
    )


def market_trade_record_to_trade_row(record: Mapping[str, Any], *, source_file: str = "") -> dict[str, Any] | None:
    payload = record.get("payload") if isinstance(record.get("payload"), Mapping) else {}
    ts = _record_event_ts(record)
    price = _first_present(payload, ("price", "last_price")) or _first_present(record, ("price", "last_price"))
    size = _first_present(payload, ("size", "volume")) or _first_present(record, ("size", "volume")) or 0.0
    side = str(_first_present(payload, ("side",)) or _first_present(record, ("side",)) or "")
    trade_id = _first_present(payload, ("trade_id", "id")) or _first_present(record, ("source_event_id", "record_id")) or ""
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


def build_trade_ohlc(trades: pd.DataFrame, *, timeframe_sec: int = DEFAULT_TIMEFRAME_SECONDS) -> pd.DataFrame:
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


def candle_records(candles: pd.DataFrame) -> list[dict[str, Any]]:
    if candles.empty:
        return []
    records: list[dict[str, Any]] = []
    for index, row in candles.sort_values("ts").reset_index(drop=True).iterrows():
        ts = pd.Timestamp(row["ts"])
        if ts.tzinfo is None:
            ts = ts.tz_localize("UTC")
        ts = ts.tz_convert("UTC")
        records.append(
            {
                "time": int(ts.timestamp()),
                "time_utc": _iso_utc(ts),
                "candle_index": int(index),
                "open": float(row["open"]),
                "high": float(row["high"]),
                "low": float(row["low"]),
                "close": float(row["close"]),
                "volume": float(row.get("volume") or 0.0),
                "trade_count": int(row.get("trade_count") or 0),
                "timeframe_sec": int(row.get("timeframe_sec") or DEFAULT_TIMEFRAME_SECONDS),
                "source_family": str(row.get("source_family") or "warroom_market_trade_plain_ohlc"),
            }
        )
    return records


def market_trade_root(root: Path | None = None, *, exchange: str = DEFAULT_EXCHANGE, symbol: str = DEFAULT_SYMBOL) -> tuple[Path, str]:
    resolved_root, reason = resolve_dhot_root() if root is None else (Path(root), "explicit")
    return resolved_root / MARKET_TRADE_RELATIVE.format(exchange=exchange, symbol=symbol), reason


def _date_labels_between(start_ts: pd.Timestamp, end_ts: pd.Timestamp) -> set[str]:
    start_date = pd.Timestamp(start_ts).tz_convert("UTC").date()
    end_date = pd.Timestamp(end_ts).tz_convert("UTC").date()
    return {item.strftime("%Y-%m-%d") for item in pd.date_range(start=start_date, end=end_date, freq="D")}


def iter_candidate_part_files(root: Path | None, *, start_ts: pd.Timestamp, end_ts: pd.Timestamp, exchange: str = DEFAULT_EXCHANGE, symbol: str = DEFAULT_SYMBOL) -> tuple[list[Path], Path, str]:
    trade_root, reason = market_trade_root(root, exchange=exchange, symbol=symbol)
    if not trade_root.exists():
        return [], trade_root, reason
    labels = _date_labels_between(start_ts, end_ts)
    parts: list[Path] = []
    for label in sorted(labels):
        date_dir = trade_root / f"date={label}"
        if date_dir.is_dir():
            parts.extend(sorted(date_dir.glob("part-*.jsonl")))
    return parts, trade_root, reason


def load_market_trade_rows_time_range(
    *,
    root: Path | None = None,
    start_ts: Any,
    end_ts: Any,
    exchange: str = DEFAULT_EXCHANGE,
    symbol: str = DEFAULT_SYMBOL,
    max_range_minutes: int = DEFAULT_MAX_RANGE_MINUTES,
    max_files: int = DEFAULT_MAX_FILES,
    max_trades: int = DEFAULT_MAX_TRADES,
) -> tuple[pd.DataFrame, WarRoomPlainCandleReadMeta]:
    requested_start = _parse_ts(start_ts)
    requested_end = _parse_ts(end_ts)
    fallback_root, fallback_reason = market_trade_root(root, exchange=exchange, symbol=symbol)
    if requested_start is None or requested_end is None or requested_start >= requested_end:
        meta = WarRoomPlainCandleReadMeta(
            ok=False,
            version=WARROOM_PLAIN_CANDLES_VERSION,
            source_root=str(fallback_root),
            source_root_reason=fallback_reason,
            exchange=exchange,
            symbol=symbol,
            start_ts_utc="",
            end_ts_utc="",
            requested_start_ts_utc=str(start_ts),
            requested_end_ts_utc=str(end_ts),
            max_range_minutes=max_range_minutes,
            range_clamped=False,
            timeframe_sec=DEFAULT_TIMEFRAME_SECONDS,
            candidate_file_count=0,
            scanned_file_count=0,
            max_files=max_files,
            max_trades=max_trades,
            trades_read=0,
            candles_returned=0,
            error="invalid_time_range",
        )
        return _empty_trade_frame(), meta
    start = requested_start
    end = requested_end
    max_delta = pd.Timedelta(minutes=max(1, int(max_range_minutes)))
    range_clamped = False
    if end - start > max_delta:
        start = end - max_delta
        range_clamped = True
    candidates, trade_root, root_reason = iter_candidate_part_files(root, start_ts=start, end_ts=end, exchange=exchange, symbol=symbol)
    overlapping_candidates = [path for path in candidates if _part_file_overlaps_range(path, start_ts=start, end_ts=end)]
    rows: list[dict[str, Any]] = []
    scanned = 0
    for path in overlapping_candidates[: max(0, int(max_files))]:
        scanned += 1
        source_file = str(path.relative_to(trade_root.parent.parent.parent.parent)) if trade_root.exists() else str(path)
        with path.open("rb") as handle:
            for line in handle:
                record = _json_record_from_line(line)
                if record is None:
                    continue
                ts = _record_event_ts(record)
                if ts is None or ts < start or ts > end:
                    continue
                row = market_trade_record_to_trade_row(record, source_file=source_file)
                if row is None:
                    continue
                rows.append(row)
                if len(rows) >= max_trades:
                    break
        if len(rows) >= max_trades:
            break
    frame = pd.DataFrame(rows, columns=TRADE_ROW_COLUMNS) if rows else _empty_trade_frame()
    if not frame.empty:
        frame = frame.drop_duplicates(subset=["ts", "price", "trade_id"]).sort_values("ts").reset_index(drop=True)
    meta = WarRoomPlainCandleReadMeta(
        ok=not frame.empty,
        version=WARROOM_PLAIN_CANDLES_VERSION,
        source_root=str(trade_root),
        source_root_reason=root_reason,
        exchange=exchange,
        symbol=symbol,
        start_ts_utc=_iso_utc(start),
        end_ts_utc=_iso_utc(end),
        requested_start_ts_utc=_iso_utc(requested_start),
        requested_end_ts_utc=_iso_utc(requested_end),
        max_range_minutes=int(max_range_minutes),
        range_clamped=range_clamped,
        timeframe_sec=DEFAULT_TIMEFRAME_SECONDS,
        candidate_file_count=len(overlapping_candidates),
        scanned_file_count=scanned,
        max_files=int(max_files),
        max_trades=int(max_trades),
        trades_read=len(frame),
        candles_returned=0,
        error=None if not frame.empty else "no_trade_rows_in_range",
    )
    return frame, meta


def load_plain_trade_candles_time_range(
    *,
    root: Path | None = None,
    start_ts: Any,
    end_ts: Any,
    exchange: str = DEFAULT_EXCHANGE,
    symbol: str = DEFAULT_SYMBOL,
    timeframe_sec: int = DEFAULT_TIMEFRAME_SECONDS,
    max_range_minutes: int = DEFAULT_MAX_RANGE_MINUTES,
    max_files: int = DEFAULT_MAX_FILES,
    max_trades: int = DEFAULT_MAX_TRADES,
) -> tuple[pd.DataFrame, WarRoomPlainCandleReadMeta]:
    trades, meta = load_market_trade_rows_time_range(
        root=root,
        start_ts=start_ts,
        end_ts=end_ts,
        exchange=exchange,
        symbol=symbol,
        max_range_minutes=max_range_minutes,
        max_files=max_files,
        max_trades=max_trades,
    )
    candles = build_trade_ohlc(trades, timeframe_sec=timeframe_sec)
    meta = WarRoomPlainCandleReadMeta(
        **{**meta.to_dict(), "timeframe_sec": int(timeframe_sec), "candles_returned": len(candles), "ok": not candles.empty, "error": None if not candles.empty else meta.error or "no_candles_returned"}
    )
    return candles, meta
