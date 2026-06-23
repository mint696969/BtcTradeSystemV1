# path: ./btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_latest_prediction_summary_widget_mapped_payload_value_rows_panel.py
# desc: PS-Q18L pure-data mapped payload value rows for latest_prediction_summary_widget. No Streamlit, no Q18J invocation, no component packet builder invocation, no source read, no D-hot discovery, no writes.

from __future__ import annotations

from typing import Any, Mapping

from btcts.apps.operator_ui.components.prediction_widgets.latest_prediction_summary_widget import SOURCE_PACKET_ID, WIDGET_FAMILY_ID
from btcts.apps.operator_ui.components.prediction_warroom_latest_prediction_summary_widget_mapped_payload_render_disabled_packet_validation import LATEST_PREDICTION_SUMMARY_WIDGET_MAPPED_PAYLOAD_RENDER_DISABLED_PACKET_VALIDATION_VERSION

LATEST_PREDICTION_SUMMARY_WIDGET_MAPPED_PAYLOAD_VALUE_ROWS_PANEL_VERSION = "prediction_warroom_latest_prediction_summary_widget_mapped_payload_value_rows_panel.ps_q18l.v1"
VALUE_ITEMS = (
    "mapped_prediction_run_id",
    "mapped_market_uid",
    "mapped_source_generated_at",
    "mapped_source_artifact_ref",
    "component_source_generated_at",
    "component_source_artifact_ref",
)


def _as_mapping(value: Any) -> Mapping[str, Any]:
    if hasattr(value, "to_dict"):
        converted = value.to_dict()
        return converted if isinstance(converted, Mapping) else {}
    return value if isinstance(value, Mapping) else {}


def _value_row(item: str, value: Any, source: str) -> dict[str, Any]:
    supplied = value not in (None, "")
    return {
        "value_item": item,
        "value": "" if value is None else str(value),
        "state": "observed" if supplied else "not_supplied",
        "source": source,
        "read_only": True,
        "non_executing": True,
        "q18j_validation_invoked_by_mount": False,
        "component_packet_builder_invoked_by_mount": False,
        "component_packet_builder_allowed_by_mount": False,
        "component_runtime_binding_allowed": False,
        "streamlit_render_allowed": False,
        "streamlit_render_invoked": False,
        "real_prediction_widget_rendering_allowed": False,
        "actual_source_read_invoked_by_mount": False,
        "d_hot_directory_scan_allowed": False,
        "refresh_invocation_allowed": False,
        "runtime_artifact_write_allowed": False,
    }


def build_latest_prediction_summary_widget_mapped_payload_value_rows(*, supplied_validation_report: Mapping[str, Any] | Any | None = None) -> list[dict[str, Any]]:
    report = _as_mapping(supplied_validation_report)
    return [
        _value_row("mapped_prediction_run_id", report.get("mapped_prediction_run_id"), "q18j_report"),
        _value_row("mapped_market_uid", report.get("mapped_market_uid"), "q18j_report"),
        _value_row("mapped_source_generated_at", report.get("mapped_source_generated_at"), "q18j_report"),
        _value_row("mapped_source_artifact_ref", report.get("mapped_source_artifact_ref"), "q18j_report"),
        _value_row("component_source_generated_at", report.get("component_source_generated_at"), "q18j_component_packet"),
        _value_row("component_source_artifact_ref", report.get("component_source_artifact_ref"), "q18j_component_packet"),
    ]


def build_latest_prediction_summary_widget_mapped_payload_value_rows_packet(*, supplied_validation_report: Mapping[str, Any] | Any | None = None) -> dict[str, Any]:
    report = _as_mapping(supplied_validation_report)
    rows = build_latest_prediction_summary_widget_mapped_payload_value_rows(supplied_validation_report=report)
    failures: list[str] = []
    if len(rows) != 6:
        failures.append("value_row_count_mismatch")
    for row in rows:
        item = str(row.get("value_item") or "")
        if item not in VALUE_ITEMS:
            failures.append(f"unexpected_value_item:{item}")
        for key in ("read_only", "non_executing"):
            if row.get(key) is not True:
                failures.append(f"row_true_boundary_missing:{item}:{key}")
        for key in (
            "q18j_validation_invoked_by_mount",
            "component_packet_builder_invoked_by_mount",
            "component_packet_builder_allowed_by_mount",
            "component_runtime_binding_allowed",
            "streamlit_render_allowed",
            "streamlit_render_invoked",
            "real_prediction_widget_rendering_allowed",
            "actual_source_read_invoked_by_mount",
            "d_hot_directory_scan_allowed",
            "refresh_invocation_allowed",
            "runtime_artifact_write_allowed",
        ):
            if row.get(key) is not False:
                failures.append(f"row_false_boundary_not_false:{item}:{key}")
    supplied = bool(report)
    values_supplied = supplied and all(str(row.get("value") or "") for row in rows)
    return {
        "ok": not failures,
        "panel_version": LATEST_PREDICTION_SUMMARY_WIDGET_MAPPED_PAYLOAD_VALUE_ROWS_PANEL_VERSION,
        "source_validation_version": LATEST_PREDICTION_SUMMARY_WIDGET_MAPPED_PAYLOAD_RENDER_DISABLED_PACKET_VALIDATION_VERSION,
        "widget_family_id": WIDGET_FAMILY_ID,
        "source_packet_id": SOURCE_PACKET_ID,
        "value_mount_state": "latest_prediction_summary_widget_mapped_payload_value_rows_ready_no_validation_builder_or_render",
        "value_row_count": len(rows),
        "value_rows": rows,
        "validation_failures": failures,
        "supplied_validation_report": supplied,
        "values_supplied": values_supplied,
        "observed_mapped_prediction_run_id": str(report.get("mapped_prediction_run_id") or "") if report else "",
        "observed_mapped_market_uid": str(report.get("mapped_market_uid") or "") if report else "",
        "observed_mapped_source_generated_at": str(report.get("mapped_source_generated_at") or "") if report else "",
        "observed_mapped_source_artifact_ref": str(report.get("mapped_source_artifact_ref") or "") if report else "",
        "observed_component_source_generated_at": str(report.get("component_source_generated_at") or "") if report else "",
        "observed_component_source_artifact_ref": str(report.get("component_source_artifact_ref") or "") if report else "",
        "read_only": True,
        "non_executing": True,
        "latest_prediction_summary_widget_mapped_payload_value_rows_mount_only": True,
        "warroom_value_rows_ready": True,
        "value_report_display_only": True,
        "mapped_payload_values_display_only": True,
        "q18j_validation_invoked_by_mount": False,
        "component_packet_builder_invoked_by_mount": False,
        "component_packet_builder_allowed_by_mount": False,
        "component_runtime_binding_allowed": False,
        "streamlit_render_allowed": False,
        "streamlit_render_invoked": False,
        "real_prediction_widget_rendering_allowed": False,
        "actual_source_read_invoked_by_mount": False,
        "actual_source_read_allowed_by_mount": False,
        "payload_reparse_allowed": False,
        "source_discovery_allowed": False,
        "d_hot_directory_scan_allowed": False,
        "d_hot_actual_read_allowed": False,
        "freshness_checked_against_d_hot": False,
        "warroom_page_mutation_allowed": False,
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
