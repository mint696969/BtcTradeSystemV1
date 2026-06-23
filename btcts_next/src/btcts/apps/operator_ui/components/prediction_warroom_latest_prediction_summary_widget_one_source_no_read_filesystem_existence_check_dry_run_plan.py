# path: ./btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_latest_prediction_summary_widget_one_source_no_read_filesystem_existence_check_dry_run_plan.py
# desc: PS-Q18V pure-data no-read filesystem existence-check dry-run plan for latest_prediction_summary_widget one-source candidate. Plan only: no filesystem check, no schema check, no actual read, no D-hot discovery, no render, no refresh, no writes.

from __future__ import annotations

from typing import Any, Mapping

from btcts.apps.operator_ui.components.prediction_widgets.latest_prediction_summary_widget import SOURCE_PACKET_ID, WIDGET_FAMILY_ID
from btcts.apps.operator_ui.components.prediction_warroom_latest_prediction_summary_widget_one_source_no_read_existence_check_gate_open_contract import EXISTENCE_GATE_OPEN_CONTRACT_KIND, EXISTENCE_GATE_OPEN_CONTRACT_STATE, LATEST_PREDICTION_SUMMARY_WIDGET_ONE_SOURCE_NO_READ_EXISTENCE_CHECK_GATE_OPEN_CONTRACT_VERSION, ONE_SOURCE_NO_READ_EXISTENCE_CHECK_GATE_OPEN_CONTRACT_ACK

LATEST_PREDICTION_SUMMARY_WIDGET_ONE_SOURCE_NO_READ_FILESYSTEM_EXISTENCE_CHECK_DRY_RUN_PLAN_VERSION = "prediction_warroom_latest_prediction_summary_widget_one_source_no_read_filesystem_existence_check_dry_run_plan.ps_q18v.v1"
ONE_SOURCE_NO_READ_FILESYSTEM_EXISTENCE_CHECK_DRY_RUN_PLAN_ACK = "PS_Q18V_DECLARE_ONE_SOURCE_NO_READ_FILESYSTEM_EXISTENCE_CHECK_DRY_RUN_PLAN_ONLY"
FILESYSTEM_EXISTENCE_CHECK_DRY_RUN_PLAN_KIND = "no_read_filesystem_existence_check_dry_run_plan"
FILESYSTEM_EXISTENCE_CHECK_DRY_RUN_PLAN_STATE = "plan_declared_not_executed"
FILESYSTEM_EXISTENCE_CHECK_DRY_RUN_PLAN_ITEMS = (
    "dry_run_plan_source_candidate_count",
    "dry_run_plan_widget_family_id",
    "dry_run_plan_source_packet_id",
    "dry_run_plan_candidate_generated_at",
    "dry_run_plan_candidate_source_artifact_ref",
    "dry_run_plan_candidate_market_uid",
    "path_shape_preview",
    "source_gate_open_contract_kind",
    "source_gate_open_contract_state",
    "dry_run_plan_kind",
    "dry_run_plan_state",
    "dry_run_plan_decision",
    "explicit_dry_run_plan_ack",
    "deferred_runtime_boundary",
)


def _as_mapping(value: Any) -> Mapping[str, Any]:
    if hasattr(value, "to_dict"):
        converted = value.to_dict()
        return converted if isinstance(converted, Mapping) else {}
    return value if isinstance(value, Mapping) else {}


def _clean(value: Any) -> str:
    return "" if value is None else str(value)


def _row(item: str, value: Any, note: str) -> dict[str, Any]:
    text = _clean(value)
    return {
        "dry_run_plan_item": item,
        "value": text,
        "state": "declared" if text else "not_supplied",
        "operator_note": note,
        "read_only": True,
        "non_executing": True,
        "one_source_no_read_filesystem_existence_check_dry_run_plan_only": True,
        "source_candidate_count_fixed_to_one": True,
        "filesystem_existence_check_dry_run_plan_declared": True,
        "filesystem_existence_check_dry_run_execution_allowed": False,
        "filesystem_existence_check_dry_run_executed": False,
        "path_shape_preview_string_only": True,
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
        "q18u_validation_invoked_by_mount": False,
        "q18t_validation_invoked_by_mount": False,
        "component_packet_builder_invoked_by_mount": False,
        "streamlit_render_invoked": False,
        "real_prediction_widget_rendering_allowed": False,
        "refresh_invocation_allowed": False,
        "runtime_artifact_write_allowed": False,
    }


