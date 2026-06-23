# path: ./btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_prediction_widget_source_artifact_resolution_preflight_panel.py
# desc: PS-Q18A pure-data source artifact resolution preflight rows for Prediction WarRoom widgets. No Streamlit import, no D-hot read, no source artifact resolution, no refresh, no writes.

from __future__ import annotations

from typing import Any, Mapping

from btcts.apps.operator_ui.components.prediction_warroom_prediction_widget_source_readiness_preflight_panel import (
    PREDICTION_WARROOM_SOURCE_READINESS_PREFLIGHT_PANEL_VERSION,
    build_prediction_warroom_prediction_widget_source_readiness_preflight_packet,
)

PREDICTION_WARROOM_SOURCE_ARTIFACT_RESOLUTION_PREFLIGHT_PANEL_VERSION = "prediction_warroom_prediction_widget_source_artifact_resolution_preflight_panel.ps_q18a.v1"


def _as_mapping(value: Any) -> Mapping[str, Any]:
    if hasattr(value, "to_dict"):
        converted = value.to_dict()
        return converted if isinstance(converted, Mapping) else {}
    return value if isinstance(value, Mapping) else {}


def build_prediction_warroom_prediction_widget_source_artifact_resolution_rows(*, source_readiness_packet: Mapping[str, Any] | Any | None = None) -> list[dict[str, Any]]:
    packet = _as_mapping(source_readiness_packet) or build_prediction_warroom_prediction_widget_source_readiness_preflight_packet()
    rows: list[dict[str, Any]] = []
    for item in packet.get("readiness_rows") or []:
        row = _as_mapping(item)
        widget_id = str(row.get("widget_family_id") or "")
        source_packet_id = str(row.get("source_packet_id") or "")
        source_artifact_ref_field = str(row.get("source_artifact_ref_field") or "")
        rows.append({
            "row_index": int(row.get("row_index") or 0),
            "widget_family_id": widget_id,
            "source_packet_id": source_packet_id,
            "source_artifact_ref_field": source_artifact_ref_field,
            "freshness_field": str(row.get("freshness_field") or ""),
            "release_gate_field": str(row.get("release_gate_field") or ""),
            "mount_zone_hint": str(row.get("mount_zone_hint") or ""),
            "artifact_resolution_key": f"{source_packet_id}:{source_artifact_ref_field}",
            "artifact_resolution_preflight_state": "artifact_ref_field_ready_resolution_deferred",
            "artifact_ref_field_present": bool(source_artifact_ref_field),
            "source_packet_id_present": bool(source_packet_id),
            "source_artifact_resolution_preflight_ready": True,
            "source_artifact_resolution_allowed": False,
            "source_artifact_resolved": False,
            "source_artifact_path_materialized": False,
            "source_artifact_exists_checked": False,
            "source_artifact_schema_checked": False,
            "actual_source_bound": False,
            "actual_source_read_allowed": False,
            "d_hot_actual_read_allowed": False,
            "freshness_checked_against_d_hot": False,
            "real_widget_render_ready": False,
            "render_allowed": False,
            "refresh_invocation_allowed": False,
            "runtime_artifact_write_allowed": False,
            "status_artifact_write_allowed": False,
            "confidence_increase_allowed": False,
            "parameter_apply_allowed": False,
            "parameter_staging_write_allowed": False,
            "ledger_append_allowed": False,
            "autotrade_trigger_allowed": False,
            "broker_private_api_allowed": False,
        })
    return rows


def build_prediction_warroom_prediction_widget_source_artifact_resolution_preflight_packet(*, source_readiness_packet: Mapping[str, Any] | Any | None = None) -> dict[str, Any]:
    readiness_packet = _as_mapping(source_readiness_packet) or build_prediction_warroom_prediction_widget_source_readiness_preflight_packet()
    rows = build_prediction_warroom_prediction_widget_source_artifact_resolution_rows(source_readiness_packet=readiness_packet)
    failures: list[str] = []
    if readiness_packet.get("panel_version") != PREDICTION_WARROOM_SOURCE_READINESS_PREFLIGHT_PANEL_VERSION:
        failures.append("source_readiness_panel_version_mismatch")
    if readiness_packet.get("ok") is not True:
        failures.append("source_readiness_packet_not_ok")
    if len(rows) != int(readiness_packet.get("readiness_row_count") or 0):
        failures.append("artifact_resolution_row_count_mismatch")
    for row in rows:
        widget_id = str(row.get("widget_family_id") or "")
        for field in ("source_packet_id", "source_artifact_ref_field", "freshness_field", "release_gate_field", "artifact_resolution_key"):
            if not str(row.get(field) or ""):
                failures.append(f"missing_artifact_resolution_field:{widget_id}:{field}")
        if row.get("source_artifact_resolution_preflight_ready") is not True:
            failures.append(f"artifact_resolution_preflight_not_ready:{widget_id}")
        if row.get("artifact_ref_field_present") is not True:
            failures.append(f"artifact_ref_field_missing:{widget_id}")
        if row.get("source_packet_id_present") is not True:
            failures.append(f"source_packet_id_missing:{widget_id}")
        for key in (
            "source_artifact_resolution_allowed",
            "source_artifact_resolved",
            "source_artifact_path_materialized",
            "source_artifact_exists_checked",
            "source_artifact_schema_checked",
            "actual_source_bound",
            "actual_source_read_allowed",
            "d_hot_actual_read_allowed",
            "freshness_checked_against_d_hot",
            "real_widget_render_ready",
            "render_allowed",
            "refresh_invocation_allowed",
            "runtime_artifact_write_allowed",
            "status_artifact_write_allowed",
            "confidence_increase_allowed",
            "parameter_apply_allowed",
            "parameter_staging_write_allowed",
            "ledger_append_allowed",
            "autotrade_trigger_allowed",
            "broker_private_api_allowed",
        ):
            if row.get(key) is not False:
                failures.append(f"false_boundary_not_false:{widget_id}:{key}")
    unique_resolution_keys = sorted({str(row.get("artifact_resolution_key") or "") for row in rows})
    unique_source_packet_ids = sorted({str(row.get("source_packet_id") or "") for row in rows})
    return {
        "ok": not failures,
        "panel_version": PREDICTION_WARROOM_SOURCE_ARTIFACT_RESOLUTION_PREFLIGHT_PANEL_VERSION,
        "source_readiness_panel_version": PREDICTION_WARROOM_SOURCE_READINESS_PREFLIGHT_PANEL_VERSION,
        "source_artifact_resolution_preflight_state": "artifact_ref_fields_ready_resolution_deferred",
        "artifact_resolution_row_count": len(rows),
        "unique_artifact_resolution_key_count": len(unique_resolution_keys),
        "unique_artifact_resolution_keys": unique_resolution_keys,
        "unique_source_packet_count": len(unique_source_packet_ids),
        "unique_source_packet_ids": unique_source_packet_ids,
        "artifact_resolution_rows": rows,
        "validation_failures": failures,
        "read_only": True,
        "non_executing": True,
        "source_artifact_resolution_preflight_only": True,
        "source_artifact_resolution_preflight_ready": not failures,
        "source_artifact_resolution_allowed": False,
        "source_artifact_resolved": False,
        "source_artifact_path_materialized": False,
        "source_artifact_exists_checked": False,
        "source_artifact_schema_checked": False,
        "actual_source_bound": False,
        "actual_source_read_allowed": False,
        "d_hot_actual_read_allowed": False,
        "freshness_checked_against_d_hot": False,
        "real_prediction_widget_rendering_allowed": False,
        "warroom_widget_rendering_allowed": False,
        "warroom_page_mutation_allowed": False,
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
