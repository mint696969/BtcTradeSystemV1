# path: ./tools/run_market_engine_live_runtime.py
# desc: Minimal live runner that feeds canonical orderbook snapshot/diff jsonl into MarketEngineRuntime.

from __future__ import annotations

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from btcts.market_engine.config import load_market_engine_config
from btcts.market_engine.runtime import MarketEngineRuntime


def _env_str(name: str, default: str) -> str:
    raw = os.getenv(name, "").strip()
    return raw if raw else default


def _env_float(name: str, default: float) -> float:
    raw = os.getenv(name, "").strip()
    if not raw:
        return default
    try:
        return float(raw)
    except Exception:
        return default


def _utc_date_str() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def _data_root() -> Path:
    raw = os.getenv("BTC_TS_DATA_DIR", "").strip()
    if raw:
        return Path(raw)
    return Path.cwd() / "data"


def _canonical_dir(*, exchange: str, symbol: str, record_type: str) -> Path:
    return (
        _data_root()
        / "market_data"
        / f"exchange={exchange}"
        / f"symbol={symbol}"
        / f"type={record_type}"
        / f"date={_utc_date_str()}"
    )


def _latest_part_file(dir_path: Path) -> Path | None:
    if not dir_path.exists():
        return None
    parts = sorted(dir_path.glob("part-*.jsonl"))
    if not parts:
        return None
    return parts[-1]


def _read_last_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except Exception:
        return None

    for line in reversed(lines):
        text = line.strip()
        if not text:
            continue
        try:
            obj = json.loads(text)
        except Exception:
            continue
        if isinstance(obj, dict):
            return obj
    return None


def _iter_new_jsonl(path: Path, start_pos: int) -> tuple[list[dict[str, Any]], int]:
    rows: list[dict[str, Any]] = []
    if not path.exists():
        return rows, start_pos

    with path.open("r", encoding="utf-8") as fh:
        fh.seek(start_pos)
        for line in fh:
            text = line.strip()
            if not text:
                continue
            try:
                obj = json.loads(text)
            except Exception:
                continue
            if isinstance(obj, dict):
                rows.append(obj)
        end_pos = fh.tell()

    return rows, end_pos


def _record_type_of(row: dict[str, Any]) -> str:
    return str(row.get("record_type") or "")


def _event_time_key(row: dict[str, Any]) -> tuple[str, int]:
    payload = row.get("payload")
    payload_dict = payload if isinstance(payload, dict) else {}

    ts = str(
        row.get("collector_ts")
        or row.get("exchange_ts")
        or payload_dict.get("collector_ts")
        or payload_dict.get("exchange_ts")
        or ""
    )

    record_type = _record_type_of(row)
    priority = 0 if record_type == "market.orderbook.snapshot" else 1
    return (ts, priority)


def main() -> int:
    cfg = load_market_engine_config()
    runtime = MarketEngineRuntime(cfg)

    poll_sec = _env_float("BTCTS_MARKET_ENGINE_LIVE_POLL_SEC", 1.0)
    max_seconds = _env_float("BTCTS_MARKET_ENGINE_LIVE_SECONDS", 60.0)

    snapshot_dir = _canonical_dir(
        exchange=cfg.exchange,
        symbol=cfg.symbol_raw,
        record_type="market.orderbook.snapshot",
    )
    diff_dir = _canonical_dir(
        exchange=cfg.exchange,
        symbol=cfg.symbol_raw,
        record_type="market.orderbook.diff",
    )

    snapshot_file = _latest_part_file(snapshot_dir)
    diff_file = _latest_part_file(diff_dir)

    if snapshot_file is None:
        raise RuntimeError(f"snapshot canonical file not found: {snapshot_dir}")
    if diff_file is None:
        raise RuntimeError(f"diff canonical file not found: {diff_dir}")

    seeded = False
    snapshot_seed = _read_last_json(snapshot_file)
    last_output_path: str | None = None
    processed = 0

    if isinstance(snapshot_seed, dict) and _record_type_of(snapshot_seed) == "market.orderbook.snapshot":
        result = runtime.step(snapshot_seed)
        last_output_path = result.output_path
        processed += 1
        seeded = True

    # 起動時点以降に追記される snapshot / diff の両方を追う
    snapshot_pos = snapshot_file.stat().st_size if snapshot_file.exists() else 0
    diff_pos = diff_file.stat().st_size if diff_file.exists() else 0

    started = time.monotonic()
    while True:
        if max_seconds > 0:
            if (time.monotonic() - started) >= max_seconds:
                break
        # 日付ローテや part 切替にも追従
        latest_snapshot_file = _latest_part_file(snapshot_dir)
        latest_diff_file = _latest_part_file(diff_dir)

        if latest_snapshot_file is not None and latest_snapshot_file != snapshot_file:
            snapshot_file = latest_snapshot_file
            snapshot_pos = 0

        if latest_diff_file is not None and latest_diff_file != diff_file:
            diff_file = latest_diff_file
            diff_pos = 0

        if not seeded and snapshot_file is not None:
            snapshot_seed = _read_last_json(snapshot_file)
            if isinstance(snapshot_seed, dict) and _record_type_of(snapshot_seed) == "market.orderbook.snapshot":
                result = runtime.step(snapshot_seed)
                last_output_path = result.output_path
                processed += 1
                seeded = True
                snapshot_pos = snapshot_file.stat().st_size if snapshot_file.exists() else 0

        snapshot_rows, snapshot_pos = _iter_new_jsonl(snapshot_file, snapshot_pos)
        diff_rows, diff_pos = _iter_new_jsonl(diff_file, diff_pos)

        pending_rows: list[dict[str, Any]] = []
        for row in snapshot_rows:
            if _record_type_of(row) == "market.orderbook.snapshot":
                pending_rows.append(row)
        for row in diff_rows:
            if _record_type_of(row) == "market.orderbook.diff":
                pending_rows.append(row)

        pending_rows.sort(key=_event_time_key)

        for row in pending_rows:
            result = runtime.step(row)
            last_output_path = result.output_path
            processed += 1

        time.sleep(poll_sec)

    summary = {
        "ok": True,
        "seeded_from_snapshot": seeded,
        "processed_events": processed,
        "snapshot_file": str(snapshot_file),
        "diff_file": str(diff_file),
        "last_output_path": last_output_path,
        "data_root": str(_data_root()),
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())