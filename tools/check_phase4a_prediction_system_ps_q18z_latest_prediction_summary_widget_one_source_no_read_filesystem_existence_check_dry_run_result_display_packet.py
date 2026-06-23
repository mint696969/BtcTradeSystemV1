# path: ./tools/check_phase4a_prediction_system_ps_q18z_latest_prediction_summary_widget_one_source_no_read_filesystem_existence_check_dry_run_result_display_packet.py
# desc: PS-Q18Z checker for latest_prediction_summary_widget one-source no-read filesystem existence-check dry-run result display packet. No mount, render, exists check, schema check, actual read, refresh, writes, AutoTrade, or broker APIs.

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Any, Mapping

BTCTS_SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "btcts_next", "src")
if BTCTS_SRC not in sys.path:
    sys.path.insert(0, BTCTS_SRC)

from check_phase4a_prediction_system_ps_q18q_latest_prediction_summary_widget_one_source_resolver_dry_run_path_shape_preflight import EXPECTED_PATH_SHAPE_PREVIEW
from check_phase4a_prediction_system_ps_q18y_latest_prediction_summary_widget_one_source_no_read_filesystem_existence_check_dry_run_result_display_contract import CHECKER_VERSION as PS_Q18Y_CHECKER_VERSION
from check_phase4a_prediction_system_ps_q18y_latest_prediction_summary_widget_one_source_no_read_filesystem_existence_check_dry_run_result_display_contract import build_report as build_ps_q18y_report
from btcts.apps.operator_ui.prediction_warroom.contracts.latest_prediction_summary_widget_q18z_display_packet import (
    FALSE_BOUNDARIES,
    LATEST_PREDICTION_SUMMARY_WIDGET_Q18Z_DISPLAY_PACKET_ACK,
    LATEST_PREDICTION_SUMMARY_WIDGET_Q18Z_DISPLAY_PACKET_KIND,
    LATEST_PREDICTION_SUMMARY_WIDGET_Q18Z_DISPLAY_PACKET_STATE,
    LATEST_PREDICTION_SUMMARY_WIDGET_Q18Z_DISPLAY_PACKET_VERSION,
    TRUE_BOUNDARIES,
)
from btcts.apps.operator_ui.prediction_warroom.presenters.latest_prediction_summary_widget_q18z_display_rows import build_latest_prediction_summary_widget_q18z_display_packet

CHECKER = "ps_q18z_latest_prediction_summary_widget_one_source_no_read_filesystem_existence_check_dry_run_result_display_packet"
CHECKER_VERSION = "check_phase4a_prediction_system_ps_q18z_latest_prediction_summary_widget_one_source_no_read_filesystem_existence_check_dry_run_result_display_packet.v1"
PS_Q18Y_SOURCE_CHECKER_VERSION = PS_Q18Y_CHECKER_VERSION
EXPECTED_SELECTED = {
    "selected_candidate_generated_at": "2026-06-22T00:00:00Z",
    "selected_candidate_source_artifact_ref": "fixture://ps_q18i/latest_prediction.json",
    "selected_candidate_market_uid": "BTC-USD",
}


def _as_mapping(value: Any) -> Mapping[str, Any]:
    if hasattr(value, "to_dict"):
        converted = value.to_dict()
        return converted if isinstance(converted, Mapping) else {}
    return value if isinstance(value, Mapping) else {}


def _safe_q18z_packet(packet: Mapping[str, Any]) -> tuple[bool, list[str]]:
    failures: list[str] = []
    if packet.get("display_packet_version") != LATEST_PREDICTION_SUMMARY_WIDGET_Q18Z_DISPLAY_PACKET_VERSION:
        failures.append("display_packet_version_mismatch")
    if packet.get("display_packet_ack") != LATEST_PREDICTION_SUMMARY_WIDGET_Q18Z_DISPLAY_PACKET_ACK:
        failures.append("display_packet_ack_mismatch")
    if packet.get("display_packet_kind") != LATEST_PREDICTION_SUMMARY_WIDGET_Q18Z_DISPLAY_PACKET_KIND:
        failures.append("display_packet_kind_mismatch")
    if packet.get("display_packet_state") != LATEST_PREDICTION_SUMMARY_WIDGET_Q18Z_DISPLAY_PACKET_STATE:
        failures.append("display_packet_state_mismatch")
    if packet.get("ok") is not True:
        failures.append("display_packet_not_ok")
    if packet.get("display_packet_ready") is not True:
        failures.append("display_packet_not_ready")
    if packet.get("display_packet_row_count") != 12:
        failures.append("display_packet_row_count_mismatch")
    if packet.get("source_candidate_count") != 1:
        failures.append("source_candidate_count_not_one")
    if packet.get("path_shape_preview") != EXPECTED_PATH_SHAPE_PREVIEW:
        failures.append("path_shape_preview_mismatch")
    for key, value in EXPECTED_SELECTED.items():
        if packet.get(key) != value:
            failures.append(f"selected_candidate_mismatch:{key}")
    for key in TRUE_BOUNDARIES:
        if packet.get(key) is not True:
            failures.append(f"true_boundary_missing:{key}")
    for key in FALSE_BOUNDARIES:
        if packet.get(key) is not False:
            failures.append(f"false_boundary_not_false:{key}")
    return not failures, failures


