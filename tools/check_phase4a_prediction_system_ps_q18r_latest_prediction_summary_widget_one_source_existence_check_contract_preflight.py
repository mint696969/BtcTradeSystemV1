# path: ./tools/check_phase4a_prediction_system_ps_q18r_latest_prediction_summary_widget_one_source_existence_check_contract_preflight.py
# desc: PS-Q18R checker for latest_prediction_summary_widget one-source existence-check contract preflight. No resolver invocation, filesystem existence/schema check, actual read, D-hot discovery, render, refresh, writes, AutoTrade, or broker APIs.

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Any, Mapping

BTCTS_SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "btcts_next", "src")
if BTCTS_SRC not in sys.path:
    sys.path.insert(0, BTCTS_SRC)

from check_phase4a_prediction_system_ps_q18q_latest_prediction_summary_widget_one_source_resolver_dry_run_path_shape_preflight import CHECKER_VERSION as PS_Q18Q_CHECKER_VERSION
from check_phase4a_prediction_system_ps_q18q_latest_prediction_summary_widget_one_source_resolver_dry_run_path_shape_preflight import EXPECTED_PATH_SHAPE_PREVIEW
from check_phase4a_prediction_system_ps_q18q_latest_prediction_summary_widget_one_source_resolver_dry_run_path_shape_preflight import build_report as build_ps_q18q_report
from btcts.apps.operator_ui.components.prediction_warroom_latest_prediction_summary_widget_one_source_existence_check_contract_preflight import EXISTENCE_CHECK_KIND, EXISTENCE_RESULT_STATE, LATEST_PREDICTION_SUMMARY_WIDGET_ONE_SOURCE_EXISTENCE_CHECK_CONTRACT_PREFLIGHT_VERSION, ONE_SOURCE_EXISTENCE_CHECK_CONTRACT_ACK, build_latest_prediction_summary_widget_one_source_existence_check_contract_preflight_packet

CHECKER = "ps_q18r_latest_prediction_summary_widget_one_source_existence_check_contract_preflight"
CHECKER_VERSION = "check_phase4a_prediction_system_ps_q18r_latest_prediction_summary_widget_one_source_existence_check_contract_preflight.v1"
ONE_SOURCE_EXISTENCE_CHECK_CONTRACT_PREFLIGHT_CHECK_VERSION = "latest_prediction_summary_widget_one_source_existence_check_contract_preflight.v1"
PS_Q18Q_SOURCE_CHECKER_VERSION = PS_Q18Q_CHECKER_VERSION
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


def _safe_q18q_boundary(report: Mapping[str, Any]) -> tuple[bool, list[str]]:
    failures: list[str] = []
    if report.get("checker_version") != PS_Q18Q_SOURCE_CHECKER_VERSION:
        failures.append("q18q_checker_version_mismatch")
    if report.get("ok") is not True:
        failures.append("q18q_report_not_ok")
    if report.get("path_shape_packet_valid") is not True:
        failures.append("q18q_path_shape_packet_not_valid")
    if report.get("source_candidate_count") != 1:
        failures.append("q18q_source_candidate_count_not_one")
    if report.get("path_shape_candidate_ready") is not True:
        failures.append("q18q_path_shape_candidate_not_ready")
    if report.get("path_shape_preview") != EXPECTED_PATH_SHAPE_PREVIEW:
        failures.append("q18q_path_shape_preview_mismatch")
    for key, value in EXPECTED_SELECTED.items():
        if report.get(key) != value:
            failures.append(f"q18q_selected_candidate_mismatch:{key}")
    for key in ("latest_prediction_summary_widget_one_source_resolver_dry_run_path_shape_preflight_only", "path_shape_declared", "path_shape_preview_string_only", "source_candidate_count_fixed_to_one"):
        if report.get(key) is not True:
            failures.append(f"q18q_true_boundary_missing:{key}")
    for key in ("warroom_page_mutation_allowed", "source_artifact_resolver_invoked", "source_artifact_resolution_allowed", "source_artifact_path_materialized", "source_artifact_exists_checked", "source_artifact_schema_checked", "actual_source_read_allowed", "actual_source_read_invoked", "payload_reparse_allowed", "source_discovery_allowed", "d_hot_directory_scan_allowed", "d_hot_actual_read_allowed", "q18p_validation_invoked_by_mount", "component_packet_builder_invoked_by_mount", "streamlit_render_invoked", "real_prediction_widget_rendering_allowed", "refresh_invocation_allowed", "runtime_artifact_write_allowed", "parameter_apply_allowed", "broker_private_api_allowed"):
        if report.get(key) is not False:
            failures.append(f"q18q_boundary_not_false:{key}")
    return not failures, failures


