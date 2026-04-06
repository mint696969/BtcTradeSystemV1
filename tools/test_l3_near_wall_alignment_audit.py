# path: ./tools/test_l3_near_wall_alignment_audit.py
# desc: Audit alignment between near wall side and pressure bias.

from __future__ import annotations

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

import json
import os
from pathlib import Path
from typing import Any

from btcts.core import paths as core_paths
from btcts.replay.replay_pipeline import ReplayPipeline


def _load_jsonl(path: Path, *, max_records: int | None = None) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as fh:
        for line in fh:
            text = line.strip()
            if not text:
                continue
            try:
                raw = json.loads(text)
            except Exception:
                continue
            if isinstance(raw, dict):
                rows.append(raw)
                if max_records is not None and len(rows) >= max_records:
                    break
    return rows


def _market_data_part_path(*, event_type: str, date_str: str) -> Path:
    return (
        core_paths.data_dir(ensure=False)
        / "market_data"
        / "exchange=bitflyer"
        / "symbol=BTC_JPY"
        / f"type={event_type}"
        / f"date={date_str}"
        / "part-00001.jsonl"
    )


def _discover_latest_snapshot_diff_pair() -> tuple[Path, Path] | None:
    snapshot_root = (
        core_paths.data_dir(ensure=False)
        / "market_data"
        / "exchange=bitflyer"
        / "symbol=BTC_JPY"
        / "type=market.orderbook.snapshot"
    )
    if not snapshot_root.exists():
        return None

    candidate_dates: list[str] = []
    for child in snapshot_root.iterdir():
        if child.is_dir() and child.name.startswith("date="):
            candidate_dates.append(child.name.replace("date=", "", 1).strip())

    for date_str in sorted(candidate_dates, reverse=True):
        snapshot_path = _market_data_part_path(
            event_type="market.orderbook.snapshot",
            date_str=date_str,
        )
        diff_path = _market_data_part_path(
            event_type="market.orderbook.diff",
            date_str=date_str,
        )
        if snapshot_path.exists() and diff_path.exists():
            return snapshot_path, diff_path

    return None


def _load_records(max_records: int) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    pair = _discover_latest_snapshot_diff_pair()
    if pair is None:
        raise RuntimeError("latest snapshot/diff pair not found under data_root")

    snapshot_path, diff_path = pair
    snapshot_records = _load_jsonl(snapshot_path, max_records=max_records)
    diff_records = _load_jsonl(diff_path, max_records=max_records)

    return (
        snapshot_records + diff_records,
        {
            "snapshot_input_jsonl": str(snapshot_path),
            "diff_input_jsonl": str(diff_path),
            "snapshot_input_record_count": len(snapshot_records),
            "diff_input_record_count": len(diff_records),
        },
    )


def _safe_get(payload: dict[str, Any] | None, *path: str, default=None):
    cur: Any = payload
    for key in path:
        if not isinstance(cur, dict):
            return default
        cur = cur.get(key)
    return default if cur is None else cur


def main() -> int:
    max_records_env = os.environ.get("BTCTS_L3_AUDIT_MAX_RECORDS", "").strip()
    max_records = int(max_records_env) if max_records_env else 200

    records, input_info = _load_records(max_records)

    pipeline = ReplayPipeline(
        semantic_policy={
            "wall_ratio_threshold": 0.25,
            "wall_near_rank_threshold": 8,
            "pressure_threshold": 0.20,
            "pull_threshold": 0.20,
        }
    )
    processed = pipeline.process_records(records)

    counts = {
        "near_wall_detected_rows": 0,
        "near_wall_ask_rows": 0,
        "near_wall_bid_rows": 0,
        "near_ask_with_buy_pressure": 0,
        "near_bid_with_sell_pressure": 0,
        "near_ask_with_sell_pressure": 0,
        "near_bid_with_buy_pressure": 0,
        "buy_pressure_rows": 0,
        "sell_pressure_rows": 0,
        "neutral_rows": 0,
    }

    for row in processed:
        signal = row.get("signal") or {}

        pressure_bias = str(_safe_get(signal, "pressure", "bias", default="neutral"))
        if pressure_bias == "buy_pressure":
            counts["buy_pressure_rows"] += 1
        elif pressure_bias == "sell_pressure":
            counts["sell_pressure_rows"] += 1
        else:
            counts["neutral_rows"] += 1

        near_wall_detected = bool(_safe_get(signal, "wall", "near_wall_detected", default=False))
        near_wall_side = _safe_get(signal, "wall", "near_strongest_side")

        if not near_wall_detected:
            continue

        counts["near_wall_detected_rows"] += 1

        if near_wall_side == "ask":
            counts["near_wall_ask_rows"] += 1
            if pressure_bias == "buy_pressure":
                counts["near_ask_with_buy_pressure"] += 1
            elif pressure_bias == "sell_pressure":
                counts["near_ask_with_sell_pressure"] += 1

        elif near_wall_side == "bid":
            counts["near_wall_bid_rows"] += 1
            if pressure_bias == "sell_pressure":
                counts["near_bid_with_sell_pressure"] += 1
            elif pressure_bias == "buy_pressure":
                counts["near_bid_with_buy_pressure"] += 1

    report = {
        "input": input_info,
        "input_record_count": len(records),
        "counts": counts,
    }

    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())