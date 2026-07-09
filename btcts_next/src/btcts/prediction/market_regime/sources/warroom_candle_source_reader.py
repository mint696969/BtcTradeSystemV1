# path: ./btcts_next/src/btcts/prediction/market_regime/sources/warroom_candle_source_reader.py
# desc: Read-only WarRoom derived L4 candle source reader for MarketRegime. Reads derived closed/forming candle artifacts only; no raw market reads or writes.

from __future__ import annotations

import json
from collections import deque
from pathlib import Path
from typing import Any, Mapping

from ..source_snapshot import SourceAdapterSafetyFlags, WarroomCandleSourceSnapshot

WARROOM_L4_CANDLE_SOURCE_READER_VERSION = "prediction.market_regime.sources.warroom_candle_source_reader.mr_a2.2026_07_09.v1"
DEFAULT_EXCHANGE = "bitflyer"
DEFAULT_SYMBOL = "FX_BTC_JPY"
DEFAULT_TIMEFRAME_SEC = 60
DEFAULT_MAX_CLOSED_CANDLES = 240


def warroom_candle_timeframe_relpath(*, exchange: str = DEFAULT_EXCHANGE, symbol: str = DEFAULT_SYMBOL, timeframe_sec: int = DEFAULT_TIMEFRAME_SEC) -> str:
    return f"data/derived/warroom/candles/exchange={exchange}/symbol={symbol}/timeframe={int(timeframe_sec)}s"


def _read_json(path: Path) -> Mapping[str, Any]:
    if not path.exists():
        return {}
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    return dict(value) if isinstance(value, Mapping) else {}


def _read_tail_jsonl(path: Path, *, max_rows: int) -> tuple[tuple[Mapping[str, Any], ...], int, tuple[str, ...]]:
    warnings: list[str] = []
    if not path.exists():
        return (), 0, ("warroom_candle_closed_missing",)
    rows: deque[Mapping[str, Any]] = deque(maxlen=max(1, int(max_rows)))
    scanned = 0
    try:
        with path.open("r", encoding="utf-8") as handle:
            for raw in handle:
                text = raw.strip()
                if not text:
                    continue
                scanned += 1
                try:
                    value = json.loads(text)
                except Exception:
                    warnings.append("warroom_candle_closed_json_decode_error")
                    continue
                if isinstance(value, Mapping):
                    rows.append(dict(value))
    except Exception as exc:
        return (), scanned, (f"warroom_candle_closed_read_error:{type(exc).__name__}",)
    return tuple(rows), scanned, tuple(dict.fromkeys(warnings))


def load_warroom_candle_source_snapshot(
    hot_root: str | Path,
    *,
    exchange: str = DEFAULT_EXCHANGE,
    symbol: str = DEFAULT_SYMBOL,
    timeframe_sec: int = DEFAULT_TIMEFRAME_SEC,
    max_closed_candles: int = DEFAULT_MAX_CLOSED_CANDLES,
) -> WarroomCandleSourceSnapshot:
    root = Path(hot_root)
    base_rel = warroom_candle_timeframe_relpath(exchange=exchange, symbol=symbol, timeframe_sec=timeframe_sec)
    closed_rel = f"{base_rel}/closed.jsonl"
    forming_rel = f"{base_rel}/forming.json"
    meta_rel = f"{base_rel}/meta.json"
    closed_path = root / closed_rel
    forming = _read_json(root / forming_rel)
    meta = _read_json(root / meta_rel)
    closed_rows, scanned, warnings = _read_tail_jsonl(closed_path, max_rows=max_closed_candles)
    if not meta:
        warnings = tuple(dict.fromkeys((*warnings, "warroom_candle_meta_missing")))
    latest_closed_ts = ""
    if closed_rows:
        latest_closed_ts = str(closed_rows[-1].get("time_utc") or "")
    latest_forming_ts = str(forming.get("time_utc") or "") if forming else ""
    latest_ts = latest_forming_ts or latest_closed_ts
    ok = bool(closed_rows) and bool(meta.get("ok", bool(meta)))
    return WarroomCandleSourceSnapshot(
        relative_path=closed_rel,
        ok=ok,
        timeframe_sec=int(timeframe_sec),
        closed_candle_count=len(closed_rows),
        scanned_closed_lines=int(scanned),
        closed_candles=closed_rows,
        forming=dict(forming),
        meta=dict(meta),
        latest_closed_time_utc=latest_closed_ts,
        latest_forming_time_utc=latest_forming_ts,
        latest_time_utc=latest_ts,
        meta_relative_path=meta_rel,
        forming_relative_path=forming_rel,
        warnings=tuple(dict.fromkeys(warnings)),
        safety=SourceAdapterSafetyFlags(),
    )
