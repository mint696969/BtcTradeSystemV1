# path: ./btcts_next/src/btcts/processing/l4_consumer_models/operator_ui/warroom_candle_store.py
# desc: Rolling multi-timeframe WarRoom candle store. Closed candles are append-stable; forming candle is mutable. Missing periods are represented by absent candles, not synthetic null rows.

from __future__ import annotations

import argparse
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence

import pandas as pd

from btcts.processing.l4_consumer_models.market_trade_candle_core import (
    _date_dirs_desc,
    DEFAULT_DHOT_ROOT,
    DEFAULT_EXCHANGE,
    DEFAULT_SYMBOL,
    DEFAULT_TIMEFRAME_SECONDS,
    _first_json_record,
    _first_present,
    _json_record_from_line,
    _last_json_record,
    _parse_ts,
    _record_event_ts,
    build_trade_ohlc,
    market_trade_record_to_trade_row,
    market_trade_root,
)

WARROOM_CANDLE_STORE_VERSION = "warroom_candle_store.2026_07_07.v1_rolling_closed_forming"
WARROOM_CANDLE_STORE_LAYER = "L4_CONSUMER_MODEL_OPERATOR_UI"
WARROOM_CANDLE_STORE_CANONICAL_MODULE = "btcts.processing.l4_consumer_models.operator_ui.warroom_candle_store"
DEFAULT_TIMEFRAMES_SEC = (60, 300, 900, 1800, 3600, 86400)
DEFAULT_RETENTION_DAYS = 92
DEFAULT_MAX_CANDLES = 720
DEFAULT_BOOTSTRAP_MAX_BYTES = 320 * 1024 * 1024
CANDLE_STORE_RELATIVE = "data/derived/warroom/candles/exchange={exchange}/symbol={symbol}"
CLOSED_NAME = "closed.jsonl"
FORMING_NAME = "forming.json"
META_NAME = "meta.json"
STATE_NAME = "update_state.json"


def _root(root: Path | None) -> Path:
    return Path(root) if root is not None else DEFAULT_DHOT_ROOT


def candle_symbol_store_dir(root: Path | None = None, *, exchange: str = DEFAULT_EXCHANGE, symbol: str = DEFAULT_SYMBOL) -> Path:
    return _root(root) / CANDLE_STORE_RELATIVE.format(exchange=exchange, symbol=symbol)


def candle_timeframe_dir(root: Path | None = None, *, exchange: str = DEFAULT_EXCHANGE, symbol: str = DEFAULT_SYMBOL, timeframe_sec: int = DEFAULT_TIMEFRAME_SECONDS) -> Path:
    return candle_symbol_store_dir(root, exchange=exchange, symbol=symbol) / f"timeframe={int(timeframe_sec)}s"


def candle_store_paths(root: Path | None = None, *, exchange: str = DEFAULT_EXCHANGE, symbol: str = DEFAULT_SYMBOL, timeframe_sec: int = DEFAULT_TIMEFRAME_SECONDS) -> dict[str, Path]:
    directory = candle_timeframe_dir(root, exchange=exchange, symbol=symbol, timeframe_sec=timeframe_sec)
    symbol_dir = candle_symbol_store_dir(root, exchange=exchange, symbol=symbol)
    return {
        "dir": directory,
        "closed": directory / CLOSED_NAME,
        "forming": directory / FORMING_NAME,
        "meta": directory / META_NAME,
        "state": symbol_dir / STATE_NAME,
    }


def _iso_utc(value: Any) -> str:
    ts = pd.Timestamp(value)
    if ts.tzinfo is None:
        ts = ts.tz_localize("UTC")
    return ts.tz_convert("UTC").strftime("%Y-%m-%dT%H:%M:%SZ")


def _epoch_seconds(value: Any) -> int | None:
    ts = pd.to_datetime(value, utc=True, errors="coerce")
    if pd.isna(ts):
        return None
    return int(pd.Timestamp(ts).timestamp())


