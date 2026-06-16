# path: ./tools/test_l3_wall_rank_distribution_audit.py
# desc: Audit strongest wall rank distribution and near-threshold coverage.

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


def _rank_key(rank: int | None) -> str:
    return "none" if rank is None else str(rank)


def _bump(counter: dict[str, int], key: str) -> None:
    counter[key] = int(counter.get(key, 0)) + 1


def _summarize_rank_thresholds(ranks: list[int]) -> dict[str, int]:
    return {
        "rank_le_3": sum(1 for rank in ranks if rank <= 3),
        "rank_le_5": sum(1 for rank in ranks if rank <= 5),
        "rank_le_8": sum(1 for rank in ranks if rank <= 8),
        "rank_le_10": sum(1 for rank in ranks if rank <= 10),
    }


def _collect_rank_distribution(
    records: list[dict[str, Any]],
    *,
    wall_ratio_threshold: float,
) -> dict[str, Any]:
    rebuilder = OrderBookRebuilder()

    all_rank_histogram: dict[str, int] = {}
    detected_rank_histogram: dict[str, int] = {}
    all_detected_ranks: list[int] = []

    processed_rows = 0
    wall_detected_rows = 0
    strongest_side_bid_rows = 0
    strongest_side_ask_rows = 0

    for record in records:
        payload = record.get("payload")
        if not isinstance(payload, dict):
            continue

        signal = build_liquidity_payload(
            rebuilder,
            payload,
            levels=10,
            wall_levels=20,
            semantic_policy={
                "wall_ratio_threshold": wall_ratio_threshold,
            },
        )
        if signal is None:
            continue

        processed_rows += 1

        wall = signal.get("wall") or {}
        strongest_rank_raw = wall.get("strongest_rank")
        strongest_side = wall.get("strongest_side")
        wall_detected = bool(wall.get("wall_detected", False))

        strongest_rank = None
        if strongest_rank_raw is not None:
            strongest_rank = int(strongest_rank_raw)
            _bump(all_rank_histogram, _rank_key(strongest_rank))

        if strongest_side == "bid":
            strongest_side_bid_rows += 1
        elif strongest_side == "ask":
            strongest_side_ask_rows += 1

        if wall_detected:
            wall_detected_rows += 1
            if strongest_rank is not None:
                all_detected_ranks.append(strongest_rank)
                _bump(detected_rank_histogram, _rank_key(strongest_rank))

    return {
        "wall_ratio_threshold": wall_ratio_threshold,
        "processed_rows": processed_rows,
        "wall_detected_rows": wall_detected_rows,
        "strongest_side_bid_rows": strongest_side_bid_rows,
        "strongest_side_ask_rows": strongest_side_ask_rows,
        "all_rank_histogram": dict(sorted(all_rank_histogram.items(), key=lambda kv: (kv[0] == "none", kv[0]))),
        "detected_rank_histogram": dict(sorted(detected_rank_histogram.items(), key=lambda kv: (kv[0] == "none", kv[0]))),
        "detected_rank_threshold_counts": _summarize_rank_thresholds(all_detected_ranks),
    }


def main() -> int:
    max_records_env = os.environ.get("BTCTS_L3_AUDIT_MAX_RECORDS", "").strip()
    max_records = int(max_records_env) if max_records_env else 200

    records, input_info = _load_records(max_records)

    report = {
        "input": input_info,
        "input_record_count": len(records),
        "thresholds": {
            "wall_0_25": _collect_rank_distribution(records, wall_ratio_threshold=0.25),
            "wall_0_30": _collect_rank_distribution(records, wall_ratio_threshold=0.30),
            "wall_0_35": _collect_rank_distribution(records, wall_ratio_threshold=0.35),
        },
    }

    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())