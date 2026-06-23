# path: ./btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_latest_prediction_summary_widget_operator_value_summary_panel.py
# desc: PS-Q18M pure-data operator-readable mapped value summary for latest_prediction_summary_widget. No Streamlit, no Q18J invocation, no component packet builder invocation, no source read, no D-hot discovery, no writes.

from __future__ import annotations

from typing import Any, Mapping

from btcts.apps.operator_ui.components.prediction_widgets.latest_prediction_summary_widget import SOURCE_PACKET_ID, WIDGET_FAMILY_ID
from btcts.apps.operator_ui.components.prediction_warroom_latest_prediction_summary_widget_mapped_payload_render_disabled_packet_validation import LATEST_PREDICTION_SUMMARY_WIDGET_MAPPED_PAYLOAD_RENDER_DISABLED_PACKET_VALIDATION_VERSION

LATEST_PREDICTION_SUMMARY_WIDGET_OPERATOR_VALUE_SUMMARY_PANEL_VERSION = "prediction_warroom_latest_prediction_summary_widget_operator_value_summary_panel.ps_q18m.v1"
SUMMARY_ITEMS = (
    "prediction_run",
    "market",
    "generated_at",
    "source_artifact",
    "component_generated_at",
    "component_source_artifact",
    "display_boundary",
)


def _as_mapping(value: Any) -> Mapping[str, Any]:
    if hasattr(value, "to_dict"):
        converted = value.to_dict()
        return converted if isinstance(converted, Mapping) else {}
    return value if isinstance(value, Mapping) else {}


def _clean(value: Any) -> str:
    return "" if value is None else str(value)


def _summary_row(item: str, label: str, value: Any, note: str) -> dict[str, Any]:
    text = _clean(value)
    return {
        "summary_item": item,
        "label": label,
        "value": text,
        "state": "observed" if text else "not_supplied",
        "operator_note": note,
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


def build_latest_prediction_summary_widget_operator_value_summary_rows(*, supplied_validation_report: Mapping[str, Any] | Any | None = None) -> list[dict[str, Any]]:
    report = _as_mapping(supplied_validation_report)
    return [
        _summary_row("prediction_run", "Prediction run", report.get("mapped_prediction_run_id"), "Mapped run id from supplied Q18J report only."),
        _summary_row("market", "Market", report.get("mapped_market_uid"), "Mapped market uid from supplied Q18J report only."),
        _summary_row("generated_at", "Generated at", report.get("mapped_source_generated_at"), "Mapped generated_at from supplied Q18J report only."),
        _summary_row("source_artifact", "Source artifact", report.get("mapped_source_artifact_ref"), "Mapped source artifact ref from supplied Q18J report only."),
        _summary_row("component_generated_at", "Component generated_at", report.get("component_source_generated_at"), "Render-disabled packet generated_at from supplied Q18J report only."),
        _summary_row("component_source_artifact", "Component source artifact", report.get("component_source_artifact_ref"), "Render-disabled packet artifact ref from supplied Q18J report only."),
        _summary_row("display_boundary", "Display boundary", "q18j_mount=false; component_builder_mount=false; streamlit_render=false; actual_read=false", "WarRoom summary mount is display-only."),
    ]


def build_latest_prediction_summary_widget_operator_value_summary_packet(*, supplied_validation_report: Mapping[str, Any] | Any | None = None) -> dict[str, Any]:
    report = _as_mapping(supplied_validation_report)
    rows = build_latest_prediction_summary_widget_operator_value_summary_rows(supplied_validation_report=report)
    failures: list[str] = []
    if len(rows) != 7:
        failures.append("summary_row_count_mismatch")
    for row in rows:
        item = str(row.get("summary_item") or "")
        if item not in SUMMARY_ITEMS:
            failures.append(f"unexpected_summary_item:{item}")
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
    expected_value_items = [row for row in rows if row.get("summary_item") != "display_boundary"]
    values_supplied = supplied and all(str(row.get("value") or "") for row in expected_value_items)
    compact_line = ""
    if values_supplied:
        compact_line = "latest_prediction_summary_widget: run={run} / market={market} / generated_at={generated_at} / source={source}".format(
            run=report.get("mapped_prediction_run_id"),
            market=report.get("mapped_market_uid"),
            generated_at=report.get("mapped_source_generated_at"),
            source=report.get("mapped_source_artifact_ref"),
        )
    return {
        "ok": not failures,
        "panel_version": LATEST_PREDICTION_SUMMARY_WIDGET_OPERATOR_VALUE_SUMMARY_PANEL_VERSION,
        "source_validation_version": LATEST_PREDICTION_SUMMARY_WIDGET_MAPPED_PAYLOAD_RENDER_DISABLED_PACKET_VALIDATION_VERSION,
        "widget_family_id": WIDGET_FAMILY_ID,
        "source_packet_id": SOURCE_PACKET_ID,
        "summary_mount_state": "latest_prediction_summary_widget_operator_value_summary_ready_no_validation_builder_or_render",
        "summary_row_count": len(rows),
        "summary_rows": rows,
        "compact_line": compact_line,
        "compact_line_ready": bool(compact_line),
        "validation_failures": failures,
        "supplied_validation_report": supplied,
        "values_supplied": values_supplied,
        "observed_mapped_prediction_run_id": _clean(report.get("mapped_prediction_run_id")) if report else "",
        "observed_mapped_market_uid": _clean(report.get("mapped_market_uid")) if report else "",
        "observed_mapped_source_generated_at": _clean(report.get("mapped_source_generated_at")) if report else "",
        "observed_mapped_source_artifact_ref": _clean(report.get("mapped_source_artifact_ref")) if report else "",
        "observed_component_source_generated_at": _clean(report.get("component_source_generated_at")) if report else "",
        "observed_component_source_artifact_ref": _clean(report.get("component_source_artifact_ref")) if report else "",
        "read_only": True,
        "non_executing": True,
        "latest_prediction_summary_widget_operator_value_summary_mount_only": True,
        "warroom_operator_summary_rows_ready": True,
        "operator_summary_display_only": True,
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
