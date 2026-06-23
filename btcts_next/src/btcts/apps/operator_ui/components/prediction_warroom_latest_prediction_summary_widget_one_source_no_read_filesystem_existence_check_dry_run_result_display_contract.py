# path: ./btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_latest_prediction_summary_widget_one_source_no_read_filesystem_existence_check_dry_run_result_display_contract.py
# desc: PS-Q18Y pure-data no-read filesystem existence-check dry-run result display contract for latest_prediction_summary_widget one-source candidate. Contract only: no existence result, no filesystem check, no schema check, no actual read, no D-hot discovery, no render, no refresh, no writes.

from __future__ import annotations

from typing import Any, Mapping

from btcts.apps.operator_ui.components.prediction_widgets.latest_prediction_summary_widget import SOURCE_PACKET_ID, WIDGET_FAMILY_ID
from btcts.apps.operator_ui.components.prediction_warroom_latest_prediction_summary_widget_one_source_no_read_filesystem_existence_check_dry_run_result_placeholder import FILESYSTEM_EXISTENCE_CHECK_DRY_RUN_RESULT_PLACEHOLDER_KIND, FILESYSTEM_EXISTENCE_CHECK_DRY_RUN_RESULT_PLACEHOLDER_STATE, LATEST_PREDICTION_SUMMARY_WIDGET_ONE_SOURCE_NO_READ_FILESYSTEM_EXISTENCE_CHECK_DRY_RUN_RESULT_PLACEHOLDER_VERSION, ONE_SOURCE_NO_READ_FILESYSTEM_EXISTENCE_CHECK_DRY_RUN_RESULT_PLACEHOLDER_ACK

