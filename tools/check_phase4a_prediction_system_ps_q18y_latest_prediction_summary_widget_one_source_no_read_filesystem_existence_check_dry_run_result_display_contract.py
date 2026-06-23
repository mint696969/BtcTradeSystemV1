# path: ./tools/check_phase4a_prediction_system_ps_q18y_latest_prediction_summary_widget_one_source_no_read_filesystem_existence_check_dry_run_result_display_contract.py
# desc: PS-Q18Y checker for latest_prediction_summary_widget one-source no-read filesystem existence-check dry-run result display contract. Contract only; no existence result, filesystem check, schema check, actual read, mount, render, refresh, writes, AutoTrade, or broker APIs.

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
from check_phase4a_prediction_system_ps_q18x_latest_prediction_summary_widget_one_source_no_read_filesystem_existence_check_dry_run_result_placeholder import CHECKER_VERSION as PS_Q18X_CHECKER_VERSION
from check_phase4a_prediction_system_ps_q18x_latest_prediction_summary_widget_one_source_no_read_filesystem_existence_check_dry_run_result_placeholder import build_report as build_ps_q18x_report
from btcts.apps.operator_ui.components.prediction_warroom_latest_prediction_summary_widget_one_source_no_read_filesystem_existence_check_dry_run_result_display_contract import FILESYSTEM_EXISTENCE_CHECK_DRY_RUN_RESULT_DISPLAY_CONTRACT_KIND, FILESYSTEM_EXISTENCE_CHECK_DRY_RUN_RESULT_DISPLAY_CONTRACT_STATE, LATEST_PREDICTION_SUMMARY_WIDGET_ONE_SOURCE_NO_READ_FILESYSTEM_EXISTENCE_CHECK_DRY_RUN_RESULT_DISPLAY_CONTRACT_VERSION, ONE_SOURCE_NO_READ_FILESYSTEM_EXISTENCE_CHECK_DRY_RUN_RESULT_DISPLAY_CONTRACT_ACK, build_latest_prediction_summary_widget_one_source_no_read_filesystem_existence_check_dry_run_result_display_contract_packet

CHECKER = "ps_q18y_latest_prediction_summary_widget_one_source_no_read_filesystem_existence_check_dry_run_result_display_contract"
CHECKER_VERSION = "check_phase4a_prediction_system_ps_q18y_latest_prediction_summary_widget_one_source_no_read_filesystem_existence_check_dry_run_result_display_contract.v1"
ONE_SOURCE_NO_READ_FILESYSTEM_EXISTENCE_CHECK_DRY_RUN_RESULT_DISPLAY_CONTRACT_CHECK_VERSION = "latest_prediction_summary_widget_one_source_no_read_filesystem_existence_check_dry_run_result_display_contract.v1"
PS_Q18X_SOURCE_CHECKER_VERSION = PS_Q18X_CHECKER_VERSION
EXPECTED_SELECTED = {
    "selected_candidate_generated_at": "2026-06-22T00:00:00Z",
    "selected_candidate_source_artifact_ref": "fixture://ps_q18i/latest_prediction.json",
    "selected_candidate_market_uid": "BTC-USD",
}
TRUE_KEYS = (
    "read_only",
    "non_executing",
    "latest_prediction_summary_widget_one_source_no_read_filesystem_existence_check_dry_run_result_display_contract_only",
    "one_source_no_read_filesystem_existence_check_dry_run_result_display_contract_ready",
    "filesystem_existence_check_dry_run_result_display_contract_declared",
    "filesystem_existence_check_dry_run_result_placeholder_preserved",
    "one_source_candidate_preserved",
    "source_candidate_count_fixed_to_one",
    "explicit_dry_run_result_display_contract_ack_matched",
    "path_shape_preview_string_only",
)
FALSE_KEYS = (
    "filesystem_existence_check_dry_run_result_available",
    "filesystem_existence_check_dry_run_result_display_mount_allowed",
    "filesystem_existence_check_dry_run_result_display_mounted",
    "filesystem_existence_check_dry_run_execution_allowed",
    "filesystem_existence_check_dry_run_executed",
    "warroom_page_mutation_allowed",
    "source_artifact_resolver_invoked",
    "source_artifact_resolution_allowed",
    "source_artifact_resolved",
    "source_artifact_path_materialized",
    "source_artifact_exists_check_allowed",
    "source_artifact_exists_checked",
    "source_artifact_exists_result_available",
    "source_artifact_schema_check_allowed",
    "source_artifact_schema_checked",
    "actual_source_read_allowed",
    "actual_source_read_invoked",
    "payload_reparse_allowed",
    "source_discovery_allowed",
    "d_hot_directory_scan_allowed",
    "d_hot_actual_read_allowed",
    "q18x_validation_invoked_by_mount",
    "q18w_validation_invoked_by_mount",
    "component_packet_builder_invoked_by_mount",
    "component_packet_builder_allowed_by_mount",
    "component_runtime_binding_allowed",
    "streamlit_render_allowed",
    "streamlit_render_invoked",
    "real_prediction_widget_rendering_allowed",
    "warroom_widget_rendering_allowed",
    "warroom_ui_trigger_enabled",
    "refresh_invocation_allowed",
    "scheduler_enabled",
    "runtime_artifact_write_allowed",
    "status_artifact_write_allowed",
    "confidence_increase_allowed",
    "parameter_apply_allowed",
    "parameter_staging_write_allowed",
    "approval_or_authorization_allowed",
    "ledger_append_allowed",
    "autotrade_trigger_allowed",
    "broker_private_api_allowed",
    "would_write_runtime_artifact",
    "would_write_collector_state",
    "would_send_to_broker",
)