def build_report(*, supplied_q18y_display_contract_report: Mapping[str, Any] | Any | None = None, use_observed_fixture: bool = False) -> dict[str, Any]:
    q18y_report = _as_mapping(supplied_q18y_display_contract_report)
    if not q18y_report and use_observed_fixture:
        q18y_report = build_ps_q18y_report(use_observed_fixture=True)
    source_q18y_valid = bool(q18y_report and q18y_report.get("checker_version") == PS_Q18Y_SOURCE_CHECKER_VERSION and q18y_report.get("ok") is True)
    packet = build_latest_prediction_summary_widget_q18z_display_packet(supplied_q18y_display_contract_report=q18y_report) if source_q18y_valid else {}
    safe_packet, packet_failures = _safe_q18z_packet(packet) if packet else (False, ["q18y_source_not_valid"])
    report = {
        "ok": bool(source_q18y_valid and safe_packet),
        "checker": CHECKER,
        "checker_version": CHECKER_VERSION,
        "stage": "latest_prediction_summary_widget_one_source_no_read_filesystem_existence_check_dry_run_result_display_packet_before_mount_render_exists_result_schema_read_refresh_and_writes",
        "source_q18y_checker_version": PS_Q18Y_SOURCE_CHECKER_VERSION,
        "source_q18y_report_valid": source_q18y_valid,
        "display_packet_valid": safe_packet,
        "display_packet_validation_failures": packet_failures,
        "use_observed_fixture": bool(use_observed_fixture),
        "display_packet_version": packet.get("display_packet_version", "") if packet else "",
        "display_packet_ack": packet.get("display_packet_ack", "") if packet else "",
        "display_packet_kind": packet.get("display_packet_kind", "") if packet else "",
        "display_packet_state": packet.get("display_packet_state", "") if packet else "",
        "display_packet_row_count": int(packet.get("display_packet_row_count") or 0) if packet else 0,
        "source_candidate_count": int(packet.get("source_candidate_count") or 0) if packet else 0,
        "path_shape_preview": str(packet.get("path_shape_preview") or "") if packet else "",
        **EXPECTED_SELECTED,
        "recommended_first_validation": "ps_q18z_latest_prediction_summary_widget_one_source_no_read_filesystem_existence_check_dry_run_result_display_packet_guard" if safe_packet else "",
        "recommended_next_slice": "WarRoom mount preflight/gate; keep actual source read, real widget rendering, refresh invocation, confidence increase, and parameter staging/apply deferred unless explicitly approved.",
        "human_interpretation": "PS-Q18Z declares an explicit pure-data display packet from the PS-Q18Y display contract. It does not mount or render UI, produce an existence result, run filesystem existence checks, run schema checks, read D-hot, reparse payloads, refresh, write artifacts, stage/apply parameters, append ledgers, trigger AutoTrade, or call broker APIs.",
    }
    report.update({key: True for key in TRUE_BOUNDARIES})
    report.update({key: False for key in FALSE_BOUNDARIES})
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="PS-Q18Z latest prediction summary widget one-source no-read filesystem existence-check dry-run result display packet")
    parser.add_argument("--use-observed-fixture", action="store_true", help="Use Q18Y observed fixture report; no filesystem exists/schema/read/render/refresh/write is performed and no existence result is produced.")
    args = parser.parse_args(argv)
    report = build_report(use_observed_fixture=args.use_observed_fixture)
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if report.get("ok") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
