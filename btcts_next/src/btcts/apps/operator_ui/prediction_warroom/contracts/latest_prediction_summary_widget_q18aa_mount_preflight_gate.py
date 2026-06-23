# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/contracts/latest_prediction_summary_widget_q18aa_mount_preflight_gate.py
# desc: PS-Q18AA pure-data WarRoom mount preflight gate for latest_prediction_summary_widget display packet. No page mutation, mount, render, exists check, schema check, actual read, refresh, writes, AutoTrade, or broker behavior.

from __future__ import annotations

from typing import Any, Mapping

from btcts.apps.operator_ui.prediction_warroom.contracts.latest_prediction_summary_widget_q18z_display_packet import (
    LATEST_PREDICTION_SUMMARY_WIDGET_Q18Z_DISPLAY_PACKET_ACK,
    LATEST_PREDICTION_SUMMARY_WIDGET_Q18Z_DISPLAY_PACKET_KIND,
    LATEST_PREDICTION_SUMMARY_WIDGET_Q18Z_DISPLAY_PACKET_STATE,
    LATEST_PREDICTION_SUMMARY_WIDGET_Q18Z_DISPLAY_PACKET_VERSION,
)

LATEST_PREDICTION_SUMMARY_WIDGET_Q18AA_MOUNT_PREFLIGHT_GATE_VERSION = "prediction_warroom.latest_prediction_summary_widget.q18aa_mount_preflight_gate.v1"
LATEST_PREDICTION_SUMMARY_WIDGET_Q18AA_MOUNT_PREFLIGHT_GATE_ACK = "PS_Q18AA_DECLARE_WARROOM_MOUNT_PREFLIGHT_GATE_ONLY"
LATEST_PREDICTION_SUMMARY_WIDGET_Q18AA_MOUNT_PREFLIGHT_GATE_KIND = "warroom_mount_preflight_gate_for_one_source_no_read_display_packet"
LATEST_PREDICTION_SUMMARY_WIDGET_Q18AA_MOUNT_PREFLIGHT_GATE_STATE = "preflight_gate_ready_mount_not_enabled_no_render_no_read"

TRUE_BOUNDARIES = (
    "read_only",
    "non_executing",
    "display_only",
    "preflight_only",
    "q18z_display_packet_consumed",
    "q18aa_mount_preflight_gate_declared",
    "source_candidate_count_fixed_to_one",
    "path_shape_preview_string_only",
    "safe_display_mount_candidate_declared",
)

FALSE_BOUNDARIES = (
    "warroom_page_mutation_allowed",
    "warroom_import_mutation_allowed",
    "warroom_body_call_allowed",
    "warroom_display_mount_allowed",
    "warroom_display_mounted",
    "streamlit_render_allowed",
    "streamlit_render_invoked",
    "real_prediction_widget_rendering_allowed",
    "component_runtime_binding_allowed",
    "filesystem_existence_check_dry_run_result_available",
    "filesystem_existence_check_dry_run_execution_allowed",
    "filesystem_existence_check_dry_run_executed",
    "source_artifact_exists_check_allowed",
    "source_artifact_exists_checked",
    "source_artifact_exists_result_available",
    "source_artifact_schema_check_allowed",
    "source_artifact_schema_checked",
    "actual_source_read_allowed",
    "actual_source_read_invoked",
    "payload_reparse_allowed",
    "refresh_invocation_allowed",
    "scheduler_enabled",
    "runtime_artifact_write_allowed",
    "status_artifact_write_allowed",
    "parameter_apply_allowed",
    "parameter_staging_write_allowed",
    "approval_or_authorization_allowed",
    "ledger_append_allowed",
    "autotrade_trigger_allowed",
    "broker_private_api_allowed",
    "would_write_runtime_artifact",
    "would_send_to_broker",
)

REQUIRED_Q18Z_TRUE = (
    "read_only",
    "non_executing",
    "display_only",
    "q18z_display_packet_declared",
    "q18y_display_contract_consumed",
    "source_candidate_count_fixed_to_one",
    "path_shape_preview_string_only",
)

REQUIRED_Q18Z_FALSE = (
    "warroom_page_mutation_allowed",
    "warroom_display_mount_allowed",
    "warroom_display_mounted",
    "source_artifact_exists_checked",
    "source_artifact_schema_checked",
    "actual_source_read_invoked",
    "streamlit_render_invoked",
    "real_prediction_widget_rendering_allowed",
    "refresh_invocation_allowed",
    "runtime_artifact_write_allowed",
    "autotrade_trigger_allowed",
    "broker_private_api_allowed",
)


