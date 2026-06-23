# path: ./tools/check_phase4a_prediction_system_ps_q18x_latest_prediction_summary_widget_one_source_no_read_filesystem_existence_check_dry_run_result_placeholder.py
# desc: PS-Q18X checker for latest_prediction_summary_widget one-source no-read filesystem existence-check dry-run result placeholder. Placeholder only; no existence result, filesystem check, schema check, actual read, render, refresh, writes, AutoTrade, or broker APIs.

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
from check_phase4a_prediction_system_ps_q18w_latest_prediction_summary_widget_one_source_no_read_filesystem_existence_check_dry_run_packet import CHECKER_VERSION as PS_Q18W_CHECKER_VERSION
from check_phase4a_prediction_system_ps_q18w_latest_prediction_summary_widget_one_source_no_read_filesystem_existence_check_dry_run_packet import build_report as build_ps_q18w_report
from btcts.apps.operator_ui.components.prediction_warroom_latest_prediction_summary_widget_one_source_no_read_filesystem_existence_check_dry_run_result_placeholder import FILESYSTEM_EXISTENCE_CHECK_DRY_RUN_RESULT_PLACEHOLDER_KIND, FILESYSTEM_EXISTENCE_CHECK_DRY_RUN_RESULT_PLACEHOLDER_STATE, LATEST_PREDICTION_SUMMARY_WIDGET_ONE_SOURCE_NO_READ_FILESYSTEM_EXISTENCE_CHECK_DRY_RUN_RESULT_PLACEHOLDER_VERSION, ONE_SOURCE_NO_READ_FILESYSTEM_EXISTENCE_CHECK_DRY_RUN_RESULT_PLACEHOLDER_ACK, build_latest_prediction_summary_widget_one_source_no_read_filesystem_existence_check_dry_run_result_placeholder_packet

CHECKER = "ps_q18x_latest_prediction_summary_widget_one_source_no_read_filesystem_existence_check_dry_run_result_placeholder"
CHECKER_VERSION = "check_phase4a_prediction_system_ps_q18x_latest_prediction_summary_widget_one_source_no_read_filesystem_existence_check_dry_run_result_placeholder.v1"
ONE_SOURCE_NO_READ_FILESYSTEM_EXISTENCE_CHECK_DRY_RUN_RESULT_PLACEHOLDER_CHECK_VERSION = "latest_prediction_summary_widget_one_source_no_read_filesystem_existence_check_dry_run_result_placeholder.v1"
PS_Q18W_SOURCE_CHECKER_VERSION = PS_Q18W_CHECKER_VERSION
EXPECTED_SELECTED = {
    "selected_candidate_generated_at": "2026-06-22T00:00:00Z",
    "selected_candidate_source_artifact_ref": "fixture://ps_q18i/latest_prediction.json",
    "selected_candidate_market_uid": "BTC-USD",
}
TRUE_KEYS = (
    "read_only",
    "non_executing",
    "latest_prediction_summary_widget_one_source_no_read_filesystem_existence_check_dry_run_result_placeholder_only",
    "one_source_no_read_filesystem_existence_check_dry_run_result_placeholder_ready",
    "filesystem_existence_check_dry_run_result_placeholder_declared",
    "one_source_candidate_preserved",
    "source_candidate_count_fixed_to_one",
    "explicit_dry_run_result_placeholder_ack_matched",
    "path_shape_preview_string_only",
)
FALSE_KEYS = (
    "filesystem_existence_check_dry_run_result_available",
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
    "q18w_validation_invoked_by_mount",
    "q18v_validation_invoked_by_mount",
    "component_packet_builder_invoked_by_mount",
    "streamlit_render_invoked",
    "real_prediction_widget_rendering_allowed",
    "refresh_invocation_allowed",
    "runtime_artifact_write_allowed",
    "parameter_apply_allowed",
    "broker_private_api_allowed",
)


def _as_mapping(value: Any) -> Mapping[str, Any]:
    if hasattr(value, "to_dict"):
        converted = value.to_dict()
        return converted if isinstance(converted, Mapping) else {}
    return value if isinstance(value, Mapping) else {}


