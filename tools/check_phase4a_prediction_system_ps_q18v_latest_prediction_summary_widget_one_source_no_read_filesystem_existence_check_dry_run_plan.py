# path: ./tools/check_phase4a_prediction_system_ps_q18v_latest_prediction_summary_widget_one_source_no_read_filesystem_existence_check_dry_run_plan.py
# desc: PS-Q18V checker for latest_prediction_summary_widget one-source no-read filesystem existence-check dry-run plan. Plan only; no filesystem check, schema check, actual read, render, refresh, writes, AutoTrade, or broker APIs.

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
from check_phase4a_prediction_system_ps_q18u_latest_prediction_summary_widget_one_source_no_read_existence_check_gate_open_contract import CHECKER_VERSION as PS_Q18U_CHECKER_VERSION
from check_phase4a_prediction_system_ps_q18u_latest_prediction_summary_widget_one_source_no_read_existence_check_gate_open_contract import build_report as build_ps_q18u_report
from btcts.apps.operator_ui.components.prediction_warroom_latest_prediction_summary_widget_one_source_no_read_filesystem_existence_check_dry_run_plan import FILESYSTEM_EXISTENCE_CHECK_DRY_RUN_PLAN_KIND, FILESYSTEM_EXISTENCE_CHECK_DRY_RUN_PLAN_STATE, LATEST_PREDICTION_SUMMARY_WIDGET_ONE_SOURCE_NO_READ_FILESYSTEM_EXISTENCE_CHECK_DRY_RUN_PLAN_VERSION, ONE_SOURCE_NO_READ_FILESYSTEM_EXISTENCE_CHECK_DRY_RUN_PLAN_ACK, build_latest_prediction_summary_widget_one_source_no_read_filesystem_existence_check_dry_run_plan_packet

CHECKER = "ps_q18v_latest_prediction_summary_widget_one_source_no_read_filesystem_existence_check_dry_run_plan"
CHECKER_VERSION = "check_phase4a_prediction_system_ps_q18v_latest_prediction_summary_widget_one_source_no_read_filesystem_existence_check_dry_run_plan.v1"
ONE_SOURCE_NO_READ_FILESYSTEM_EXISTENCE_CHECK_DRY_RUN_PLAN_CHECK_VERSION = "latest_prediction_summary_widget_one_source_no_read_filesystem_existence_check_dry_run_plan.v1"
PS_Q18U_SOURCE_CHECKER_VERSION = PS_Q18U_CHECKER_VERSION
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


def _safe_q18u_boundary(report: Mapping[str, Any]) -> tuple[bool, list[str]]:
    failures: list[str] = []
    if report.get("checker_version") != PS_Q18U_SOURCE_CHECKER_VERSION:
        failures.append("q18u_checker_version_mismatch")
    if report.get("ok") is not True:
        failures.append("q18u_report_not_ok")
    if report.get("gate_open_contract_packet_valid") is not True:
        failures.append("q18u_gate_open_contract_packet_not_valid")
    if report.get("source_candidate_count") != 1:
        failures.append("q18u_source_candidate_count_not_one")
    if report.get("gate_open_contract_candidate_ready") is not True:
        failures.append("q18u_gate_open_contract_candidate_not_ready")
    if report.get("path_shape_preview") != EXPECTED_PATH_SHAPE_PREVIEW:
        failures.append("q18u_path_shape_preview_mismatch")
    for key, value in EXPECTED_SELECTED.items():
        if report.get(key) != value:
            failures.append(f"q18u_selected_candidate_mismatch:{key}")
    for key in ("latest_prediction_summary_widget_one_source_no_read_existence_check_gate_open_contract_only", "existence_check_gate_open_contract_declared", "path_shape_preview_string_only", "source_candidate_count_fixed_to_one"):
        if report.get(key) is not True:
            failures.append(f"q18u_true_boundary_missing:{key}")
    for key in ("existence_check_execution_gate_open_allowed", "existence_check_execution_gate_opened", "warroom_page_mutation_allowed", "source_artifact_resolver_invoked", "source_artifact_resolution_allowed", "source_artifact_path_materialized", "source_artifact_exists_check_allowed", "source_artifact_exists_checked", "source_artifact_schema_check_allowed", "source_artifact_schema_checked", "actual_source_read_allowed", "actual_source_read_invoked", "payload_reparse_allowed", "source_discovery_allowed", "d_hot_directory_scan_allowed", "d_hot_actual_read_allowed", "q18t_validation_invoked_by_mount", "component_packet_builder_invoked_by_mount", "streamlit_render_invoked", "real_prediction_widget_rendering_allowed", "refresh_invocation_allowed", "runtime_artifact_write_allowed", "parameter_apply_allowed", "broker_private_api_allowed"):
        if report.get(key) is not False:
            failures.append(f"q18u_boundary_not_false:{key}")
    return not failures, failures


