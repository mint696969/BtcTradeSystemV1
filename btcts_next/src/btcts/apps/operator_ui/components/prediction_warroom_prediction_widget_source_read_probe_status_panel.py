# path: ./btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_prediction_widget_source_read_probe_status_panel.py
# desc: PS-Q18C pure-data status rows for the Prediction widget bounded source read probe. No Streamlit import, no probe invocation, no D-hot discovery, no refresh, no writes.

from __future__ import annotations

from typing import Any, Mapping

from btcts.apps.operator_ui.components.prediction_warroom_prediction_widget_bounded_actual_source_read_probe import BOUNDED_ACTUAL_SOURCE_READ_PROBE_VERSION

PREDICTION_WARROOM_SOURCE_READ_PROBE_STATUS_PANEL_VERSION = "prediction_warroom_prediction_widget_source_read_probe_status_panel.ps_q18c.v1"


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
        "warroom_probe_invocation_allowed": False,
        "actual_source_read_invoked_by_mount": False,
        "d_hot_directory_scan_allowed": False,
        "real_widget_rendering_allowed": False,
        "refresh_invocation_allowed": False,
        "runtime_artifact_write_allowed": False,
    }


def build_prediction_warroom_prediction_widget_source_read_probe_status_rows(*, supplied_probe_report: Mapping[str, Any] | Any | None = None) -> list[dict[str, Any]]:
    report = _as_mapping(supplied_probe_report)
    observed_ok = report.get("ok") is True
    observed_probe_valid = report.get("probe_packet_valid") is True
    observed_read = report.get("actual_file_read_succeeded") is True
    observed_decode = report.get("payload_decode_succeeded") is True
    observed_schema = report.get("schema_probe_ok") is True
    observed_source_packet = str(report.get("probe_source_packet_id") or "not_supplied")
    observed_ref_field = str(report.get("probe_source_artifact_ref_field") or "not_supplied")
    status_state = "observed_probe_succeeded_status_only" if observed_ok else "no_probe_report_supplied_status_only"
    return [
        _status_row("probe_report", status_state, observed_ok, "Q18B probe report status; WarRoom does not invoke the probe."),
        _status_row("source_packet_id", observed_source_packet, observed_source_packet, "Source packet id shown for operator review only."),
        _status_row("source_artifact_ref_field", observed_ref_field, observed_ref_field, "Artifact ref field shown for operator review only."),
        _status_row("actual_file_read", "observed_succeeded" if observed_read else "not_invoked_by_warroom", observed_read, "Actual read may be observed from supplied report; mount never reads."),
        _status_row("payload_decode", "observed_succeeded" if observed_decode else "not_invoked_by_warroom", observed_decode, "Payload decode may be observed from supplied report; mount never decodes."),
        _status_row("schema_probe", "observed_ok" if observed_schema else "not_invoked_by_warroom", observed_schema, "Schema probe may be observed from supplied report; mount never probes."),
        _status_row("probe_packet_valid", "observed_valid" if observed_probe_valid else "not_supplied", observed_probe_valid, "Validation status is display-only."),
    ]


def build_prediction_warroom_prediction_widget_source_read_probe_status_packet(*, supplied_probe_report: Mapping[str, Any] | Any | None = None) -> dict[str, Any]:
    report = _as_mapping(supplied_probe_report)
    rows = build_prediction_warroom_prediction_widget_source_read_probe_status_rows(supplied_probe_report=report)
    failures: list[str] = []
    if len(rows) != 7:
        failures.append("status_row_count_mismatch")
    for row in rows:
        item = str(row.get("status_item") or "")
        if not item:
            failures.append("missing_status_item")
        for key in (
            "read_only",
            "non_executing",
        ):
            if row.get(key) is not True:
                failures.append(f"row_true_boundary_missing:{item}:{key}")
        for key in (
            "warroom_probe_invocation_allowed",
            "actual_source_read_invoked_by_mount",
            "d_hot_directory_scan_allowed",
            "real_widget_rendering_allowed",
            "refresh_invocation_allowed",
            "runtime_artifact_write_allowed",
        ):
            if row.get(key) is not False:
                failures.append(f"row_false_boundary_not_false:{item}:{key}")
    supplied = bool(report)
    observed_probe_ok = report.get("ok") is True if report else False
    return {
        "ok": not failures,
        "panel_version": PREDICTION_WARROOM_SOURCE_READ_PROBE_STATUS_PANEL_VERSION,
        "source_probe_version": BOUNDED_ACTUAL_SOURCE_READ_PROBE_VERSION,
        "status_mount_state": "source_read_probe_status_rows_ready_no_warroom_probe_invocation",
        "status_row_count": len(rows),
        "status_rows": rows,
        "validation_failures": failures,
        "supplied_probe_report": supplied,
        "observed_probe_ok": observed_probe_ok,
        "observed_actual_file_read_succeeded": report.get("actual_file_read_succeeded") is True if report else False,
        "observed_payload_decode_succeeded": report.get("payload_decode_succeeded") is True if report else False,
        "observed_schema_probe_ok": report.get("schema_probe_ok") is True if report else False,
        "read_only": True,
        "non_executing": True,
        "source_read_probe_status_row_mount_only": True,
        "warroom_status_rows_ready": True,
        "bounded_probe_report_display_only": True,
        "bounded_actual_source_read_probe_called_by_mount": False,
        "actual_source_read_invoked_by_mount": False,
        "actual_source_read_allowed_by_warroom_mount": False,
        "source_discovery_allowed": False,
        "d_hot_directory_scan_allowed": False,
        "d_hot_actual_read_allowed": False,
        "freshness_checked_against_d_hot": False,
        "warroom_page_mutation_allowed": False,
        "warroom_widget_rendering_allowed": False,
        "real_prediction_widget_rendering_allowed": False,
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
