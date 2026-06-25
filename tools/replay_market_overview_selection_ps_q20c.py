# path: ./tools/replay_market_overview_selection_ps_q20c.py
# desc: PS-Q20C compact read-only replay diagnostic for market.overview consumer-row selection. Applies the PS-Q20B contract to bounded timestamp windows and emits summary-only evidence.

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from datetime import timedelta
import json
from pathlib import Path
import sys
from typing import Any, Mapping

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "btcts_next" / "src"
for _path in (REPO_ROOT, SRC_ROOT):
    if str(_path) not in sys.path:
        sys.path.insert(0, str(_path))

from btcts.market_engine.market_state.consumer_row_selection import (  # noqa: E402
    CONSUMER_PREFERRED,
    DIAGNOSTIC_TRANSITION,
    FAIL_CLOSED,
    select_market_overview_consumer_preferred_row,
)
from tools.diagnose_market_overview_quality_block_ps_q19w import (  # noqa: E402
    DEFAULT_EXCHANGE,
    DEFAULT_KIND,
    DEFAULT_ROOT,
    DEFAULT_SYMBOL,
    _default_market_path,
    _extract_collector_ts_fast,
    _iso_z,
    _parse_iso_z,
)
from tools.diagnose_collector_reanchor_crossed_book_ps_q20a import _display_ts  # noqa: E402

PS_Q20C_REPLAY_VERSION = "prediction_warroom.ps_q20c_market_overview_selection_replay_diagnostic.v1"
DEFAULT_MAX_SECOND_SAMPLES = 20
HARD_MAX_SECOND_SAMPLES = 100
DEFAULT_OUTPUT_MAX_BYTES = 200_000
HARD_OUTPUT_MAX_BYTES = 1_000_000

SAFETY_FALSE_FIELDS = (
    "runtime_artifact_write_performed_by_replay",
    "status_artifact_write_performed_by_replay",
    "prediction_artifact_write_performed_by_replay",
    "view_artifact_write_performed_by_replay",
    "collector_state_write_performed_by_replay",
    "collector_runtime_behavior_changed",
    "ps_q19r_scoring_policy_changed",
    "scheduler_enabled",
    "producer_enabled",
    "warroom_ui_trigger_enabled",
    "ui_triggered_runner_execution",
    "approval_or_authorization_allowed",
    "ledger_append_allowed",
    "autotrade_trigger_allowed",
    "broker_private_api_allowed",
    "parameter_apply_allowed",
    "parameter_staging_write_allowed",
    "would_send_to_broker",
)


def _counter_dict(counter: Counter[str]) -> dict[str, int]:
    return {str(k): int(v) for k, v in sorted(counter.items()) if str(k)}


def _compact_selected_row(row: Mapping[str, Any] | None) -> dict[str, Any] | None:
    if row is None:
        return None
    return {
        "collector_ts": row.get("collector_ts"),
        "trust_state": row.get("trust_state"),
        "interpretation_bucket": row.get("interpretation_bucket"),
        "semantic_observer_status": row.get("semantic_observer_status"),
        "best_bid": row.get("best_bid"),
        "best_ask": row.get("best_ask"),
        "spread": row.get("spread"),
        "mid_price": row.get("mid_price"),
        "source_series_id": row.get("source_series_id"),
        "source_stream_session_id": row.get("source_stream_session_id"),
    }


def _second_summary(ts: str, rows: list[Mapping[str, Any]]) -> dict[str, Any]:
    selection = select_market_overview_consumer_preferred_row(rows)
    role_counts: Counter[str] = Counter(role.row_role for role in selection.row_roles)
    reason_counts: Counter[str] = Counter()
    source_series_counts: Counter[str] = Counter()
    source_stream_counts: Counter[str] = Counter()
    for role in selection.row_roles:
        reason_counts.update(role.quality_reasons)
        source_series_counts[str(role.row.get("source_series_id") or "")]
        source_stream_counts[str(role.row.get("source_stream_session_id") or "")]
        source_series_counts[str(role.row.get("source_series_id") or "")] += 1
        source_stream_counts[str(role.row.get("source_stream_session_id") or "")] += 1
    return {
        "collector_ts": ts,
        "input_row_count": selection.input_row_count,
        "selection_state": selection.selection_state,
        "selected_row_index": selection.selected_row_index,
        "consumer_preferred_count": selection.consumer_preferred_count,
        "diagnostic_transition_count": selection.diagnostic_transition_count,
        "mixed_preferred_and_diagnostic": bool(selection.consumer_preferred_count and selection.diagnostic_transition_count),
        "blocked_reasons": list(selection.blocked_reasons),
        "warning_reasons": list(selection.warning_reasons),
        "role_counts": _counter_dict(role_counts),
        "quality_reason_counts": _counter_dict(reason_counts),
        "source_series_id_counts": _counter_dict(source_series_counts),
        "source_stream_session_id_counts": _counter_dict(source_stream_counts),
        "selected_row": _compact_selected_row(selection.selected_row),
    }


