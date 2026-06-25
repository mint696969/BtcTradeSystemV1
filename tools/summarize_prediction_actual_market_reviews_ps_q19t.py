# path: ./tools/summarize_prediction_actual_market_reviews_ps_q19t.py
# desc: PS-Q19T read-only helper to summarize multiple PS-Q19R prediction-vs-actual review JSON packets. No writes, scheduler, UI trigger, AutoTrade, broker, ledger, or parameter behavior.

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import glob
import json
from pathlib import Path
import sys
from typing import Any, Iterable, Mapping

REPO_ROOT = Path(__file__).resolve().parents[1]

PS_Q19T_SUMMARY_VERSION = "prediction_warroom.ps_q19t_multi_window_review_summary.v1"
ALIGNMENT_KEYS = (
    "direction_match",
    "direction_mismatch",
    "range_or_neutral_match",
    "range_or_neutral_broken",
    "actual_unavailable",
    "not_scored_non_directional",
)
SAFETY_FALSE_FIELDS = (
    "runtime_artifact_write_performed_by_summary",
    "status_artifact_write_performed_by_summary",
    "prediction_artifact_write_performed_by_summary",
    "view_artifact_write_performed_by_summary",
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


def _to_float(value: Any) -> float | None:
    try:
        if value is None or value == "":
            return None
        return float(value)
    except Exception:
        return None


def _to_int(value: Any) -> int | None:
    try:
        if value is None or value == "":
            return None
        return int(value)
    except Exception:
        return None


def _load_json(path: Path) -> tuple[Mapping[str, Any] | None, str | None]:
    try:
        loaded = json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception as exc:  # noqa: BLE001
        return None, f"json_load_failed:{exc.__class__.__name__}"
    if not isinstance(loaded, Mapping):
        return None, "json_root_not_object"
    return loaded, None


def _stdin_payload() -> tuple[Mapping[str, Any] | None, str | None]:
    text = sys.stdin.read()
    if not text.strip():
        return None, "stdin_empty"
    try:
        loaded = json.loads(text)
    except Exception as exc:  # noqa: BLE001
        return None, f"stdin_json_load_failed:{exc.__class__.__name__}"
    if not isinstance(loaded, Mapping):
        return None, "stdin_json_root_not_object"
    return loaded, None


def _expand_paths(paths: Iterable[str], globs: Iterable[str]) -> list[Path]:
    out: list[Path] = []
    seen: set[str] = set()
    for raw in paths:
        if not raw:
            continue
        path = Path(raw)
        key = str(path.resolve()) if path.exists() else str(path)
        if key not in seen:
            out.append(path)
            seen.add(key)
    for pattern in globs:
        if not pattern:
            continue
        for item in glob.glob(pattern):
            path = Path(item)
            key = str(path.resolve()) if path.exists() else str(path)
            if key not in seen:
                out.append(path)
                seen.add(key)
    return out


def _review_rows(packet: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    rows = packet.get("review_rows")
    return [row for row in rows if isinstance(row, Mapping)] if isinstance(rows, list) else []


def _actual_by_horizon(packet: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    raw = packet.get("actual_by_horizon")
    return {str(k): v for k, v in raw.items() if isinstance(v, Mapping)} if isinstance(raw, Mapping) else {}


def _review_key(packet: Mapping[str, Any], index: int, path: str) -> str:
    generated_at = str(packet.get("prediction_generated_at") or "")
    if generated_at:
        return generated_at
    if path:
        return path
    return f"stdin:{index}"


def summarize_prediction_actual_market_reviews(
    packets: list[Mapping[str, Any]],
    *,
    source_paths: list[str] | None = None,
) -> dict[str, Any]:
    source_paths = source_paths or [""] * len(packets)
    blockers: list[str] = []
    warnings: list[str] = []
    window_summaries: list[dict[str, Any]] = []
    overall_alignment: Counter[str] = Counter()
    horizon_direction_counts: dict[str, Counter[str]] = defaultdict(Counter)
    horizon_alignment_counts: dict[str, Counter[str]] = defaultdict(Counter)
    horizon_return_values: dict[str, list[float]] = defaultdict(list)
    family_alignment_counts: dict[str, Counter[str]] = defaultdict(Counter)
    family_direction_counts: dict[str, Counter[str]] = defaultdict(Counter)
    actual_available_total = 0
    review_row_total = 0

    if not packets:
        blockers.append("review_packets_missing")

    for idx, packet in enumerate(packets):
        path = source_paths[idx] if idx < len(source_paths) else ""
        rows = _review_rows(packet)
        actual = _actual_by_horizon(packet)
        alignment = Counter(str(k) for k, v in (packet.get("alignment_summary") or {}).items() for _ in range(int(v)) if isinstance(packet.get("alignment_summary"), Mapping))
        row_alignment = Counter(str(row.get("alignment_hint") or "") for row in rows)
        if not alignment and row_alignment:
            alignment = row_alignment
        actual_available = sum(1 for row in rows if row.get("actual_available") is True)
        review_count = len(rows)
        quality_rejected_horizons = sorted(
            str(h)
            for h, item in actual.items()
            if item.get("actual_quality_ok") is False or item.get("available") is False and item.get("actual_quality_reasons")
        )
        window_summary = {
            "window_index": idx,
            "review_key": _review_key(packet, idx, path),
            "source_path": path,
            "ok": packet.get("ok") is True,
            "prediction_generated_at": str(packet.get("prediction_generated_at") or ""),
            "review_row_count": review_count,
            "actual_available_row_count": actual_available,
            "actual_available_ratio": (actual_available / review_count) if review_count else 0.0,
            "alignment_summary": dict(alignment),
            "warning_reasons": list(packet.get("warning_reasons") or []) if isinstance(packet.get("warning_reasons"), list) else [],
            "blocked_reasons": list(packet.get("blocked_reasons") or []) if isinstance(packet.get("blocked_reasons"), list) else [],
            "quality_rejected_horizons": quality_rejected_horizons,
            "horizon_realized_direction": {str(h): str(item.get("realized_direction") or "") for h, item in sorted(actual.items())},
            "horizon_return_bps": {str(h): item.get("return_bps") for h, item in sorted(actual.items())},
        }
        window_summaries.append(window_summary)
        if packet.get("ok") is not True:
            warnings.append(f"review_packet_not_ok:{idx}")
        if window_summary["blocked_reasons"]:
            warnings.append(f"review_packet_blocked:{idx}")
        if window_summary["warning_reasons"]:
            warnings.append(f"review_packet_warnings_present:{idx}")

        actual_available_total += actual_available
        review_row_total += review_count
        overall_alignment.update(alignment)
        for h, item in actual.items():
            direction = str(item.get("realized_direction") or "unknown")
            horizon_direction_counts[str(h)][direction] += 1
            rv = _to_float(item.get("return_bps"))
            if rv is not None and item.get("available") is True:
                horizon_return_values[str(h)].append(rv)
        for row in rows:
            family = str(row.get("family") or "unknown")
            horizon = str(row.get("horizon_sec") or "unknown")
            alignment_key = str(row.get("alignment_hint") or "unknown")
            direction = str(row.get("realized_direction") or "unknown")
            family_alignment_counts[family][alignment_key] += 1
            family_direction_counts[family][direction] += 1
            horizon_alignment_counts[horizon][alignment_key] += 1

    horizon_return_summary = {}
    for horizon, values in sorted(horizon_return_values.items(), key=lambda kv: _to_int(kv[0]) or 0):
        if values:
            horizon_return_summary[horizon] = {
                "count": len(values),
                "average_return_bps": sum(values) / len(values),
                "min_return_bps": min(values),
                "max_return_bps": max(values),
            }

    packet = {
        "ok": bool(not blockers and packets),
        "ps_q19t_version": PS_Q19T_SUMMARY_VERSION,
        "source_review_count": len(packets),
        "source_paths": source_paths,
        "window_summaries": window_summaries,
        "review_row_total": review_row_total,
        "actual_available_row_total": actual_available_total,
        "actual_available_ratio": (actual_available_total / review_row_total) if review_row_total else 0.0,
        "overall_alignment_summary": {key: overall_alignment.get(key, 0) for key in ALIGNMENT_KEYS if overall_alignment.get(key, 0)},
        "horizon_direction_summary": {h: dict(c) for h, c in sorted(horizon_direction_counts.items(), key=lambda kv: _to_int(kv[0]) or 0)},
        "horizon_alignment_summary": {h: dict(c) for h, c in sorted(horizon_alignment_counts.items(), key=lambda kv: _to_int(kv[0]) or 0)},
        "horizon_return_summary": horizon_return_summary,
        "family_alignment_summary": {k: dict(v) for k, v in sorted(family_alignment_counts.items())},
        "family_direction_summary": {k: dict(v) for k, v in sorted(family_direction_counts.items())},
        "blocked_reasons": list(dict.fromkeys(blockers)),
        "warning_reasons": list(dict.fromkeys(warnings)),
        "read_only_summary": True,
        **{field: False for field in SAFETY_FALSE_FIELDS},
    }
    return packet


def load_and_summarize_review_files(paths: list[Path], *, stdin_packet: Mapping[str, Any] | None = None) -> dict[str, Any]:
    packets: list[Mapping[str, Any]] = []
    source_paths: list[str] = []
    warnings: list[str] = []
    if stdin_packet is not None:
        packets.append(stdin_packet)
        source_paths.append("stdin")
    for path in paths:
        payload, error = _load_json(path)
        if error:
            warnings.append(f"review_file_unreadable:{path}:{error}")
            continue
        if payload is not None:
            packets.append(payload)
            source_paths.append(str(path))
    summary = summarize_prediction_actual_market_reviews(packets, source_paths=source_paths)
    if warnings:
        summary["warning_reasons"] = list(dict.fromkeys(list(summary.get("warning_reasons") or []) + warnings))
    return summary


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="PS-Q19T summarize multiple PS-Q19R review JSON packets")
    parser.add_argument("--review-path", action="append", default=[], help="Path to a saved PS-Q19R JSON review packet. Repeatable.")
    parser.add_argument("--review-glob", action="append", default=[], help="Glob pattern for saved PS-Q19R JSON review packets. Repeatable.")
    parser.add_argument("--stdin-json", action="store_true", help="Read one PS-Q19R JSON review packet from stdin.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    stdin_packet = None
    stdin_error = None
    if args.stdin_json:
        stdin_packet, stdin_error = _stdin_payload()
    paths = _expand_paths(args.review_path, args.review_glob)
    packet = load_and_summarize_review_files(paths, stdin_packet=stdin_packet)
    if stdin_error and stdin_error != "stdin_empty":
        packet["warning_reasons"] = list(dict.fromkeys(list(packet.get("warning_reasons") or []) + [stdin_error]))
    print(json.dumps(packet, ensure_ascii=False, indent=2, sort_keys=True, default=str))
    return 0 if packet.get("ok") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