def _safe_plan_packet(packet: Mapping[str, Any]) -> tuple[bool, list[str]]:
    failures: list[str] = []
    if packet.get("no_read_filesystem_existence_check_dry_run_plan_version") != LATEST_PREDICTION_SUMMARY_WIDGET_ONE_SOURCE_NO_READ_FILESYSTEM_EXISTENCE_CHECK_DRY_RUN_PLAN_VERSION:
        failures.append("dry_run_plan_version_mismatch")
    if packet.get("one_source_no_read_filesystem_existence_check_dry_run_plan_ack") != ONE_SOURCE_NO_READ_FILESYSTEM_EXISTENCE_CHECK_DRY_RUN_PLAN_ACK:
        failures.append("dry_run_plan_ack_mismatch")
    if packet.get("filesystem_existence_check_dry_run_plan_kind") != FILESYSTEM_EXISTENCE_CHECK_DRY_RUN_PLAN_KIND:
        failures.append("dry_run_plan_kind_mismatch")
    if packet.get("filesystem_existence_check_dry_run_plan_state") != FILESYSTEM_EXISTENCE_CHECK_DRY_RUN_PLAN_STATE:
        failures.append("dry_run_plan_state_mismatch")
    if packet.get("ok") is not True:
        failures.append("dry_run_plan_packet_not_ok")
    if packet.get("dry_run_plan_row_count") != 14:
        failures.append("dry_run_plan_row_count_mismatch")
    if packet.get("path_shape_preview") != EXPECTED_PATH_SHAPE_PREVIEW:
        failures.append("path_shape_preview_mismatch")
    for key in ("latest_prediction_summary_widget_one_source_no_read_filesystem_existence_check_dry_run_plan_only", "one_source_no_read_filesystem_existence_check_dry_run_plan_ready", "filesystem_existence_check_dry_run_plan_declared", "source_candidate_count_fixed_to_one", "explicit_dry_run_plan_ack_matched", "path_shape_preview_string_only"):
        if packet.get(key) is not True:
            failures.append(f"dry_run_plan_true_boundary_missing:{key}")
    for key in ("filesystem_existence_check_dry_run_execution_allowed", "filesystem_existence_check_dry_run_executed", "source_artifact_resolver_invoked", "source_artifact_resolution_allowed", "source_artifact_resolved", "source_artifact_path_materialized", "source_artifact_exists_check_allowed", "source_artifact_exists_checked", "source_artifact_exists_result_available", "source_artifact_schema_check_allowed", "source_artifact_schema_checked", "actual_source_read_allowed", "actual_source_read_invoked", "payload_reparse_allowed", "source_discovery_allowed", "d_hot_directory_scan_allowed", "d_hot_actual_read_allowed", "q18u_validation_invoked_by_mount", "q18t_validation_invoked_by_mount", "component_packet_builder_invoked_by_mount", "streamlit_render_invoked", "real_prediction_widget_rendering_allowed", "refresh_invocation_allowed", "runtime_artifact_write_allowed", "parameter_apply_allowed", "broker_private_api_allowed"):
        if packet.get(key) is not False:
            failures.append(f"dry_run_plan_boundary_not_false:{key}")
    return not failures, failures