def _atomic_write_text(path: Path, text: str, *, attempts: int = 12, initial_sleep_sec: float = 0.05) -> None:
    """Atomically write text with Windows-friendly replace retries.

    On Windows, os.replace/path.replace can transiently fail with WinError 5/32
    when Streamlit, an endpoint reader, antivirus, or another process briefly
    holds the target file.  Chart Engine must not exit on a single transient
    lock while updating closed.jsonl, so use a unique tmp file and bounded
    exponential backoff before surfacing the error.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    suffix = f".tmp.{os.getpid()}.{time.time_ns()}"
    tmp = path.with_name(path.name + suffix)
    tmp.write_text(text, encoding="utf-8")
    last_error: OSError | None = None
    for attempt in range(1, max(1, int(attempts)) + 1):
        try:
            tmp.replace(path)
            return
        except PermissionError as exc:
            last_error = exc
        except OSError as exc:
            winerror = getattr(exc, "winerror", None)
            if winerror not in (5, 32):
                raise
            last_error = exc
        sleep_sec = min(1.0, float(initial_sleep_sec) * (2 ** min(attempt - 1, 5)))
        time.sleep(sleep_sec)
    try:
        tmp.unlink(missing_ok=True)
    except Exception:
        pass
    if last_error is not None:
        raise last_error
    raise RuntimeError(f"atomic write failed without captured error: {path}")


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        item = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    return dict(item) if isinstance(item, Mapping) else {}


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if not path.exists():
        return rows
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            try:
                item = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(item, dict) and item.get("time") is not None:
                rows.append(item)
    return rows


def _write_jsonl(path: Path, rows: Sequence[Mapping[str, Any]]) -> None:
    text = "".join(json.dumps(dict(row), ensure_ascii=False, separators=(",", ":")) + "\n" for row in rows)
    _atomic_write_text(path, text)


def _normalize_candle_record(record: Mapping[str, Any], *, timeframe_sec: int, status: str) -> dict[str, Any] | None:
    time_value = record.get("time")
    if time_value is None and record.get("time_utc") is not None:
        time_value = _epoch_seconds(record.get("time_utc"))
    if time_value is None:
        return None
    try:
        epoch = int(time_value)
        open_v = float(record.get("open"))
        high_v = float(record.get("high"))
        low_v = float(record.get("low"))
        close_v = float(record.get("close"))
    except Exception:
        return None
    ts = pd.Timestamp(epoch, unit="s", tz="UTC")
    return {
        "time": epoch,
        "time_utc": _iso_utc(ts),
        "open": open_v,
        "high": high_v,
        "low": low_v,
        "close": close_v,
        "volume": float(record.get("volume") or 0.0),
        "trade_count": int(record.get("trade_count") or 0),
        "timeframe_sec": int(timeframe_sec),
        "candle_status": status,
        "source_role": "warroom_candle_store",
        "store_version": WARROOM_CANDLE_STORE_VERSION,
    }


def _record_from_ohlc_row(row: Mapping[str, Any], *, timeframe_sec: int, status: str) -> dict[str, Any] | None:
    epoch = _epoch_seconds(row.get("ts"))
    if epoch is None:
        return None
    return _normalize_candle_record(
        {
            "time": epoch,
            "open": row.get("open"),
            "high": row.get("high"),
            "low": row.get("low"),
            "close": row.get("close"),
            "volume": row.get("volume") or 0.0,
            "trade_count": row.get("trade_count") or 0,
        },
        timeframe_sec=timeframe_sec,
        status=status,
    )


def _merge_record(base: Mapping[str, Any] | None, incoming: Mapping[str, Any], *, timeframe_sec: int, status: str) -> dict[str, Any] | None:
    incoming_norm = _normalize_candle_record(incoming, timeframe_sec=timeframe_sec, status=status)
    if incoming_norm is None:
        return None
    if not base:
        return incoming_norm
    base_norm = _normalize_candle_record(base, timeframe_sec=timeframe_sec, status=status)
    if base_norm is None or int(base_norm["time"]) != int(incoming_norm["time"]):
        return incoming_norm
    return {
        **base_norm,
        "high": max(float(base_norm["high"]), float(incoming_norm["high"])),
        "low": min(float(base_norm["low"]), float(incoming_norm["low"])),
        "close": float(incoming_norm["close"]),
        "volume": float(base_norm.get("volume") or 0.0) + float(incoming_norm.get("volume") or 0.0),
        "trade_count": int(base_norm.get("trade_count") or 0) + int(incoming_norm.get("trade_count") or 0),
        "candle_status": status,
    }


def _latest_trade_part(raw_root: Path | None, *, exchange: str, symbol: str, max_days: int = 7) -> tuple[Path | None, dict[str, Any]]:
    trade_root, reason = market_trade_root(raw_root, exchange=exchange, symbol=symbol)
    scanned_days = 0
    scanned_files = 0
    if not trade_root.exists():
        return None, {"ok": False, "error": "market_trade_root_missing", "source_root": str(trade_root), "source_root_reason": reason}
    for date_dir in _date_dirs_desc(trade_root, max_days=max_days):
        scanned_days += 1
        for part in sorted(date_dir.glob("part-*.jsonl"), reverse=True):
            scanned_files += 1
            last = _last_json_record(part)
            ts = _record_event_ts(last or {})
            if ts is None:
                continue
            return part, {
                "ok": True,
                "source_root": str(trade_root),
                "source_root_reason": reason,
                "latest_part_file": str(part),
                "latest_ts_utc": _iso_utc(ts),
                "scanned_day_count": scanned_days,
                "scanned_file_count": scanned_files,
            }
    return None, {"ok": False, "error": "latest_trade_part_not_found", "source_root": str(trade_root), "source_root_reason": reason, "scanned_day_count": scanned_days, "scanned_file_count": scanned_files}


def _read_trade_rows_from_offset(part: Path, *, offset: int, max_bootstrap_bytes: int) -> tuple[list[dict[str, Any]], int, int, bool]:
    size = part.stat().st_size
    effective_offset = max(0, int(offset))
    tail_bootstrap = False
    if effective_offset <= 0 and size > int(max_bootstrap_bytes):
        effective_offset = max(0, size - int(max_bootstrap_bytes))
        tail_bootstrap = True
    rows: list[dict[str, Any]] = []
    lines_read = 0
    with part.open("rb") as handle:
        handle.seek(effective_offset)
        # Discard a partial first line only when we intentionally start from
        # the middle of a large file for tail bootstrap.  A stored byte offset
        # is already positioned at a line boundary, so discarding there would
        # drop the first newly appended trade.
        if tail_bootstrap and effective_offset > 0:
            handle.readline()
        for line in handle:
            lines_read += 1
            record = _json_record_from_line(line)
            if record is None:
                continue
            row = market_trade_record_to_trade_row(record, source_file=str(part))
            if row is not None:
                rows.append(row)
        new_offset = handle.tell()
    return rows, new_offset, lines_read, tail_bootstrap


def _aggregate_trade_rows(rows: list[dict[str, Any]], *, timeframe_sec: int) -> list[dict[str, Any]]:
    if not rows:
        return []
    frame = pd.DataFrame(rows)
    candles = build_trade_ohlc(frame, timeframe_sec=timeframe_sec)
    out: list[dict[str, Any]] = []
    for row in candles.to_dict("records"):
        item = _record_from_ohlc_row(row, timeframe_sec=timeframe_sec, status="forming")
        if item is not None:
            out.append(item)
    return out


def _load_store_timeframe(root: Path | None, *, exchange: str, symbol: str, timeframe_sec: int) -> tuple[list[dict[str, Any]], dict[str, Any] | None, dict[str, Any]]:
    paths = candle_store_paths(root, exchange=exchange, symbol=symbol, timeframe_sec=timeframe_sec)
    closed = [_normalize_candle_record(row, timeframe_sec=timeframe_sec, status="closed") for row in _read_jsonl(paths["closed"])]
    closed_rows = [row for row in closed if row is not None]
    forming_raw = _read_json(paths["forming"])
    forming = _normalize_candle_record(forming_raw, timeframe_sec=timeframe_sec, status="forming") if forming_raw else None
    meta = _read_json(paths["meta"])
    return closed_rows, forming, meta


def _write_store_timeframe(
    root: Path | None,
    *,
    exchange: str,
    symbol: str,
    timeframe_sec: int,
    closed_rows: list[dict[str, Any]],
    forming: dict[str, Any] | None,
    retention_days: int,
    source_meta: Mapping[str, Any],
    update_meta: Mapping[str, Any],
) -> dict[str, Any]:
    paths = candle_store_paths(root, exchange=exchange, symbol=symbol, timeframe_sec=timeframe_sec)
    ordered_closed = sorted((row for row in closed_rows if row is not None), key=lambda row: int(row["time"]))
    if forming is not None:
        forming = _normalize_candle_record(forming, timeframe_sec=timeframe_sec, status="forming")
    latest_ts = None
    if forming is not None:
        latest_ts = pd.Timestamp(int(forming["time"]), unit="s", tz="UTC")
    elif ordered_closed:
        latest_ts = pd.Timestamp(int(ordered_closed[-1]["time"]), unit="s", tz="UTC")
    if latest_ts is not None:
        cutoff = latest_ts - pd.Timedelta(days=max(1, int(retention_days)))
        ordered_closed = [row for row in ordered_closed if pd.Timestamp(int(row["time"]), unit="s", tz="UTC") >= cutoff]
    for index, row in enumerate(ordered_closed):
        row["candle_index"] = index
        row["candle_status"] = "closed"
    if forming is not None:
        forming["candle_index"] = len(ordered_closed)
        forming["candle_status"] = "forming"
    _write_jsonl(paths["closed"], ordered_closed)
    _atomic_write_text(paths["forming"], json.dumps(forming or {}, ensure_ascii=False, indent=2) + "\n")
    first_ts = ordered_closed[0]["time_utc"] if ordered_closed else (forming or {}).get("time_utc", "")
    last_ts = (forming or {}).get("time_utc") or (ordered_closed[-1]["time_utc"] if ordered_closed else "")
    meta = {
        "ok": bool(ordered_closed or forming),
        "version": WARROOM_CANDLE_STORE_VERSION,
        "store_role": "rolling_closed_forming_candle_store",
        "exchange": exchange,
        "symbol": symbol,
        "timeframe_sec": int(timeframe_sec),
        "retention_days": int(retention_days),
        "closed_path": str(paths["closed"]),
        "forming_path": str(paths["forming"]),
        "meta_path": str(paths["meta"]),
        "start_ts_utc": first_ts,
        "end_ts_utc": last_ts,
        "closed_count": len(ordered_closed),
        "forming_present": bool(forming),
        "candle_count": len(ordered_closed) + (1 if forming else 0),
        "gap_policy": "absent_candles_no_synthetic_null",
        "missing_periods_error": False,
        "closed_candles_append_stable": True,
        "forming_candle_mutable": True,
        "source_meta": dict(source_meta),
        "update_meta": dict(update_meta),
        "read_only_source": True,
        "derived_cache_write_only": True,
        "broker_send_enabled": False,
        "order_intent_submitted": False,
        "prediction_invoked": False,
        "classifier_invoked": False,
    }
    _atomic_write_text(paths["meta"], json.dumps(meta, ensure_ascii=False, indent=2) + "\n")
    return meta



def _trade_parts_asc(raw_root: Path | None, *, exchange: str, symbol: str, max_days: int) -> tuple[list[Path], dict[str, Any]]:
    trade_root, reason = market_trade_root(raw_root, exchange=exchange, symbol=symbol)
    if not trade_root.exists():
        return [], {"ok": False, "error": "market_trade_root_missing", "source_root": str(trade_root), "source_root_reason": reason}
    date_dirs = list(_date_dirs_desc(trade_root, max_days=max_days))
    parts: list[Path] = []
    for date_dir in sorted(date_dirs, key=lambda item: item.name):
        parts.extend(sorted(date_dir.glob("part-*.jsonl")))
    if not parts:
        return [], {"ok": False, "error": "trade_parts_not_found", "source_root": str(trade_root), "source_root_reason": reason, "scanned_day_count": len(date_dirs)}
    first = _first_json_record(parts[0])
    last = _last_json_record(parts[-1])
    first_ts = _record_event_ts(first or {})
    last_ts = _record_event_ts(last or {})
    return parts, {
        "ok": True,
        "source_root": str(trade_root),
        "source_root_reason": reason,
        "first_part_file": str(parts[0]),
        "latest_part_file": str(parts[-1]),
        "first_ts_utc": _iso_utc(first_ts) if first_ts is not None else "",
        "latest_ts_utc": _iso_utc(last_ts) if last_ts is not None else "",
        "scanned_day_count": len(date_dirs),
        "scanned_file_count": len(parts),
    }




def _trade_parts_asc_from_roots(raw_roots: Sequence[Path | str | None], *, exchange: str, symbol: str, max_days: int) -> tuple[list[Path], dict[str, Any]]:
    """Return ascending trade parts from multiple roots, preferring later roots for duplicate date partitions.

    This is used for cold archive + hot live rebuilds.  If E:\btc_ts and
    D:\btc_ts_hot both contain the same date=YYYY-MM-DD partition, the later
    root in raw_roots wins for that whole date.  The expected call order is
    cold first, hot last, so the final update_state adopts the D-hot latest
    part and live append can continue from update_state.source_part_file +
    byte_offset without replaying D-hot from byte 0.
    """
    selected_by_date: dict[str, tuple[int, Path, list[Path]]] = {}
    root_summaries: list[dict[str, Any]] = []
    replaced_dates: list[dict[str, Any]] = []

    for root_index, root in enumerate(raw_roots):
        trade_root, reason = market_trade_root(Path(root) if root is not None else None, exchange=exchange, symbol=symbol)
        summary = {
            "root_index": root_index,
            "raw_root": str(root) if root is not None else "default",
            "source_root": str(trade_root),
            "source_root_reason": reason,
            "exists": trade_root.exists(),
            "date_count": 0,
            "part_count": 0,
        }
        if not trade_root.exists():
            summary["error"] = "market_trade_root_missing"
            root_summaries.append(summary)
            continue

        date_dirs = sorted(list(_date_dirs_desc(trade_root, max_days=max_days)), key=lambda item: item.name)
        summary["date_count"] = len(date_dirs)
        for date_dir in date_dirs:
            date_label = date_dir.name.removeprefix("date=")
            parts = sorted(date_dir.glob("part-*.jsonl"))
            if not parts:
                continue
            summary["part_count"] += len(parts)
            previous = selected_by_date.get(date_label)
            if previous is not None:
                replaced_dates.append(
                    {
                        "date": date_label,
                        "previous_root_index": previous[0],
                        "previous_source_root": str(previous[1]),
                        "selected_root_index": root_index,
                        "selected_source_root": str(trade_root),
                        "policy": "later_root_replaces_entire_date_partition",
                    }
                )
            selected_by_date[date_label] = (root_index, trade_root, parts)
        root_summaries.append(summary)

    selected_dates = sorted(selected_by_date)[-max(1, int(max_days)) :]
    parts: list[Path] = []
    selected_partition_rows: list[dict[str, Any]] = []
    for date_label in selected_dates:
        root_index, trade_root, date_parts = selected_by_date[date_label]
        parts.extend(date_parts)
        selected_partition_rows.append(
            {
                "date": date_label,
                "root_index": root_index,
                "source_root": str(trade_root),
                "part_count": len(date_parts),
                "first_part_file": str(date_parts[0]),
                "last_part_file": str(date_parts[-1]),
            }
        )

    if not parts:
        return [], {
            "ok": False,
            "error": "trade_parts_not_found",
            "source_root_order": root_summaries,
            "selected_root_policy": "later_roots_replace_earlier_roots_by_date_partition",
            "selected_day_count": 0,
            "selected_file_count": 0,
        }

    first = _first_json_record(parts[0])
    last = _last_json_record(parts[-1])
    first_ts = _record_event_ts(first or {})
    last_ts = _record_event_ts(last or {})
    latest_root_index = selected_partition_rows[-1]["root_index"] if selected_partition_rows else None
    return parts, {
        "ok": True,
        "source_root_order": root_summaries,
        "selected_root_policy": "later_roots_replace_earlier_roots_by_date_partition",
        "selected_day_count": len(selected_dates),
        "selected_file_count": len(parts),
        "selected_partitions": selected_partition_rows,
        "replaced_date_partitions": replaced_dates,
        "latest_root_index": latest_root_index,
        "first_part_file": str(parts[0]),
        "latest_part_file": str(parts[-1]),
        "first_ts_utc": _iso_utc(first_ts) if first_ts is not None else "",
        "latest_ts_utc": _iso_utc(last_ts) if last_ts is not None else "",
        "hot_append_adoption_policy": "when D-hot is listed last and owns latest date, update_state adopts D-hot source_part_file+byte_offset",
    }



def _fast_epoch_seconds(value: Any) -> int | None:
    """Fast UTC epoch parser for collector ISO timestamps used by market.trade.

    Collector timestamps are normally ISO-8601 UTC strings such as
    2026-06-25T23:59:59.8139216Z.  pandas.to_datetime is intentionally avoided
    here because the 92-day historical rebuild may parse millions of rows.
    """
    if value in (None, ""):
        return None
    if hasattr(value, "timestamp"):
        try:
            return int(value.timestamp())
        except Exception:
            return None
    if isinstance(value, (int, float)):
        raw = float(value)
        if raw > 10_000_000_000:
            raw = raw / 1000.0
        return int(raw)
    if not isinstance(value, str):
        return None
    item = value.strip()
    if not item:
        return None
    if item.endswith("Z"):
        item = item[:-1]
    if "+" in item or item.endswith("+00:00"):
        try:
            return int(datetime.fromisoformat(item.replace("Z", "+00:00")).timestamp())
        except Exception:
            return None
    if "." in item:
        head, frac = item.split(".", 1)
        frac = "".join(ch for ch in frac if ch.isdigit())[:6]
        item = head + ("." + frac if frac else "")
    try:
        return int(datetime.fromisoformat(item).replace(tzinfo=timezone.utc).timestamp())
    except Exception:
        return None


def _fast_trade_values(record: Mapping[str, Any]) -> tuple[int, float, float, str] | None:
    payload = record.get("payload") if isinstance(record.get("payload"), Mapping) else {}
    ts_value = (
        _first_present(record, ("event_ts", "exchange_ts", "ingest_ts", "collector_ts", "ts", "timestamp"))
        or _first_present(payload, ("trade_ts", "event_ts", "timestamp", "ts"))
    )
    epoch = _fast_epoch_seconds(ts_value)
    price = _first_present(payload, ("price", "last_price")) or _first_present(record, ("price", "last_price"))
    size = _first_present(payload, ("size", "volume")) or _first_present(record, ("size", "volume")) or 0.0
    trade_id = _first_present(payload, ("trade_id", "id")) or _first_present(record, ("source_event_id", "record_id")) or ""
    if epoch is None or price in (None, ""):
        return None
    try:
        price_v = float(price)
        size_v = float(size or 0.0)
    except Exception:
        return None
    return epoch, price_v, size_v, str(trade_id or "")


def _merge_fast_trade_into_timeframes(
    records_by_timeframe: dict[int, dict[int, dict[str, Any]]],
    *,
    epoch: int,
    price: float,
    size: float,
    timeframes_sec: Sequence[int],
) -> None:
    for timeframe in tuple(int(item) for item in timeframes_sec):
        bucket = int(epoch) - (int(epoch) % timeframe)
        records_by_time = records_by_timeframe.setdefault(timeframe, {})
        record = records_by_time.get(bucket)
        if record is None:
            records_by_time[bucket] = {
                "time": bucket,
                "open": float(price),
                "high": float(price),
                "low": float(price),
                "close": float(price),
                "volume": float(size or 0.0),
                "trade_count": 1,
                "timeframe_sec": timeframe,
                "candle_status": "forming",
                "source_role": "warroom_candle_store",
                "store_version": WARROOM_CANDLE_STORE_VERSION,
            }
            continue
        record["high"] = max(float(record.get("high") or price), float(price))
        record["low"] = min(float(record.get("low") or price), float(price))
        record["close"] = float(price)
        record["volume"] = float(record.get("volume") or 0.0) + float(size or 0.0)
        record["trade_count"] = int(record.get("trade_count") or 0) + 1


def _rebuild_progress_path(store_root: Path | None) -> Path:
    return _root(store_root) / "state" / "warroom_candle_rebuild" / "progress.json"


def _write_rebuild_progress(store_root: Path | None, payload: Mapping[str, Any]) -> None:
    progress = {
        "ok": True,
        "version": WARROOM_CANDLE_STORE_VERSION,
        "role": "warroom_candle_store_history_rebuild_progress",
        **dict(payload),
        "read_only_source": True,
        "broker_send_enabled": False,
        "prediction_invoked": False,
        "classifier_invoked": False,
    }
    _atomic_write_text(_rebuild_progress_path(store_root), json.dumps(progress, ensure_ascii=False, indent=2) + "\n")

def _merge_rows_into_timeframes(records_by_timeframe: dict[int, dict[int, dict[str, Any]]], rows: list[dict[str, Any]], *, timeframes_sec: Sequence[int]) -> None:
    if not rows:
        return
    for timeframe in tuple(int(item) for item in timeframes_sec):
        records_by_time = records_by_timeframe.setdefault(timeframe, {})
        for record in _aggregate_trade_rows(rows, timeframe_sec=timeframe):
            key = int(record["time"])
            merged = _merge_record(records_by_time.get(key), record, timeframe_sec=timeframe, status="forming")
            if merged is not None:
                records_by_time[key] = merged


def rebuild_candle_store_from_trade_history(
    *,
    raw_root: Path | None = None,
    raw_roots: Sequence[Path | str | None] | None = None,
    store_root: Path | None = None,
    exchange: str = DEFAULT_EXCHANGE,
    symbol: str = DEFAULT_SYMBOL,
    timeframes_sec: Sequence[int] = DEFAULT_TIMEFRAMES_SEC,
    retention_days: int = DEFAULT_RETENTION_DAYS,
    max_days: int = DEFAULT_RETENTION_DAYS,
    chunk_rows: int = 200_000,
) -> dict[str, Any]:
    """Rebuild the rolling candle store from historical trade parts and adopt the latest source offset.

    This is the initial/backfill path for the WarRoom Chart Engine.  It reads
    historical market.trade parts in ascending order, writes only derived candle
    cache files, and finally sets update_state.source_part_file + byte_offset to
    the end of the latest processed part so live append resumes without
    reaggregating already processed trades.
    """
    history_roots: tuple[Path | str | None, ...]
    if raw_roots:
        history_roots = tuple(raw_roots)
    else:
        history_roots = (raw_root,)
    parts, source_meta = _trade_parts_asc_from_roots(history_roots, exchange=exchange, symbol=symbol, max_days=max_days)
    if not parts:
        return {"ok": False, "version": WARROOM_CANDLE_STORE_VERSION, "error": source_meta.get("error") or "trade_parts_missing", "source_meta": source_meta, "read_only_source": True, "broker_send_enabled": False, "order_intent_submitted": False, "prediction_invoked": False, "classifier_invoked": False}

    selected_timeframes = tuple(int(item) for item in timeframes_sec)
    records_by_timeframe: dict[int, dict[int, dict[str, Any]]] = {timeframe: {} for timeframe in selected_timeframes}
    total_lines = 0
    total_trade_rows = 0
    first_trade_ts: str | None = None
    latest_trade_ts: str | None = None
    latest_offset = 0
    chunk_limit = max(1, int(chunk_rows))

    total_input_bytes = sum(part.stat().st_size for part in parts)
    processed_bytes = 0
    seen_trade_ids: set[str] = set()
    current_dedupe_date = ""
    duplicate_trade_rows = 0
    dedupe_scope = "date_partition_trade_id"
    _write_rebuild_progress(
        store_root,
        {
            "phase": "started",
            "part_index": 0,
            "part_count": len(parts),
            "total_input_bytes": total_input_bytes,
            "processed_bytes": 0,
            "lines_read": 0,
            "trade_rows_read": 0,
            "duplicate_trade_rows": 0,
            "source_part_file": str(parts[0]),
        },
    )
    print(f"[PROGRESS] history rebuild start parts={len(parts)} bytes={total_input_bytes}", flush=True)

    for part_index, part in enumerate(parts, start=1):
        part_size = part.stat().st_size
        part_date = part.parent.name.removeprefix("date=")
        if part_date != current_dedupe_date:
            seen_trade_ids = set()
            current_dedupe_date = part_date
        part_lines = 0
        part_trade_rows = 0
        print(f"[PROGRESS] part {part_index}/{len(parts)} start bytes={part_size} path={part}", flush=True)
        _write_rebuild_progress(
            store_root,
            {
                "phase": "reading",
                "part_index": part_index,
                "part_count": len(parts),
                "source_part_file": str(part),
                "part_bytes": part_size,
                "total_input_bytes": total_input_bytes,
                "processed_bytes": processed_bytes,
                "lines_read": total_lines,
                "trade_rows_read": total_trade_rows,
        "duplicate_trade_rows": duplicate_trade_rows,
            "dedupe_scope": dedupe_scope,
        "aggregation_mode": "streaming_fast_ohlc_no_pandas_dataframe",
        "dedupe_scope": dedupe_scope,
                "duplicate_trade_rows": duplicate_trade_rows,
                "latest_source_ts_utc": latest_trade_ts or "",
            },
        )
        with part.open("rb") as handle:
            for line in handle:
                total_lines += 1
                part_lines += 1
                record = _json_record_from_line(line)
                if record is None:
                    continue
                values = _fast_trade_values(record)
                if values is None:
                    continue
                epoch, price, size, trade_id = values
                if trade_id:
                    if trade_id in seen_trade_ids:
                        duplicate_trade_rows += 1
                        continue
                    seen_trade_ids.add(trade_id)
                total_trade_rows += 1
                part_trade_rows += 1
                ts_text = _iso_utc(pd.Timestamp(epoch, unit="s", tz="UTC"))
                if first_trade_ts is None:
                    first_trade_ts = ts_text
                latest_trade_ts = ts_text
                _merge_fast_trade_into_timeframes(
                    records_by_timeframe,
                    epoch=epoch,
                    price=price,
                    size=size,
                    timeframes_sec=selected_timeframes,
                )
                if total_trade_rows % chunk_limit == 0:
                    latest_offset = handle.tell()
                    current_processed = processed_bytes + latest_offset
                    pct = (current_processed / total_input_bytes * 100.0) if total_input_bytes else 0.0
                    print(
                        f"[PROGRESS] {pct:.2f}% part={part_index}/{len(parts)} rows={total_trade_rows} dup={duplicate_trade_rows} latest={latest_trade_ts}",
                        flush=True,
                    )
                    _write_rebuild_progress(
                        store_root,
                        {
                            "phase": "reading",
                            "part_index": part_index,
                            "part_count": len(parts),
                            "source_part_file": str(part),
                            "part_offset": latest_offset,
                            "part_bytes": part_size,
                            "total_input_bytes": total_input_bytes,
                            "processed_bytes": current_processed,
                            "progress_pct": pct,
                            "lines_read": total_lines,
                            "trade_rows_read": total_trade_rows,
                            "duplicate_trade_rows": duplicate_trade_rows,
                            "latest_source_ts_utc": latest_trade_ts or "",
                        },
                    )
            latest_offset = handle.tell()
        processed_bytes += part_size
        pct = (processed_bytes / total_input_bytes * 100.0) if total_input_bytes else 0.0
        print(
            f"[PROGRESS] part {part_index}/{len(parts)} done pct={pct:.2f}% lines={part_lines} rows={part_trade_rows} total_rows={total_trade_rows}",
            flush=True,
        )
        _write_rebuild_progress(
            store_root,
            {
                "phase": "part_completed",
                "part_index": part_index,
                "part_count": len(parts),
                "source_part_file": str(part),
                "part_offset": latest_offset,
                "part_bytes": part_size,
                "total_input_bytes": total_input_bytes,
                "processed_bytes": processed_bytes,
                "progress_pct": pct,
                "lines_read": total_lines,
                "trade_rows_read": total_trade_rows,
                "duplicate_trade_rows": duplicate_trade_rows,
                "latest_source_ts_utc": latest_trade_ts or "",
            },
        )

    _write_rebuild_progress(
        store_root,
        {
            "phase": "writing_store",
            "part_index": len(parts),
            "part_count": len(parts),
            "source_part_file": str(parts[-1]),
            "part_offset": latest_offset,
            "total_input_bytes": total_input_bytes,
            "processed_bytes": processed_bytes,
            "progress_pct": 100.0,
            "lines_read": total_lines,
            "trade_rows_read": total_trade_rows,
            "duplicate_trade_rows": duplicate_trade_rows,
            "latest_source_ts_utc": latest_trade_ts or "",
        },
    )

    update_meta = {
        "source_part_file": str(parts[-1]),
        "previous_part_file": "",
        "previous_offset": 0,
        "new_offset": latest_offset,
        "lines_read": total_lines,
        "trade_rows_read": total_trade_rows,
        "tail_bootstrap": False,
        "history_rebuild": True,
        "history_part_count": len(parts),
        "history_max_days": int(max_days),
        "chunk_rows": chunk_limit,
        "retention_days": int(retention_days),
        "gap_policy": "absent_candles_no_synthetic_null",
        "append_boundary": "update_state.source_part_file+byte_offset",
        "duplicate_policy": "resume_from_update_state_no_reaggregate_processed_trades",
    }

    timeframe_metas: dict[str, Any] = {}
    for timeframe in selected_timeframes:
        records_by_time = records_by_timeframe.get(timeframe, {})
        ordered_keys = sorted(records_by_time)
        latest_key = ordered_keys[-1] if ordered_keys else None
        closed_rows: list[dict[str, Any]] = []
        forming: dict[str, Any] | None = None
        for key in ordered_keys:
            row = records_by_time[key]
            if latest_key is not None and key == latest_key:
                forming = _normalize_candle_record(row, timeframe_sec=timeframe, status="forming")
            else:
                closed = _normalize_candle_record(row, timeframe_sec=timeframe, status="closed")
                if closed is not None:
                    closed_rows.append(closed)
        timeframe_metas[str(timeframe)] = _write_store_timeframe(
            store_root,
            exchange=exchange,
            symbol=symbol,
            timeframe_sec=timeframe,
            closed_rows=closed_rows,
            forming=forming,
            retention_days=retention_days,
            source_meta=source_meta,
            update_meta=update_meta,
        )

    state_path = candle_symbol_store_dir(store_root, exchange=exchange, symbol=symbol) / STATE_NAME
    state_payload = {
        "ok": True,
        "version": WARROOM_CANDLE_STORE_VERSION,
        "source_part_file": str(parts[-1]),
        "byte_offset": latest_offset,
        "latest_source_ts_utc": latest_trade_ts or source_meta.get("latest_ts_utc"),
        "first_source_ts_utc": first_trade_ts or source_meta.get("first_ts_utc"),
        "timeframes_sec": [int(item) for item in selected_timeframes],
        "retention_days": int(retention_days),
        "gap_policy": "absent_candles_no_synthetic_null",
        "updated_rows": total_trade_rows,
        "duplicate_trade_rows": duplicate_trade_rows,
        "aggregation_mode": "streaming_fast_ohlc_no_pandas_dataframe",
        "history_rebuild": True,
        "history_part_count": len(parts),
        "history_max_days": int(max_days),
        "append_boundary": "update_state.source_part_file+byte_offset",
        "duplicate_policy": "resume_from_update_state_no_reaggregate_processed_trades",
        "read_only_source": True,
        "broker_send_enabled": False,
        "order_intent_submitted": False,
        "prediction_invoked": False,
        "classifier_invoked": False,
    }
    _atomic_write_text(state_path, json.dumps(state_payload, ensure_ascii=False, indent=2) + "\n")
    _write_rebuild_progress(
        store_root,
        {
            "phase": "completed",
            "part_index": len(parts),
            "part_count": len(parts),
            "source_part_file": str(parts[-1]),
            "part_offset": latest_offset,
            "total_input_bytes": total_input_bytes,
            "processed_bytes": processed_bytes,
            "progress_pct": 100.0,
            "lines_read": total_lines,
            "trade_rows_read": total_trade_rows,
            "duplicate_trade_rows": duplicate_trade_rows,
            "latest_source_ts_utc": latest_trade_ts or "",
            "state_path": str(state_path),
        },
    )
    print(f"[PROGRESS] history rebuild completed rows={total_trade_rows} dup={duplicate_trade_rows} state={state_path}", flush=True)
    return {
        "ok": True,
        "version": WARROOM_CANDLE_STORE_VERSION,
        "store_root": str(candle_symbol_store_dir(store_root, exchange=exchange, symbol=symbol)),
        "source_meta": source_meta,
        "update_meta": update_meta,
        "state_path": str(state_path),
        "progress_path": str(_rebuild_progress_path(store_root)),
        "timeframes": timeframe_metas,
        "gap_policy": "absent_candles_no_synthetic_null",
        "read_only_source": True,
        "derived_cache_write_only": True,
        "broker_send_enabled": False,
        "order_intent_submitted": False,
        "prediction_invoked": False,
        "classifier_invoked": False,
    }



def _history_lineage_from_state(state: Mapping[str, Any], *, progress: Mapping[str, Any] | None = None, first_candle_ts_utc: str = "") -> dict[str, Any]:
    """Return stable historical rebuild lineage that should survive live append state rewrites."""
    lineage: dict[str, Any] = {
        "append_boundary": "update_state.source_part_file+byte_offset",
        "duplicate_policy": "resume_from_update_state_no_reaggregate_processed_trades",
    }
    if state.get("history_rebuild") is True:
        lineage.update(
            {
                "previous_history_rebuild": True,
                "previous_history_source_part_file": state.get("source_part_file") or "",
                "previous_history_byte_offset": int(state.get("byte_offset") or 0),
                "previous_history_first_source_ts_utc": state.get("first_source_ts_utc") or "",
                "previous_history_latest_source_ts_utc": state.get("latest_source_ts_utc") or "",
                "previous_history_part_count": int(state.get("history_part_count") or 0),
                "previous_history_max_days": int(state.get("history_max_days") or 0),
            }
        )
    else:
        for key in (
            "previous_history_rebuild",
            "previous_history_source_part_file",
            "previous_history_byte_offset",
            "previous_history_first_source_ts_utc",
            "previous_history_latest_source_ts_utc",
            "previous_history_part_count",
            "previous_history_max_days",
        ):
            if key in state:
                lineage[key] = state.get(key)
    progress_payload = dict(progress or {})
    if lineage.get("previous_history_rebuild") is not True and progress_payload.get("phase") == "completed":
        lineage.update(
            {
                "previous_history_rebuild": True,
                "previous_history_source_part_file": progress_payload.get("source_part_file") or "",
                "previous_history_byte_offset": int(progress_payload.get("part_offset") or 0),
                "previous_history_first_source_ts_utc": first_candle_ts_utc or progress_payload.get("first_source_ts_utc") or "",
                "previous_history_latest_source_ts_utc": progress_payload.get("latest_source_ts_utc") or "",
                "previous_history_part_count": int(progress_payload.get("part_count") or 0),
                "previous_history_max_days": int(progress_payload.get("history_max_days") or 0),
                "previous_history_recovered_from": "warroom_candle_rebuild_progress_json",
            }
        )
    return lineage

# WARROOM_CANDLE_ROLLOVER_CONTIGUOUS_PARTS_2026_07_10
def _path_identity(value: Path | str) -> str:
    return os.path.normcase(os.path.normpath(str(value)))


def _pending_live_trade_parts(
    raw_root: Path | None,
    *,
    exchange: str,
    symbol: str,
    max_days: int,
    state: Mapping[str, Any],
) -> tuple[list[Path], dict[str, Any], int, dict[str, Any] | None]:
    """Select every trade part from the stored part/offset through the latest part.

    A live state without a source part keeps the legacy tail-bootstrap behavior
    and starts from only the latest part.  Once a source part is recorded, that
    exact part must still be present in the bounded scan; otherwise fail closed
    rather than silently skipping intermediate parts.
    """

    parts, source_meta = _trade_parts_asc(
        raw_root,
        exchange=exchange,
        symbol=symbol,
        max_days=max_days,
    )
    if not parts:
        return [], source_meta, 0, {
            "error": source_meta.get("error") or "trade_parts_missing",
            "source_meta": source_meta,
        }

    previous_part = str(state.get("source_part_file") or "")
    if not previous_part:
        return [parts[-1]], source_meta, 0, None

    by_identity = {_path_identity(part): index for index, part in enumerate(parts)}
    previous_identity = _path_identity(previous_part)
    previous_index = by_identity.get(previous_identity)
    if previous_index is None:
        return [], source_meta, 0, {
            "error": "state_source_part_not_found_in_scan",
            "state_source_part_file": previous_part,
            "scan_first_part_file": str(parts[0]),
            "scan_latest_part_file": str(parts[-1]),
            "max_days": int(max_days),
            "recovery": "run_explicit_history_rebuild_or_expand_max_days",
            "source_meta": source_meta,
        }

    previous_offset = int(state.get("byte_offset") or 0)
    previous_size = parts[previous_index].stat().st_size
    if previous_offset < 0 or previous_offset > previous_size:
        return [], source_meta, 0, {
            "error": "state_byte_offset_out_of_range",
            "state_source_part_file": previous_part,
            "state_byte_offset": previous_offset,
            "source_part_size": previous_size,
            "recovery": "run_explicit_history_rebuild",
            "source_meta": source_meta,
        }

    return parts[previous_index:], source_meta, previous_offset, None


def update_candle_store_from_latest_part(
    *,
    raw_root: Path | None = None,
    store_root: Path | None = None,
    exchange: str = DEFAULT_EXCHANGE,
    symbol: str = DEFAULT_SYMBOL,
    timeframes_sec: Sequence[int] = DEFAULT_TIMEFRAMES_SEC,
    retention_days: int = DEFAULT_RETENTION_DAYS,
    max_days: int = 7,
    max_bootstrap_bytes: int = DEFAULT_BOOTSTRAP_MAX_BYTES,
) -> dict[str, Any]:
    state_path = candle_symbol_store_dir(store_root, exchange=exchange, symbol=symbol) / STATE_NAME
    state = _read_json(state_path)
    pending_parts, source_meta, first_offset, selection_error = _pending_live_trade_parts(
        raw_root,
        exchange=exchange,
        symbol=symbol,
        max_days=max_days,
        state=state,
    )
    if selection_error is not None:
        return {
            "ok": False,
            "version": WARROOM_CANDLE_STORE_VERSION,
            **selection_error,
            "read_only_source": True,
            "broker_send_enabled": False,
            "order_intent_submitted": False,
            "prediction_invoked": False,
            "classifier_invoked": False,
        }

    previous_part = str(state.get("source_part_file") or "")
    selected_timeframes = tuple(int(item) for item in timeframes_sec)
    lineage_first_timeframe = selected_timeframes[0] if selected_timeframes else DEFAULT_TIMEFRAME_SECONDS
    lineage_meta_path = candle_store_paths(
        store_root,
        exchange=exchange,
        symbol=symbol,
        timeframe_sec=lineage_first_timeframe,
    )["meta"]
    lineage_timeframe_meta = _read_json(lineage_meta_path)
    lineage_meta = _history_lineage_from_state(
        state,
        progress=_read_json(_rebuild_progress_path(store_root)),
        first_candle_ts_utc=str(lineage_timeframe_meta.get("start_ts_utc") or ""),
    )

    records_by_timeframe: dict[int, dict[int, dict[str, Any]]] = {}
    for timeframe in selected_timeframes:
        closed, forming, _meta = _load_store_timeframe(
            store_root,
            exchange=exchange,
            symbol=symbol,
            timeframe_sec=timeframe,
        )
        records_by_time = {int(row["time"]): row for row in closed}
        if forming is not None:
            records_by_time[int(forming["time"])] = forming
        records_by_timeframe[timeframe] = records_by_time

    total_lines_read = 0
    total_trade_rows = 0
    tail_bootstrap_any = False
    final_offset = first_offset
    first_processed_part = str(pending_parts[0])
    latest_processed_part = str(pending_parts[-1])

    for part_index, part in enumerate(pending_parts):
        offset = first_offset if part_index == 0 else 0
        rows, new_offset, lines_read, tail_bootstrap = _read_trade_rows_from_offset(
            part,
            offset=offset,
            max_bootstrap_bytes=max_bootstrap_bytes,
        )
        total_lines_read += lines_read
        total_trade_rows += len(rows)
        tail_bootstrap_any = tail_bootstrap_any or tail_bootstrap
        final_offset = new_offset

        for timeframe in selected_timeframes:
            records_by_time = records_by_timeframe[timeframe]
            for record in _aggregate_trade_rows(rows, timeframe_sec=timeframe):
                key = int(record["time"])
                merged = _merge_record(
                    records_by_time.get(key),
                    record,
                    timeframe_sec=timeframe,
                    status="forming",
                )
                if merged is not None:
                    records_by_time[key] = merged

    update_meta = {
        "source_part_file": latest_processed_part,
        "previous_part_file": previous_part,
        "previous_offset": first_offset,
        "new_offset": final_offset,
        "lines_read": total_lines_read,
        "trade_rows_read": total_trade_rows,
        "tail_bootstrap": tail_bootstrap_any,
        "processed_part_count": len(pending_parts),
        "processed_part_first_file": first_processed_part,
        "processed_part_latest_file": latest_processed_part,
        "part_rollover_count": max(len(pending_parts) - 1, 0),
        "contiguous_part_rollover": True,
        "retention_days": int(retention_days),
        "gap_policy": "absent_candles_no_synthetic_null",
        **lineage_meta,
    }

    timeframe_metas: dict[str, Any] = {}
    for timeframe in selected_timeframes:
        records_by_time = records_by_timeframe[timeframe]
        ordered_keys = sorted(records_by_time)
        latest_key = ordered_keys[-1] if ordered_keys else None
        next_closed: list[dict[str, Any]] = []
        next_forming: dict[str, Any] | None = None
        for key in ordered_keys:
            row = records_by_time[key]
            if latest_key is not None and key == latest_key:
                next_forming = _normalize_candle_record(
                    row,
                    timeframe_sec=timeframe,
                    status="forming",
                )
            else:
                closed_row = _normalize_candle_record(
                    row,
                    timeframe_sec=timeframe,
                    status="closed",
                )
                if closed_row is not None:
                    next_closed.append(closed_row)
        timeframe_metas[str(timeframe)] = _write_store_timeframe(
            store_root,
            exchange=exchange,
            symbol=symbol,
            timeframe_sec=timeframe,
            closed_rows=next_closed,
            forming=next_forming,
            retention_days=retention_days,
            source_meta=source_meta,
            update_meta=update_meta,
        )

    state_payload = {
        "ok": True,
        "version": WARROOM_CANDLE_STORE_VERSION,
        "source_part_file": latest_processed_part,
        "byte_offset": final_offset,
        "latest_source_ts_utc": source_meta.get("latest_ts_utc"),
        "timeframes_sec": [int(item) for item in selected_timeframes],
        "retention_days": int(retention_days),
        "gap_policy": "absent_candles_no_synthetic_null",
        "updated_rows": total_trade_rows,
        "processed_part_count": len(pending_parts),
        "part_rollover_count": max(len(pending_parts) - 1, 0),
        "contiguous_part_rollover": True,
        **lineage_meta,
        "read_only_source": True,
        "broker_send_enabled": False,
        "order_intent_submitted": False,
        "prediction_invoked": False,
        "classifier_invoked": False,
    }
    _atomic_write_text(state_path, json.dumps(state_payload, ensure_ascii=False, indent=2) + "\n")
    return {
        "ok": True,
        "version": WARROOM_CANDLE_STORE_VERSION,
        "store_root": str(candle_symbol_store_dir(store_root, exchange=exchange, symbol=symbol)),
        "source_meta": source_meta,
        "update_meta": update_meta,
        "state_path": str(state_path),
        "timeframes": timeframe_metas,
        "gap_policy": "absent_candles_no_synthetic_null",
        "read_only_source": True,
        "derived_cache_write_only": True,
        "broker_send_enabled": False,
        "order_intent_submitted": False,
        "prediction_invoked": False,
        "classifier_invoked": False,
    }


def read_candle_store_chart_payload(
    *,
    store_root: Path | None = None,
    exchange: str = DEFAULT_EXCHANGE,
    symbol: str = DEFAULT_SYMBOL,
    timeframe_sec: int = DEFAULT_TIMEFRAME_SECONDS,
    max_candles: int = DEFAULT_MAX_CANDLES,
) -> dict[str, Any]:
    paths = candle_store_paths(store_root, exchange=exchange, symbol=symbol, timeframe_sec=timeframe_sec)
    closed, forming, meta = _load_store_timeframe(store_root, exchange=exchange, symbol=symbol, timeframe_sec=timeframe_sec)
    rows = sorted(closed, key=lambda row: int(row["time"]))
    if forming is not None and (not rows or int(forming["time"]) >= int(rows[-1]["time"])):
        rows.append(forming)
    rows = rows[-max(0, int(max_candles)) :]
    for index, row in enumerate(rows):
        row["candle_index"] = index
        if index < len(rows) - 1:
            row["candle_status"] = "closed"
    return {
        "ok": bool(rows),
        "version": WARROOM_CANDLE_STORE_VERSION,
        "server_role": "read_only_chart_engine_data_endpoint",
        "endpoint_family": "warroom_candle_store_latest",
        "exchange": exchange,
        "symbol": symbol,
        "timeframe_sec": int(timeframe_sec),
        "candles": rows,
        "candle_count": len(rows),
        "meta": {
            **dict(meta),
            "store_path": str(paths["dir"]),
            "server_poll_ok": bool(rows),
            "gap_policy": "absent_candles_no_synthetic_null",
            "missing_periods_error": False,
            "server_source": "warroom_candle_store",
        },
        "gap_policy": "absent_candles_no_synthetic_null",
        "read_only": True,
        "broker_send_enabled": False,
        "order_intent_submitted": False,
        "ledger_append_allowed": False,
        "prediction_invoked": False,
        "classifier_invoked": False,
    }


def _parse_timeframes(value: str | None) -> tuple[int, ...]:
    if not value:
        return DEFAULT_TIMEFRAMES_SEC
    out: list[int] = []
    for item in value.split(","):
        item = item.strip()
        if not item:
            continue
        out.append(int(item))
    return tuple(out) or DEFAULT_TIMEFRAMES_SEC


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Update rolling WarRoom candle store from latest D-hot market.trade part.")
    parser.add_argument("--raw-root", default=None)
    parser.add_argument("--history-raw-root", action="append", default=[])
    parser.add_argument("--store-root", "--cache-root", dest="store_root", default=None)
    parser.add_argument("--exchange", default=DEFAULT_EXCHANGE)
    parser.add_argument("--symbol", default=DEFAULT_SYMBOL)
    parser.add_argument("--timeframes-sec", default=",".join(str(item) for item in DEFAULT_TIMEFRAMES_SEC))
    parser.add_argument("--retention-days", type=int, default=DEFAULT_RETENTION_DAYS)
    parser.add_argument("--max-days", type=int, default=7)
    parser.add_argument("--max-bootstrap-bytes", type=int, default=DEFAULT_BOOTSTRAP_MAX_BYTES)
    parser.add_argument("--rebuild-history", action="store_true")
    parser.add_argument("--chunk-rows", type=int, default=200000)
    args = parser.parse_args(argv)
    if args.rebuild_history:
        history_roots = [Path(item) for item in (args.history_raw_root or [])]
        if not history_roots and args.raw_root:
            history_roots = [Path(args.raw_root)]
        payload = rebuild_candle_store_from_trade_history(
            raw_root=Path(args.raw_root) if args.raw_root and not history_roots else None,
            raw_roots=history_roots or None,
            store_root=Path(args.store_root) if args.store_root else None,
            exchange=args.exchange,
            symbol=args.symbol,
            timeframes_sec=_parse_timeframes(args.timeframes_sec),
            retention_days=args.retention_days,
            max_days=args.max_days,
            chunk_rows=args.chunk_rows,
        )
    else:
        payload = update_candle_store_from_latest_part(
            raw_root=Path(args.raw_root) if args.raw_root else None,
            store_root=Path(args.store_root) if args.store_root else None,
            exchange=args.exchange,
            symbol=args.symbol,
            timeframes_sec=_parse_timeframes(args.timeframes_sec),
            retention_days=args.retention_days,
            max_days=args.max_days,
            max_bootstrap_bytes=args.max_bootstrap_bytes,
        )
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if payload.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
