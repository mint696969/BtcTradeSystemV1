# path: ./tools/check_phase4a_prediction_system_ps_q18o_latest_prediction_summary_widget_one_source_handoff_design_checkpoint.py
# desc: PS-Q18O checker for latest_prediction_summary_widget explicit one-source handoff design checkpoint. No source resolution, actual read, D-hot discovery, render, refresh, writes, AutoTrade, or broker APIs.

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Any, Mapping

BTCTS_SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "btcts_next", "src")
if BTCTS_SRC not in sys.path:
    sys.path.insert(0, BTCTS_SRC)

from check_phase4a_prediction_system_ps_q18n_latest_prediction_summary_widget_real_source_handoff_preflight_mount import CHECKER_VERSION as PS_Q18N_CHECKER_VERSION
from check_phase4a_prediction_system_ps_q18n_latest_prediction_summary_widget_real_source_handoff_preflight_mount import build_report as build_ps_q18n_report
from btcts.apps.operator_ui.components.prediction_warroom_latest_prediction_summary_widget_one_source_handoff_design_checkpoint import LATEST_PREDICTION_SUMMARY_WIDGET_ONE_SOURCE_HANDOFF_DESIGN_CHECKPOINT_VERSION, ONE_SOURCE_HANDOFF_DESIGN_ACK, build_latest_prediction_summary_widget_one_source_handoff_design_checkpoint_packet

CHECKER = "ps_q18o_latest_prediction_summary_widget_one_source_handoff_design_checkpoint"
CHECKER_VERSION = "check_phase4a_prediction_system_ps_q18o_latest_prediction_summary_widget_one_source_handoff_design_checkpoint.v1"
ONE_SOURCE_HANDOFF_DESIGN_CHECK_VERSION = "latest_prediction_summary_widget_one_source_handoff_design_checkpoint.v1"
PS_Q18N_SOURCE_CHECKER_VERSION = PS_Q18N_CHECKER_VERSION
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


def _safe_q18n_boundary(report: Mapping[str, Any]) -> tuple[bool, list[str]]:
    failures: list[str] = []
    if report.get("checker_version") != PS_Q18N_SOURCE_CHECKER_VERSION:
        failures.append("q18n_checker_version_mismatch")
    if report.get("ok") is not True:
        failures.append("q18n_report_not_ok")
    if report.get("handoff_packet_valid") is not True:
        failures.append("q18n_handoff_packet_not_valid")
    if report.get("handoff_candidate_ready") is not True:
        failures.append("q18n_handoff_candidate_not_ready")
    for key, value in {
        "candidate_generated_at": "2026-06-22T00:00:00Z",
        "candidate_source_artifact_ref": "fixture://ps_q18i/latest_prediction.json",
        "candidate_market_uid": "BTC-USD",
    }.items():
        if report.get(key) != value:
            failures.append(f"q18n_candidate_mismatch:{key}")
    for key in ("latest_prediction_summary_widget_real_source_handoff_preflight_mount_only", "real_source_handoff_preflight_only"):
        if report.get(key) is not True:
            failures.append(f"q18n_true_boundary_missing:{key}")
    for key in ("real_source_handoff_invoked", "actual_source_resolution_allowed", "actual_source_read_invoked", "payload_reparse_allowed", "source_discovery_allowed", "d_hot_directory_scan_allowed", "d_hot_actual_read_allowed", "q18m_validation_invoked_by_mount", "q18j_validation_invoked_by_mount", "component_packet_builder_invoked_by_mount", "streamlit_render_invoked", "real_prediction_widget_rendering_allowed", "refresh_invocation_allowed", "runtime_artifact_write_allowed", "parameter_apply_allowed", "broker_private_api_allowed"):
        if report.get(key) is not False:
            failures.append(f"q18n_boundary_not_false:{key}")
    return not failures, failures


def _safe_design_packet(packet: Mapping[str, Any]) -> tuple[bool, list[str]]:
    failures: list[str] = []
    if packet.get("design_checkpoint_version") != LATEST_PREDICTION_SUMMARY_WIDGET_ONE_SOURCE_HANDOFF_DESIGN_CHECKPOINT_VERSION:
        failures.append("design_checkpoint_version_mismatch")
    if packet.get("one_source_handoff_design_ack") != ONE_SOURCE_HANDOFF_DESIGN_ACK:
        failures.append("design_ack_mismatch")
    if packet.get("ok") is not True:
        failures.append("design_packet_not_ok")
    if packet.get("design_row_count") != 8:
        failures.append("design_row_count_mismatch")
    if packet.get("source_candidate_count") != 1:
        failures.append("source_candidate_count_mismatch")
    for key in ("latest_prediction_summary_widget_one_source_handoff_design_checkpoint_only", "one_source_handoff_design_checkpoint_ready", "source_candidate_count_fixed_to_one", "explicit_design_ack_matched"):
        if packet.get(key) is not True:
            failures.append(f"design_true_boundary_missing:{key}")
    for key in ("real_source_handoff_invoked", "source_artifact_resolution_allowed", "source_artifact_resolved", "source_artifact_path_materialized", "source_artifact_exists_checked", "source_artifact_schema_checked", "actual_source_read_allowed", "actual_source_read_invoked", "payload_reparse_allowed", "source_discovery_allowed", "d_hot_directory_scan_allowed", "d_hot_actual_read_allowed", "q18n_validation_invoked_by_mount", "q18m_validation_invoked_by_mount", "q18j_validation_invoked_by_mount", "component_packet_builder_invoked_by_mount", "streamlit_render_invoked", "real_prediction_widget_rendering_allowed", "refresh_invocation_allowed", "runtime_artifact_write_allowed", "parameter_apply_allowed", "broker_private_api_allowed"):
        if packet.get(key) is not False:
            failures.append(f"design_boundary_not_false:{key}")
    return not failures, failures


