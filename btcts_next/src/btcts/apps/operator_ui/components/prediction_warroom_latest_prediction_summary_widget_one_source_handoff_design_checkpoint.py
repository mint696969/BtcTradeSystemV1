# path: ./btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_latest_prediction_summary_widget_one_source_handoff_design_checkpoint.py
# desc: PS-Q18O pure-data explicit one-source handoff design checkpoint for latest_prediction_summary_widget. No source resolution, no actual read, no D-hot discovery, no render, no refresh, no writes.

from __future__ import annotations

from typing import Any, Mapping

from btcts.apps.operator_ui.components.prediction_widgets.latest_prediction_summary_widget import SOURCE_PACKET_ID, WIDGET_FAMILY_ID
from btcts.apps.operator_ui.components.prediction_warroom_latest_prediction_summary_widget_real_source_handoff_preflight_panel import LATEST_PREDICTION_SUMMARY_WIDGET_REAL_SOURCE_HANDOFF_PREFLIGHT_PANEL_VERSION

LATEST_PREDICTION_SUMMARY_WIDGET_ONE_SOURCE_HANDOFF_DESIGN_CHECKPOINT_VERSION = "prediction_warroom_latest_prediction_summary_widget_one_source_handoff_design_checkpoint.ps_q18o.v1"
ONE_SOURCE_HANDOFF_DESIGN_ACK = "PS_Q18O_DECLARE_ONE_SOURCE_HANDOFF_DESIGN_ONLY"
DESIGN_ITEMS = (
    "handoff_candidate_count",
    "selected_widget_family_id",
    "selected_source_packet_id",
    "selected_candidate_generated_at",
    "selected_candidate_source_artifact_ref",
    "selected_candidate_market_uid",
    "explicit_design_ack",
    "deferred_runtime_boundary",
)


def _as_mapping(value: Any) -> Mapping[str, Any]:
    if hasattr(value, "to_dict"):
        converted = value.to_dict()
        return converted if isinstance(converted, Mapping) else {}
    return value if isinstance(value, Mapping) else {}


def _clean(value: Any) -> str:
    return "" if value is None else str(value)


def _design_row(item: str, value: Any, note: str) -> dict[str, Any]:
    text = _clean(value)
    return {
        "design_item": item,
        "value": text,
        "state": "declared" if text else "not_supplied",
        "operator_note": note,
        "read_only": True,
        "non_executing": True,
        "one_source_handoff_design_checkpoint_only": True,
        "source_candidate_count_fixed_to_one": True,
        "source_artifact_resolution_allowed": False,
        "source_artifact_path_materialized": False,
        "source_artifact_exists_checked": False,
        "source_artifact_schema_checked": False,
        "actual_source_read_allowed": False,
        "actual_source_read_invoked": False,
        "payload_reparse_allowed": False,
        "source_discovery_allowed": False,
        "d_hot_directory_scan_allowed": False,
        "d_hot_actual_read_allowed": False,
        "q18n_validation_invoked_by_mount": False,
        "q18m_validation_invoked_by_mount": False,
        "q18j_validation_invoked_by_mount": False,
        "component_packet_builder_invoked_by_mount": False,
        "streamlit_render_invoked": False,
        "real_prediction_widget_rendering_allowed": False,
        "refresh_invocation_allowed": False,
        "runtime_artifact_write_allowed": False,
    }


def build_latest_prediction_summary_widget_one_source_handoff_design_checkpoint_rows(*, supplied_handoff_preflight_report: Mapping[str, Any] | Any | None = None) -> list[dict[str, Any]]:
    report = _as_mapping(supplied_handoff_preflight_report)
    return [
        _design_row("handoff_candidate_count", "1", "Exactly one latest_prediction_summary_widget source candidate is declared for the next design step."),
        _design_row("selected_widget_family_id", WIDGET_FAMILY_ID, "The selected widget family is fixed before any resolver/read path is introduced."),
        _design_row("selected_source_packet_id", SOURCE_PACKET_ID, "The selected source packet is fixed before any resolver/read path is introduced."),
        _design_row("selected_candidate_generated_at", report.get("candidate_generated_at"), "Candidate generated_at from supplied PS-Q18N report only; no fresh read."),
        _design_row("selected_candidate_source_artifact_ref", report.get("candidate_source_artifact_ref"), "Candidate source_artifact_ref from supplied PS-Q18N report only; not materialized or read."),
        _design_row("selected_candidate_market_uid", report.get("candidate_market_uid"), "Candidate market uid from supplied PS-Q18N report only."),
        _design_row("explicit_design_ack", ONE_SOURCE_HANDOFF_DESIGN_ACK, "Design-only acknowledgement; not an approval for source resolution or actual read."),
        _design_row("deferred_runtime_boundary", "resolution=false; exists_check=false; actual_read=false; render=false; refresh=false; write=false", "All runtime behavior remains deferred after this checkpoint."),
    ]