def _safe_q18w_boundary(report: Mapping[str, Any]) -> tuple[bool, list[str]]:
    failures: list[str] = []
    if report.get("checker_version") != PS_Q18W_SOURCE_CHECKER_VERSION:
        failures.append("q18w_checker_version_mismatch")
    if report.get("ok") is not True:
        failures.append("q18w_report_not_ok")
    if report.get("dry_run_packet_valid") is not True:
        failures.append("q18w_dry_run_packet_not_valid")
    if report.get("source_candidate_count") != 1:
        failures.append("q18w_source_candidate_count_not_one")
    if report.get("dry_run_packet_candidate_ready") is not True:
        failures.append("q18w_dry_run_packet_candidate_not_ready")
    if report.get("path_shape_preview") != EXPECTED_PATH_SHAPE_PREVIEW:
        failures.append("q18w_path_shape_preview_mismatch")
    for key, value in EXPECTED_SELECTED.items():
        if report.get(key) != value:
            failures.append(f"q18w_selected_candidate_mismatch:{key}")
    for key in ("latest_prediction_summary_widget_one_source_no_read_filesystem_existence_check_dry_run_packet_only", "filesystem_existence_check_dry_run_packet_declared", "path_shape_preview_string_only", "source_candidate_count_fixed_to_one"):
        if report.get(key) is not True:
            failures.append(f"q18w_true_boundary_missing:{key}")
    for key in ("filesystem_existence_check_dry_run_execution_allowed", "filesystem_existence_check_dry_run_executed", "source_artifact_exists_checked", "source_artifact_exists_result_available", "actual_source_read_invoked", "runtime_artifact_write_allowed", "broker_private_api_allowed"):
        if report.get(key) is not False:
            failures.append(f"q18w_boundary_not_false:{key}")
    return not failures, failures


def _safe_placeholder_packet(packet: Mapping[str, Any]) -> tuple[bool, list[str]]:
    failures: list[str] = []
    if packet.get("no_read_filesystem_existence_check_dry_run_result_placeholder_version") != LATEST_PREDICTION_SUMMARY_WIDGET_ONE_SOURCE_NO_READ_FILESYSTEM_EXISTENCE_CHECK_DRY_RUN_RESULT_PLACEHOLDER_VERSION:
        failures.append("dry_run_result_placeholder_version_mismatch")
    if packet.get("one_source_no_read_filesystem_existence_check_dry_run_result_placeholder_ack") != ONE_SOURCE_NO_READ_FILESYSTEM_EXISTENCE_CHECK_DRY_RUN_RESULT_PLACEHOLDER_ACK:
        failures.append("dry_run_result_placeholder_ack_mismatch")
    if packet.get("filesystem_existence_check_dry_run_result_placeholder_kind") != FILESYSTEM_EXISTENCE_CHECK_DRY_RUN_RESULT_PLACEHOLDER_KIND:
        failures.append("dry_run_result_placeholder_kind_mismatch")
    if packet.get("filesystem_existence_check_dry_run_result_placeholder_state") != FILESYSTEM_EXISTENCE_CHECK_DRY_RUN_RESULT_PLACEHOLDER_STATE:
        failures.append("dry_run_result_placeholder_state_mismatch")
    if packet.get("ok") is not True:
        failures.append("dry_run_result_placeholder_packet_not_ok")
    if packet.get("dry_run_result_placeholder_row_count") != 14:
        failures.append("dry_run_result_placeholder_row_count_mismatch")
    if packet.get("path_shape_preview") != EXPECTED_PATH_SHAPE_PREVIEW:
        failures.append("path_shape_preview_mismatch")
    for key in TRUE_KEYS:
        if packet.get(key) is not True:
            failures.append(f"dry_run_result_placeholder_true_boundary_missing:{key}")
    for key in FALSE_KEYS:
        if packet.get(key) is not False:
            failures.append(f"dry_run_result_placeholder_boundary_not_false:{key}")
    return not failures, failures


