# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/sources/latest_prediction_summary_widget_q18ac_filesystem_exists_check.py
# desc: PS-Q18AC bounded filesystem existence check for latest_prediction_summary_widget candidate path. Existence metadata only; no read, schema validation, refresh, writes, AutoTrade, or broker behavior.

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

from btcts.apps.operator_ui.prediction_warroom.panels.latest_prediction_summary_widget_q18ab_safe_display_mount_panel import (
    build_latest_prediction_summary_widget_q18ab_safe_display_mount_panel_packet,
)

LATEST_PREDICTION_SUMMARY_WIDGET_Q18AC_FILESYSTEM_EXISTS_CHECK_VERSION = "prediction_warroom.latest_prediction_summary_widget.q18ac_filesystem_exists_check.v1"
LATEST_PREDICTION_SUMMARY_WIDGET_Q18AC_FILESYSTEM_EXISTS_CHECK_ACK = "PS_Q18AC_EXECUTE_BOUNDED_FILESYSTEM_EXISTS_CHECK_ONLY"
LATEST_PREDICTION_SUMMARY_WIDGET_Q18AC_FILESYSTEM_EXISTS_CHECK_KIND = "bounded_filesystem_exists_check_for_one_source_path_preview"
LATEST_PREDICTION_SUMMARY_WIDGET_Q18AC_FILESYSTEM_EXISTS_CHECK_STATE = "filesystem_exists_check_executed_result_available_no_schema_no_read"

TRUE_BOUNDARIES = (
    "read_only",
    "non_executing",
    "display_only",
    "filesystem_exists_check_only",
    "q18ab_safe_display_mount_consumed",
    "q18ac_filesystem_exists_check_declared",
    "filesystem_exists_check_execution_allowed",
    "filesystem_exists_check_executed",
    "source_artifact_exists_check_allowed",
    "source_artifact_exists_checked",
    "source_artifact_exists_result_available",
    "path_shape_preview_string_only",
    "source_candidate_count_fixed_to_one",
)

