# path: ./btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_latest_prediction_summary_widget_one_source_no_read_existence_check_execution_preflight.py
# desc: PS-Q18T pure-data no-read existence-check execution preflight for latest_prediction_summary_widget one-source candidate. Preflight only: gate remains closed; no filesystem check, no schema check, no actual read, no D-hot discovery, no render, no refresh, no writes.

from __future__ import annotations

from typing import Any, Mapping

from btcts.apps.operator_ui.components.prediction_widgets.latest_prediction_summary_widget import SOURCE_PACKET_ID, WIDGET_FAMILY_ID
from btcts.apps.operator_ui.components.prediction_warroom_latest_prediction_summary_widget_one_source_no_read_existence_check_execution_gate import EXISTENCE_EXECUTION_GATE_KIND, EXISTENCE_EXECUTION_GATE_STATE, LATEST_PREDICTION_SUMMARY_WIDGET_ONE_SOURCE_NO_READ_EXISTENCE_CHECK_EXECUTION_GATE_VERSION, ONE_SOURCE_NO_READ_EXISTENCE_CHECK_EXECUTION_GATE_ACK

LATEST_PREDICTION_SUMMARY_WIDGET_ONE_SOURCE_NO_READ_EXISTENCE_CHECK_EXECUTION_PREFLIGHT_VERSION = "prediction_warroom_latest_prediction_summary_widget_one_source_no_read_existence_check_execution_preflight.ps_q18t.v1"
ONE_SOURCE_NO_READ_EXISTENCE_CHECK_EXECUTION_PREFLIGHT_ACK = "PS_Q18T_DECLARE_ONE_SOURCE_NO_READ_EXISTENCE_CHECK_EXECUTION_PREFLIGHT_ONLY"
EXISTENCE_EXECUTION_PREFLIGHT_KIND = "no_read_existence_check_execution_preflight_closed"
EXISTENCE_EXECUTION_PREFLIGHT_STATE = "preflight_declared_not_executed"
EXISTENCE_EXECUTION_PREFLIGHT_ITEMS = (
    "execution_preflight_source_candidate_count",
    "execution_preflight_widget_family_id",
    "execution_preflight_source_packet_id",
    "execution_preflight_candidate_generated_at",
    "execution_preflight_candidate_source_artifact_ref",
    "execution_preflight_candidate_market_uid",
    "path_shape_preview",
    "source_gate_kind",
    "source_gate_state",
    "execution_preflight_kind",
    "execution_preflight_state",
    "execution_preflight_decision",
    "explicit_execution_preflight_ack",
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
        "execution_preflight_item": item,
        "value": text,
        "state": "declared" if text else "not_supplied",
        "operator_note": note,
        "read_only": True,
        "non_executing": True,
        "one_source_no_read_existence_check_execution_preflight_only": True,
        "source_candidate_count_fixed_to_one": True,
        "existence_check_execution_preflight_declared": True,
        "existence_check_execution_preflight_would_open_gate": False,
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
        "q18s_validation_invoked_by_mount": False,
        "q18r_validation_invoked_by_mount": False,
        "component_packet_builder_invoked_by_mount": False,
        "streamlit_render_invoked": False,
        "real_prediction_widget_rendering_allowed": False,
        "refresh_invocation_allowed": False,
        "runtime_artifact_write_allowed": False,
    }


def build_latest_prediction_summary_widget_one_source_no_read_existence_check_execution_preflight_rows(*, supplied_execution_gate_report: Mapping[str, Any] | Any | None = None) -> list[dict[str, Any]]:
    report = _as_mapping(supplied_execution_gate_report)
    return [
        _row("execution_preflight_source_candidate_count", "1", "Exactly one candidate is held behind this no-read execution preflight."),
        _row("execution_preflight_widget_family_id", WIDGET_FAMILY_ID, "Execution preflight is scoped to latest_prediction_summary_widget only."),
        _row("execution_preflight_source_packet_id", SOURCE_PACKET_ID, "Execution preflight is scoped to latest_prediction_source_review_packet only."),
        _row("execution_preflight_candidate_generated_at", report.get("selected_candidate_generated_at"), "Candidate generated_at copied from supplied PS-Q18S report only."),
        _row("execution_preflight_candidate_source_artifact_ref", report.get("selected_candidate_source_artifact_ref"), "Candidate source artifact ref copied from supplied PS-Q18S report only; not resolved."),
        _row("execution_preflight_candidate_market_uid", report.get("selected_candidate_market_uid"), "Candidate market uid copied from supplied PS-Q18S report only."),
        _row("path_shape_preview", report.get("path_shape_preview"), "Path-shape preview is still text only; no filesystem path object is created."),
        _row("source_gate_kind", report.get("existence_execution_gate_kind") or EXISTENCE_EXECUTION_GATE_KIND, "Source gate kind is carried forward from PS-Q18S."),
        _row("source_gate_state", report.get("existence_execution_gate_state") or EXISTENCE_EXECUTION_GATE_STATE, "Source gate state remains closed_not_executed."),
        _row("execution_preflight_kind", EXISTENCE_EXECUTION_PREFLIGHT_KIND, "Execution preflight is declared as closed; it does not open the gate."),
        _row("execution_preflight_state", EXISTENCE_EXECUTION_PREFLIGHT_STATE, "Execution preflight is declared but not executed."),
        _row("execution_preflight_decision", "do_not_open_gate_or_execute_in_this_slice", "This slice prepares the preflight contract only."),
        _row("explicit_execution_preflight_ack", ONE_SOURCE_NO_READ_EXISTENCE_CHECK_EXECUTION_PREFLIGHT_ACK, "Acknowledgement is not approval for filesystem checks, schema checks, or reads."),
        _row("deferred_runtime_boundary", "preflight_would_open_gate=false; exists_check=false; schema_check=false; actual_read=false", "All runtime behavior remains deferred."),
    ]


