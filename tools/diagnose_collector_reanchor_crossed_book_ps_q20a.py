# path: ./tools/diagnose_collector_reanchor_crossed_book_ps_q20a.py
# desc: PS-Q20A compact read-only collector/reanchor/crossed-book diagnosis. It wraps PS-Q19W quality-block evidence with source/session/time-axis summaries, bounded samples, and repair candidates without writing runtime artifacts.

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
from typing import Any, Mapping
from zoneinfo import ZoneInfo

from tools.diagnose_market_overview_quality_block_ps_q19w import (
    DEFAULT_EXCHANGE,
    DEFAULT_KIND,
    DEFAULT_ROOT,
    DEFAULT_SYMBOL,
    SAFETY_FALSE_FIELDS,
    _default_market_path,
    _extract_collector_ts_fast,
    _iso_z,
    _parse_iso_z,
    _projection,
    _record_quality_reasons,
    _to_float,
)

PS_Q20A_DIAGNOSIS_VERSION = "prediction_warroom.ps_q20a_collector_reanchor_crossed_book_compact_diagnosis.v1"
DEFAULT_MAX_SAMPLES = 20
HARD_MAX_SAMPLES = 100
DEFAULT_OUTPUT_MAX_BYTES = 200_000
HARD_OUTPUT_MAX_BYTES = 1_000_000


def _display_ts(dt: datetime, timezone_name: str) -> str:
    try:
        tz = ZoneInfo(timezone_name)
    except Exception:
        tz = ZoneInfo("Asia/Tokyo")
    return dt.astimezone(tz).replace(microsecond=0).isoformat()


def _counter_dict(counter: Counter[str]) -> dict[str, int]:
    return {k: int(v) for k, v in sorted(counter.items()) if k != ""}


def _compact_row(record: Mapping[str, Any], reasons: list[str], *, row_index: int) -> dict[str, Any]:
    row = _projection(record, reasons)
    row.update(
        {
            "row_index_in_window": row_index,
            "source_series_id": str(record.get("source_series_id") or ""),
            "source_stream_session_id": str(record.get("source_stream_session_id") or ""),
            "top_book_summary": {
                "best_bid": record.get("best_bid"),
                "best_ask": record.get("best_ask"),
                "spread": record.get("spread"),
                "mid_price": record.get("mid_price"),
            },
        }
    )
    return row


def _transition_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    first_bad: dict[str, Any] | None = None
    first_recovered: dict[str, Any] | None = None
    for row in rows:
        if first_bad is None and not bool(row.get("quality_ok")):
            first_bad = row
            continue
        if first_bad is not None and bool(row.get("quality_ok")):
            first_recovered = row
            break

    if first_bad is None:
        return {
            "transition_state": "no_rejected_row_in_window",
            "first_bad_row": None,
            "first_recovered_row": None,
            "bad_to_good_row_gap": None,
            "bad_to_good_delta_sec": None,
        }
    if first_recovered is None:
        return {
            "transition_state": "rejected_without_recovery_in_window",
            "first_bad_row": first_bad,
            "first_recovered_row": None,
            "bad_to_good_row_gap": None,
            "bad_to_good_delta_sec": None,
        }

    bad_dt = _parse_iso_z(str(first_bad.get("collector_ts") or ""))
    good_dt = _parse_iso_z(str(first_recovered.get("collector_ts") or ""))
    return {
        "transition_state": "bad_to_good_recovery_observed",
        "first_bad_row": first_bad,
        "first_recovered_row": first_recovered,
        "bad_to_good_row_gap": int(first_recovered.get("row_index_in_window") or 0) - int(first_bad.get("row_index_in_window") or 0),
        "bad_to_good_delta_sec": (good_dt - bad_dt).total_seconds(),
    }


def _repair_candidates(*, rejected_count: int, crossed_count: int, mixed_second_count: int, bad_to_good_state: str) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    if mixed_second_count > 0:
        out.append(
            {
                "candidate_id": "separate_consumer_preferred_from_diagnostic_rows",
                "priority": "P0",
                "reason": "same-second trusted and rejected market.overview rows coexist",
                "implementation_bias": "keep rejected rows visible for diagnosis, but expose a bounded preferred-row contract for consumers",
            }
        )
    if crossed_count > 0:
        out.append(
            {
                "candidate_id": "quarantine_crossed_book_as_transition_diagnostic",
                "priority": "P0",
                "reason": "crossed or negative top-of-book rows were observed",
                "implementation_bias": "do not score or trigger from crossed rows; classify as reanchor/transition evidence",
            }
        )
    if bad_to_good_state == "bad_to_good_recovery_observed":
        out.append(
            {
                "candidate_id": "add_row_quality_rank_and_recovery_trace",
                "priority": "P1",
                "reason": "a rejected row recovered to a trusted row inside the bounded window",
                "implementation_bias": "record sequence and recovery evidence so later replay can explain which row was consumer-preferred",
            }
        )
    if rejected_count == 0:
        out.append(
            {
                "candidate_id": "no_repair_needed_for_this_window",
                "priority": "observe",
                "reason": "no rejected market.overview rows were observed in this bounded window",
                "implementation_bias": "continue bounded observation rather than changing collector semantics from this window alone",
            }
        )
    return out