def build_report(*, supplied_q18w_report: Mapping[str, Any] | Any | None = None, use_observed_fixture: bool = False) -> dict[str, Any]:
    q18w_report = _as_mapping(supplied_q18w_report)
    if not q18w_report and use_observed_fixture:
        q18w_report = build_ps_q18w_report(use_observed_fixture=True)
    safe_q18w, q18w_failures = _safe_q18w_boundary(q18w_report)
    placeholder_packet = build_latest_prediction_summary_widget_one_source_no_read_filesystem_existence_check_dry_run_result_placeholder_packet(supplied_dry_run_packet_report=q18w_report) if safe_q18w else {}
    safe_placeholder, placeholder_failures = _safe_placeholder_packet(placeholder_packet) if placeholder_packet else (False, [])
    ok = bool(safe_q18w and safe_placeholder)
    report = {
        "ok": ok,
        "checker": CHECKER,
        "checker_version": CHECKER_VERSION,
        "one_source_no_read_filesystem_existence_check_dry_run_result_placeholder_check_version": ONE_SOURCE_NO_READ_FILESYSTEM_EXISTENCE_CHECK_DRY_RUN_RESULT_PLACEHOLDER_CHECK_VERSION,
        "stage": "latest_prediction_summary_widget_one_source_no_read_filesystem_existence_check_dry_run_result_placeholder_before_exists_result_schema_read_render_refresh_and_writes",
        "source_q18w_checker_version": PS_Q18W_SOURCE_CHECKER_VERSION,
        "source_q18w_report_valid": safe_q18w,
        "source_q18w_validation_failures": q18w_failures,
        "dry_run_result_placeholder_packet_valid": safe_placeholder,
        "dry_run_result_placeholder_validation_failures": placeholder_failures,
        "use_observed_fixture": bool(use_observed_fixture),
        "no_read_filesystem_existence_check_dry_run_result_placeholder_version": LATEST_PREDICTION_SUMMARY_WIDGET_ONE_SOURCE_NO_READ_FILESYSTEM_EXISTENCE_CHECK_DRY_RUN_RESULT_PLACEHOLDER_VERSION,
        "one_source_no_read_filesystem_existence_check_dry_run_result_placeholder_ack": ONE_SOURCE_NO_READ_FILESYSTEM_EXISTENCE_CHECK_DRY_RUN_RESULT_PLACEHOLDER_ACK,
        "dry_run_result_placeholder_row_count": int(placeholder_packet.get("dry_run_result_placeholder_row_count") or 0) if placeholder_packet else 0,
        "source_candidate_count": int(placeholder_packet.get("source_candidate_count") or 0) if placeholder_packet else 0,
        "dry_run_result_placeholder_candidate_ready": bool(placeholder_packet.get("dry_run_result_placeholder_candidate_ready")) if placeholder_packet else False,
        "filesystem_existence_check_dry_run_result_placeholder_kind": str(placeholder_packet.get("filesystem_existence_check_dry_run_result_placeholder_kind") or "") if placeholder_packet else "",
        "filesystem_existence_check_dry_run_result_placeholder_state": str(placeholder_packet.get("filesystem_existence_check_dry_run_result_placeholder_state") or "") if placeholder_packet else "",
        "path_shape_preview": str(placeholder_packet.get("path_shape_preview") or "") if placeholder_packet else "",
        **EXPECTED_SELECTED,
        "recommended_first_validation": "latest_prediction_summary_widget_one_source_no_read_filesystem_existence_check_dry_run_result_placeholder_guard" if ok else "",
        "recommended_next_slice": "PS-Q18Y explicit one-source no-read filesystem existence-check dry-run result display contract; actual source read, real widget rendering, refresh invocation, confidence increase, and parameter staging/apply remain deferred.",
        "human_interpretation": "PS-Q18X declares a pure-data no-read filesystem existence-check dry-run result placeholder. It does not produce an existence result, run filesystem existence checks, run schema checks, read D-hot, reparse payloads, render widgets, refresh, write artifacts, stage/apply parameters, append ledgers, trigger AutoTrade, or call broker APIs.",
    }
    report.update({key: True for key in TRUE_KEYS})
    report.update({key: False for key in FALSE_KEYS})
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="PS-Q18X latest prediction summary widget one-source no-read filesystem existence-check dry-run result placeholder")
    parser.add_argument("--use-observed-fixture", action="store_true", help="Use Q18W observed fixture report; no filesystem exists/schema/read/render/refresh/write is performed and no existence result is produced.")
    args = parser.parse_args(argv)
    report = build_report(use_observed_fixture=args.use_observed_fixture)
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if report.get("ok") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
