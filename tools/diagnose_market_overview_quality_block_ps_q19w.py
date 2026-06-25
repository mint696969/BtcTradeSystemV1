# path: ./tools/diagnose_market_overview_quality_block_ps_q19w.py
# desc: PS-Q19W read-only diagnostic helper for market.overview quality-block windows. Scans a bounded timestamp window in JSONL, classifies trusted/structural/crossed/negative-spread rows, and does not write artifacts or trigger runtime behavior.

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
from typing import Any, Iterable, Mapping

PS_Q19W_DIAGNOSIS_VERSION = "prediction_warroom.ps_q19w_market_overview_quality_block_diagnosis.v1"
DEFAULT_ROOT = r"D:\btc_ts_hot"
DEFAULT_EXCHANGE = "bitflyer"
DEFAULT_SYMBOL = "FX_BTC_JPY"
DEFAULT_KIND = "market.overview"
SAFETY_FALSE_FIELDS = (
    "runtime_artifact_write_performed_by_diagnosis",
    "status_artifact_write_performed_by_diagnosis",
    "prediction_artifact_write_performed_by_diagnosis",
    "view_artifact_write_performed_by_diagnosis",
    "collector_state_write_performed_by_diagnosis",
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


def _parse_iso_z(value: str) -> datetime:
    text = str(value).strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    dt = datetime.fromisoformat(text)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def _iso_z(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _date_from_ts(target_ts: str) -> str:
    return _iso_z(_parse_iso_z(target_ts))[:10]


def _default_market_path(root: str, target_ts: str, exchange: str, symbol: str, kind: str) -> Path:
    date = _date_from_ts(target_ts)
    return Path(str(root).rstrip("\\/")) / "data" / "market_state" / f"exchange={exchange}" / f"symbol={symbol}" / f"type={kind}" / f"date={date}" / "part-00001.jsonl"


def _extract_collector_ts_fast(line: str) -> str:
    marker = '"collector_ts":"'
    idx = line.find(marker)
    if idx < 0:
        marker = '"collector_ts": "'
        idx = line.find(marker)
    if idx < 0:
        return ""
    start = idx + len(marker)
    end = line.find('"', start)
    return line[start:end] if end > start else ""


def _to_float(value: Any) -> float | None:
    try:
        if value is None or value == "":
            return None
        return float(value)
    except Exception:
        return None


def _record_quality_reasons(record: Mapping[str, Any]) -> list[str]:
    reasons: list[str] = []
    trust_state = str(record.get("trust_state") or "")
    bucket = str(record.get("interpretation_bucket") or "")
    spread = _to_float(record.get("spread"))
    bid = _to_float(record.get("best_bid"))
    ask = _to_float(record.get("best_ask"))
    semantic_status = str(record.get("semantic_observer_status") or "")
    if trust_state != "trusted":
        reasons.append("market_overview_not_trusted")
    if bucket != "allow_structural_use":
        reasons.append("market_overview_not_allow_structural_use")
    if spread is not None and spread < 0:
        reasons.append("market_overview_negative_spread")
    if bid is not None and ask is not None and bid > ask:
        reasons.append("market_overview_crossed_book")
    if semantic_status == "broken":
        reasons.append("market_overview_semantic_observer_broken")
    return reasons


def _projection(record: Mapping[str, Any], reasons: list[str]) -> dict[str, Any]:
    return {
        "collector_ts": str(record.get("collector_ts") or ""),
        "exchange_ts": record.get("exchange_ts"),
        "trust_state": str(record.get("trust_state") or ""),
        "boundary_reason": str(record.get("boundary_reason") or ""),
        "continuity_state": str(record.get("continuity_state") or ""),
        "interpretation_bucket": str(record.get("interpretation_bucket") or ""),
        "interpretation_reason": str(record.get("interpretation_reason") or ""),
        "semantic_observer_status": str(record.get("semantic_observer_status") or ""),
        "best_bid": record.get("best_bid"),
        "best_ask": record.get("best_ask"),
        "spread": record.get("spread"),
        "mid_price": record.get("mid_price"),
        "quality_ok": not reasons,
        "quality_reasons": reasons,
    }


def _spread_summary(values: Iterable[float]) -> dict[str, Any]:
    vals = list(values)
    if not vals:
        return {"count": 0}
    return {
        "count": len(vals),
        "min": min(vals),
        "max": max(vals),
        "average": sum(vals) / len(vals),
        "negative_count": sum(1 for v in vals if v < 0),
        "zero_count": sum(1 for v in vals if v == 0),
    }


def diagnose_market_overview_quality_block(
    *,
    market_path: Path,
    target_ts: str,
    window_sec: int = 90,
    exact_second: bool = True,
    max_rejected_records: int = 20,
    max_transition_records: int = 30,
) -> dict[str, Any]:
    blockers: list[str] = []
    warnings: list[str] = []
    target = _parse_iso_z(target_ts)
    window = max(0, int(window_sec))
    start = target - timedelta(seconds=window)
    end = target + timedelta(seconds=window)
    start_s = _iso_z(start)
    end_s = _iso_z(end)
    target_s = _iso_z(target)
    if not market_path.exists():
        blockers.append("market_overview_path_missing")
        return {
            "ok": False,
            "ps_q19w_version": PS_Q19W_DIAGNOSIS_VERSION,
            "source_market_path": str(market_path),
            "target_ts": target_s,
            "window_start_ts": start_s,
            "window_end_ts": end_s,
            "blocked_reasons": blockers,
            "warning_reasons": warnings,
            "read_only_diagnosis": True,
            **{field: False for field in SAFETY_FALSE_FIELDS},
        }

    scanned_lines = 0
    parsed_window_records = 0
    malformed_window_lines = 0
    window_records: list[dict[str, Any]] = []
    rejected_records: list[dict[str, Any]] = []
    transition_records: list[dict[str, Any]] = []
    trust_counts: Counter[str] = Counter()
    bucket_counts: Counter[str] = Counter()
    boundary_counts: Counter[str] = Counter()
    continuity_counts: Counter[str] = Counter()
    semantic_counts: Counter[str] = Counter()
    quality_reason_counts: Counter[str] = Counter()
    per_second: dict[str, Counter[str]] = defaultdict(Counter)
    spreads: list[float] = []
    crossed_count = 0
    exact_second_record_count = 0
    exact_second_rejected_count = 0
    exact_second_quality_ok_count = 0
    entered_window = False

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
            if exact_second and ts != target_s:
                continue
            try:
                record = json.loads(line)
            except Exception:
                malformed_window_lines += 1
                continue
            if not isinstance(record, Mapping):
                malformed_window_lines += 1
                continue
            parsed_window_records += 1
            reasons = _record_quality_reasons(record)
            quality_ok = not reasons
            trust = str(record.get("trust_state") or "")
            bucket = str(record.get("interpretation_bucket") or "")
            boundary = str(record.get("boundary_reason") or "")
            continuity = str(record.get("continuity_state") or "")
            semantic = str(record.get("semantic_observer_status") or "")
            trust_counts[trust] += 1
            bucket_counts[bucket] += 1
            boundary_counts[boundary] += 1
            continuity_counts[continuity] += 1
            semantic_counts[semantic] += 1
            quality_reason_counts.update(reasons)
            spread = _to_float(record.get("spread"))
            bid = _to_float(record.get("best_bid"))
            ask = _to_float(record.get("best_ask"))
            if spread is not None:
                spreads.append(spread)
            if bid is not None and ask is not None and bid > ask:
                crossed_count += 1
            per_second[ts]["record_count"] += 1
            per_second[ts]["quality_ok_count" if quality_ok else "rejected_count"] += 1
            if ts == target_s:
                exact_second_record_count += 1
                if quality_ok:
                    exact_second_quality_ok_count += 1
                else:
                    exact_second_rejected_count += 1
            projection = _projection(record, reasons)
            if len(transition_records) < max_transition_records:
                transition_records.append(projection)
            if not quality_ok and len(rejected_records) < max_rejected_records:
                rejected_records.append(projection)
            window_records.append(projection)

    if parsed_window_records == 0:
        warnings.append("market_overview_window_records_missing")
    mixed_seconds = []
    for ts, counts in sorted(per_second.items()):
        if counts.get("quality_ok_count", 0) and counts.get("rejected_count", 0):
            mixed_seconds.append(ts)

    exact_second_mixed_quality = bool(exact_second_record_count and exact_second_quality_ok_count and exact_second_rejected_count)
    fail_closed_recommended = bool(rejected_records or quality_reason_counts)
    same_second_quality_ok_candidate_present = bool(exact_second_mixed_quality)
    diagnosis = "market_overview_quality_stable"
    if exact_second_mixed_quality:
        diagnosis = "same_second_mixed_quality_reanchor_and_trusted_records"
    elif rejected_records:
        diagnosis = "market_overview_quality_rejected_records_present"

    return {
        "ok": bool(not blockers and parsed_window_records > 0),
        "ps_q19w_version": PS_Q19W_DIAGNOSIS_VERSION,
        "source_market_path": str(market_path),
        "target_ts": target_s,
        "window_sec": window,
        "exact_second_only": bool(exact_second),
        "window_start_ts": start_s,
        "window_end_ts": end_s,
        "scanned_lines": scanned_lines,
        "parsed_window_record_count": parsed_window_records,
        "malformed_window_lines": malformed_window_lines,
        "exact_second_record_count": exact_second_record_count,
        "exact_second_quality_ok_count": exact_second_quality_ok_count,
        "exact_second_rejected_count": exact_second_rejected_count,
        "exact_second_mixed_quality": exact_second_mixed_quality,
        "mixed_quality_second_count": len(mixed_seconds),
        "mixed_quality_seconds": mixed_seconds[:20],
        "trust_state_counts": dict(trust_counts),
        "interpretation_bucket_counts": dict(bucket_counts),
        "boundary_reason_counts": dict(boundary_counts),
        "continuity_state_counts": dict(continuity_counts),
        "semantic_observer_status_counts": dict(semantic_counts),
        "spread_summary": _spread_summary(spreads),
        "crossed_book_count": crossed_count,
        "quality_reason_counts": dict(quality_reason_counts),
        "rejected_record_count": sum(per_second[ts].get("rejected_count", 0) for ts in per_second),
        "quality_ok_record_count": sum(per_second[ts].get("quality_ok_count", 0) for ts in per_second),
        "rejected_records_sample": rejected_records,
        "transition_records_sample": transition_records,
        "diagnosis": diagnosis,
        "policy_observation": {
            "fail_closed_recommended": fail_closed_recommended,
            "quality_rejected_records_should_not_be_scored": True,
            "same_second_quality_ok_candidate_present": same_second_quality_ok_candidate_present,
            "collector_side_reanchor_or_crossed_book_diagnosis_needed": bool(rejected_records),
            "do_not_auto_retry_or_trade_from_diagnosis": True,
        },
        "blocked_reasons": blockers,
        "warning_reasons": warnings,
        "read_only_diagnosis": True,
        **{field: False for field in SAFETY_FALSE_FIELDS},
    }


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="PS-Q19W diagnose market.overview quality block around a target timestamp")
    parser.add_argument("--root", default=DEFAULT_ROOT)
    parser.add_argument("--market-path", default="", help="Explicit market.overview JSONL path. If omitted, derive from --root and --target-ts.")
    parser.add_argument("--target-ts", required=True)
    parser.add_argument("--window-sec", type=int, default=90)
    parser.add_argument("--all-window-records", action="store_true", help="Analyze all records in target±window instead of exact target second only.")
    parser.add_argument("--exchange", default=DEFAULT_EXCHANGE)
    parser.add_argument("--symbol", default=DEFAULT_SYMBOL)
    parser.add_argument("--kind", default=DEFAULT_KIND)
    parser.add_argument("--max-rejected-records", type=int, default=20)
    parser.add_argument("--max-transition-records", type=int, default=30)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    market_path = Path(args.market_path) if args.market_path else _default_market_path(str(args.root), str(args.target_ts), str(args.exchange), str(args.symbol), str(args.kind))
    packet = diagnose_market_overview_quality_block(
        market_path=market_path,
        target_ts=str(args.target_ts),
        window_sec=int(args.window_sec),
        exact_second=not bool(args.all_window_records),
        max_rejected_records=int(args.max_rejected_records),
        max_transition_records=int(args.max_transition_records),
    )
    print(json.dumps(packet, ensure_ascii=False, indent=2, sort_keys=True, default=str))
    return 0 if packet.get("ok") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
