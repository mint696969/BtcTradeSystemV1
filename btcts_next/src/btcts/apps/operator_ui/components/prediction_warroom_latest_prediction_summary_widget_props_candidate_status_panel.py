# path: ./btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_latest_prediction_summary_widget_props_candidate_status_panel.py
# desc: PS-Q18F pure-data status rows for latest_prediction_summary_widget props candidate. No Streamlit import, no checker invocation, no component binding, no widget render, no file read, no D-hot discovery, no writes.

from __future__ import annotations

from typing import Any, Mapping

from btcts.apps.operator_ui.components.prediction_widgets.latest_prediction_summary_widget import SOURCE_PACKET_ID, WIDGET_FAMILY_ID
from btcts.apps.operator_ui.components.prediction_warroom_latest_prediction_summary_widget_props_binding_preflight import LATEST_PREDICTION_SUMMARY_WIDGET_PROPS_BINDING_PREFLIGHT_VERSION

LATEST_PREDICTION_SUMMARY_WIDGET_PROPS_CANDIDATE_STATUS_PANEL_VERSION = "prediction_warroom_latest_prediction_summary_widget_props_candidate_status_panel.ps_q18f.v1"


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
        "component_props_binding_allowed": False,
        "component_props_bound_by_mount": False,
        "render_invocation_allowed": False,
        "real_prediction_widget_rendering_allowed": False,
        "actual_source_read_invoked_by_mount": False,
        "d_hot_directory_scan_allowed": False,
        "refresh_invocation_allowed": False,
        "runtime_artifact_write_allowed": False,
    }


def build_latest_prediction_summary_widget_props_candidate_status_rows(*, supplied_props_preflight_report: Mapping[str, Any] | Any | None = None) -> list[dict[str, Any]]:
    report = _as_mapping(supplied_props_preflight_report)
    observed_ok = report.get("ok") is True
    observed_valid = report.get("props_packet_valid") is True
    observed_contract = report.get("props_contract_complete") is True
    observed_candidate = report.get("props_candidate_ready") is True
    missing_component_props = list(report.get("missing_required_component_props") or []) if report else []
    missing_schema_keys = list(report.get("missing_required_schema_keys") or []) if report else []
    status_state = "observed_props_candidate_ready_status_only" if observed_ok else "no_props_preflight_report_supplied_status_only"
    return [
        _status_row("props_preflight_report", status_state, observed_ok, "Q18E props preflight report status; WarRoom does not run the checker."),
        _status_row("widget_family_id", WIDGET_FAMILY_ID, WIDGET_FAMILY_ID, "Target widget family shown for operator review only."),
        _status_row("source_packet_id", SOURCE_PACKET_ID, SOURCE_PACKET_ID, "Source packet id shown for operator review only."),
        _status_row("props_packet_valid", "observed_valid" if observed_valid else "not_supplied", observed_valid, "Validation status is display-only."),
        _status_row("props_candidate_ready", "observed_ready" if observed_candidate else "not_bound_by_warroom", observed_candidate, "Props candidate readiness may be observed from supplied report; mount never binds props."),
        _status_row("props_contract_complete", "observed_complete" if observed_contract else "not_verified_by_warroom", observed_contract, "Props contract completeness may be observed from supplied report; mount never renders."),
        _status_row("missing_required_component_props", "none" if not missing_component_props else "missing", ",".join(str(v) for v in missing_component_props), "Missing component props are displayed only."),
        _status_row("missing_required_schema_keys", "none" if not missing_schema_keys else "missing", ",".join(str(v) for v in missing_schema_keys), "Missing schema keys are displayed only."),
    ]


def build_latest_prediction_summary_widget_props_candidate_status_packet(*, supplied_props_preflight_report: Mapping[str, Any] | Any | None = None) -> dict[str, Any]:
    report = _as_mapping(supplied_props_preflight_report)
    rows = build_latest_prediction_summary_widget_props_candidate_status_rows(supplied_props_preflight_report=report)
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
            "component_props_binding_allowed",
            "component_props_bound_by_mount",
            "render_invocation_allowed",
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
        "panel_version": LATEST_PREDICTION_SUMMARY_WIDGET_PROPS_CANDIDATE_STATUS_PANEL_VERSION,
        "source_preflight_version": LATEST_PREDICTION_SUMMARY_WIDGET_PROPS_BINDING_PREFLIGHT_VERSION,
        "widget_family_id": WIDGET_FAMILY_ID,
        "source_packet_id": SOURCE_PACKET_ID,
        "status_mount_state": "latest_prediction_summary_widget_props_candidate_status_rows_ready_no_component_binding",
        "status_row_count": len(rows),
        "status_rows": rows,
        "validation_failures": failures,
        "supplied_props_preflight_report": supplied,
        "observed_props_preflight_ok": observed_ok,
        "observed_props_candidate_ready": report.get("props_candidate_ready") is True if report else False,
        "observed_props_contract_complete": report.get("props_contract_complete") is True if report else False,
        "observed_missing_required_component_props": list(report.get("missing_required_component_props") or []) if report else [],
        "read_only": True,
        "non_executing": True,
        "latest_prediction_summary_widget_props_candidate_status_row_mount_only": True,
        "warroom_status_rows_ready": True,
        "props_preflight_report_display_only": True,
        "props_candidate_status_display_only": True,
        "component_props_binding_allowed": False,
        "component_props_bound_by_mount": False,
        "widget_props_binding_allowed": False,
        "widget_props_bound_to_component": False,
        "render_invocation_allowed": False,
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
