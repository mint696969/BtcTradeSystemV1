# path: ./tools/check_phase4a_prediction_system_ps_q18t_latest_prediction_summary_widget_one_source_no_read_existence_check_execution_preflight.py
# desc: PS-Q18T checker for latest_prediction_summary_widget one-source no-read existence-check execution preflight. Preflight only; gate remains closed, no filesystem check, schema check, actual read, render, refresh, writes, AutoTrade, or broker APIs.

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
from check_phase4a_prediction_system_ps_q18s_latest_prediction_summary_widget_one_source_no_read_existence_check_execution_gate import CHECKER_VERSION as PS_Q18S_CHECKER_VERSION
from check_phase4a_prediction_system_ps_q18s_latest_prediction_summary_widget_one_source_no_read_existence_check_execution_gate import build_report as build_ps_q18s_report
from btcts.apps.operator_ui.components.prediction_warroom_latest_prediction_summary_widget_one_source_no_read_existence_check_execution_preflight import EXISTENCE_EXECUTION_PREFLIGHT_KIND, EXISTENCE_EXECUTION_PREFLIGHT_STATE, LATEST_PREDICTION_SUMMARY_WIDGET_ONE_SOURCE_NO_READ_EXISTENCE_CHECK_EXECUTION_PREFLIGHT_VERSION, ONE_SOURCE_NO_READ_EXISTENCE_CHECK_EXECUTION_PREFLIGHT_ACK, build_latest_prediction_summary_widget_one_source_no_read_existence_check_execution_preflight_packet

CHECKER = "ps_q18t_latest_prediction_summary_widget_one_source_no_read_existence_check_execution_preflight"
CHECKER_VERSION = "check_phase4a_prediction_system_ps_q18t_latest_prediction_summary_widget_one_source_no_read_existence_check_execution_preflight.v1"
ONE_SOURCE_NO_READ_EXISTENCE_CHECK_EXECUTION_PREFLIGHT_CHECK_VERSION = "latest_prediction_summary_widget_one_source_no_read_existence_check_execution_preflight.v1"
PS_Q18S_SOURCE_CHECKER_VERSION = PS_Q18S_CHECKER_VERSION
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


def _safe_q18s_boundary(report: Mapping[str, Any]) -> tuple[bool, list[str]]:
    failures: list[str] = []
    if report.get("checker_version") != PS_Q18S_SOURCE_CHECKER_VERSION:
        failures.append("q18s_checker_version_mismatch")
    if report.get("ok") is not True:
        failures.append("q18s_report_not_ok")
    if report.get("execution_gate_packet_valid") is not True:
        failures.append("q18s_execution_gate_packet_not_valid")
    if report.get("source_candidate_count") != 1:
        failures.append("q18s_source_candidate_count_not_one")
    if report.get("execution_gate_candidate_ready") is not True:
        failures.append("q18s_execution_gate_candidate_not_ready")
    if report.get("path_shape_preview") != EXPECTED_PATH_SHAPE_PREVIEW:
        failures.append("q18s_path_shape_preview_mismatch")
    if report.get("existence_check_execution_gate_open") is not False:
        failures.append("q18s_gate_open_should_be_false")
    for key, value in EXPECTED_SELECTED.items():
        if report.get(key) != value:
            failures.append(f"q18s_selected_candidate_mismatch:{key}")
    for key in ("latest_prediction_summary_widget_one_source_no_read_existence_check_execution_gate_only", "existence_check_execution_gate_declared", "path_shape_preview_string_only", "source_candidate_count_fixed_to_one"):
        if report.get(key) is not True:
            failures.append(f"q18s_true_boundary_missing:{key}")
    for key in ("warroom_page_mutation_allowed", "source_artifact_resolver_invoked", "source_artifact_resolution_allowed", "source_artifact_path_materialized", "source_artifact_exists_check_allowed", "source_artifact_exists_checked", "source_artifact_schema_check_allowed", "source_artifact_schema_checked", "actual_source_read_allowed", "actual_source_read_invoked", "payload_reparse_allowed", "source_discovery_allowed", "d_hot_directory_scan_allowed", "d_hot_actual_read_allowed", "q18r_validation_invoked_by_mount", "component_packet_builder_invoked_by_mount", "streamlit_render_invoked", "real_prediction_widget_rendering_allowed", "refresh_invocation_allowed", "runtime_artifact_write_allowed", "parameter_apply_allowed", "broker_private_api_allowed"):
        if report.get(key) is not False:
            failures.append(f"q18s_boundary_not_false:{key}")
    return not failures, failures