def _as_mapping(value: Any) -> Mapping[str, Any]:
    if hasattr(value, "to_dict"):
        converted = value.to_dict()
        return converted if isinstance(converted, Mapping) else {}
    return value if isinstance(value, Mapping) else {}


def _safe_q18x_boundary(report: Mapping[str, Any]) -> tuple[bool, list[str]]:
    failures: list[str] = []
    if report.get("checker_version") != PS_Q18X_SOURCE_CHECKER_VERSION:
        failures.append("q18x_checker_version_mismatch")
    if report.get("ok") is not True:
        failures.append("q18x_report_not_ok")
    if report.get("dry_run_result_placeholder_packet_valid") is not True:
        failures.append("q18x_result_placeholder_packet_not_valid")
    if report.get("source_candidate_count") != 1:
        failures.append("q18x_source_candidate_count_not_one")
    if report.get("dry_run_result_placeholder_candidate_ready") is not True:
        failures.append("q18x_result_placeholder_candidate_not_ready")
    if report.get("path_shape_preview") != EXPECTED_PATH_SHAPE_PREVIEW:
        failures.append("q18x_path_shape_preview_mismatch")
    for key, value in EXPECTED_SELECTED.items():
        if report.get(key) != value:
            failures.append(f"q18x_selected_candidate_mismatch:{key}")
    for key in ("read_only", "non_executing", "latest_prediction_summary_widget_one_source_no_read_filesystem_existence_check_dry_run_result_placeholder_only", "filesystem_existence_check_dry_run_result_placeholder_declared", "path_shape_preview_string_only", "source_candidate_count_fixed_to_one"):
        if report.get(key) is not True:
            failures.append(f"q18x_true_boundary_missing:{key}")
    for key in ("filesystem_existence_check_dry_run_result_available", "filesystem_existence_check_dry_run_execution_allowed", "filesystem_existence_check_dry_run_executed", "warroom_page_mutation_allowed", "source_artifact_exists_checked", "source_artifact_exists_result_available", "actual_source_read_invoked", "streamlit_render_invoked", "real_prediction_widget_rendering_allowed", "runtime_artifact_write_allowed", "broker_private_api_allowed"):
        if report.get(key) is not False:
            failures.append(f"q18x_boundary_not_false:{key}")
    return not failures, failures


def _safe_display_contract_packet(packet: Mapping[str, Any]) -> tuple[bool, list[str]]:
    failures: list[str] = []
    if packet.get("no_read_filesystem_existence_check_dry_run_result_display_contract_version") != LATEST_PREDICTION_SUMMARY_WIDGET_ONE_SOURCE_NO_READ_FILESYSTEM_EXISTENCE_CHECK_DRY_RUN_RESULT_DISPLAY_CONTRACT_VERSION:
        failures.append("dry_run_result_display_contract_version_mismatch")
    if packet.get("one_source_no_read_filesystem_existence_check_dry_run_result_display_contract_ack") != ONE_SOURCE_NO_READ_FILESYSTEM_EXISTENCE_CHECK_DRY_RUN_RESULT_DISPLAY_CONTRACT_ACK:
        failures.append("dry_run_result_display_contract_ack_mismatch")
    if packet.get("filesystem_existence_check_dry_run_result_display_contract_kind") != FILESYSTEM_EXISTENCE_CHECK_DRY_RUN_RESULT_DISPLAY_CONTRACT_KIND:
        failures.append("dry_run_result_display_contract_kind_mismatch")
    if packet.get("filesystem_existence_check_dry_run_result_display_contract_state") != FILESYSTEM_EXISTENCE_CHECK_DRY_RUN_RESULT_DISPLAY_CONTRACT_STATE:
        failures.append("dry_run_result_display_contract_state_mismatch")
    if packet.get("ok") is not True:
        failures.append("dry_run_result_display_contract_packet_not_ok")
    if packet.get("dry_run_result_display_contract_row_count") != 14:
        failures.append("dry_run_result_display_contract_row_count_mismatch")
    if packet.get("path_shape_preview") != EXPECTED_PATH_SHAPE_PREVIEW:
        failures.append("path_shape_preview_mismatch")
    for key in TRUE_KEYS:
        if packet.get(key) is not True:
            failures.append(f"dry_run_result_display_contract_true_boundary_missing:{key}")
    for key in FALSE_KEYS:
        if packet.get(key) is not False:
            failures.append(f"dry_run_result_display_contract_boundary_not_false:{key}")
    return not failures, failures