def build_report(*, supplied_q18u_report: Mapping[str, Any] | Any | None = None, use_observed_fixture: bool = False) -> dict[str, Any]:
    q18u_report = _as_mapping(supplied_q18u_report)
    if not q18u_report and use_observed_fixture:
        q18u_report = build_ps_q18u_report(use_observed_fixture=True)
    safe_q18u, q18u_failures = _safe_q18u_boundary(q18u_report)
    plan_packet = build_latest_prediction_summary_widget_one_source_no_read_filesystem_existence_check_dry_run_plan_packet(supplied_gate_open_contract_report=q18u_report) if safe_q18u else {}
    safe_plan, plan_failures = _safe_plan_packet(plan_packet) if plan_packet else (False, [])
    ok = bool(safe_q18u and safe_plan)
    return {
        "ok": ok,
        "checker": CHECKER,
        "checker_version": CHECKER_VERSION,
        "one_source_no_read_filesystem_existence_check_dry_run_plan_check_version": ONE_SOURCE_NO_READ_FILESYSTEM_EXISTENCE_CHECK_DRY_RUN_PLAN_CHECK_VERSION,
        "stage": "latest_prediction_summary_widget_one_source_no_read_filesystem_existence_check_dry_run_plan_before_exists_schema_read_render_refresh_and_writes",
        "source_q18u_checker_version": PS_Q18U_SOURCE_CHECKER_VERSION,
        "source_q18u_report_valid": safe_q18u,
        "source_q18u_validation_failures": q18u_failures,
        "dry_run_plan_packet_valid": safe_plan,
        "dry_run_plan_validation_failures": plan_failures,
        "use_observed_fixture": bool(use_observed_fixture),
        "no_read_filesystem_existence_check_dry_run_plan_version": LATEST_PREDICTION_SUMMARY_WIDGET_ONE_SOURCE_NO_READ_FILESYSTEM_EXISTENCE_CHECK_DRY_RUN_PLAN_VERSION,
        "one_source_no_read_filesystem_existence_check_dry_run_plan_ack": ONE_SOURCE_NO_READ_FILESYSTEM_EXISTENCE_CHECK_DRY_RUN_PLAN_ACK,
        "dry_run_plan_row_count": int(plan_packet.get("dry_run_plan_row_count") or 0) if plan_packet else 0,
        "source_candidate_count": int(plan_packet.get("source_candidate_count") or 0) if plan_packet else 0,
        "dry_run_plan_candidate_ready": bool(plan_packet.get("dry_run_plan_candidate_ready")) if plan_packet else False,
        "filesystem_existence_check_dry_run_plan_kind": str(plan_packet.get("filesystem_existence_check_dry_run_plan_kind") or "") if plan_packet else "",
        "filesystem_existence_check_dry_run_plan_state": str(plan_packet.get("filesystem_existence_check_dry_run_plan_state") or "") if plan_packet else "",
        "path_shape_preview": str(plan_packet.get("path_shape_preview") or "") if plan_packet else "",
        **EXPECTED_SELECTED,
        "recommended_first_validation": "latest_prediction_summary_widget_one_source_no_read_filesystem_existence_check_dry_run_plan_guard" if ok else "",
        "recommended_next_slice": "PS-Q18W explicit one-source no-read filesystem existence-check dry-run packet; actual source read, real widget rendering, refresh invocation, confidence increase, and parameter staging/apply remain deferred.",
        "human_interpretation": "PS-Q18V declares a no-read filesystem existence-check dry-run plan. It does not run filesystem existence checks, run schema checks, read D-hot, reparse payloads, render widgets, refresh, write artifacts, stage/apply parameters, append ledgers, trigger AutoTrade, or call broker APIs.",
        "read_only": True,
        "non_executing": True,
        "latest_prediction_summary_widget_one_source_no_read_filesystem_existence_check_dry_run_plan_only": True,
        "one_source_no_read_filesystem_existence_check_dry_run_plan_ready": ok,
        "filesystem_existence_check_dry_run_plan_declared": ok,
        "filesystem_existence_check_dry_run_execution_allowed": False,
        "filesystem_existence_check_dry_run_executed": False,
        "one_source_candidate_preserved": ok,
        "source_candidate_count_fixed_to_one": ok,
        "explicit_dry_run_plan_ack_matched": ok,
        "path_shape_preview_string_only": ok,
        "warroom_page_mutation_allowed": False,
        "source_artifact_resolver_invoked": False,
        "source_artifact_resolution_allowed": False,
        "source_artifact_resolved": False,
        "source_artifact_path_materialized": False,
        "source_artifact_exists_check_allowed": False,
        "source_artifact_exists_checked": False,
        "source_artifact_exists_result_available": False,
        "source_artifact_schema_check_allowed": False,
        "source_artifact_schema_checked": False,
        "actual_source_read_allowed": False,
        "actual_source_read_invoked": False,
        "payload_reparse_allowed": False,
        "source_discovery_allowed": False,
        "d_hot_directory_scan_allowed": False,
        "d_hot_actual_read_allowed": False,
        "freshness_checked_against_d_hot": False,
        "q18u_validation_invoked_by_mount": False,
        "q18t_validation_invoked_by_mount": False,
        "q18s_validation_invoked_by_mount": False,
        "q18r_validation_invoked_by_mount": False,
        "q18q_validation_invoked_by_mount": False,
        "q18p_validation_invoked_by_mount": False,
        "q18o_validation_invoked_by_mount": False,
        "q18n_validation_invoked_by_mount": False,
        "q18m_validation_invoked_by_mount": False,
        "q18j_validation_invoked_by_mount": False,
        "component_packet_builder_invoked_by_mount": False,
        "component_packet_builder_allowed_by_mount": False,
        "component_runtime_binding_allowed": False,
        "streamlit_render_allowed": False,
        "streamlit_render_invoked": False,
        "real_prediction_widget_rendering_allowed": False,
        "warroom_widget_rendering_allowed": False,
        "warroom_ui_trigger_enabled": False,
        "refresh_invocation_allowed": False,
        "scheduler_enabled": False,
        "runtime_artifact_write_allowed": False,
        "status_artifact_write_allowed": False,
        "confidence_increase_allowed": False,
        "parameter_apply_allowed": False,
        "parameter_staging_write_allowed": False,
        "approval_or_authorization_allowed": False,
        "ledger_append_allowed": False,
        "autotrade_trigger_allowed": False,
        "broker_private_api_allowed": False,
        "would_write_runtime_artifact": False,
        "would_write_collector_state": False,
        "would_send_to_broker": False,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="PS-Q18V latest prediction summary widget one-source no-read filesystem existence-check dry-run plan")
    parser.add_argument("--use-observed-fixture", action="store_true", help="Use Q18U observed fixture report; no filesystem exists/schema/read/render/refresh/write is performed.")
    args = parser.parse_args(argv)
    report = build_report(use_observed_fixture=args.use_observed_fixture)
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if report.get("ok") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
