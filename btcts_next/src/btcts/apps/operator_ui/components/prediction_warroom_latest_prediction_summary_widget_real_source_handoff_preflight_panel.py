# path: ./btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_latest_prediction_summary_widget_real_source_handoff_preflight_panel.py
# desc: PS-Q18N pure-data real-source handoff preflight for latest_prediction_summary_widget. No Streamlit, no Q18J invocation, no source resolution/read, no D-hot discovery, no writes.

from __future__ import annotations

from typing import Any, Mapping

from btcts.apps.operator_ui.components.prediction_widgets.latest_prediction_summary_widget import SOURCE_PACKET_ID, WIDGET_FAMILY_ID
from btcts.apps.operator_ui.components.prediction_warroom_latest_prediction_summary_widget_operator_value_summary_panel import LATEST_PREDICTION_SUMMARY_WIDGET_OPERATOR_VALUE_SUMMARY_PANEL_VERSION

LATEST_PREDICTION_SUMMARY_WIDGET_REAL_SOURCE_HANDOFF_PREFLIGHT_PANEL_VERSION = "prediction_warroom_latest_prediction_summary_widget_real_source_handoff_preflight_panel.ps_q18n.v1"
HANDOFF_ITEMS = (
    "source_packet_id",
    "widget_family_id",
    "candidate_generated_at",
    "candidate_source_artifact_ref",
    "candidate_market_uid",
    "handoff_boundary",
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
        "handoff_item": item,
        "value": text,
        "state": "candidate_observed" if text else "not_supplied",
        "operator_note": note,
        "read_only": True,
        "non_executing": True,
        "real_source_handoff_preflight_only": True,
        "real_source_handoff_invoked": False,
        "actual_source_resolution_allowed": False,
        "actual_source_resolved": False,
        "actual_source_read_allowed": False,
        "actual_source_read_invoked": False,
        "payload_reparse_allowed": False,
        "source_discovery_allowed": False,
        "d_hot_directory_scan_allowed": False,
        "d_hot_actual_read_allowed": False,
        "q18j_validation_invoked_by_mount": False,
        "component_packet_builder_invoked_by_mount": False,
        "streamlit_render_invoked": False,
        "real_prediction_widget_rendering_allowed": False,
        "refresh_invocation_allowed": False,
        "runtime_artifact_write_allowed": False,
    }


def build_latest_prediction_summary_widget_real_source_handoff_preflight_rows(*, supplied_operator_summary_report: Mapping[str, Any] | Any | None = None) -> list[dict[str, Any]]:
    report = _as_mapping(supplied_operator_summary_report)
    return [
        _row("source_packet_id", SOURCE_PACKET_ID, "Static source packet id required before a real source handoff can be introduced."),
        _row("widget_family_id", WIDGET_FAMILY_ID, "Static widget family id required before a real source handoff can be introduced."),
        _row("candidate_generated_at", report.get("observed_mapped_source_generated_at"), "Candidate generated_at from supplied PS-Q18M report only; no fresh read."),
        _row("candidate_source_artifact_ref", report.get("observed_mapped_source_artifact_ref"), "Candidate source artifact ref from supplied PS-Q18M report only; not resolved or read."),
        _row("candidate_market_uid", report.get("observed_mapped_market_uid"), "Candidate market uid from supplied PS-Q18M report only."),
        _row("handoff_boundary", "real_handoff=false; source_resolution=false; actual_read=false; render=false", "Boundary row: this slice only declares the handoff contract."),
    ]


def build_latest_prediction_summary_widget_real_source_handoff_preflight_packet(*, supplied_operator_summary_report: Mapping[str, Any] | Any | None = None) -> dict[str, Any]:
    report = _as_mapping(supplied_operator_summary_report)
    rows = build_latest_prediction_summary_widget_real_source_handoff_preflight_rows(supplied_operator_summary_report=report)
    failures: list[str] = []
    if len(rows) != 6:
        failures.append("handoff_row_count_mismatch")
    for row in rows:
        item = str(row.get("handoff_item") or "")
        if item not in HANDOFF_ITEMS:
            failures.append(f"unexpected_handoff_item:{item}")
        for key in ("read_only", "non_executing", "real_source_handoff_preflight_only"):
            if row.get(key) is not True:
                failures.append(f"row_true_boundary_missing:{item}:{key}")
        for key in (
            "real_source_handoff_invoked",
            "actual_source_resolution_allowed",
            "actual_source_resolved",
            "actual_source_read_allowed",
            "actual_source_read_invoked",
            "payload_reparse_allowed",
            "source_discovery_allowed",
            "d_hot_directory_scan_allowed",
            "d_hot_actual_read_allowed",
            "q18j_validation_invoked_by_mount",
            "component_packet_builder_invoked_by_mount",
            "streamlit_render_invoked",
            "real_prediction_widget_rendering_allowed",
            "refresh_invocation_allowed",
            "runtime_artifact_write_allowed",
        ):
            if row.get(key) is not False:
                failures.append(f"row_false_boundary_not_false:{item}:{key}")
    supplied = bool(report)
    handoff_candidate_ready = supplied and all(
        _clean(report.get(key))
        for key in ("observed_mapped_source_generated_at", "observed_mapped_source_artifact_ref", "observed_mapped_market_uid")
    )
    return {
        "ok": not failures,
        "panel_version": LATEST_PREDICTION_SUMMARY_WIDGET_REAL_SOURCE_HANDOFF_PREFLIGHT_PANEL_VERSION,
        "source_operator_summary_panel_version": LATEST_PREDICTION_SUMMARY_WIDGET_OPERATOR_VALUE_SUMMARY_PANEL_VERSION,
        "widget_family_id": WIDGET_FAMILY_ID,
        "source_packet_id": SOURCE_PACKET_ID,
        "handoff_mount_state": "latest_prediction_summary_widget_real_source_handoff_preflight_ready_no_resolution_read_or_render",
        "handoff_row_count": len(rows),
        "handoff_rows": rows,
        "validation_failures": failures,
        "supplied_operator_summary_report": supplied,
        "handoff_candidate_ready": handoff_candidate_ready,
        "candidate_generated_at": _clean(report.get("observed_mapped_source_generated_at")) if report else "",
        "candidate_source_artifact_ref": _clean(report.get("observed_mapped_source_artifact_ref")) if report else "",
        "candidate_market_uid": _clean(report.get("observed_mapped_market_uid")) if report else "",
        "read_only": True,
        "non_executing": True,
        "latest_prediction_summary_widget_real_source_handoff_preflight_mount_only": True,
        "warroom_handoff_preflight_rows_ready": True,
        "operator_summary_report_display_only": True,
        "real_source_handoff_preflight_only": True,
        "real_source_handoff_invoked": False,
        "actual_source_resolution_allowed": False,
        "actual_source_resolved": False,
        "actual_source_read_allowed": False,
        "actual_source_read_invoked": False,
        "payload_reparse_allowed": False,
        "source_discovery_allowed": False,
        "d_hot_directory_scan_allowed": False,
        "d_hot_actual_read_allowed": False,
        "freshness_checked_against_d_hot": False,
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