def build_latest_prediction_summary_widget_one_source_no_read_filesystem_existence_check_dry_run_plan_rows(*, supplied_gate_open_contract_report: Mapping[str, Any] | Any | None = None) -> list[dict[str, Any]]:
    report = _as_mapping(supplied_gate_open_contract_report)
    return [
        _row("dry_run_plan_source_candidate_count", "1", "Exactly one candidate is named in this dry-run plan."),
        _row("dry_run_plan_widget_family_id", WIDGET_FAMILY_ID, "Dry-run plan is scoped to latest_prediction_summary_widget only."),
        _row("dry_run_plan_source_packet_id", SOURCE_PACKET_ID, "Dry-run plan is scoped to latest_prediction_source_review_packet only."),
        _row("dry_run_plan_candidate_generated_at", report.get("selected_candidate_generated_at"), "Candidate generated_at copied from supplied PS-Q18U report only."),
        _row("dry_run_plan_candidate_source_artifact_ref", report.get("selected_candidate_source_artifact_ref"), "Candidate source artifact ref copied from supplied PS-Q18U report only; not resolved."),
        _row("dry_run_plan_candidate_market_uid", report.get("selected_candidate_market_uid"), "Candidate market uid copied from supplied PS-Q18U report only."),
        _row("path_shape_preview", report.get("path_shape_preview"), "Path-shape preview is still text only; no filesystem path object is created."),
        _row("source_gate_open_contract_kind", report.get("existence_gate_open_contract_kind") or EXISTENCE_GATE_OPEN_CONTRACT_KIND, "Source gate-open contract kind is carried forward from PS-Q18U."),
        _row("source_gate_open_contract_state", report.get("existence_gate_open_contract_state") or EXISTENCE_GATE_OPEN_CONTRACT_STATE, "Source gate-open contract state remains gate not opened."),
        _row("dry_run_plan_kind", FILESYSTEM_EXISTENCE_CHECK_DRY_RUN_PLAN_KIND, "A no-read filesystem existence-check dry-run plan is declared."),
        _row("dry_run_plan_state", FILESYSTEM_EXISTENCE_CHECK_DRY_RUN_PLAN_STATE, "Plan is declared but not executed."),
        _row("dry_run_plan_decision", "plan_only_do_not_execute", "This slice plans a future dry-run but performs no filesystem call."),
        _row("explicit_dry_run_plan_ack", ONE_SOURCE_NO_READ_FILESYSTEM_EXISTENCE_CHECK_DRY_RUN_PLAN_ACK, "Acknowledgement is not approval for filesystem checks, schema checks, or reads."),
        _row("deferred_runtime_boundary", "dry_run_execution_allowed=false; dry_run_executed=false; exists_check=false; schema_check=false; actual_read=false", "All runtime behavior remains deferred."),
    ]


