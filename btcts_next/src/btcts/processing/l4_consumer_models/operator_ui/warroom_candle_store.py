# path: ./btcts_next/src/btcts/processing/l4_consumer_models/operator_ui/warroom_candle_store.py
# desc: Rolling multi-timeframe WarRoom candle store. Closed candles are append-stable; forming candle is mutable. Missing periods are represented by absent candles, not synthetic null rows.

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

import pandas as pd

from btcts.prediction.warroom_plain_candle_refresh import _date_dirs_desc
from btcts.prediction.warroom_plain_candles import (
    DEFAULT_DHOT_ROOT,
    DEFAULT_EXCHANGE,
    DEFAULT_SYMBOL,
    DEFAULT_TIMEFRAME_SECONDS,
    _json_record_from_line,
    _last_json_record,
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


def _atomic_write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(text, encoding="utf-8")
    tmp.replace(path)


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
    part, source_meta = _latest_trade_part(raw_root, exchange=exchange, symbol=symbol, max_days=max_days)
    state_path = candle_symbol_store_dir(store_root, exchange=exchange, symbol=symbol) / STATE_NAME
    state = _read_json(state_path)
    if part is None:
        return {"ok": False, "version": WARROOM_CANDLE_STORE_VERSION, "error": source_meta.get("error") or "latest_part_missing", "source_meta": source_meta, "read_only_source": True, "broker_send_enabled": False, "order_intent_submitted": False, "prediction_invoked": False, "classifier_invoked": False}
    previous_part = str(state.get("source_part_file") or "")
    previous_offset = int(state.get("byte_offset") or 0) if previous_part == str(part) else 0
    rows, new_offset, lines_read, tail_bootstrap = _read_trade_rows_from_offset(part, offset=previous_offset, max_bootstrap_bytes=max_bootstrap_bytes)
    update_meta = {
        "source_part_file": str(part),
        "previous_part_file": previous_part,
        "previous_offset": previous_offset,
        "new_offset": new_offset,
        "lines_read": lines_read,
        "trade_rows_read": len(rows),
        "tail_bootstrap": tail_bootstrap,
        "retention_days": int(retention_days),
        "gap_policy": "absent_candles_no_synthetic_null",
    }
    timeframe_metas: dict[str, Any] = {}
    for timeframe in tuple(int(item) for item in timeframes_sec):
        closed, forming, _meta = _load_store_timeframe(store_root, exchange=exchange, symbol=symbol, timeframe_sec=timeframe)
        records_by_time: dict[int, dict[str, Any]] = {int(row["time"]): row for row in closed}
        if forming is not None:
            records_by_time[int(forming["time"])] = forming
        for record in _aggregate_trade_rows(rows, timeframe_sec=timeframe):
            key = int(record["time"])
            merged = _merge_record(records_by_time.get(key), record, timeframe_sec=timeframe, status="forming")
            if merged is not None:
                records_by_time[key] = merged
        ordered_keys = sorted(records_by_time)
        latest_key = ordered_keys[-1] if ordered_keys else None
        next_closed: list[dict[str, Any]] = []
        next_forming: dict[str, Any] | None = None
        for key in ordered_keys:
            row = records_by_time[key]
            if latest_key is not None and key == latest_key:
                next_forming = _normalize_candle_record(row, timeframe_sec=timeframe, status="forming")
            else:
                closed_row = _normalize_candle_record(row, timeframe_sec=timeframe, status="closed")
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
        "source_part_file": str(part),
        "byte_offset": new_offset,
        "latest_source_ts_utc": source_meta.get("latest_ts_utc"),
        "timeframes_sec": [int(item) for item in timeframes_sec],
        "retention_days": int(retention_days),
        "gap_policy": "absent_candles_no_synthetic_null",
        "updated_rows": len(rows),
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
    parser.add_argument("--store-root", "--cache-root", dest="store_root", default=None)
    parser.add_argument("--exchange", default=DEFAULT_EXCHANGE)
    parser.add_argument("--symbol", default=DEFAULT_SYMBOL)
    parser.add_argument("--timeframes-sec", default=",".join(str(item) for item in DEFAULT_TIMEFRAMES_SEC))
    parser.add_argument("--retention-days", type=int, default=DEFAULT_RETENTION_DAYS)
    parser.add_argument("--max-days", type=int, default=7)
    parser.add_argument("--max-bootstrap-bytes", type=int, default=DEFAULT_BOOTSTRAP_MAX_BYTES)
    args = parser.parse_args(argv)
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
