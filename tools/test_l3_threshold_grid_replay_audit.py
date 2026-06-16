# path: ./tools/test_l3_threshold_grid_replay_audit.py
# desc: Small replay audit for L3 threshold sensitivity using a compact parameter grid.

from __future__ import annotations

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

import json
import os
from pathlib import Path
from typing import Any

from btcts.core import paths as core_paths
from btcts.replay.replay_pipeline import ReplayPipeline


REPO_ROOT = Path(__file__).resolve().parents[1]


def _env_str(name: str, default: str) -> str:
    value = os.environ.get(name)
    return value.strip() if isinstance(value, str) and value.strip() else default


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
    diff_root = (
        core_paths.data_dir(ensure=False)
        / "market_data"
        / "exchange=bitflyer"
        / "symbol=BTC_JPY"
        / "type=market.orderbook.diff"
    )

    if not snapshot_root.exists() or not diff_root.exists():
        return None

    candidate_dates: list[str] = []
    for child in snapshot_root.iterdir():
        if not child.is_dir():
            continue
        name = child.name
        if not name.startswith("date="):
            continue
        date_str = name.replace("date=", "", 1).strip()
        if date_str:
            candidate_dates.append(date_str)

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


def _event_count(processed_rows: list[dict[str, Any]], event_name: str) -> int:
    total = 0
    for row in processed_rows:
        events = row.get("events") or []
        for event in events:
            if str(event.get("event_name") or "") == event_name:
                total += 1
    return total


def _candidate_count(processed_rows: list[dict[str, Any]], event_name: str) -> int:
    total = 0
    for row in processed_rows:
        signal = row.get("signal") or {}
        events = (row.get("events") or []) + []
        for event in events:
            if str(event.get("event_name") or "") == event_name:
                total += 1

        # candidate_events are included in "events", so nothing special needed.
        _ = signal
    return total


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


def _event_field_value_count(
    processed_rows: list[dict[str, Any]],
    event_name: str,
    field_name: str,
    expected_value: str,
) -> int:
    total = 0
    for row in processed_rows:
        events = row.get("events") or []
        for event in events:
            if str(event.get("event_name") or "") != event_name:
                continue
            if str(event.get(field_name) or "") == expected_value:
                total += 1
    return total


def _safe_ratio(numerator: int, denominator: int) -> float:
    if denominator <= 0:
        return 0.0
    return round(float(numerator) / float(denominator), 4)


def _grid() -> list[dict[str, float]]:
    pressures = [0.15, 0.20, 0.25]
    walls = [0.25, 0.30, 0.35]
    pulls = [0.15, 0.20, 0.25]

    rows: list[dict[str, float]] = []
    for pressure_threshold in pressures:
        for wall_ratio_threshold in walls:
            for pull_threshold in pulls:
                rows.append(
                    {
                        "pressure_threshold": pressure_threshold,
                        "wall_ratio_threshold": wall_ratio_threshold,
                        "pull_threshold": pull_threshold,
                    }
                )
    return rows


