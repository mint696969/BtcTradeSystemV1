# path: ./tools/diagnose_phase4a_prediction_system_ps_q21g_source_mapping_trust_blocker_drilldown.py
# desc: PS-Q21G read-only drilldown for source mapping and market overview trust blockers. Bounded D-hot reads only; stdout JSON only; no writes or enablement.

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any, Mapping

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC = REPO_ROOT / "btcts_next" / "src"
for candidate in (REPO_ROOT, SRC):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

from btcts.apps.operator_ui.components.prediction_warroom_source_mapping_probe_runner import (  # noqa: E402
    SOURCE_MAPPING_PROBE_RUNNER_VERSION,
    build_prediction_warroom_source_mapping_probe_runner,
)

DIAGNOSTIC_VERSION = "prediction_warroom.source_mapping_trust_blocker_drilldown.ps_q21g.v1"
DEFAULT_HOT_ROOT = Path(r"D:\btc_ts_hot")
TARGET_BLOCKERS = (
    "market_overview_trust_state_not_trusted",
    "market_overview_interpretation_bucket_not_allow_structural_use",
    "ps_q9z_probe_not_ready_for_future_prediction_source_mapping",
    "source_mapping_runner_not_ready_for_prediction_system_result_builder",
)


def _as_mapping(value: Any) -> Mapping[str, Any]:
    if hasattr(value, "to_dict"):
        converted = value.to_dict()
        return converted if isinstance(converted, Mapping) else {}
    return value if isinstance(value, Mapping) else {}


def _as_list(value: Any) -> list[Any]:
    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return list(value)
    return []


def _str_list(value: Any) -> list[str]:
    return [str(item) for item in _as_list(value) if item]


def _source_by_role(q9z_packet: Mapping[str, Any], role: str) -> Mapping[str, Any]:
    for item in _as_list(q9z_packet.get("source_summaries")):
        mapped = _as_mapping(item)
        if str(mapped.get("source_role") or "") == role:
            return mapped
    return {}