def build_report(*, supplied_q18x_report: Mapping[str, Any] | Any | None = None, use_observed_fixture: bool = False) -> dict[str, Any]:
    q18x_report = _as_mapping(supplied_q18x_report)
    if not q18x_report and use_observed_fixture:
        q18x_report = build_ps_q18x_report(use_observed_fixture=True)
    safe_q18x, q18x_failures = _safe_q18x_boundary(q18x_report)
    display_packet = build_latest_prediction_summary_widget_one_source_no_read_filesystem_existence_check_dry_run_result_display_contract_packet(supplied_result_placeholder_report=q18x_report) if safe_q18x else {}
    safe_display, display_failures = _safe_display_contract_packet(display_packet) if display_packet else (False, [])
    ok = bool(safe_q18x and safe_display)
    report = {
        "ok": ok,
        "checker": CHECKER,
        "checker_version": CHECKER_VERSION,
        "one_source_no_read_filesystem_existence_check_dry_run_result_display_contract_check_version": ONE_SOURCE_NO_READ_FILESYSTEM_EXISTENCE_CHECK_DRY_RUN_RESULT_DISPLAY_CONTRACT_CHECK_VERSION,
        "stage": "latest_prediction_summary_widget_one_source_no_read_filesystem_existence_check_dry_run_result_display_contract_before_mount_render_exists_result_schema_read_refresh_and_writes",
        "source_q18x_checker_version": PS_Q18X_SOURCE_CHECKER_VERSION,
        "source_q18x_report_valid": safe_q18x,
        "source_q18x_validation_failures": q18x_failures,
        "dry_run_result_display_contract_packet_valid": safe_display,
        "dry_run_result_display_contract_validation_failures": display_failures,
        "use_observed_fixture": bool(use_observed_fixture),
        "no_read_filesystem_existence_check_dry_run_result_display_contract_version": LATEST_PREDICTION_SUMMARY_WIDGET_ONE_SOURCE_NO_READ_FILESYSTEM_EXISTENCE_CHECK_DRY_RUN_RESULT_DISPLAY_CONTRACT_VERSION,
        "one_source_no_read_filesystem_existence_check_dry_run_result_display_contract_ack": ONE_SOURCE_NO_READ_FILESYSTEM_EXISTENCE_CHECK_DRY_RUN_RESULT_DISPLAY_CONTRACT_ACK,
        "dry_run_result_display_contract_row_count": int(display_packet.get("dry_run_result_display_contract_row_count") or 0) if display_packet else 0,
        "source_candidate_count": int(display_packet.get("source_candidate_count") or 0) if display_packet else 0,
        "dry_run_result_display_contract_candidate_ready": bool(display_packet.get("dry_run_result_display_contract_candidate_ready")) if display_packet else False,
        "filesystem_existence_check_dry_run_result_display_contract_kind": str(display_packet.get("filesystem_existence_check_dry_run_result_display_contract_kind") or "") if display_packet else "",
        "filesystem_existence_check_dry_run_result_display_contract_state": str(display_packet.get("filesystem_existence_check_dry_run_result_display_contract_state") or "") if display_packet else "",
        "path_shape_preview": str(display_packet.get("path_shape_preview") or "") if display_packet else "",
        **EXPECTED_SELECTED,
        "recommended_first_validation": "latest_prediction_summary_widget_one_source_no_read_filesystem_existence_check_dry_run_result_display_contract_guard" if ok else "",
        "recommended_next_slice": "PS-Q18Z explicit one-source no-read filesystem existence-check dry-run result display packet; actual source read, real widget rendering, refresh invocation, confidence increase, and parameter staging/apply remain deferred.",
        "human_interpretation": "PS-Q18Y declares a pure-data no-read filesystem existence-check dry-run result display contract. It does not mount or render UI, produce an existence result, run filesystem existence checks, run schema checks, read D-hot, reparse payloads, refresh, write artifacts, stage/apply parameters, append ledgers, trigger AutoTrade, or call broker APIs.",
    }
    report.update({key: True for key in TRUE_KEYS})
    report.update({key: False for key in FALSE_KEYS})
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="PS-Q18Y latest prediction summary widget one-source no-read filesystem existence-check dry-run result display contract")
    parser.add_argument("--use-observed-fixture", action="store_true", help="Use Q18X observed fixture report; no filesystem exists/schema/read/render/refresh/write is performed and no existence result is produced.")
    args = parser.parse_args(argv)
    report = build_report(use_observed_fixture=args.use_observed_fixture)
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if report.get("ok") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