def _safe_preflight_packet(packet: Mapping[str, Any]) -> tuple[bool, list[str]]:
    failures: list[str] = []
    if packet.get("no_read_existence_check_execution_preflight_version") != LATEST_PREDICTION_SUMMARY_WIDGET_ONE_SOURCE_NO_READ_EXISTENCE_CHECK_EXECUTION_PREFLIGHT_VERSION:
        failures.append("execution_preflight_version_mismatch")
    if packet.get("one_source_no_read_existence_check_execution_preflight_ack") != ONE_SOURCE_NO_READ_EXISTENCE_CHECK_EXECUTION_PREFLIGHT_ACK:
        failures.append("execution_preflight_ack_mismatch")
    if packet.get("existence_execution_preflight_kind") != EXISTENCE_EXECUTION_PREFLIGHT_KIND:
        failures.append("execution_preflight_kind_mismatch")
    if packet.get("existence_execution_preflight_state") != EXISTENCE_EXECUTION_PREFLIGHT_STATE:
        failures.append("execution_preflight_state_mismatch")
    if packet.get("ok") is not True:
        failures.append("execution_preflight_packet_not_ok")
    if packet.get("execution_preflight_row_count") != 14:
        failures.append("execution_preflight_row_count_mismatch")
    if packet.get("path_shape_preview") != EXPECTED_PATH_SHAPE_PREVIEW:
        failures.append("path_shape_preview_mismatch")
    for key in ("latest_prediction_summary_widget_one_source_no_read_existence_check_execution_preflight_only", "one_source_no_read_existence_check_execution_preflight_ready", "existence_check_execution_preflight_declared", "source_candidate_count_fixed_to_one", "explicit_execution_preflight_ack_matched", "path_shape_preview_string_only"):
        if packet.get(key) is not True:
            failures.append(f"execution_preflight_true_boundary_missing:{key}")
    for key in ("existence_check_execution_preflight_would_open_gate", "source_artifact_resolver_invoked", "source_artifact_resolution_allowed", "source_artifact_resolved", "source_artifact_path_materialized", "source_artifact_exists_check_allowed", "source_artifact_exists_checked", "source_artifact_exists_result_available", "source_artifact_schema_check_allowed", "source_artifact_schema_checked", "actual_source_read_allowed", "actual_source_read_invoked", "payload_reparse_allowed", "source_discovery_allowed", "d_hot_directory_scan_allowed", "d_hot_actual_read_allowed", "q18s_validation_invoked_by_mount", "q18r_validation_invoked_by_mount", "component_packet_builder_invoked_by_mount", "streamlit_render_invoked", "real_prediction_widget_rendering_allowed", "refresh_invocation_allowed", "runtime_artifact_write_allowed", "parameter_apply_allowed", "broker_private_api_allowed"):
        if packet.get(key) is not False:
            failures.append(f"execution_preflight_boundary_not_false:{key}")
    return not failures, failures


