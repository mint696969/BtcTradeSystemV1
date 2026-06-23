# path: ./btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_latest_prediction_summary_widget_render_disabled_packet_status_panel.py
# desc: PS-Q18H pure-data status rows for latest_prediction_summary_widget render-disabled packet validation. No Streamlit import, no Q18G checker invocation, no component packet builder invocation, no source read, no D-hot discovery, no writes.

from __future__ import annotations

from typing import Any, Mapping

from btcts.apps.operator_ui.components.prediction_widgets.latest_prediction_summary_widget import SOURCE_PACKET_ID, WIDGET_FAMILY_ID
from btcts.apps.operator_ui.components.prediction_warroom_latest_prediction_summary_widget_render_disabled_packet_validation import LATEST_PREDICTION_SUMMARY_WIDGET_RENDER_DISABLED_PACKET_VALIDATION_VERSION

LATEST_PREDICTION_SUMMARY_WIDGET_RENDER_DISABLED_PACKET_STATUS_PANEL_VERSION = "prediction_warroom_latest_prediction_summary_widget_render_disabled_packet_status_panel.ps_q18h.v1"


def _as_mapping(value: Any) -> Mapping[str, Any]:
    if hasattr(value, "to_dict"):
        converted = value.to_dict()
        return converted if isinstance(converted, Mapping) else {}
    return value if isinstance(value, Mapping) else {}


def _status_row(item: str, state: str, observed: Any, note: str) -> dict[str, Any]:
    return {
        "status_item": item,
        "state": state,
        "observed": observed,
        "operator_note": note,
        "read_only": True,
        "non_executing": True,
        "q18g_validation_invoked_by_mount": False,
        "component_packet_builder_invoked_by_mount": False,
        "streamlit_render_allowed": False,
        "streamlit_render_invoked": False,
        "real_prediction_widget_rendering_allowed": False,
        "actual_source_read_invoked_by_mount": False,
        "d_hot_directory_scan_allowed": False,
        "refresh_invocation_allowed": False,
        "runtime_artifact_write_allowed": False,
    }


def build_latest_prediction_summary_widget_render_disabled_packet_status_rows(*, supplied_validation_report: Mapping[str, Any] | Any | None = None) -> list[dict[str, Any]]:
    report = _as_mapping(supplied_validation_report)
    observed_ok = report.get("ok") is True
    observed_packet_valid = report.get("component_packet_valid") is True
    observed_builder = report.get("component_packet_builder_invoked") is True
    observed_state = str(report.get("component_packet_state") or "")
    observed_missing = list(report.get("component_missing_props") or []) if report else []
    status_state = "observed_render_disabled_packet_valid_status_only" if observed_ok else "no_validation_report_supplied_status_only"
    return [
        _status_row("render_disabled_validation_report", status_state, observed_ok, "Q18G validation report status; WarRoom does not run Q18G."),
        _status_row("widget_family_id", WIDGET_FAMILY_ID, WIDGET_FAMILY_ID, "Target widget family shown for operator review only."),
        _status_row("source_packet_id", SOURCE_PACKET_ID, SOURCE_PACKET_ID, "Source packet id shown for operator review only."),
        _status_row("component_packet_builder", "observed_invoked" if observed_builder else "not_invoked_by_warroom", observed_builder, "Component packet builder invocation may be observed from supplied report; mount never invokes it."),
        _status_row("component_packet_valid", "observed_valid" if observed_packet_valid else "not_verified_by_warroom", observed_packet_valid, "Component packet validity is displayed only."),
        _status_row("component_packet_state", observed_state or "not_supplied", observed_state, "Render-disabled component packet state is displayed only."),
        _status_row("component_missing_props", "none" if not observed_missing else "missing", ",".join(str(v) for v in observed_missing), "Missing component props are displayed only."),
        _status_row("render_boundary", "render_disabled_status_only", "streamlit_render=false; real_render=false; actual_read=false", "Boundary row; WarRoom status mount does not render or read."),
    ]


def build_latest_prediction_summary_widget_render_disabled_packet_status_packet(*, supplied_validation_report: Mapping[str, Any] | Any | None = None) -> dict[str, Any]:
    report = _as_mapping(supplied_validation_report)
    rows = build_latest_prediction_summary_widget_render_disabled_packet_status_rows(supplied_validation_report=report)
    failures: list[str] = []
    if len(rows) != 8:
        failures.append("status_row_count_mismatch")
    for row in rows:
        item = str(row.get("status_item") or "")
        if not item:
            failures.append("missing_status_item")
        for key in ("read_only", "non_executing"):
            if row.get(key) is not True:
                failures.append(f"row_true_boundary_missing:{item}:{key}")
        for key in (
            "q18g_validation_invoked_by_mount",
            "component_packet_builder_invoked_by_mount",
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
    observed_ok = report.get("ok") is True if report else False
    return {
        "ok": not failures,
        "panel_version": LATEST_PREDICTION_SUMMARY_WIDGET_RENDER_DISABLED_PACKET_STATUS_PANEL_VERSION,
        "source_validation_version": LATEST_PREDICTION_SUMMARY_WIDGET_RENDER_DISABLED_PACKET_VALIDATION_VERSION,
        "widget_family_id": WIDGET_FAMILY_ID,
        "source_packet_id": SOURCE_PACKET_ID,
        "status_mount_state": "latest_prediction_summary_widget_render_disabled_packet_status_rows_ready_no_validation_or_rendering",
        "status_row_count": len(rows),
        "status_rows": rows,
        "validation_failures": failures,
        "supplied_validation_report": supplied,
        "observed_validation_ok": observed_ok,
        "observed_component_packet_builder_invoked": report.get("component_packet_builder_invoked") is True if report else False,
        "observed_component_packet_valid": report.get("component_packet_valid") is True if report else False,
        "observed_component_packet_state": str(report.get("component_packet_state") or "") if report else "",
        "observed_component_missing_props": list(report.get("component_missing_props") or []) if report else [],
        "read_only": True,
        "non_executing": True,
        "latest_prediction_summary_widget_render_disabled_packet_status_row_mount_only": True,
        "warroom_status_rows_ready": True,
        "validation_report_display_only": True,
        "render_disabled_packet_status_display_only": True,
        "q18g_validation_invoked_by_mount": False,
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