def main() -> int:
    input_default = str(REPO_ROOT / "tmp" / "market_engine_onboarding_input.jsonl")
    merged_input_jsonl = Path(_env_str("BTCTS_L3_AUDIT_INPUT_JSONL", input_default)).resolve()

    snapshot_input = os.environ.get("BTCTS_L3_AUDIT_SNAPSHOT_JSONL", "").strip()
    diff_input = os.environ.get("BTCTS_L3_AUDIT_DIFF_JSONL", "").strip()

    records: list[dict[str, Any]]
    input_descriptor: dict[str, Any]
    max_records_env = os.environ.get("BTCTS_L3_AUDIT_MAX_RECORDS", "").strip()
    max_records = int(max_records_env) if max_records_env else 2000

    if merged_input_jsonl.exists():
        merged_records = _load_jsonl(merged_input_jsonl, max_records=max_records)
        records = merged_records
        input_descriptor = {
            "mode": "merged_jsonl",
            "merged_input_jsonl": str(merged_input_jsonl),
            "merged_input_record_count": len(merged_records),
        }
    elif snapshot_input and diff_input:
        snapshot_path = Path(snapshot_input).expanduser().resolve()
        diff_path = Path(diff_input).expanduser().resolve()

        if not snapshot_path.exists():
            raise RuntimeError(f"snapshot jsonl not found: {snapshot_path}")
        if not diff_path.exists():
            raise RuntimeError(f"diff jsonl not found: {diff_path}")

        snapshot_records = _load_jsonl(snapshot_path, max_records=max_records)
        diff_records = _load_jsonl(diff_path, max_records=max_records)
        records = snapshot_records + diff_records
        input_descriptor = {
            "mode": "snapshot_diff_pair_env",
            "snapshot_input_jsonl": str(snapshot_path),
            "diff_input_jsonl": str(diff_path),
            "snapshot_input_record_count": len(snapshot_records),
            "diff_input_record_count": len(diff_records),
        }
    else:
        pair = _discover_latest_snapshot_diff_pair()
        if pair is None:
            raise RuntimeError(
                "L3 audit input not found. "
                "Tried merged input at repo tmp, explicit env pair, and latest snapshot/diff pair under data_root."
            )

        snapshot_path, diff_path = pair
        snapshot_records = _load_jsonl(snapshot_path, max_records=max_records)
        diff_records = _load_jsonl(diff_path, max_records=max_records)
        records = snapshot_records + diff_records
        input_descriptor = {
            "mode": "snapshot_diff_pair_auto",
            "snapshot_input_jsonl": str(snapshot_path),
            "diff_input_jsonl": str(diff_path),
            "snapshot_input_record_count": len(snapshot_records),
            "diff_input_record_count": len(diff_records),
        }

    grid_rows = _grid()
    report_rows: list[dict[str, Any]] = []

    for idx, policy_row in enumerate(grid_rows, start=1):
        print(
            f"[{idx}/{len(grid_rows)}] "
            f"pressure={policy_row['pressure_threshold']:.2f} "
            f"wall={policy_row['wall_ratio_threshold']:.2f} "
            f"pull={policy_row['pull_threshold']:.2f}",
            flush=True,
        )
        pipeline = ReplayPipeline(
            semantic_policy={
                "pressure_threshold": policy_row["pressure_threshold"],
                "wall_ratio_threshold": policy_row["wall_ratio_threshold"],
                "pull_threshold": policy_row["pull_threshold"],
            }
        )
        processed = pipeline.process_records(records)

        report_rows.append(
            {
                **policy_row,
                "processed_rows": len(processed),
                "wall_created": _event_count(processed, "wall_created"),
                "wall_removed": _event_count(processed, "wall_removed"),
                "wall_detected_rows": _signal_true_count(processed, "wall", "wall_detected"),
                "near_wall_detected_rows": _signal_true_count(
                    processed,
                    "wall",
                    "near_wall_detected",
                ),
                "bid_liquidity_pulled": _event_count(processed, "bid_liquidity_pulled"),
                "ask_liquidity_pulled": _event_count(processed, "ask_liquidity_pulled"),
                "absorption_candidate": _candidate_count(processed, "absorption_candidate"),
                "absorption_candidate_near_wall": _event_reason_count(
                    processed,
                    "absorption_candidate",
                    "_near_",
                ),
                "support_candidate": _candidate_count(processed, "support_candidate"),
                "resistance_candidate": _candidate_count(processed, "resistance_candidate"),
                "near_wall_continued": _event_count(processed, "near_wall_continued"),
                "support_continued": _event_count(processed, "support_continued"),
                "resistance_continued": _event_count(processed, "resistance_continued"),
                "near_wall_continuation_ratio": _safe_ratio(
                    _event_count(processed, "near_wall_continued"),
                    _signal_true_count(processed, "wall", "near_wall_detected"),
                ),
                "support_continuation_ratio": _safe_ratio(
                    _event_count(processed, "support_continued"),
                    _candidate_count(processed, "support_candidate"),
                ),
                "resistance_continuation_ratio": _safe_ratio(
                    _event_count(processed, "resistance_continued"),
                    _candidate_count(processed, "resistance_candidate"),
                ),
                "sweep_candidate": _candidate_count(processed, "sweep_candidate"),
                "sweep_candidate_strong_pull": _event_field_value_count(
                    processed,
                    "sweep_candidate",
                    "pull_strength",
                    "strong",
                ),
            }
        )

    report = {
        "input": input_descriptor,
        "input_record_count": len(records),
        "max_records_per_file": max_records,
        "grid_size": len(report_rows),
        "rows": report_rows,
    }

    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())