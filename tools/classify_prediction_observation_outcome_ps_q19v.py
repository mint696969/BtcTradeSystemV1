# path: ./tools/classify_prediction_observation_outcome_ps_q19v.py
# desc: PS-Q19V read-only classifier for bounded producer observation outcomes, market-overview quality blocks, and partial observation usability. No writes, scheduler, UI trigger, AutoTrade, broker, ledger, or parameter behavior.

from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import sys
from typing import Any, Mapping

PS_Q19V_OUTCOME_VERSION = "prediction_warroom.ps_q19v_observation_outcome_policy.v1"
MARKET_QUALITY_BLOCKERS = (
    "market_overview_trust_state_not_trusted",
    "market_overview_interpretation_bucket_not_allow_structural_use",
)
MARKET_POINT_QUALITY_REJECTIONS = (
    "market_point_not_trusted",
    "market_point_not_structural_use",
    "market_point_negative_spread",
    "market_point_crossed_book",
)
SAFETY_FALSE_FIELDS = (
    "runtime_artifact_write_performed_by_classifier",
    "status_artifact_write_performed_by_classifier",
    "prediction_artifact_write_performed_by_classifier",
    "view_artifact_write_performed_by_classifier",
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


def _load_json(path: str) -> tuple[Mapping[str, Any] | None, str | None]:
    if not path:
        return None, None
    try:
        loaded = json.loads(Path(path).read_text(encoding="utf-8-sig"))
    except Exception as exc:  # noqa: BLE001
        return None, f"json_load_failed:{Path(path)}:{exc.__class__.__name__}"
    if not isinstance(loaded, Mapping):
        return None, f"json_root_not_object:{Path(path)}"
    return loaded, None


def _as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _as_map(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _to_int(value: Any, default: int = 0) -> int:
    try:
        if value is None or value == "":
            return default
        return int(value)
    except Exception:
        return default


def _to_float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None or value == "":
            return default
        return float(value)
    except Exception:
        return default


def _contains_any(items: list[str], needles: tuple[str, ...]) -> bool:
    return any(any(needle in item for needle in needles) for item in items)


def _producer_block_reasons(producer_packet: Mapping[str, Any]) -> list[str]:
    reasons = [str(item) for item in _as_list(producer_packet.get("blocked_reasons"))]
    for cycle in _as_list(producer_packet.get("cycle_packets")):
        if isinstance(cycle, Mapping):
            reasons.extend(str(item) for item in _as_list(cycle.get("blocked_reasons")))
    return list(dict.fromkeys(reasons))


def _producer_cycle_stats(producer_packet: Mapping[str, Any]) -> dict[str, Any]:
    cycles = [cycle for cycle in _as_list(producer_packet.get("cycle_packets")) if isinstance(cycle, Mapping)]
    blocked_cycles = [cycle for cycle in cycles if _as_list(cycle.get("blocked_reasons"))]
    successful_cycles = [cycle for cycle in cycles if cycle.get("latest_prediction_artifact_written") is True]
    generated = [str(cycle.get("generated_at") or "") for cycle in successful_cycles if cycle.get("generated_at")]
    return {
        "cycle_count": _to_int(producer_packet.get("cycle_count"), len(cycles)),
        "requested_max_cycles": _to_int(producer_packet.get("requested_max_cycles"), 0),
        "effective_max_cycles": _to_int(producer_packet.get("effective_max_cycles"), 0),
        "latest_prediction_artifact_written_count": _to_int(producer_packet.get("latest_prediction_artifact_written_count"), len(successful_cycles)),
        "status_artifact_written_count": _to_int(producer_packet.get("status_artifact_written_count"), 0),
        "blocked_cycle_count": len(blocked_cycles),
        "blocked_cycle_indexes": [cycle.get("cycle_index") for cycle in blocked_cycles],
        "last_success_generated_at": generated[-1] if generated else "",
        "request_state": str(producer_packet.get("request_state") or ""),
        "producer_ok": producer_packet.get("ok") is True,
        "stopped_by_stop_file": producer_packet.get("stopped_by_stop_file") is True,
    }


def _review_quality_rejections(review_packet: Mapping[str, Any]) -> dict[str, Any]:
    actual = _as_map(review_packet.get("actual_by_horizon"))
    rejected: dict[str, list[str]] = {}
    for horizon, item in actual.items():
        if not isinstance(item, Mapping):
            continue
        reasons = [str(r) for r in _as_list(item.get("actual_quality_reasons"))]
        if item.get("actual_quality_ok") is False or reasons:
            rejected[str(horizon)] = reasons
    warning_reasons = [str(item) for item in _as_list(review_packet.get("warning_reasons"))]
    return {
        "quality_rejected_horizons": sorted(rejected.keys(), key=lambda h: _to_int(h, 0)),
        "quality_rejected_horizon_reasons": rejected,
        "review_warning_reasons": warning_reasons,
        "market_point_quality_rejection_present": bool(rejected) or _contains_any(warning_reasons, MARKET_POINT_QUALITY_REJECTIONS),
        "actual_available_row_count": _to_int(review_packet.get("actual_available_row_count"), 0),
        "review_row_count": _to_int(review_packet.get("review_row_count"), 0),
        "prediction_generated_at": str(review_packet.get("prediction_generated_at") or ""),
        "review_ok": review_packet.get("ok") is True,
    }


def _summary_stats(summary_packet: Mapping[str, Any]) -> dict[str, Any]:
    windows = [item for item in _as_list(summary_packet.get("window_summaries")) if isinstance(item, Mapping)]
    quality_windows = [w for w in windows if _as_list(w.get("quality_rejected_horizons"))]
    warning_windows = [w for w in windows if _as_list(w.get("warning_reasons"))]
    horizon_directions = _as_map(summary_packet.get("horizon_direction_summary"))
    return {
        "summary_ok": summary_packet.get("ok") is True,
        "source_review_count": _to_int(summary_packet.get("source_review_count"), len(windows)),
        "review_row_total": _to_int(summary_packet.get("review_row_total"), 0),
        "actual_available_row_total": _to_int(summary_packet.get("actual_available_row_total"), 0),
        "actual_available_ratio": _to_float(summary_packet.get("actual_available_ratio"), 0.0),
        "quality_rejected_window_count": len(quality_windows),
        "warning_window_count": len(warning_windows),
        "horizon_direction_summary": {str(k): dict(v) for k, v in horizon_directions.items() if isinstance(v, Mapping)},
        "summary_warning_reasons": [str(item) for item in _as_list(summary_packet.get("warning_reasons"))],
    }


def classify_prediction_observation_outcome(
    *,
    producer_packet: Mapping[str, Any] | None = None,
    review_packet: Mapping[str, Any] | None = None,
    summary_packet: Mapping[str, Any] | None = None,
    minimum_usable_review_ratio: float = 0.5,
) -> dict[str, Any]:
    producer_packet = producer_packet or {}
    review_packet = review_packet or {}
    summary_packet = summary_packet or {}
    blockers: list[str] = []
    warnings: list[str] = []

    pstats = _producer_cycle_stats(producer_packet) if producer_packet else {
        "cycle_count": 0,
        "requested_max_cycles": 0,
        "effective_max_cycles": 0,
        "latest_prediction_artifact_written_count": 0,
        "status_artifact_written_count": 0,
        "blocked_cycle_count": 0,
        "blocked_cycle_indexes": [],
        "last_success_generated_at": "",
        "request_state": "",
        "producer_ok": False,
        "stopped_by_stop_file": False,
    }
    rstats = _review_quality_rejections(review_packet) if review_packet else {
        "quality_rejected_horizons": [],
        "quality_rejected_horizon_reasons": {},
        "review_warning_reasons": [],
        "market_point_quality_rejection_present": False,
        "actual_available_row_count": 0,
        "review_row_count": 0,
        "prediction_generated_at": "",
        "review_ok": False,
    }
    sstats = _summary_stats(summary_packet) if summary_packet else {
        "summary_ok": False,
        "source_review_count": 0,
        "review_row_total": 0,
        "actual_available_row_total": 0,
        "actual_available_ratio": 0.0,
        "quality_rejected_window_count": 0,
        "warning_window_count": 0,
        "horizon_direction_summary": {},
        "summary_warning_reasons": [],
    }
    producer_reasons = _producer_block_reasons(producer_packet) if producer_packet else []
    producer_market_quality_block = _contains_any(producer_reasons, MARKET_QUALITY_BLOCKERS)
    review_market_quality_rejection = bool(rstats["market_point_quality_rejection_present"])
    successful_cycles = int(pstats["latest_prediction_artifact_written_count"])
    cycle_count = int(pstats["cycle_count"])
    effective_max_cycles = int(pstats["effective_max_cycles"])
    blocked_cycle_count = int(pstats["blocked_cycle_count"])

    if not producer_packet and not review_packet and not summary_packet:
        blockers.append("observation_packets_missing")

    review_ratio = (rstats["actual_available_row_count"] / rstats["review_row_count"]) if rstats["review_row_count"] else 0.0
    review_usable = bool(rstats["review_ok"] and rstats["review_row_count"] and review_ratio >= float(minimum_usable_review_ratio))
    summary_usable = bool(sstats["summary_ok"] and sstats["source_review_count"] and sstats["actual_available_ratio"] >= float(minimum_usable_review_ratio))

    if producer_packet and pstats["producer_ok"] and successful_cycles == cycle_count and (effective_max_cycles == 0 or cycle_count == effective_max_cycles):
        outcome_class = "complete_success"
        recommendation = "accept_as_complete_bounded_observation"
    elif producer_packet and successful_cycles > 0 and blocked_cycle_count > 0 and producer_market_quality_block:
        outcome_class = "partial_success_with_market_quality_block"
        recommendation = "accept_successful_cycles_for_review_and_record_quality_block_separately"
    elif producer_packet and successful_cycles > 0 and blocked_cycle_count > 0:
        outcome_class = "partial_success_with_non_quality_block"
        recommendation = "review_successful_cycles_but_investigate_blocker_before_repeat"
    elif producer_packet and successful_cycles == 0 and blocked_cycle_count > 0:
        outcome_class = "blocked_without_success"
        recommendation = "do_not_use_as_observation_window"
    elif review_packet or summary_packet:
        outcome_class = "review_only_observation"
        recommendation = "accept_review_summary_without_reclassifying_producer"
    else:
        outcome_class = "unclassified"
        recommendation = "inspect_packets"

    if producer_market_quality_block:
        warnings.append("producer_market_overview_quality_block_present")
    if review_market_quality_rejection:
        warnings.append("review_market_point_quality_rejection_present")
    if review_packet and not review_usable:
        warnings.append("review_packet_below_minimum_usable_ratio")
    if summary_packet and not summary_usable:
        warnings.append("summary_packet_below_minimum_usable_ratio")

    policy = {
        "complete_success_requires_all_requested_cycles_written": True,
        "partial_success_can_be_accepted_for_review": successful_cycles > 0 and review_usable,
        "quality_rejected_horizons_are_not_scored": True,
        "quality_block_should_not_trigger_auto_retry_or_trade": True,
        "operator_should_record_block_class_separately": True,
        "minimum_usable_review_ratio": float(minimum_usable_review_ratio),
    }

    return {
        "ok": bool(not blockers and outcome_class != "unclassified"),
        "ps_q19v_version": PS_Q19V_OUTCOME_VERSION,
        "outcome_class": outcome_class,
        "recommendation": recommendation,
        "producer_cycle_summary": pstats,
        "producer_block_reason_summary": {
            "unique_blocked_reasons": producer_reasons,
            "reason_counts": dict(Counter(producer_reasons)),
            "market_overview_quality_block_present": bool(producer_market_quality_block),
        },
        "review_quality_summary": rstats | {"actual_available_ratio": review_ratio, "review_usable": review_usable},
        "multi_review_summary": sstats | {"summary_usable": summary_usable},
        "policy_decision": policy,
        "blocked_reasons": list(dict.fromkeys(blockers)),
        "warning_reasons": list(dict.fromkeys(warnings)),
        "read_only_classifier": True,
        **{field: False for field in SAFETY_FALSE_FIELDS},
    }


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="PS-Q19V classify bounded observation outcome packets")
    parser.add_argument("--producer-path", default="", help="Path to saved PS-Q19K producer JSON packet")
    parser.add_argument("--review-path", default="", help="Path to saved PS-Q19R review JSON packet")
    parser.add_argument("--summary-path", default="", help="Path to saved PS-Q19T summary JSON packet")
    parser.add_argument("--minimum-usable-review-ratio", type=float, default=0.5)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    producer, perr = _load_json(str(args.producer_path or ""))
    review, rerr = _load_json(str(args.review_path or ""))
    summary, serr = _load_json(str(args.summary_path or ""))
    packet = classify_prediction_observation_outcome(
        producer_packet=producer,
        review_packet=review,
        summary_packet=summary,
        minimum_usable_review_ratio=float(args.minimum_usable_review_ratio),
    )
    errors = [err for err in (perr, rerr, serr) if err]
    if errors:
        packet["warning_reasons"] = list(dict.fromkeys(list(packet.get("warning_reasons") or []) + errors))
    print(json.dumps(packet, ensure_ascii=False, indent=2, sort_keys=True, default=str))
    return 0 if packet.get("ok") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
