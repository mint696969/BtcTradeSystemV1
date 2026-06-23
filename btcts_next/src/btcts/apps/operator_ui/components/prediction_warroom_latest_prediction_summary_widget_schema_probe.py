# path: ./btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_latest_prediction_summary_widget_schema_probe.py
# desc: PS-Q18D pure-data schema-specific probe for latest_prediction_summary_widget. Consumes supplied Q18B probe packet metadata only; no file read, no Streamlit import, no D-hot discovery, no refresh, no writes.

from __future__ import annotations

from typing import Any, Mapping

from btcts.apps.operator_ui.components.prediction_widgets.latest_prediction_summary_widget import SOURCE_PACKET_ID, WIDGET_FAMILY_ID
from btcts.apps.operator_ui.components.prediction_warroom_prediction_widget_bounded_actual_source_read_probe import BOUNDED_ACTUAL_SOURCE_READ_PROBE_VERSION

LATEST_PREDICTION_SUMMARY_WIDGET_SCHEMA_PROBE_VERSION = "prediction_warroom_latest_prediction_summary_widget_schema_probe.ps_q18d.v1"
REQUIRED_SUMMARY_SCHEMA_KEYS = (
    "prediction_run_id",
    "generated_at",
    "market_uid",
    "source_artifact_ref",
)
EXPECTED_SOURCE_ARTIFACT_REF_FIELD = "latest_prediction.source_artifact_ref"


def _as_mapping(value: Any) -> Mapping[str, Any]:
    if hasattr(value, "to_dict"):
        converted = value.to_dict()
        return converted if isinstance(converted, Mapping) else {}
    return value if isinstance(value, Mapping) else {}


def build_latest_prediction_summary_widget_schema_probe_rows(*, supplied_probe_packet: Mapping[str, Any] | Any | None = None) -> list[dict[str, Any]]:
    packet = _as_mapping(supplied_probe_packet)
    preview_keys = {str(key) for key in (packet.get("payload_preview_keys") or [])}
    rows: list[dict[str, Any]] = []
    for key in REQUIRED_SUMMARY_SCHEMA_KEYS:
        present = key in preview_keys
        rows.append(
            {
                "widget_family_id": WIDGET_FAMILY_ID,
                "source_packet_id": SOURCE_PACKET_ID,
                "required_schema_key": key,
                "schema_key_present": present,
                "schema_probe_state": "present" if present else "missing",
                "schema_probe_scope": "preview_key_contract_only",
                "read_only": True,
                "non_executing": True,
                "actual_source_read_invoked_by_schema_probe": False,
                "d_hot_directory_scan_allowed": False,
                "real_widget_rendering_allowed": False,
                "refresh_invocation_allowed": False,
                "runtime_artifact_write_allowed": False,
            }
        )
    return rows


def build_latest_prediction_summary_widget_schema_probe_packet(*, supplied_probe_packet: Mapping[str, Any] | Any | None = None) -> dict[str, Any]:
    packet = _as_mapping(supplied_probe_packet)
    rows = build_latest_prediction_summary_widget_schema_probe_rows(supplied_probe_packet=packet)
    failures: list[str] = []
    if packet.get("probe_version") != BOUNDED_ACTUAL_SOURCE_READ_PROBE_VERSION:
        failures.append("probe_version_mismatch")
    if packet.get("ok") is not True:
        failures.append("probe_packet_not_ok")
    if packet.get("source_packet_id") != SOURCE_PACKET_ID:
        failures.append("source_packet_id_mismatch")
    if packet.get("source_artifact_ref_field") != EXPECTED_SOURCE_ARTIFACT_REF_FIELD:
        failures.append("source_artifact_ref_field_mismatch")
    if packet.get("payload_decode_succeeded") is not True:
        failures.append("payload_decode_not_succeeded")
    if packet.get("schema_probe_ok") is not True:
        failures.append("q18b_schema_probe_not_ok")
    missing = [row["required_schema_key"] for row in rows if row.get("schema_key_present") is not True]
    failures.extend(f"missing_required_schema_key:{key}" for key in missing)
    for row in rows:
        item = str(row.get("required_schema_key") or "")
        for key in ("read_only", "non_executing"):
            if row.get(key) is not True:
                failures.append(f"row_true_boundary_missing:{item}:{key}")
        for key in (
            "actual_source_read_invoked_by_schema_probe",
            "d_hot_directory_scan_allowed",
            "real_widget_rendering_allowed",
            "refresh_invocation_allowed",
            "runtime_artifact_write_allowed",
        ):
            if row.get(key) is not False:
                failures.append(f"row_false_boundary_not_false:{item}:{key}")
    ok = not failures
    return {
        "ok": ok,
        "probe_version": LATEST_PREDICTION_SUMMARY_WIDGET_SCHEMA_PROBE_VERSION,
        "source_probe_version": BOUNDED_ACTUAL_SOURCE_READ_PROBE_VERSION,
        "widget_family_id": WIDGET_FAMILY_ID,
        "source_packet_id": SOURCE_PACKET_ID,
        "source_artifact_ref_field": EXPECTED_SOURCE_ARTIFACT_REF_FIELD,
        "schema_probe_state": "latest_prediction_summary_widget_minimum_schema_ready" if ok else "latest_prediction_summary_widget_minimum_schema_blocked",
        "required_schema_keys": list(REQUIRED_SUMMARY_SCHEMA_KEYS),
        "schema_probe_row_count": len(rows),
        "schema_probe_rows": rows,
        "missing_required_schema_keys": missing,
        "validation_failures": failures,
        "read_only": True,
        "non_executing": True,
        "latest_prediction_summary_widget_schema_probe_only": True,
        "schema_specific_probe_ready": ok,
        "preview_key_contract_only": True,
        "payload_reparse_allowed": False,
        "actual_source_read_invoked_by_schema_probe": False,
        "actual_source_read_allowed_by_schema_probe": False,
        "source_discovery_allowed": False,
        "d_hot_directory_scan_allowed": False,
        "d_hot_actual_read_allowed": False,
        "freshness_checked_against_d_hot": False,
        "warroom_page_mutation_allowed": False,
        "warroom_widget_rendering_allowed": False,
        "real_prediction_widget_rendering_allowed": False,
        "widget_props_binding_allowed": False,
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
