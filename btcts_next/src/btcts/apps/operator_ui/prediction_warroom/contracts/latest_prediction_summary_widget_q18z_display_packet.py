# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/contracts/latest_prediction_summary_widget_q18z_display_packet.py
# desc: PS-Q18Z pure-data display-packet contract for latest_prediction_summary_widget one-source no-read filesystem existence-check dry-run result. No mount, render, exists check, schema check, actual read, refresh, writes, AutoTrade, or broker behavior.

from __future__ import annotations

from typing import Any, Mapping

from btcts.apps.operator_ui.components.prediction_widgets.latest_prediction_summary_widget import SOURCE_PACKET_ID, WIDGET_FAMILY_ID
from btcts.apps.operator_ui.components.prediction_warroom_latest_prediction_summary_widget_one_source_no_read_filesystem_existence_check_dry_run_result_display_contract import (
    FILESYSTEM_EXISTENCE_CHECK_DRY_RUN_RESULT_DISPLAY_CONTRACT_KIND,
    FILESYSTEM_EXISTENCE_CHECK_DRY_RUN_RESULT_DISPLAY_CONTRACT_STATE,
    LATEST_PREDICTION_SUMMARY_WIDGET_ONE_SOURCE_NO_READ_FILESYSTEM_EXISTENCE_CHECK_DRY_RUN_RESULT_DISPLAY_CONTRACT_VERSION,
    ONE_SOURCE_NO_READ_FILESYSTEM_EXISTENCE_CHECK_DRY_RUN_RESULT_DISPLAY_CONTRACT_ACK,
)

LATEST_PREDICTION_SUMMARY_WIDGET_Q18Z_DISPLAY_PACKET_VERSION = "prediction_warroom.latest_prediction_summary_widget.q18z_display_packet.v1"
LATEST_PREDICTION_SUMMARY_WIDGET_Q18Z_DISPLAY_PACKET_ACK = "PS_Q18Z_DECLARE_ONE_SOURCE_NO_READ_FILESYSTEM_EXISTENCE_CHECK_DRY_RUN_RESULT_DISPLAY_PACKET_ONLY"
LATEST_PREDICTION_SUMMARY_WIDGET_Q18Z_DISPLAY_PACKET_KIND = "one_source_no_read_filesystem_existence_check_dry_run_result_display_packet"
LATEST_PREDICTION_SUMMARY_WIDGET_Q18Z_DISPLAY_PACKET_STATE = "display_packet_declared_no_mount_no_render_no_exists_result"

TRUE_BOUNDARIES = (
    "read_only",
    "non_executing",
    "display_only",
    "one_source_no_read_filesystem_existence_check_dry_run_result_display_packet_only",
    "q18y_display_contract_consumed",
    "q18z_display_packet_declared",
    "source_candidate_count_fixed_to_one",
    "path_shape_preview_string_only",
)