def build_latest_prediction_summary_widget_one_source_no_read_existence_check_execution_preflight_packet(*, supplied_execution_gate_report: Mapping[str, Any] | Any | None = None) -> dict[str, Any]:
    report = _as_mapping(supplied_execution_gate_report)
    rows = build_latest_prediction_summary_widget_one_source_no_read_existence_check_execution_preflight_rows(supplied_execution_gate_report=report)
    failures: list[str] = []
    if len(rows) != 14:
        failures.append("execution_preflight_row_count_mismatch")
    for row in rows:
        item = str(row.get("execution_preflight_item") or "")
        if item not in EXISTENCE_EXECUTION_PREFLIGHT_ITEMS:
            failures.append(f"unexpected_execution_preflight_item:{item}")
        for key in ("read_only", "non_executing", "one_source_no_read_existence_check_execution_preflight_only", "source_candidate_count_fixed_to_one", "existence_check_execution_preflight_declared", "path_shape_preview_string_only"):
            if row.get(key) is not True:
                failures.append(f"row_true_boundary_missing:{item}:{key}")
        for key in (
            "existence_check_execution_preflight_would_open_gate",
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
            "q18s_validation_invoked_by_mount",
            "q18r_validation_invoked_by_mount",
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
        "no_read_existence_check_execution_preflight_version": LATEST_PREDICTION_SUMMARY_WIDGET_ONE_SOURCE_NO_READ_EXISTENCE_CHECK_EXECUTION_PREFLIGHT_VERSION,
        "source_no_read_existence_check_execution_gate_version": LATEST_PREDICTION_SUMMARY_WIDGET_ONE_SOURCE_NO_READ_EXISTENCE_CHECK_EXECUTION_GATE_VERSION,
        "source_no_read_existence_check_execution_gate_ack": ONE_SOURCE_NO_READ_EXISTENCE_CHECK_EXECUTION_GATE_ACK,
        "widget_family_id": WIDGET_FAMILY_ID,
        "source_packet_id": SOURCE_PACKET_ID,
        "one_source_no_read_existence_check_execution_preflight_ack": ONE_SOURCE_NO_READ_EXISTENCE_CHECK_EXECUTION_PREFLIGHT_ACK,
        "execution_preflight_state": "latest_prediction_summary_widget_one_source_no_read_existence_check_execution_preflight_declared_no_exists_schema_read_or_render",
        "execution_preflight_row_count": len(rows),
        "execution_preflight_rows": rows,
        "validation_failures": failures,
        "supplied_execution_gate_report": supplied,
        "execution_preflight_candidate_ready": candidate_ready,
        "one_source_candidate_preserved": True,
        "source_candidate_count": 1,
        "path_shape_preview": _clean(report.get("path_shape_preview")) if report else "",
        "path_shape_preview_string_only": True,
        "source_gate_kind": str(report.get("existence_execution_gate_kind") or EXISTENCE_EXECUTION_GATE_KIND),
        "source_gate_state": str(report.get("existence_execution_gate_state") or EXISTENCE_EXECUTION_GATE_STATE),
        "existence_execution_preflight_kind": EXISTENCE_EXECUTION_PREFLIGHT_KIND,
        "existence_execution_preflight_state": EXISTENCE_EXECUTION_PREFLIGHT_STATE,
        "selected_candidate_generated_at": _clean(report.get("selected_candidate_generated_at")) if report else "",
        "selected_candidate_source_artifact_ref": _clean(report.get("selected_candidate_source_artifact_ref")) if report else "",
        "selected_candidate_market_uid": _clean(report.get("selected_candidate_market_uid")) if report else "",
        "read_only": True,
        "non_executing": True,
        "latest_prediction_summary_widget_one_source_no_read_existence_check_execution_preflight_only": True,
        "one_source_no_read_existence_check_execution_preflight_ready": True,
        "existence_check_execution_preflight_declared": True,
        "existence_check_execution_preflight_would_open_gate": False,
        "source_candidate_count_fixed_to_one": True,
        "explicit_execution_preflight_ack_matched": True,
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