def _safe_existence_packet(packet: Mapping[str, Any]) -> tuple[bool, list[str]]:
    failures: list[str] = []
    if packet.get("existence_check_contract_preflight_version") != LATEST_PREDICTION_SUMMARY_WIDGET_ONE_SOURCE_EXISTENCE_CHECK_CONTRACT_PREFLIGHT_VERSION:
        failures.append("existence_contract_preflight_version_mismatch")
    if packet.get("one_source_existence_check_contract_ack") != ONE_SOURCE_EXISTENCE_CHECK_CONTRACT_ACK:
        failures.append("existence_contract_ack_mismatch")
    if packet.get("existence_check_kind") != EXISTENCE_CHECK_KIND:
        failures.append("existence_check_kind_mismatch")
    if packet.get("existence_result_state") != EXISTENCE_RESULT_STATE:
        failures.append("existence_result_state_mismatch")
    if packet.get("ok") is not True:
        failures.append("existence_contract_packet_not_ok")
    if packet.get("existence_contract_row_count") != 14:
        failures.append("existence_contract_row_count_mismatch")
    if packet.get("source_candidate_count") != 1:
        failures.append("source_candidate_count_mismatch")
    if packet.get("path_shape_preview") != EXPECTED_PATH_SHAPE_PREVIEW:
        failures.append("path_shape_preview_mismatch")
    for key in ("latest_prediction_summary_widget_one_source_existence_check_contract_preflight_only", "one_source_existence_check_contract_preflight_ready", "existence_check_contract_declared", "source_candidate_count_fixed_to_one", "explicit_existence_check_contract_ack_matched", "path_shape_preview_string_only"):
        if packet.get(key) is not True:
            failures.append(f"existence_true_boundary_missing:{key}")
    for key in ("source_artifact_resolver_invoked", "source_artifact_resolution_allowed", "source_artifact_resolved", "source_artifact_path_materialized", "source_artifact_exists_check_allowed", "source_artifact_exists_checked", "source_artifact_exists_result_available", "source_artifact_schema_check_allowed", "source_artifact_schema_checked", "actual_source_read_allowed", "actual_source_read_invoked", "payload_reparse_allowed", "source_discovery_allowed", "d_hot_directory_scan_allowed", "d_hot_actual_read_allowed", "q18q_validation_invoked_by_mount", "q18p_validation_invoked_by_mount", "component_packet_builder_invoked_by_mount", "streamlit_render_invoked", "real_prediction_widget_rendering_allowed", "refresh_invocation_allowed", "runtime_artifact_write_allowed", "parameter_apply_allowed", "broker_private_api_allowed"):
        if packet.get(key) is not False:
            failures.append(f"existence_boundary_not_false:{key}")
    return not failures, failures


def build_report(*, supplied_q18q_report: Mapping[str, Any] | Any | None = None, use_observed_fixture: bool = False) -> dict[str, Any]:
    q18q_report = _as_mapping(supplied_q18q_report)
    if not q18q_report and use_observed_fixture:
        q18q_report = build_ps_q18q_report(use_observed_fixture=True)
    safe_q18q, q18q_failures = _safe_q18q_boundary(q18q_report)
    existence_packet = build_latest_prediction_summary_widget_one_source_existence_check_contract_preflight_packet(supplied_path_shape_report=q18q_report) if safe_q18q else {}
    safe_existence, existence_failures = _safe_existence_packet(existence_packet) if existence_packet else (False, [])
    ok = bool(safe_q18q and safe_existence)
    return {
        "ok": ok,
        "checker": CHECKER,
        "checker_version": CHECKER_VERSION,
        "one_source_existence_check_contract_preflight_check_version": ONE_SOURCE_EXISTENCE_CHECK_CONTRACT_PREFLIGHT_CHECK_VERSION,
        "stage": "latest_prediction_summary_widget_one_source_existence_check_contract_preflight_before_exists_schema_read_render_refresh_and_writes",
        "source_q18q_checker_version": PS_Q18Q_SOURCE_CHECKER_VERSION,
        "source_q18q_report_valid": safe_q18q,
        "source_q18q_validation_failures": q18q_failures,
        "existence_contract_packet_valid": safe_existence,
        "existence_contract_validation_failures": existence_failures,
        "use_observed_fixture": bool(use_observed_fixture),
        "existence_check_contract_preflight_version": LATEST_PREDICTION_SUMMARY_WIDGET_ONE_SOURCE_EXISTENCE_CHECK_CONTRACT_PREFLIGHT_VERSION,
        "one_source_existence_check_contract_ack": ONE_SOURCE_EXISTENCE_CHECK_CONTRACT_ACK,
        "existence_contract_row_count": int(existence_packet.get("existence_contract_row_count") or 0) if existence_packet else 0,
        "source_candidate_count": int(existence_packet.get("source_candidate_count") or 0) if existence_packet else 0,
        "existence_contract_candidate_ready": bool(existence_packet.get("existence_contract_candidate_ready")) if existence_packet else False,
        "existence_check_kind": str(existence_packet.get("existence_check_kind") or "") if existence_packet else "",
        "existence_result_state": str(existence_packet.get("existence_result_state") or "") if existence_packet else "",
        "path_shape_preview": str(existence_packet.get("path_shape_preview") or "") if existence_packet else "",
        **EXPECTED_SELECTED,
        "recommended_first_validation": "latest_prediction_summary_widget_one_source_existence_check_contract_preflight_guard" if ok else "",
        "recommended_next_slice": "PS-Q18S explicit one-source no-read existence check execution gate; actual source read, real widget rendering, refresh invocation, confidence increase, and parameter staging/apply remain deferred.",
        "human_interpretation": "PS-Q18R declares the existence-check contract for one latest_prediction_summary_widget path-shape candidate. It does not run filesystem existence checks, does not materialize a path object, does not run schema checks, does not read D-hot, does not reparse payloads, render widgets, refresh, write artifacts, stage/apply parameters, append ledgers, trigger AutoTrade, or call broker APIs.",
        "read_only": True,
        "non_executing": True,
        "latest_prediction_summary_widget_one_source_existence_check_contract_preflight_only": True,
        "one_source_existence_check_contract_preflight_ready": ok,
        "existence_check_contract_declared": ok,
        "one_source_candidate_preserved": ok,
        "source_candidate_count_fixed_to_one": ok,
        "explicit_existence_check_contract_ack_matched": ok,
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
    parser = argparse.ArgumentParser(description="PS-Q18R latest prediction summary widget one-source existence-check contract preflight")
    parser.add_argument("--use-observed-fixture", action="store_true", help="Use Q18Q observed fixture report; no filesystem exists/schema/read/render/refresh/write is performed.")
    args = parser.parse_args(argv)
    report = build_report(use_observed_fixture=args.use_observed_fixture)
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if report.get("ok") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