def build_latest_prediction_summary_widget_one_source_no_read_filesystem_existence_check_dry_run_plan_packet(*, supplied_gate_open_contract_report: Mapping[str, Any] | Any | None = None) -> dict[str, Any]:
    report = _as_mapping(supplied_gate_open_contract_report)
    rows = build_latest_prediction_summary_widget_one_source_no_read_filesystem_existence_check_dry_run_plan_rows(supplied_gate_open_contract_report=report)
    failures: list[str] = []
    if len(rows) != 14:
        failures.append("dry_run_plan_row_count_mismatch")
    for row in rows:
        item = str(row.get("dry_run_plan_item") or "")
        if item not in FILESYSTEM_EXISTENCE_CHECK_DRY_RUN_PLAN_ITEMS:
            failures.append(f"unexpected_dry_run_plan_item:{item}")
        for key in ("read_only", "non_executing", "one_source_no_read_filesystem_existence_check_dry_run_plan_only", "source_candidate_count_fixed_to_one", "filesystem_existence_check_dry_run_plan_declared", "path_shape_preview_string_only"):
            if row.get(key) is not True:
                failures.append(f"row_true_boundary_missing:{item}:{key}")
        for key in (
            "filesystem_existence_check_dry_run_execution_allowed",
            "filesystem_existence_check_dry_run_executed",
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
            "q18u_validation_invoked_by_mount",
            "q18t_validation_invoked_by_mount",
            "component_packet_builder_invoked_by_mount",
            "streamlit_render_invoked",
            "real_prediction_widget_rendering_allowed",
            "refresh_invocation_allowed",
            "runtime_artifact_write_allowed",
        ):
            if row.get(key) is not False:
                failures.append(f"row_false_boundary_not_false:{item}:{key}")
    supplied = bool(report)
    candidate_ready = supplied and all(
        _clean(report.get(key))
        for key in ("selected_candidate_generated_at", "selected_candidate_source_artifact_ref", "selected_candidate_market_uid", "path_shape_preview")
    )
    return {
        "ok": not failures,
        "no_read_filesystem_existence_check_dry_run_plan_version": LATEST_PREDICTION_SUMMARY_WIDGET_ONE_SOURCE_NO_READ_FILESYSTEM_EXISTENCE_CHECK_DRY_RUN_PLAN_VERSION,
        "source_no_read_existence_check_gate_open_contract_version": LATEST_PREDICTION_SUMMARY_WIDGET_ONE_SOURCE_NO_READ_EXISTENCE_CHECK_GATE_OPEN_CONTRACT_VERSION,
        "source_no_read_existence_check_gate_open_contract_ack": ONE_SOURCE_NO_READ_EXISTENCE_CHECK_GATE_OPEN_CONTRACT_ACK,
        "widget_family_id": WIDGET_FAMILY_ID,
        "source_packet_id": SOURCE_PACKET_ID,
        "one_source_no_read_filesystem_existence_check_dry_run_plan_ack": ONE_SOURCE_NO_READ_FILESYSTEM_EXISTENCE_CHECK_DRY_RUN_PLAN_ACK,
        "dry_run_plan_state": "latest_prediction_summary_widget_one_source_no_read_filesystem_existence_check_dry_run_plan_declared_not_executed_no_exists_schema_read_or_render",
        "dry_run_plan_row_count": len(rows),
        "dry_run_plan_rows": rows,
        "validation_failures": failures,
        "supplied_gate_open_contract_report": supplied,
        "dry_run_plan_candidate_ready": candidate_ready,
        "one_source_candidate_preserved": True,
        "source_candidate_count": 1,
        "path_shape_preview": _clean(report.get("path_shape_preview")) if report else "",
        "path_shape_preview_string_only": True,
        "source_gate_open_contract_kind": str(report.get("existence_gate_open_contract_kind") or EXISTENCE_GATE_OPEN_CONTRACT_KIND),
        "source_gate_open_contract_state": str(report.get("existence_gate_open_contract_state") or EXISTENCE_GATE_OPEN_CONTRACT_STATE),
        "filesystem_existence_check_dry_run_plan_kind": FILESYSTEM_EXISTENCE_CHECK_DRY_RUN_PLAN_KIND,
        "filesystem_existence_check_dry_run_plan_state": FILESYSTEM_EXISTENCE_CHECK_DRY_RUN_PLAN_STATE,
        "selected_candidate_generated_at": _clean(report.get("selected_candidate_generated_at")) if report else "",
        "selected_candidate_source_artifact_ref": _clean(report.get("selected_candidate_source_artifact_ref")) if report else "",
        "selected_candidate_market_uid": _clean(report.get("selected_candidate_market_uid")) if report else "",
        "read_only": True,
        "non_executing": True,
        "latest_prediction_summary_widget_one_source_no_read_filesystem_existence_check_dry_run_plan_only": True,
        "one_source_no_read_filesystem_existence_check_dry_run_plan_ready": True,
        "filesystem_existence_check_dry_run_plan_declared": True,
        "filesystem_existence_check_dry_run_execution_allowed": False,
        "filesystem_existence_check_dry_run_executed": False,
        "source_candidate_count_fixed_to_one": True,
        "explicit_dry_run_plan_ack_matched": True,
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
