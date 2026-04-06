# path: ./tools/test_l3_wall_created_transition_audit.py
# desc: Inspect wall_created transitions under different wall ratio thresholds.

from __future__ import annotations

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

import json
import os
from pathlib import Path
from typing import Any

from btcts.core import paths as core_paths
from btcts.ingestion.l2_canonical.orderbook.book_rebuilder import OrderBookRebuilder
from btcts.processing.l3_market_semantics.orderbook.liquidity_pipeline import build_liquidity_payload


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


def _wall_view(signal: dict[str, Any] | None) -> dict[str, Any]:
    wall = (signal or {}).get("wall") or {}
    return {
        "wall_detected": wall.get("wall_detected"),
        "strongest_side": wall.get("strongest_side"),
        "strongest_ratio": wall.get("strongest_ratio"),
        "strongest_rank": wall.get("strongest_rank"),
        "strongest_is_near": wall.get("strongest_is_near"),
    }


def _collect_wall_created_samples(
    records: list[dict[str, Any]],
    *,
    wall_ratio_threshold: float,
    sample_limit: int = 12,
) -> list[dict[str, Any]]:
    rebuilder = OrderBookRebuilder()
    prev_signal: dict[str, Any] | None = None
    samples: list[dict[str, Any]] = []

    for record in records:
        payload = record.get("payload")
        if not isinstance(payload, dict):
            continue

        curr_signal = build_liquidity_payload(
            rebuilder,
            payload,
            levels=10,
            wall_levels=20,
            semantic_policy={
                "wall_ratio_threshold": wall_ratio_threshold,
            },
        )
        if curr_signal is None:
            continue

        prev_detected = bool(((prev_signal or {}).get("wall") or {}).get("wall_detected", False))
        curr_detected = bool(((curr_signal or {}).get("wall") or {}).get("wall_detected", False))

        if (not prev_detected) and curr_detected:
            samples.append(
                {
                    "event_ts": record.get("event_ts"),
                    "record_type": record.get("record_type"),
                    "wall_ratio_threshold": wall_ratio_threshold,
                    "prev_wall": _wall_view(prev_signal),
                    "curr_wall": _wall_view(curr_signal),
                }
            )
            if len(samples) >= sample_limit:
                break

        prev_signal = curr_signal

    return samples


def main() -> int:
    max_records_env = os.environ.get("BTCTS_L3_AUDIT_MAX_RECORDS", "").strip()
    max_records = int(max_records_env) if max_records_env else 200

    records, input_info = _load_records(max_records)

    report = {
        "input": input_info,
        "input_record_count": len(records),
        "threshold_samples": {
            "wall_0_25": _collect_wall_created_samples(records, wall_ratio_threshold=0.25),
            "wall_0_35": _collect_wall_created_samples(records, wall_ratio_threshold=0.35),
        },
    }

    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())