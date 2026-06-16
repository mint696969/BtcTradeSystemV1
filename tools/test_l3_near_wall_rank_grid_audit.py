# path: ./tools/test_l3_near_wall_rank_grid_audit.py
# desc: Audit near wall coverage by wall_near_rank_threshold.

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


def _safe_get(payload: dict[str, Any] | None, *path: str, default=None):
    cur: Any = payload
    for key in path:
        if not isinstance(cur, dict):
            return default
        cur = cur.get(key)
    return default if cur is None else cur


def _signal_true_count(processed_rows: list[dict[str, Any]], *path: str) -> int:
    total = 0
    for row in processed_rows:
        signal = row.get("signal") or {}
        if bool(_safe_get(signal, *path, default=False)):
            total += 1
    return total


def _event_reason_count(processed_rows: list[dict[str, Any]], event_name: str, reason_substr: str) -> int:
    total = 0
    for row in processed_rows:
        events = row.get("events") or []
        for event in events:
            if str(event.get("event_name") or "") != event_name:
                continue
            reason = str(event.get("reason") or "")
            if reason_substr in reason:
                total += 1
    return total


def _candidate_count(processed_rows: list[dict[str, Any]], event_name: str) -> int:
    total = 0
    for row in processed_rows:
        events = row.get("events") or []
        for event in events:
            if str(event.get("event_name") or "") == event_name:
                total += 1
    return total


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


def main() -> int:
    max_records_env = os.environ.get("BTCTS_L3_AUDIT_MAX_RECORDS", "").strip()
    max_records = int(max_records_env) if max_records_env else 200

    records, input_info = _load_records(max_records)

    near_rank_thresholds = [3, 5, 8]
    report_rows: list[dict[str, Any]] = []

    for idx, near_rank_threshold in enumerate(near_rank_thresholds, start=1):
        print(f"[{idx}/{len(near_rank_thresholds)}] near_rank={near_rank_threshold}", flush=True)

        pipeline = ReplayPipeline(
            semantic_policy={
                "wall_ratio_threshold": 0.25,
                "wall_near_rank_threshold": near_rank_threshold,
                "pressure_threshold": 0.20,
                "pull_threshold": 0.20,
            }
        )
        processed = pipeline.process_records(records)

        report_rows.append(
            {
                "wall_near_rank_threshold": near_rank_threshold,
                "processed_rows": len(processed),
                "wall_detected_rows": _signal_true_count(processed, "wall", "wall_detected"),
                "near_wall_detected_rows": _signal_true_count(processed, "wall", "near_wall_detected"),
                "absorption_candidate": _candidate_count(processed, "absorption_candidate"),
                "absorption_candidate_near_wall": _event_reason_count(
                    processed,
                    "absorption_candidate",
                    "_near_",
                ),
                "support_candidate": _candidate_count(processed, "support_candidate"),
                "resistance_candidate": _candidate_count(processed, "resistance_candidate"),
            }
        )

    report = {
        "input": input_info,
        "input_record_count": len(records),
        "rows": report_rows,
    }

    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())