def build_latest_prediction_summary_widget_one_source_handoff_design_checkpoint_packet(*, supplied_handoff_preflight_report: Mapping[str, Any] | Any | None = None) -> dict[str, Any]:
    report = _as_mapping(supplied_handoff_preflight_report)
    rows = build_latest_prediction_summary_widget_one_source_handoff_design_checkpoint_rows(supplied_handoff_preflight_report=report)
    failures: list[str] = []
    if len(rows) != 8:
        failures.append("design_row_count_mismatch")
    for row in rows:
        item = str(row.get("design_item") or "")
        if item not in DESIGN_ITEMS:
            failures.append(f"unexpected_design_item:{item}")
        for key in ("read_only", "non_executing", "one_source_handoff_design_checkpoint_only", "source_candidate_count_fixed_to_one"):
            if row.get(key) is not True:
                failures.append(f"row_true_boundary_missing:{item}:{key}")
        for key in (
            "source_artifact_resolution_allowed",
            "source_artifact_path_materialized",
            "source_artifact_exists_checked",
            "source_artifact_schema_checked",
            "actual_source_read_allowed",
            "actual_source_read_invoked",
            "payload_reparse_allowed",
            "source_discovery_allowed",
            "d_hot_directory_scan_allowed",
            "d_hot_actual_read_allowed",
            "q18n_validation_invoked_by_mount",
            "q18m_validation_invoked_by_mount",
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
    candidate_ready = supplied and all(
        _clean(report.get(key))
        for key in ("candidate_generated_at", "candidate_source_artifact_ref", "candidate_market_uid")
    )
    return {
        "ok": not failures,
        "design_checkpoint_version": LATEST_PREDICTION_SUMMARY_WIDGET_ONE_SOURCE_HANDOFF_DESIGN_CHECKPOINT_VERSION,
        "source_handoff_preflight_panel_version": LATEST_PREDICTION_SUMMARY_WIDGET_REAL_SOURCE_HANDOFF_PREFLIGHT_PANEL_VERSION,
        "widget_family_id": WIDGET_FAMILY_ID,
        "source_packet_id": SOURCE_PACKET_ID,
        "one_source_handoff_design_ack": ONE_SOURCE_HANDOFF_DESIGN_ACK,
        "design_checkpoint_state": "latest_prediction_summary_widget_one_source_handoff_design_declared_no_resolution_read_or_render",
        "design_row_count": len(rows),
        "design_rows": rows,
        "validation_failures": failures,
        "supplied_handoff_preflight_report": supplied,
        "handoff_candidate_ready": candidate_ready,
        "one_source_candidate_declared": True,
        "source_candidate_count": 1,
        "selected_candidate_generated_at": _clean(report.get("candidate_generated_at")) if report else "",
        "selected_candidate_source_artifact_ref": _clean(report.get("candidate_source_artifact_ref")) if report else "",
        "selected_candidate_market_uid": _clean(report.get("candidate_market_uid")) if report else "",
        "read_only": True,
        "non_executing": True,
        "latest_prediction_summary_widget_one_source_handoff_design_checkpoint_only": True,
        "one_source_handoff_design_checkpoint_ready": True,
        "source_candidate_count_fixed_to_one": True,
        "explicit_design_ack_matched": True,
        "warroom_page_mutation_allowed": False,
        "real_source_handoff_invoked": False,
        "source_artifact_resolution_allowed": False,
        "source_artifact_resolved": False,
        "source_artifact_path_materialized": False,
        "source_artifact_exists_checked": False,
        "source_artifact_schema_checked": False,
        "actual_source_read_allowed": False,
        "actual_source_read_invoked": False,
        "payload_reparse_allowed": False,
        "source_discovery_allowed": False,
        "d_hot_directory_scan_allowed": False,
        "d_hot_actual_read_allowed": False,
        "freshness_checked_against_d_hot": False,
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