FALSE_BOUNDARIES = (
    "source_artifact_schema_check_allowed",
    "source_artifact_schema_checked",
    "actual_source_read_allowed",
    "actual_source_read_invoked",
    "payload_reparse_allowed",
    "real_prediction_widget_rendering_allowed",
    "render_latest_prediction_summary_widget_invoked",
    "component_runtime_binding_allowed",
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


def build_latest_prediction_summary_widget_q18ac_filesystem_exists_check_packet(
    *,
    supplied_q18ab_safe_display_mount_packet: Mapping[str, Any] | Any | None = None,
    execute_filesystem_exists_check: bool = False,
    explicit_ack: str = "",
) -> dict[str, Any]:
    source = _as_mapping(supplied_q18ab_safe_display_mount_packet)
    if not source:
        source = build_latest_prediction_summary_widget_q18ab_safe_display_mount_panel_packet()
    path_preview = _clean(source.get("path_shape_preview"))
    failures: list[str] = []
    warning_reasons: list[str] = []
    exception_class = ""
    exception_message = ""
    exists_result: bool | None = None
    exists_checked = False
    execution_allowed = bool(execute_filesystem_exists_check and explicit_ack == LATEST_PREDICTION_SUMMARY_WIDGET_Q18AC_FILESYSTEM_EXISTS_CHECK_ACK)

    if source.get("ok") is not True:
        failures.append("q18ab_safe_display_mount_not_ok")
    if source.get("warroom_display_mounted") is not True:
        failures.append("q18ab_safe_display_mount_not_mounted")
    if source.get("safe_display_mount_panel_row_count") != 12:
        failures.append("q18ab_safe_display_mount_panel_row_count_mismatch")
    if not path_preview:
        failures.append("path_shape_preview_missing")
    if not execute_filesystem_exists_check:
        failures.append("execute_filesystem_exists_check_false")
    if explicit_ack != LATEST_PREDICTION_SUMMARY_WIDGET_Q18AC_FILESYSTEM_EXISTS_CHECK_ACK:
        failures.append("explicit_ack_missing_or_mismatch")

    if execution_allowed and path_preview and not any(item.startswith("q18ab_") for item in failures):
        try:
            exists_result = bool(Path(path_preview).exists())
            exists_checked = True
            if exists_result is False:
                warning_reasons.append("source_artifact_path_does_not_exist_at_check_time")
        except Exception as exc:  # noqa: BLE001 - bounded diagnostic only
            exists_checked = True
            exists_result = False
            exception_class = exc.__class__.__name__
            exception_message = str(exc)[:240]
            warning_reasons.append("filesystem_exists_check_exception")

    result_available = exists_checked and exists_result is not None
    ok = bool(execution_allowed and exists_checked and result_available and not [item for item in failures if item.startswith("q18ab_") or item == "path_shape_preview_missing"])
    packet: dict[str, Any] = {
        "ok": ok,
        "filesystem_exists_check_version": LATEST_PREDICTION_SUMMARY_WIDGET_Q18AC_FILESYSTEM_EXISTS_CHECK_VERSION,
        "filesystem_exists_check_ack": LATEST_PREDICTION_SUMMARY_WIDGET_Q18AC_FILESYSTEM_EXISTS_CHECK_ACK,
        "filesystem_exists_check_kind": LATEST_PREDICTION_SUMMARY_WIDGET_Q18AC_FILESYSTEM_EXISTS_CHECK_KIND,
        "filesystem_exists_check_state": LATEST_PREDICTION_SUMMARY_WIDGET_Q18AC_FILESYSTEM_EXISTS_CHECK_STATE if result_available else "filesystem_exists_check_not_executed_or_no_result",
        "source_q18ab_safe_display_mount_ready": source.get("ok") is True,
        "q18ab_safe_display_mount_row_count": int(source.get("safe_display_mount_panel_row_count") or 0),
        "display_packet_row_count": int(source.get("display_packet_row_count") or 0),
        "source_candidate_count": int(source.get("source_candidate_count") or 0),
        "selected_candidate_generated_at": _clean(source.get("selected_candidate_generated_at")),
        "selected_candidate_source_artifact_ref": _clean(source.get("selected_candidate_source_artifact_ref")),
        "selected_candidate_market_uid": _clean(source.get("selected_candidate_market_uid")),
        "path_shape_preview": path_preview,
        "explicit_ack_matched": explicit_ack == LATEST_PREDICTION_SUMMARY_WIDGET_Q18AC_FILESYSTEM_EXISTS_CHECK_ACK,
        "filesystem_exists_check_executed": exists_checked,
        "source_artifact_exists_checked": exists_checked,
        "source_artifact_exists_result_available": result_available,
        "source_artifact_exists_result": bool(exists_result) if exists_result is not None else None,
        "source_artifact_exists_result_state": "exists" if exists_result is True else "missing" if exists_result is False and result_available else "not_checked",
        "validation_failures": failures,
        "warning_reasons": warning_reasons,
        "exception_class": exception_class,
        "exception_message": exception_message,
        "recommended_next_slice": "schema validation; keep actual D-hot source read, real widget rendering, refresh, AutoTrade, broker, and parameter apply deferred unless explicitly approved.",
        "human_interpretation": "PS-Q18AC executes only a bounded filesystem existence check against one explicit path preview. It does not read the file, validate schema, reparse payload, render the real widget, refresh, write artifacts, stage/apply parameters, trigger AutoTrade, or call broker APIs.",
    }
    packet.update({key: True for key in TRUE_BOUNDARIES})
    packet.update({key: False for key in FALSE_BOUNDARIES})
    packet["filesystem_exists_check_execution_allowed"] = execution_allowed
    packet["filesystem_exists_check_executed"] = exists_checked
    packet["source_artifact_exists_check_allowed"] = execution_allowed
    packet["source_artifact_exists_checked"] = exists_checked
    packet["source_artifact_exists_result_available"] = result_available
    return packet