def build_source_mapping_trust_blocker_drilldown(
    *,
    probe_runner_packet: Mapping[str, Any] | Any,
) -> dict[str, Any]:
    runner = _as_mapping(probe_runner_packet)
    q9z = _as_mapping(runner.get("q9z_probe_packet"))
    q10a = _as_mapping(runner.get("q10a_preflight_packet"))
    overview = _source_by_role(q9z, "market_overview")
    trade = _source_by_role(q9z, "market_trade")
    orderbook = _source_by_role(q9z, "orderbook_snapshot")
    runner_blockers = _str_list(runner.get("blocked_reasons"))
    q9z_blockers = _str_list(q9z.get("blocked_reasons"))
    q10a_blockers = _str_list(q10a.get("blocked_reasons"))
    overview_blockers = _str_list(overview.get("blocker_reasons"))
    warnings = list(dict.fromkeys(_str_list(runner.get("warning_reasons")) + _str_list(q9z.get("warning_reasons")) + _str_list(q10a.get("warning_reasons"))))
    combined = list(dict.fromkeys(runner_blockers + q9z_blockers + q10a_blockers + overview_blockers))
    trust_blocked = "market_overview_trust_state_not_trusted" in combined
    interpretation_blocked = "market_overview_interpretation_bucket_not_allow_structural_use" in combined
    q9z_not_ready = bool(q9z and not q9z.get("ready_for_future_prediction_source_mapping"))
    q10a_not_ready = bool(q10a and not q10a.get("ready_for_future_prediction_system_result_builder"))
    if trust_blocked or interpretation_blocked:
        next_focus = "market_overview_row_selection_or_trust_contract_repair_read_only"
        primary_root_cause = "market_overview_not_trusted_for_prediction_source_mapping"
    elif q9z_not_ready:
        next_focus = "q9z_hot_source_probe_readiness_repair_read_only"
        primary_root_cause = "q9z_probe_not_ready"
    elif q10a_not_ready:
        next_focus = "q10a_source_mapping_preflight_repair_read_only"
        primary_root_cause = "q10a_source_mapping_not_ready"
    else:
        next_focus = "no_source_mapping_trust_blocker_detected"
        primary_root_cause = "none_detected"
    return {
        "ok": True,
        "diagnostic_version": DIAGNOSTIC_VERSION,
        "source_mapping_probe_runner_version": SOURCE_MAPPING_PROBE_RUNNER_VERSION,
        "diagnosis_state": "source_mapping_trust_blocker_drilldown_ready",
        "hot_root": str(runner.get("hot_latest_root_hint") or ""),
        "runner_state": str(runner.get("runner_state") or ""),
        "runner_blocker_count": int(runner.get("blocker_count") or len(runner_blockers)),
        "runner_blockers": runner_blockers,
        "q9z_probe_state": str(q9z.get("probe_state") or ""),
        "q9z_ready_for_future_prediction_source_mapping": bool(q9z.get("ready_for_future_prediction_source_mapping")),
        "q9z_blockers": q9z_blockers,
        "q10a_contract_state": str(q10a.get("contract_state") or ""),
        "q10a_ready_for_future_prediction_system_result_builder": bool(q10a.get("ready_for_future_prediction_system_result_builder")),
        "q10a_blockers": q10a_blockers,
        "target_blockers_present": [item for item in TARGET_BLOCKERS if item in combined],
        "combined_blockers": combined,
        "warning_reasons": warnings,
        "market_overview": {
            "source_state": str(overview.get("source_state") or ""),
            "latest_part_path": str(overview.get("latest_part_path") or ""),
            "latest_date_partition": str(overview.get("latest_date_partition") or ""),
            "parsed_row_count": int(overview.get("parsed_row_count") or 0),
            "latest_collector_ts": str(overview.get("latest_collector_ts") or ""),
            "latest_event_ts": str(overview.get("latest_event_ts") or ""),
            "latest_market_uid": str(overview.get("latest_market_uid") or ""),
            "latest_trust_state": str(overview.get("latest_trust_state") or ""),
            "latest_continuity_state": str(overview.get("latest_continuity_state") or ""),
            "latest_interpretation_bucket": str(overview.get("latest_interpretation_bucket") or ""),
            "overview_mid_price": overview.get("overview_mid_price"),
            "overview_spread": overview.get("overview_spread"),
            "blocker_reasons": overview_blockers,
        },
        "market_trade": {
            "source_state": str(trade.get("source_state") or ""),
            "latest_part_path": str(trade.get("latest_part_path") or ""),
            "parsed_row_count": int(trade.get("parsed_row_count") or 0),
            "latest_event_ts": str(trade.get("latest_event_ts") or ""),
            "trade_price_sample": _as_list(trade.get("trade_price_sample")),
        },
        "orderbook_snapshot": {
            "source_state": str(orderbook.get("source_state") or ""),
            "latest_part_path": str(orderbook.get("latest_part_path") or ""),
            "parsed_row_count": int(orderbook.get("parsed_row_count") or 0),
            "latest_event_ts": str(orderbook.get("latest_event_ts") or ""),
            "orderbook_bid_level_count": int(orderbook.get("orderbook_bid_level_count") or 0),
            "orderbook_ask_level_count": int(orderbook.get("orderbook_ask_level_count") or 0),
        },
        "market_overview_trust_state_not_trusted": trust_blocked,
        "market_overview_interpretation_bucket_not_allow_structural_use": interpretation_blocked,
        "ps_q9z_probe_not_ready_for_future_prediction_source_mapping": q9z_not_ready,
        "source_mapping_runner_not_ready_for_prediction_system_result_builder": q10a_not_ready,
        "primary_root_cause": primary_root_cause,
        "next_focus": next_focus,
        "next_recommended_action": "Repair/diagnose market overview trusted row selection before any producer or scheduler enablement." if trust_blocked or interpretation_blocked else "Continue read-only drilldown before enablement.",
        "read_only_diagnostic_only": True,
        "bounded_hot_tail_read_only": True,
        "prediction_build_allowed": False,
        "latest_prediction_artifact_export_allowed": False,
        "runtime_enablement_allowed": False,
        "scheduler_enablement_allowed": False,
        "producer_enablement_allowed": False,
        "runtime_artifact_write_allowed": False,
        "status_artifact_write_allowed": False,
        "prediction_artifact_write_allowed": False,
        "view_artifact_write_allowed": False,
        "autotrade_trigger_allowed": False,
        "broker_private_api_allowed": False,
        "would_send_to_broker": False,
    }


def run_diagnostic(*, hot_root: Path | None = None) -> dict[str, Any]:
    root_hint = hot_root or os.environ.get("BTCTS_HOT_ROOT") or os.environ.get("BTC_TS_HOT_ROOT") or DEFAULT_HOT_ROOT
    packet = build_prediction_warroom_source_mapping_probe_runner(
        hot_latest_root_hint=str(root_hint),
        operator_acknowledged=True,
        allow_actual_read=True,
        allow_guard_test_root=False,
    ).to_dict()
    return build_source_mapping_trust_blocker_drilldown(probe_runner_packet=packet)


def main() -> int:
    result = run_diagnostic()
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result.get("ok") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
