# path: ./btcts_next/src/btcts/prediction/warroom_chart_history_bootstrap.py
# desc: D-hot market.trade bootstrap reader for WarRoom chart history. Read-only, bounded tail scan, no broker/order/prediction invocation.

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping

import pandas as pd

WARROOM_CHART_DHOT_BOOTSTRAP_VERSION = "warroom_chart_dhot_history_bootstrap.2026_07_05.v1"
ENV_DHOT_DATA_ROOT = "BTCTS_HOT_DATA_ROOT"
ENV_DHOT_RUNTIME_ROOT = "BTC_TS_AUTOTRADE_RUNTIME_ROOT"
DEFAULT_DHOT_ROOT = Path("D:/btc_ts_hot")
DEFAULT_SYMBOL = "FX_BTC_JPY"
DEFAULT_EXCHANGE = "bitflyer"
DEFAULT_MARKET_TRADE_RELATIVE = "data/market_data/exchange={exchange}/symbol={symbol}/type=market.trade/date={date}/part-00001.jsonl"
DEFAULT_TAIL_BYTES = 2_000_000
DEFAULT_MAX_ROWS = 900


@dataclass(frozen=True)
class WarRoomChartDhotBootstrapResult:
    ok: bool
    version: str
    source_path: str | None
    source_exists: bool
    source_root: str
    source_root_reason: str
    rows_read: int
    rows_returned: int
    skipped_rows: int
    tail_bytes: int
    max_rows: int
    error: str | None = None
    read_only: bool = True
    broker_send_enabled: bool = False
    prediction_invoked: bool = False
    classifier_invoked: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "ok": self.ok,
            "version": self.version,
            "source_path": self.source_path,
            "source_exists": self.source_exists,
            "source_root": self.source_root,
            "source_root_reason": self.source_root_reason,
            "rows_read": self.rows_read,
            "rows_returned": self.rows_returned,
            "skipped_rows": self.skipped_rows,
            "tail_bytes": self.tail_bytes,
            "max_rows": self.max_rows,
            "error": self.error,
            "read_only": self.read_only,
            "broker_send_enabled": self.broker_send_enabled,
            "prediction_invoked": self.prediction_invoked,
            "classifier_invoked": self.classifier_invoked,
        }


def resolve_dhot_root() -> tuple[Path, str]:
    for env_name in (ENV_DHOT_DATA_ROOT, ENV_DHOT_RUNTIME_ROOT):
        value = os.environ.get(env_name)
        if value and value.strip():
            return Path(value.strip()).expanduser(), f"env:{env_name}"
    return DEFAULT_DHOT_ROOT, "default:D:/btc_ts_hot"


def market_trade_path(*, root: Path | None = None, date: str | None = None, exchange: str = DEFAULT_EXCHANGE, symbol: str = DEFAULT_SYMBOL) -> tuple[Path, str]:
    resolved_root, reason = resolve_dhot_root() if root is None else (root, "explicit")
    date_label = date or datetime.now(timezone.utc).strftime("%Y-%m-%d")
    relative = DEFAULT_MARKET_TRADE_RELATIVE.format(exchange=exchange, symbol=symbol, date=date_label)
    return resolved_root / relative, reason


def read_recent_jsonl_lines(path: Path, *, tail_bytes: int = DEFAULT_TAIL_BYTES) -> list[str]:
    if tail_bytes <= 0:
        tail_bytes = DEFAULT_TAIL_BYTES
    size = path.stat().st_size
    with path.open("rb") as handle:
        if size > tail_bytes:
            handle.seek(max(0, size - tail_bytes))
            handle.readline()  # discard likely partial line
        data = handle.read()
    text = data.decode("utf-8", errors="ignore")
    return [line for line in text.splitlines() if line.strip()]


def _first_present(mapping: Mapping[str, Any], keys: Iterable[str]) -> Any:
    for key in keys:
        if key in mapping and mapping[key] not in (None, ""):
            return mapping[key]
    return None