def build_report(*, supplied_q18n_report: Mapping[str, Any] | Any | None = None, use_observed_fixture: bool = False) -> dict[str, Any]:
    q18n_report = _as_mapping(supplied_q18n_report)
    if not q18n_report and use_observed_fixture:
        q18n_report = build_ps_q18n_report(use_observed_fixture=True)
    safe_q18n, q18n_failures = _safe_q18n_boundary(q18n_report)
    design_packet = build_latest_prediction_summary_widget_one_source_handoff_design_checkpoint_packet(supplied_handoff_preflight_report=q18n_report) if safe_q18n else {}
    safe_design, design_failures = _safe_design_packet(design_packet) if design_packet else (False, [])
    ok = bool(safe_q18n and safe_design)
    return {
        "ok": ok,
        "checker": CHECKER,
        "checker_version": CHECKER_VERSION,
        "one_source_handoff_design_check_version": ONE_SOURCE_HANDOFF_DESIGN_CHECK_VERSION,
        "stage": "latest_prediction_summary_widget_one_source_handoff_design_checkpoint_before_resolution_read_render_refresh_and_writes",
        "source_q18n_checker_version": PS_Q18N_SOURCE_CHECKER_VERSION,
        "source_q18n_report_valid": safe_q18n,
        "source_q18n_validation_failures": q18n_failures,
        "design_packet_valid": safe_design,
        "design_validation_failures": design_failures,
        "use_observed_fixture": bool(use_observed_fixture),
        "design_checkpoint_version": LATEST_PREDICTION_SUMMARY_WIDGET_ONE_SOURCE_HANDOFF_DESIGN_CHECKPOINT_VERSION,
        "one_source_handoff_design_ack": ONE_SOURCE_HANDOFF_DESIGN_ACK,
        "design_row_count": int(design_packet.get("design_row_count") or 0) if design_packet else 0,
        "source_candidate_count": int(design_packet.get("source_candidate_count") or 0) if design_packet else 0,
        "handoff_candidate_ready": bool(design_packet.get("handoff_candidate_ready")) if design_packet else False,
        **EXPECTED_SELECTED,
        "recommended_first_validation": "latest_prediction_summary_widget_one_source_handoff_design_checkpoint_guard" if ok else "",
        "recommended_next_slice": "PS-Q18P explicit one-source resolver contract preflight; actual source resolution/read, real widget rendering, refresh invocation, confidence increase, and parameter staging/apply remain deferred.",
        "human_interpretation": "PS-Q18O declares exactly one latest_prediction_summary_widget source handoff candidate and the explicit design-only ack. It does not resolve source artifacts, materialize paths, check file existence/schema, read D-hot, reparse payloads, render widgets, refresh, write artifacts, stage/apply parameters, append ledgers, trigger AutoTrade, or call broker APIs.",
        "read_only": True,
        "non_executing": True,
        "latest_prediction_summary_widget_one_source_handoff_design_checkpoint_only": True,
        "one_source_handoff_design_checkpoint_ready": ok,
        "one_source_candidate_declared": ok,
        "source_candidate_count_fixed_to_one": ok,
        "explicit_design_ack_matched": ok,
        "warroom_page_mutation_allowed": False,
        "real_source_handoff_invoked": False,
        "source_artifact_resolution_allowed": False,
        "source_artifact_resolved": False,
        "source_artifact_path_materialized": False,
        "source_artifact_exists_checked": False,
        "source_artifact_schema_checked": False,
        "actual_source_read_allowed": False,
        "actual_source_read_invoked": False,
        "payload_reparse_allowed": False,
        "source_discovery_allowed": False,
        "d_hot_directory_scan_allowed": False,
        "d_hot_actual_read_allowed": False,
        "freshness_checked_against_d_hot": False,
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
    parser = argparse.ArgumentParser(description="PS-Q18O latest prediction summary widget one-source handoff design checkpoint")
    parser.add_argument("--use-observed-fixture", action="store_true", help="Use Q18N observed fixture report; no source resolution/read/render/refresh/write is performed.")
    args = parser.parse_args(argv)
    report = build_report(use_observed_fixture=args.use_observed_fixture)
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if report.get("ok") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