FALSE_BOUNDARIES = (
    "warroom_page_mutation_allowed",
    "warroom_display_mount_allowed",
    "warroom_display_mounted",
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
    "streamlit_render_allowed",
    "streamlit_render_invoked",
    "real_prediction_widget_rendering_allowed",
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


def _as_mapping(value: Any) -> Mapping[str, Any]:
    if hasattr(value, "to_dict"):
        converted = value.to_dict()
        return converted if isinstance(converted, Mapping) else {}
    return value if isinstance(value, Mapping) else {}


def _clean(value: Any) -> str:
    return "" if value is None else str(value)


def _source_contract_ready(report: Mapping[str, Any]) -> tuple[bool, list[str]]:
    failures: list[str] = []
    if not report:
        failures.append("missing_q18y_display_contract_report")
        return False, failures
    if report.get("ok") is not True:
        failures.append("q18y_report_not_ok")
    if report.get("one_source_no_read_filesystem_existence_check_dry_run_result_display_contract_ack") != ONE_SOURCE_NO_READ_FILESYSTEM_EXISTENCE_CHECK_DRY_RUN_RESULT_DISPLAY_CONTRACT_ACK:
        failures.append("q18y_ack_mismatch")
    if report.get("dry_run_result_display_contract_row_count") != 14:
        failures.append("q18y_row_count_mismatch")
    if report.get("source_candidate_count") != 1:
        failures.append("source_candidate_count_not_one")
    if report.get("dry_run_result_display_contract_candidate_ready") is not True:
        failures.append("q18y_candidate_not_ready")
    if not _clean(report.get("path_shape_preview")):
        failures.append("path_shape_preview_missing")
    for key in (
        "read_only",
        "non_executing",
        "filesystem_existence_check_dry_run_result_display_contract_declared",
        "filesystem_existence_check_dry_run_result_placeholder_preserved",
        "path_shape_preview_string_only",
    ):
        if report.get(key) is not True:
            failures.append(f"q18y_true_boundary_missing:{key}")
    for key in (
        "filesystem_existence_check_dry_run_result_available",
        "filesystem_existence_check_dry_run_result_display_mount_allowed",
        "source_artifact_exists_checked",
        "source_artifact_schema_checked",
        "actual_source_read_invoked",
        "streamlit_render_invoked",
        "real_prediction_widget_rendering_allowed",
        "runtime_artifact_write_allowed",
        "broker_private_api_allowed",
    ):
        if report.get(key) is not False:
            failures.append(f"q18y_false_boundary_not_false:{key}")
    return not failures, failures


def build_latest_prediction_summary_widget_q18z_display_packet_contract(*, supplied_q18y_display_contract_report: Mapping[str, Any] | Any | None = None) -> dict[str, Any]:
    """Build the PS-Q18Z display-packet contract without filesystem or UI side effects."""
    report = _as_mapping(supplied_q18y_display_contract_report)
    source_ready, source_failures = _source_contract_ready(report)
    packet = {
        "ok": source_ready,
        "display_packet_version": LATEST_PREDICTION_SUMMARY_WIDGET_Q18Z_DISPLAY_PACKET_VERSION,
        "display_packet_ack": LATEST_PREDICTION_SUMMARY_WIDGET_Q18Z_DISPLAY_PACKET_ACK,
        "display_packet_kind": LATEST_PREDICTION_SUMMARY_WIDGET_Q18Z_DISPLAY_PACKET_KIND,
        "display_packet_state": LATEST_PREDICTION_SUMMARY_WIDGET_Q18Z_DISPLAY_PACKET_STATE,
        "source_display_contract_version": LATEST_PREDICTION_SUMMARY_WIDGET_ONE_SOURCE_NO_READ_FILESYSTEM_EXISTENCE_CHECK_DRY_RUN_RESULT_DISPLAY_CONTRACT_VERSION,
        "source_display_contract_kind": FILESYSTEM_EXISTENCE_CHECK_DRY_RUN_RESULT_DISPLAY_CONTRACT_KIND,
        "source_display_contract_state": FILESYSTEM_EXISTENCE_CHECK_DRY_RUN_RESULT_DISPLAY_CONTRACT_STATE,
        "source_display_contract_ready": source_ready,
        "source_display_contract_failures": source_failures,
        "widget_family_id": WIDGET_FAMILY_ID,
        "source_packet_id": SOURCE_PACKET_ID,
        "source_candidate_count": 1,
        "selected_candidate_generated_at": _clean(report.get("selected_candidate_generated_at")),
        "selected_candidate_source_artifact_ref": _clean(report.get("selected_candidate_source_artifact_ref")),
        "selected_candidate_market_uid": _clean(report.get("selected_candidate_market_uid")),
        "path_shape_preview": _clean(report.get("path_shape_preview")),
        "display_packet_decision": "declare_display_packet_only_no_mount_no_render_no_exists_check_no_schema_no_read",
        "recommended_next_slice": "WarRoom mount preflight/gate; still no render/read unless explicitly approved.",
    }
    packet.update({key: True for key in TRUE_BOUNDARIES})
    packet.update({key: False for key in FALSE_BOUNDARIES})
    return packet