def build_report(*, supplied_q18s_report: Mapping[str, Any] | Any | None = None, use_observed_fixture: bool = False) -> dict[str, Any]:
    q18s_report = _as_mapping(supplied_q18s_report)
    if not q18s_report and use_observed_fixture:
        q18s_report = build_ps_q18s_report(use_observed_fixture=True)
    safe_q18s, q18s_failures = _safe_q18s_boundary(q18s_report)
    preflight_packet = build_latest_prediction_summary_widget_one_source_no_read_existence_check_execution_preflight_packet(supplied_execution_gate_report=q18s_report) if safe_q18s else {}
    safe_preflight, preflight_failures = _safe_preflight_packet(preflight_packet) if preflight_packet else (False, [])
    ok = bool(safe_q18s and safe_preflight)
    return {
        "ok": ok,
        "checker": CHECKER,
        "checker_version": CHECKER_VERSION,
        "one_source_no_read_existence_check_execution_preflight_check_version": ONE_SOURCE_NO_READ_EXISTENCE_CHECK_EXECUTION_PREFLIGHT_CHECK_VERSION,
        "stage": "latest_prediction_summary_widget_one_source_no_read_existence_check_execution_preflight_before_gate_open_exists_schema_read_render_refresh_and_writes",
        "source_q18s_checker_version": PS_Q18S_SOURCE_CHECKER_VERSION,
        "source_q18s_report_valid": safe_q18s,
        "source_q18s_validation_failures": q18s_failures,
        "execution_preflight_packet_valid": safe_preflight,
        "execution_preflight_validation_failures": preflight_failures,
        "use_observed_fixture": bool(use_observed_fixture),
        "no_read_existence_check_execution_preflight_version": LATEST_PREDICTION_SUMMARY_WIDGET_ONE_SOURCE_NO_READ_EXISTENCE_CHECK_EXECUTION_PREFLIGHT_VERSION,
        "one_source_no_read_existence_check_execution_preflight_ack": ONE_SOURCE_NO_READ_EXISTENCE_CHECK_EXECUTION_PREFLIGHT_ACK,
        "execution_preflight_row_count": int(preflight_packet.get("execution_preflight_row_count") or 0) if preflight_packet else 0,
        "source_candidate_count": int(preflight_packet.get("source_candidate_count") or 0) if preflight_packet else 0,
        "execution_preflight_candidate_ready": bool(preflight_packet.get("execution_preflight_candidate_ready")) if preflight_packet else False,
        "existence_execution_preflight_kind": str(preflight_packet.get("existence_execution_preflight_kind") or "") if preflight_packet else "",
        "existence_execution_preflight_state": str(preflight_packet.get("existence_execution_preflight_state") or "") if preflight_packet else "",
        "path_shape_preview": str(preflight_packet.get("path_shape_preview") or "") if preflight_packet else "",
        **EXPECTED_SELECTED,
        "recommended_first_validation": "latest_prediction_summary_widget_one_source_no_read_existence_check_execution_preflight_guard" if ok else "",
        "recommended_next_slice": "PS-Q18U explicit one-source no-read existence check execution gate-open contract; actual source read, real widget rendering, refresh invocation, confidence increase, and parameter staging/apply remain deferred.",
        "human_interpretation": "PS-Q18T declares a no-read existence-check execution preflight while keeping the gate closed. It does not open the gate, run filesystem existence checks, run schema checks, read D-hot, reparse payloads, render widgets, refresh, write artifacts, stage/apply parameters, append ledgers, trigger AutoTrade, or call broker APIs.",
        "read_only": True,
        "non_executing": True,
        "latest_prediction_summary_widget_one_source_no_read_existence_check_execution_preflight_only": True,
        "one_source_no_read_existence_check_execution_preflight_ready": ok,
        "existence_check_execution_preflight_declared": ok,
        "existence_check_execution_preflight_would_open_gate": False,
        "one_source_candidate_preserved": ok,
        "source_candidate_count_fixed_to_one": ok,
        "explicit_execution_preflight_ack_matched": ok,
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
    parser = argparse.ArgumentParser(description="PS-Q18T latest prediction summary widget one-source no-read existence-check execution preflight")
    parser.add_argument("--use-observed-fixture", action="store_true", help="Use Q18S observed fixture report; preflight does not open gate and no exists/schema/read/render/refresh/write is performed.")
    args = parser.parse_args(argv)
    report = build_report(use_observed_fixture=args.use_observed_fixture)
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if report.get("ok") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