LATEST_PREDICTION_SUMMARY_WIDGET_ONE_SOURCE_NO_READ_FILESYSTEM_EXISTENCE_CHECK_DRY_RUN_RESULT_DISPLAY_CONTRACT_VERSION = "prediction_warroom_latest_prediction_summary_widget_one_source_no_read_filesystem_existence_check_dry_run_result_display_contract.ps_q18y.v1"
ONE_SOURCE_NO_READ_FILESYSTEM_EXISTENCE_CHECK_DRY_RUN_RESULT_DISPLAY_CONTRACT_ACK = "PS_Q18Y_DECLARE_ONE_SOURCE_NO_READ_FILESYSTEM_EXISTENCE_CHECK_DRY_RUN_RESULT_DISPLAY_CONTRACT_ONLY"
FILESYSTEM_EXISTENCE_CHECK_DRY_RUN_RESULT_DISPLAY_CONTRACT_KIND = "no_read_filesystem_existence_check_dry_run_result_display_contract"
FILESYSTEM_EXISTENCE_CHECK_DRY_RUN_RESULT_DISPLAY_CONTRACT_STATE = "display_contract_declared_no_result_no_render"
FILESYSTEM_EXISTENCE_CHECK_DRY_RUN_RESULT_DISPLAY_CONTRACT_ITEMS = (
    "dry_run_result_display_contract_source_candidate_count",
    "dry_run_result_display_contract_widget_family_id",
    "dry_run_result_display_contract_source_packet_id",
    "dry_run_result_display_contract_candidate_generated_at",
    "dry_run_result_display_contract_candidate_source_artifact_ref",
    "dry_run_result_display_contract_candidate_market_uid",
    "path_shape_preview",
    "source_result_placeholder_kind",
    "source_result_placeholder_state",
    "dry_run_result_display_contract_kind",
    "dry_run_result_display_contract_state",
    "dry_run_result_display_contract_decision",
    "explicit_dry_run_result_display_contract_ack",
    "deferred_runtime_boundary",
)
TRUE_BOUNDARIES = (
    "read_only",
    "non_executing",
    "one_source_no_read_filesystem_existence_check_dry_run_result_display_contract_only",
    "source_candidate_count_fixed_to_one",
    "filesystem_existence_check_dry_run_result_display_contract_declared",
    "filesystem_existence_check_dry_run_result_placeholder_preserved",
    "path_shape_preview_string_only",
)
FALSE_BOUNDARIES = (
    "filesystem_existence_check_dry_run_result_available",
    "filesystem_existence_check_dry_run_result_display_mount_allowed",
    "filesystem_existence_check_dry_run_result_display_mounted",
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
    "q18x_validation_invoked_by_mount",
    "q18w_validation_invoked_by_mount",
    "component_packet_builder_invoked_by_mount",
    "streamlit_render_allowed",
    "streamlit_render_invoked",
    "real_prediction_widget_rendering_allowed",
    "refresh_invocation_allowed",
    "runtime_artifact_write_allowed",
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
    row = {
        "dry_run_result_display_contract_item": item,
        "value": text,
        "state": "declared" if text else "not_supplied",
        "operator_note": note,
    }
    row.update({key: True for key in TRUE_BOUNDARIES})
    row.update({key: False for key in FALSE_BOUNDARIES})
    return row


def build_latest_prediction_summary_widget_one_source_no_read_filesystem_existence_check_dry_run_result_display_contract_rows(*, supplied_result_placeholder_report: Mapping[str, Any] | Any | None = None) -> list[dict[str, Any]]:
    report = _as_mapping(supplied_result_placeholder_report)
    return [
        _row("dry_run_result_display_contract_source_candidate_count", "1", "Exactly one candidate is named in this result display contract."),
        _row("dry_run_result_display_contract_widget_family_id", WIDGET_FAMILY_ID, "Display contract is scoped to latest_prediction_summary_widget only."),
        _row("dry_run_result_display_contract_source_packet_id", SOURCE_PACKET_ID, "Display contract is scoped to latest_prediction_source_review_packet only."),
        _row("dry_run_result_display_contract_candidate_generated_at", report.get("selected_candidate_generated_at"), "Candidate generated_at copied from supplied PS-Q18X report only."),
        _row("dry_run_result_display_contract_candidate_source_artifact_ref", report.get("selected_candidate_source_artifact_ref"), "Candidate source artifact ref copied from supplied PS-Q18X report only; not resolved."),
        _row("dry_run_result_display_contract_candidate_market_uid", report.get("selected_candidate_market_uid"), "Candidate market uid copied from supplied PS-Q18X report only."),
        _row("path_shape_preview", report.get("path_shape_preview"), "Path-shape preview is text only; no filesystem path object is created."),
        _row("source_result_placeholder_kind", report.get("filesystem_existence_check_dry_run_result_placeholder_kind") or FILESYSTEM_EXISTENCE_CHECK_DRY_RUN_RESULT_PLACEHOLDER_KIND, "Source result placeholder kind is carried forward from PS-Q18X."),
        _row("source_result_placeholder_state", report.get("filesystem_existence_check_dry_run_result_placeholder_state") or FILESYSTEM_EXISTENCE_CHECK_DRY_RUN_RESULT_PLACEHOLDER_STATE, "Source result placeholder state remains no result."),
        _row("dry_run_result_display_contract_kind", FILESYSTEM_EXISTENCE_CHECK_DRY_RUN_RESULT_DISPLAY_CONTRACT_KIND, "A no-read result display contract is declared."),
        _row("dry_run_result_display_contract_state", FILESYSTEM_EXISTENCE_CHECK_DRY_RUN_RESULT_DISPLAY_CONTRACT_STATE, "Display contract is declared but not mounted or rendered."),
        _row("dry_run_result_display_contract_decision", "display_contract_only_no_mount_no_render", "This slice names the future display boundary but performs no UI mount or render."),
        _row("explicit_dry_run_result_display_contract_ack", ONE_SOURCE_NO_READ_FILESYSTEM_EXISTENCE_CHECK_DRY_RUN_RESULT_DISPLAY_CONTRACT_ACK, "Acknowledgement is not approval for rendering, filesystem checks, schema checks, or reads."),
        _row("deferred_runtime_boundary", "display_mount_allowed=false; result_available=false; dry_run_execution_allowed=false; exists_check=false; schema_check=false; actual_read=false", "All runtime behavior remains deferred."),
    ]


def build_latest_prediction_summary_widget_one_source_no_read_filesystem_existence_check_dry_run_result_display_contract_packet(*, supplied_result_placeholder_report: Mapping[str, Any] | Any | None = None) -> dict[str, Any]:
    report = _as_mapping(supplied_result_placeholder_report)
    rows = build_latest_prediction_summary_widget_one_source_no_read_filesystem_existence_check_dry_run_result_display_contract_rows(supplied_result_placeholder_report=report)
    failures: list[str] = []
    if len(rows) != 14:
        failures.append("dry_run_result_display_contract_row_count_mismatch")
    for row in rows:
        item = str(row.get("dry_run_result_display_contract_item") or "")
        if item not in FILESYSTEM_EXISTENCE_CHECK_DRY_RUN_RESULT_DISPLAY_CONTRACT_ITEMS:
            failures.append(f"unexpected_dry_run_result_display_contract_item:{item}")
        for key in TRUE_BOUNDARIES:
            if row.get(key) is not True:
                failures.append(f"row_true_boundary_missing:{item}:{key}")
        for key in FALSE_BOUNDARIES:
            if row.get(key) is not False:
                failures.append(f"row_false_boundary_not_false:{item}:{key}")
    supplied = bool(report)
    candidate_ready = supplied and all(_clean(report.get(key)) for key in ("selected_candidate_generated_at", "selected_candidate_source_artifact_ref", "selected_candidate_market_uid", "path_shape_preview"))
    packet = {
        "ok": not failures,
        "no_read_filesystem_existence_check_dry_run_result_display_contract_version": LATEST_PREDICTION_SUMMARY_WIDGET_ONE_SOURCE_NO_READ_FILESYSTEM_EXISTENCE_CHECK_DRY_RUN_RESULT_DISPLAY_CONTRACT_VERSION,
        "source_no_read_filesystem_existence_check_dry_run_result_placeholder_version": LATEST_PREDICTION_SUMMARY_WIDGET_ONE_SOURCE_NO_READ_FILESYSTEM_EXISTENCE_CHECK_DRY_RUN_RESULT_PLACEHOLDER_VERSION,
        "source_no_read_filesystem_existence_check_dry_run_result_placeholder_ack": ONE_SOURCE_NO_READ_FILESYSTEM_EXISTENCE_CHECK_DRY_RUN_RESULT_PLACEHOLDER_ACK,
        "widget_family_id": WIDGET_FAMILY_ID,
        "source_packet_id": SOURCE_PACKET_ID,
        "one_source_no_read_filesystem_existence_check_dry_run_result_display_contract_ack": ONE_SOURCE_NO_READ_FILESYSTEM_EXISTENCE_CHECK_DRY_RUN_RESULT_DISPLAY_CONTRACT_ACK,
        "dry_run_result_display_contract_state": "latest_prediction_summary_widget_one_source_no_read_filesystem_existence_check_dry_run_result_display_contract_no_result_no_mount_no_render",
        "dry_run_result_display_contract_row_count": len(rows),
        "dry_run_result_display_contract_rows": rows,
        "validation_failures": failures,
        "supplied_result_placeholder_report": supplied,
        "dry_run_result_display_contract_candidate_ready": candidate_ready,
        "one_source_candidate_preserved": True,
        "source_candidate_count": 1,
        "path_shape_preview": _clean(report.get("path_shape_preview")) if report else "",
        "source_result_placeholder_kind": str(report.get("filesystem_existence_check_dry_run_result_placeholder_kind") or FILESYSTEM_EXISTENCE_CHECK_DRY_RUN_RESULT_PLACEHOLDER_KIND),
        "source_result_placeholder_state": str(report.get("filesystem_existence_check_dry_run_result_placeholder_state") or FILESYSTEM_EXISTENCE_CHECK_DRY_RUN_RESULT_PLACEHOLDER_STATE),
        "filesystem_existence_check_dry_run_result_display_contract_kind": FILESYSTEM_EXISTENCE_CHECK_DRY_RUN_RESULT_DISPLAY_CONTRACT_KIND,
        "filesystem_existence_check_dry_run_result_display_contract_state": FILESYSTEM_EXISTENCE_CHECK_DRY_RUN_RESULT_DISPLAY_CONTRACT_STATE,
        "selected_candidate_generated_at": _clean(report.get("selected_candidate_generated_at")) if report else "",
        "selected_candidate_source_artifact_ref": _clean(report.get("selected_candidate_source_artifact_ref")) if report else "",
        "selected_candidate_market_uid": _clean(report.get("selected_candidate_market_uid")) if report else "",
        "latest_prediction_summary_widget_one_source_no_read_filesystem_existence_check_dry_run_result_display_contract_only": True,
        "one_source_no_read_filesystem_existence_check_dry_run_result_display_contract_ready": True,
        "explicit_dry_run_result_display_contract_ack_matched": True,
        "warroom_page_mutation_allowed": False,
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
        "component_packet_builder_allowed_by_mount": False,
        "component_runtime_binding_allowed": False,
        "warroom_widget_rendering_allowed": False,
        "warroom_ui_trigger_enabled": False,
        "scheduler_enabled": False,
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
    packet.update({key: True for key in TRUE_BOUNDARIES})
    packet.update({key: False for key in FALSE_BOUNDARIES})
    return packet