def _as_mapping(value: Any) -> Mapping[str, Any]:
    if hasattr(value, "to_dict"):
        converted = value.to_dict()
        return converted if isinstance(converted, Mapping) else {}
    return value if isinstance(value, Mapping) else {}


def _clean(value: Any) -> str:
    return "" if value is None else str(value)


def _source_q18z_ready(report: Mapping[str, Any]) -> tuple[bool, list[str]]:
    failures: list[str] = []
    if not report:
        return False, ["missing_q18z_display_packet_report"]
    if report.get("ok") is not True:
        failures.append("q18z_report_not_ok")
    if report.get("display_packet_version") != LATEST_PREDICTION_SUMMARY_WIDGET_Q18Z_DISPLAY_PACKET_VERSION:
        failures.append("q18z_display_packet_version_mismatch")
    if report.get("display_packet_ack") != LATEST_PREDICTION_SUMMARY_WIDGET_Q18Z_DISPLAY_PACKET_ACK:
        failures.append("q18z_display_packet_ack_mismatch")
    if report.get("display_packet_kind") != LATEST_PREDICTION_SUMMARY_WIDGET_Q18Z_DISPLAY_PACKET_KIND:
        failures.append("q18z_display_packet_kind_mismatch")
    if report.get("display_packet_state") != LATEST_PREDICTION_SUMMARY_WIDGET_Q18Z_DISPLAY_PACKET_STATE:
        failures.append("q18z_display_packet_state_mismatch")
    if report.get("display_packet_row_count") != 12:
        failures.append("q18z_display_packet_row_count_mismatch")
    if report.get("source_candidate_count") != 1:
        failures.append("source_candidate_count_not_one")
    if not _clean(report.get("path_shape_preview")):
        failures.append("path_shape_preview_missing")
    for key in REQUIRED_Q18Z_TRUE:
        if report.get(key) is not True:
            failures.append(f"q18z_true_boundary_missing:{key}")
    for key in REQUIRED_Q18Z_FALSE:
        if report.get(key) is not False:
            failures.append(f"q18z_false_boundary_not_false:{key}")
    return not failures, failures


def build_latest_prediction_summary_widget_q18aa_mount_preflight_gate_contract(*, supplied_q18z_display_packet_report: Mapping[str, Any] | Any | None = None) -> dict[str, Any]:
    report = _as_mapping(supplied_q18z_display_packet_report)
    source_ready, source_failures = _source_q18z_ready(report)
    packet = {
        "ok": source_ready,
        "mount_preflight_gate_version": LATEST_PREDICTION_SUMMARY_WIDGET_Q18AA_MOUNT_PREFLIGHT_GATE_VERSION,
        "mount_preflight_gate_ack": LATEST_PREDICTION_SUMMARY_WIDGET_Q18AA_MOUNT_PREFLIGHT_GATE_ACK,
        "mount_preflight_gate_kind": LATEST_PREDICTION_SUMMARY_WIDGET_Q18AA_MOUNT_PREFLIGHT_GATE_KIND,
        "mount_preflight_gate_state": LATEST_PREDICTION_SUMMARY_WIDGET_Q18AA_MOUNT_PREFLIGHT_GATE_STATE,
        "source_display_packet_version": LATEST_PREDICTION_SUMMARY_WIDGET_Q18Z_DISPLAY_PACKET_VERSION,
        "source_display_packet_ready": source_ready,
        "source_display_packet_failures": source_failures,
        "source_candidate_count": 1,
        "display_packet_row_count": int(report.get("display_packet_row_count") or 0) if report else 0,
        "selected_candidate_generated_at": _clean(report.get("selected_candidate_generated_at")),
        "selected_candidate_source_artifact_ref": _clean(report.get("selected_candidate_source_artifact_ref")),
        "selected_candidate_market_uid": _clean(report.get("selected_candidate_market_uid")),
        "path_shape_preview": _clean(report.get("path_shape_preview")),
        "preflight_gate_decision": "declare_mount_preflight_gate_only_no_warroom_page_mutation_no_mount_no_render_no_read",
        "safe_display_mount_candidate": source_ready,
        "next_required_gate": "safe_warroom_display_mount_slice_requires_explicit_human_approval",
        "recommended_next_slice": "Safe WarRoom display mount; still no actual source read unless explicitly approved.",
    }
    packet.update({key: True for key in TRUE_BOUNDARIES})
    packet.update({key: False for key in FALSE_BOUNDARIES})
    return packet