def _trade_row_from_record(record: Mapping[str, Any]) -> dict[str, Any] | None:
    payload = record.get("payload") if isinstance(record.get("payload"), Mapping) else {}
    source = payload if isinstance(payload, Mapping) else {}
    event_ts = _first_present(record, ("event_ts", "exchange_ts", "ingest_ts", "collector_ts")) or _first_present(source, ("trade_ts", "event_ts"))
    price = _first_present(source, ("price", "last_price")) or _first_present(record, ("price", "last_price"))
    size = _first_present(source, ("size", "volume")) or _first_present(record, ("size", "volume")) or 0.0
    side = str(_first_present(source, ("side",)) or _first_present(record, ("side",)) or "")
    sequence = _first_present(record, ("sequence_id", "continuity_sequence", "source_sequence")) or _first_present(source, ("trade_id",)) or 0
    trade_id = _first_present(source, ("trade_id",)) or _first_present(record, ("source_event_id", "record_id"))
    ts = pd.to_datetime(event_ts, utc=True, errors="coerce")
    value = pd.to_numeric(pd.Series([price]), errors="coerce").iloc[0]
    if pd.isna(ts) or pd.isna(value):
        return None
    return {
        "ts": ts,
        "topic": "market.trade.dhot_bootstrap",
        "role": "last",
        "price": float(value),
        "sequence": int(sequence or 0),
        "freshness_label": "dhot_bootstrap",
        "size": float(size or 0.0),
        "side": side.upper() if side else "",
        "trade_id": str(trade_id or ""),
        "source": "dhot_market_trade",
    }


def market_trade_records_to_history_frame(records: Iterable[Mapping[str, Any]], *, max_rows: int = DEFAULT_MAX_ROWS) -> tuple[pd.DataFrame, int]:
    rows: list[dict[str, Any]] = []
    skipped = 0
    for record in records:
        row = _trade_row_from_record(record)
        if row is None:
            skipped += 1
            continue
        rows.append(row)
    if not rows:
        return pd.DataFrame(columns=["ts", "topic", "role", "price", "sequence", "freshness_label", "size", "side", "trade_id", "source"]), skipped
    frame = pd.DataFrame(rows)
    frame = frame.drop_duplicates(subset=["ts", "price", "sequence", "trade_id"]).sort_values("ts")
    if max_rows > 0:
        frame = frame.tail(max_rows)
    return frame.reset_index(drop=True), skipped


def load_dhot_market_trade_history(*, root: Path | None = None, date: str | None = None, tail_bytes: int = DEFAULT_TAIL_BYTES, max_rows: int = DEFAULT_MAX_ROWS) -> tuple[pd.DataFrame, WarRoomChartDhotBootstrapResult]:
    path, root_reason = market_trade_path(root=root, date=date)
    root_path = root if root is not None else resolve_dhot_root()[0]
    if not path.exists():
        return (
            pd.DataFrame(columns=["ts", "topic", "role", "price", "sequence", "freshness_label", "size", "side", "trade_id", "source"]),
            WarRoomChartDhotBootstrapResult(
                ok=False,
                version=WARROOM_CHART_DHOT_BOOTSTRAP_VERSION,
                source_path=str(path),
                source_exists=False,
                source_root=str(root_path),
                source_root_reason=root_reason,
                rows_read=0,
                rows_returned=0,
                skipped_rows=0,
                tail_bytes=tail_bytes,
                max_rows=max_rows,
                error="market_trade_path_missing",
            ),
        )
    records: list[Mapping[str, Any]] = []
    skipped = 0
    try:
        lines = read_recent_jsonl_lines(path, tail_bytes=tail_bytes)
        for line in lines:
            try:
                item = json.loads(line)
            except json.JSONDecodeError:
                skipped += 1
                continue
            if isinstance(item, Mapping):
                records.append(item)
            else:
                skipped += 1
        frame, transform_skipped = market_trade_records_to_history_frame(records, max_rows=max_rows)
        skipped += transform_skipped
        return (
            frame,
            WarRoomChartDhotBootstrapResult(
                ok=not frame.empty,
                version=WARROOM_CHART_DHOT_BOOTSTRAP_VERSION,
                source_path=str(path),
                source_exists=True,
                source_root=str(root_path),
                source_root_reason=root_reason,
                rows_read=len(records),
                rows_returned=len(frame),
                skipped_rows=skipped,
                tail_bytes=tail_bytes,
                max_rows=max_rows,
                error=None if not frame.empty else "market_trade_rows_empty",
            ),
        )
    except OSError as exc:
        return (
            pd.DataFrame(columns=["ts", "topic", "role", "price", "sequence", "freshness_label", "size", "side", "trade_id", "source"]),
            WarRoomChartDhotBootstrapResult(
                ok=False,
                version=WARROOM_CHART_DHOT_BOOTSTRAP_VERSION,
                source_path=str(path),
                source_exists=True,
                source_root=str(root_path),
                source_root_reason=root_reason,
                rows_read=0,
                rows_returned=0,
                skipped_rows=skipped,
                tail_bytes=tail_bytes,
                max_rows=max_rows,
                error=f"read_error:{type(exc).__name__}",
            ),
        )