def replay_market_overview_selection_ps_q20c(
    *,
    market_path: Path,
    target_ts: str,
    window_sec: int = 90,
    display_timezone: str = "Asia/Tokyo",
    max_second_samples: int = DEFAULT_MAX_SECOND_SAMPLES,
) -> dict[str, Any]:
    target = _parse_iso_z(target_ts)
    target_s = _iso_z(target)
    window = max(0, int(window_sec))
    start_s = _iso_z(target - timedelta(seconds=window))
    end_s = _iso_z(target + timedelta(seconds=window))
    sample_limit = min(max(int(max_second_samples), 0), HARD_MAX_SECOND_SAMPLES)
    blockers: list[str] = []
    warnings: list[str] = []

    if not market_path.exists():
        blockers.append("market_overview_path_missing")
        return {
            "ok": False,
            "ps_q20c_version": PS_Q20C_REPLAY_VERSION,
            "source_market_path": str(market_path),
            "time_axis": {
                "canonical_timezone": "UTC",
                "display_timezone": display_timezone,
                "target_ts_utc": target_s,
                "target_ts_display": _display_ts(target, display_timezone),
                "window_start_ts_utc": start_s,
                "window_end_ts_utc": end_s,
            },
            "blocked_reasons": blockers,
            "warning_reasons": warnings,
            "read_only_replay_diagnostic": True,
            "bounded_gpt_friendly_output": True,
            **{field: False for field in SAFETY_FALSE_FIELDS},
        }

    scanned_lines = 0
    parsed_window_records = 0
    malformed_window_lines = 0
    entered_window = False
    rows_by_second: dict[str, list[Mapping[str, Any]]] = defaultdict(list)

    with market_path.open("r", encoding="utf-8", errors="replace") as fh:
        for line in fh:
            scanned_lines += 1
            ts = _extract_collector_ts_fast(line)
            if not ts:
                continue
            if ts < start_s:
                continue
            if ts > end_s:
                if entered_window:
                    break
                continue
            entered_window = True
            try:
                record = json.loads(line)
            except Exception:
                malformed_window_lines += 1
                continue
            if not isinstance(record, Mapping):
                malformed_window_lines += 1
                continue
            parsed_window_records += 1
            rows_by_second[ts].append(record)

    if parsed_window_records == 0:
        warnings.append("market_overview_window_records_missing")

    selection_state_counts: Counter[str] = Counter()
    role_counts_total: Counter[str] = Counter()
    quality_reason_counts_total: Counter[str] = Counter()
    source_series_counts_total: Counter[str] = Counter()
    source_stream_counts_total: Counter[str] = Counter()
    second_summaries: list[dict[str, Any]] = []
    mixed_second_count = 0
    fail_closed_second_count = 0
    preferred_second_count = 0
    diagnostic_row_count = 0
    preferred_row_count = 0

    for ts in sorted(rows_by_second):
        summary = _second_summary(ts, rows_by_second[ts])
        second_summaries.append(summary)
        selection_state_counts[str(summary["selection_state"])] += 1
        preferred_row_count += int(summary["consumer_preferred_count"])
        diagnostic_row_count += int(summary["diagnostic_transition_count"])
        if summary["selection_state"] == CONSUMER_PREFERRED:
            preferred_second_count += 1
        if summary["selection_state"] == FAIL_CLOSED:
            fail_closed_second_count += 1
        if summary["mixed_preferred_and_diagnostic"]:
            mixed_second_count += 1
        role_counts_total.update(summary["role_counts"])
        quality_reason_counts_total.update(summary["quality_reason_counts"])
        source_series_counts_total.update(summary["source_series_id_counts"])
        source_stream_counts_total.update(summary["source_stream_session_id_counts"])

    mixed_samples = [s for s in second_summaries if s["mixed_preferred_and_diagnostic"]][:sample_limit]
    fail_closed_samples = [s for s in second_summaries if s["selection_state"] == FAIL_CLOSED][:sample_limit]
    preferred_samples = [s for s in second_summaries if s["selection_state"] == CONSUMER_PREFERRED][:sample_limit]

    false_quality_block_candidate_count = mixed_second_count
    preferred_contract_likely_useful = bool(false_quality_block_candidate_count > 0)

    return {
        "ok": bool(not blockers and parsed_window_records > 0),
        "ps_q20c_version": PS_Q20C_REPLAY_VERSION,
        "source_market_path": str(market_path),
        "time_axis": {
            "canonical_timezone": "UTC",
            "display_timezone": display_timezone,
            "target_ts_utc": target_s,
            "target_ts_display": _display_ts(target, display_timezone),
            "window_start_ts_utc": start_s,
            "window_end_ts_utc": end_s,
        },
        "size_policy": {
            "bounded_gpt_friendly_output": True,
            "summary_only_default": True,
            "raw_full_window_records_included": False,
            "max_second_samples": sample_limit,
            "hard_max_second_samples": HARD_MAX_SECOND_SAMPLES,
            "default_output_max_bytes": DEFAULT_OUTPUT_MAX_BYTES,
            "hard_output_max_bytes": HARD_OUTPUT_MAX_BYTES,
        },
        "scan_summary": {
            "scanned_lines": scanned_lines,
            "parsed_window_record_count": parsed_window_records,
            "malformed_window_lines": malformed_window_lines,
            "second_count": len(second_summaries),
            "preferred_second_count": preferred_second_count,
            "fail_closed_second_count": fail_closed_second_count,
            "mixed_preferred_and_diagnostic_second_count": mixed_second_count,
            "consumer_preferred_row_count": preferred_row_count,
            "diagnostic_transition_row_count": diagnostic_row_count,
            "false_quality_block_candidate_second_count": false_quality_block_candidate_count,
        },
        "selection_distribution": {
            "selection_state_counts": _counter_dict(selection_state_counts),
            "row_role_counts": _counter_dict(role_counts_total),
            "quality_reason_counts": _counter_dict(quality_reason_counts_total),
        },
        "source_distribution": {
            "source_series_id_counts": _counter_dict(source_series_counts_total),
            "source_stream_session_id_counts": _counter_dict(source_stream_counts_total),
        },
        "samples": {
            "mixed_preferred_and_diagnostic_seconds": mixed_samples,
            "fail_closed_seconds": fail_closed_samples,
            "preferred_seconds": preferred_samples,
        },
        "policy_observation": {
            "preferred_contract_likely_useful": preferred_contract_likely_useful,
            "ps_q19r_scoring_policy_changed": False,
            "collector_runtime_behavior_changed": False,
            "diagnostic_rows_retained": True,
            "do_not_score_rejected_rows": True,
            "do_not_trigger_or_trade_from_replay": True,
            "next_recommended_slice": "PS-Q20D_MARKET_OVERVIEW_PREFERRED_ROW_CONSUMER_INTEGRATION_DESIGN" if preferred_contract_likely_useful else "continue_observation",
        },
        "blocked_reasons": blockers,
        "warning_reasons": warnings,
        "read_only_replay_diagnostic": True,
        "bounded_gpt_friendly_output": True,
        **{field: False for field in SAFETY_FALSE_FIELDS},
    }


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="PS-Q20C replay market.overview row selection over a bounded window")
    parser.add_argument("--root", default=DEFAULT_ROOT)
    parser.add_argument("--market-path", default="")
    parser.add_argument("--target-ts", required=True)
    parser.add_argument("--window-sec", type=int, default=90)
    parser.add_argument("--display-timezone", default="Asia/Tokyo")
    parser.add_argument("--exchange", default=DEFAULT_EXCHANGE)
    parser.add_argument("--symbol", default=DEFAULT_SYMBOL)
    parser.add_argument("--kind", default=DEFAULT_KIND)
    parser.add_argument("--max-second-samples", type=int, default=DEFAULT_MAX_SECOND_SAMPLES)
    parser.add_argument("--output", default="")
    parser.add_argument("--output-max-bytes", type=int, default=DEFAULT_OUTPUT_MAX_BYTES)
    return parser


def _write_output_if_requested(packet: dict[str, Any], output: str, max_bytes: int) -> None:
    if not output:
        return
    limit = min(max(int(max_bytes), 1), HARD_OUTPUT_MAX_BYTES)
    text = json.dumps(packet, ensure_ascii=False, indent=2, sort_keys=True, default=str) + "\n"
    encoded = text.encode("utf-8")
    if len(encoded) > limit:
        raise RuntimeError(f"compact replay output exceeds limit: bytes={len(encoded)} limit={limit}")
    Path(output).write_text(text, encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    market_path = Path(args.market_path) if args.market_path else _default_market_path(str(args.root), str(args.target_ts), str(args.exchange), str(args.symbol), str(args.kind))
    packet = replay_market_overview_selection_ps_q20c(
        market_path=market_path,
        target_ts=str(args.target_ts),
        window_sec=int(args.window_sec),
        display_timezone=str(args.display_timezone),
        max_second_samples=int(args.max_second_samples),
    )
    text = json.dumps(packet, ensure_ascii=False, indent=2, sort_keys=True, default=str)
    print(text)
    _write_output_if_requested(packet, str(args.output), int(args.output_max_bytes))
    return 0 if packet.get("ok") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