def diagnose_collector_reanchor_crossed_book_ps_q20a(
    *,
    market_path: Path,
    target_ts: str,
    window_sec: int = 90,
    display_timezone: str = "Asia/Tokyo",
    max_samples: int = DEFAULT_MAX_SAMPLES,
) -> dict[str, Any]:
    target = _parse_iso_z(target_ts)
    target_s = _iso_z(target)
    start_s = _iso_z(target - timedelta(seconds=max(0, int(window_sec))))
    end_s = _iso_z(target + timedelta(seconds=max(0, int(window_sec))))
    sample_limit = min(max(int(max_samples), 0), HARD_MAX_SAMPLES)
    blockers: list[str] = []
    warnings: list[str] = []

    if not market_path.exists():
        blockers.append("market_overview_path_missing")
        return {
            "ok": False,
            "ps_q20a_version": PS_Q20A_DIAGNOSIS_VERSION,
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
            "read_only_diagnosis": True,
            "bounded_gpt_friendly_output": True,
            **{field: False for field in SAFETY_FALSE_FIELDS},
        }

    scanned_lines = 0
    parsed_window_records = 0
    malformed_window_lines = 0
    entered_window = False
    row_index = 0
    compact_rows: list[dict[str, Any]] = []
    rejected_samples: list[dict[str, Any]] = []
    trusted_samples: list[dict[str, Any]] = []
    source_series_counts: Counter[str] = Counter()
    source_stream_counts: Counter[str] = Counter()
    trust_counts: Counter[str] = Counter()
    bucket_counts: Counter[str] = Counter()
    boundary_counts: Counter[str] = Counter()
    continuity_counts: Counter[str] = Counter()
    quality_reason_counts: Counter[str] = Counter()
    per_second: dict[str, Counter[str]] = defaultdict(Counter)
    crossed_count = 0
    negative_spread_count = 0

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
            row_index += 1
            parsed_window_records += 1
            reasons = _record_quality_reasons(record)
            quality_ok = not reasons
            trust = str(record.get("trust_state") or "")
            bucket = str(record.get("interpretation_bucket") or "")
            boundary = str(record.get("boundary_reason") or "")
            continuity = str(record.get("continuity_state") or "")
            source_series_id = str(record.get("source_series_id") or "")
            source_stream_session_id = str(record.get("source_stream_session_id") or "")
            trust_counts[trust] += 1
            bucket_counts[bucket] += 1
            boundary_counts[boundary] += 1
            continuity_counts[continuity] += 1
            source_series_counts[source_series_id] += 1
            source_stream_counts[source_stream_session_id] += 1
            quality_reason_counts.update(reasons)
            bid = _to_float(record.get("best_bid"))
            ask = _to_float(record.get("best_ask"))
            spread = _to_float(record.get("spread"))
            if spread is not None and spread < 0:
                negative_spread_count += 1
            if bid is not None and ask is not None and bid > ask:
                crossed_count += 1
            per_second[ts]["record_count"] += 1
            per_second[ts]["quality_ok_count" if quality_ok else "rejected_count"] += 1
            compact = _compact_row(record, reasons, row_index=row_index)
            compact_rows.append(compact)
            if quality_ok and len(trusted_samples) < sample_limit:
                trusted_samples.append(compact)
            if not quality_ok and len(rejected_samples) < sample_limit:
                rejected_samples.append(compact)

    if parsed_window_records == 0:
        warnings.append("market_overview_window_records_missing")

    mixed_seconds = [
        ts for ts, counts in sorted(per_second.items())
        if counts.get("quality_ok_count", 0) and counts.get("rejected_count", 0)
    ]
    transition = _transition_summary(compact_rows)
    rejected_count = sum(counts.get("rejected_count", 0) for counts in per_second.values())
    quality_ok_count = sum(counts.get("quality_ok_count", 0) for counts in per_second.values())
    repair_candidates = _repair_candidates(
        rejected_count=rejected_count,
        crossed_count=crossed_count,
        mixed_second_count=len(mixed_seconds),
        bad_to_good_state=str(transition.get("transition_state") or ""),
    )

    return {
        "ok": bool(not blockers and parsed_window_records > 0),
        "ps_q20a_version": PS_Q20A_DIAGNOSIS_VERSION,
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
            "max_samples": sample_limit,
            "hard_max_samples": HARD_MAX_SAMPLES,
            "default_output_max_bytes": DEFAULT_OUTPUT_MAX_BYTES,
            "hard_output_max_bytes": HARD_OUTPUT_MAX_BYTES,
        },
        "scan_summary": {
            "scanned_lines": scanned_lines,
            "parsed_window_record_count": parsed_window_records,
            "malformed_window_lines": malformed_window_lines,
            "quality_ok_record_count": quality_ok_count,
            "rejected_record_count": rejected_count,
            "mixed_quality_second_count": len(mixed_seconds),
            "mixed_quality_seconds_sample": mixed_seconds[:sample_limit],
        },
        "source_distribution": {
            "source_series_id_counts": _counter_dict(source_series_counts),
            "source_stream_session_id_counts": _counter_dict(source_stream_counts),
        },
        "quality_distribution": {
            "trust_state_counts": _counter_dict(trust_counts),
            "interpretation_bucket_counts": _counter_dict(bucket_counts),
            "boundary_reason_counts": _counter_dict(boundary_counts),
            "continuity_state_counts": _counter_dict(continuity_counts),
            "quality_reason_counts": _counter_dict(quality_reason_counts),
            "crossed_book_count": crossed_count,
            "negative_spread_count": negative_spread_count,
        },
        "bad_to_good_transition": transition,
        "samples": {
            "trusted_rows": trusted_samples,
            "rejected_rows": rejected_samples,
        },
        "repair_candidates": repair_candidates,
        "policy_observation": {
            "ps_q19r_scoring_policy_changed": False,
            "collector_side_repair_diagnosis": True,
            "separate_preferred_consumer_row_from_diagnostic_rejected_row": len(mixed_seconds) > 0,
            "do_not_score_rejected_rows": True,
            "do_not_trigger_or_trade_from_diagnosis": True,
        },
        "blocked_reasons": blockers,
        "warning_reasons": warnings,
        "read_only_diagnosis": True,
        "bounded_gpt_friendly_output": True,
        **{field: False for field in SAFETY_FALSE_FIELDS},
    }


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="PS-Q20A compact collector/reanchor/crossed-book diagnosis")
    parser.add_argument("--root", default=DEFAULT_ROOT)
    parser.add_argument("--market-path", default="")
    parser.add_argument("--target-ts", required=True, help="Target timestamp. JST offsets are accepted but normalized to UTC internally.")
    parser.add_argument("--window-sec", type=int, default=90)
    parser.add_argument("--display-timezone", default="Asia/Tokyo")
    parser.add_argument("--exchange", default=DEFAULT_EXCHANGE)
    parser.add_argument("--symbol", default=DEFAULT_SYMBOL)
    parser.add_argument("--kind", default=DEFAULT_KIND)
    parser.add_argument("--max-samples", type=int, default=DEFAULT_MAX_SAMPLES)
    parser.add_argument("--output", default="", help="Optional compact JSON output path. Stdout is always compact.")
    parser.add_argument("--output-max-bytes", type=int, default=DEFAULT_OUTPUT_MAX_BYTES)
    return parser


def _write_output_if_requested(packet: dict[str, Any], output: str, max_bytes: int) -> None:
    if not output:
        return
    limit = min(max(int(max_bytes), 1), HARD_OUTPUT_MAX_BYTES)
    text = json.dumps(packet, ensure_ascii=False, indent=2, sort_keys=True, default=str) + "\n"
    encoded = text.encode("utf-8")
    if len(encoded) > limit:
        raise RuntimeError(f"compact diagnosis output exceeds limit: bytes={len(encoded)} limit={limit}")
    Path(output).write_text(text, encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    market_path = Path(args.market_path) if args.market_path else _default_market_path(str(args.root), str(args.target_ts), str(args.exchange), str(args.symbol), str(args.kind))
    packet = diagnose_collector_reanchor_crossed_book_ps_q20a(
        market_path=market_path,
        target_ts=str(args.target_ts),
        window_sec=int(args.window_sec),
        display_timezone=str(args.display_timezone),
        max_samples=int(args.max_samples),
    )
    text = json.dumps(packet, ensure_ascii=False, indent=2, sort_keys=True, default=str)
    print(text)
    _write_output_if_requested(packet, str(args.output), int(args.output_max_bytes))
    return 0 if packet.get("ok") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
