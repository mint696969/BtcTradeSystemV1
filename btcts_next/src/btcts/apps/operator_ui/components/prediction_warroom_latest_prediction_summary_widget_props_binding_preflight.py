# path: ./btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_latest_prediction_summary_widget_props_binding_preflight.py
# desc: PS-Q18E pure-data props binding preflight for latest_prediction_summary_widget. Builds a contract-complete props candidate from supplied Q18D schema probe only; no widget render, no actual source read, no payload reparse, no D-hot discovery, no writes.

from __future__ import annotations

from typing import Any, Mapping

from btcts.apps.operator_ui.components.prediction_widgets._shared import REQUIRED_COMPONENT_PROPS
from btcts.apps.operator_ui.components.prediction_widgets.latest_prediction_summary_widget import MOUNT_SLOT_ID, MOUNT_ZONE_ID, SOURCE_PACKET_ID, WIDGET_FAMILY_ID, build_latest_prediction_summary_widget_props
from btcts.apps.operator_ui.components.prediction_warroom_latest_prediction_summary_widget_schema_probe import LATEST_PREDICTION_SUMMARY_WIDGET_SCHEMA_PROBE_VERSION, REQUIRED_SUMMARY_SCHEMA_KEYS

LATEST_PREDICTION_SUMMARY_WIDGET_PROPS_BINDING_PREFLIGHT_VERSION = "prediction_warroom_latest_prediction_summary_widget_props_binding_preflight.ps_q18e.v1"


def _as_mapping(value: Any) -> Mapping[str, Any]:
    if hasattr(value, "to_dict"):
        converted = value.to_dict()
        return converted if isinstance(converted, Mapping) else {}
    return value if isinstance(value, Mapping) else {}


def build_latest_prediction_summary_widget_props_candidate(*, supplied_schema_probe_packet: Mapping[str, Any] | Any | None = None) -> dict[str, Any]:
    packet = _as_mapping(supplied_schema_probe_packet)
    schema_ready = packet.get("ok") is True and packet.get("schema_specific_probe_ready") is True
    missing_keys = [str(item) for item in (packet.get("missing_required_schema_keys") or [])]
    fallback_reasons = [] if schema_ready and not missing_keys else ["ps_q18e_schema_probe_not_ready"]
    fallback_reasons.extend(f"missing_schema_key:{key}" for key in missing_keys)
    candidate = build_latest_prediction_summary_widget_props(
        {
            "widget_family_id": WIDGET_FAMILY_ID,
            "source_packet_id": SOURCE_PACKET_ID,
            "mount_zone_id": MOUNT_ZONE_ID,
            "mount_slot_id": MOUNT_SLOT_ID,
            "source_generated_at": "schema_verified_value_not_bound",
            "source_artifact_ref": "schema_verified_value_not_bound",
            "release_gate_state": "props_binding_preflight_only_render_disabled",
            "fallback_reason_codes": fallback_reasons or ["ps_q18e_props_candidate_not_bound_to_widget"],
            "operator_summary_ja": "latest_prediction_summary_widget props 候補は schema probe に基づく preflight です。実値 binding / render / refresh はまだ行いません。",
            "read_only": True,
            "schema_probe_version": str(packet.get("probe_version") or ""),
            "schema_required_keys": list(REQUIRED_SUMMARY_SCHEMA_KEYS),
            "schema_probe_row_count": int(packet.get("schema_probe_row_count") or 0),
            "props_binding_preflight_only": True,
            "props_value_binding_deferred": True,
            "real_payload_values_bound": False,
        }
    )
    return candidate


def build_latest_prediction_summary_widget_props_binding_preflight_packet(*, supplied_schema_probe_packet: Mapping[str, Any] | Any | None = None) -> dict[str, Any]:
    packet = _as_mapping(supplied_schema_probe_packet)
    candidate = build_latest_prediction_summary_widget_props_candidate(supplied_schema_probe_packet=packet)
    candidate_keys = set(candidate)
    missing_props = [field for field in REQUIRED_COMPONENT_PROPS if field not in candidate_keys]
    failures: list[str] = []
    if packet.get("probe_version") != LATEST_PREDICTION_SUMMARY_WIDGET_SCHEMA_PROBE_VERSION:
        failures.append("schema_probe_version_mismatch")
    if packet.get("ok") is not True:
        failures.append("schema_probe_packet_not_ok")
    if packet.get("widget_family_id") != WIDGET_FAMILY_ID:
        failures.append("widget_family_id_mismatch")
    if packet.get("source_packet_id") != SOURCE_PACKET_ID:
        failures.append("source_packet_id_mismatch")
    if packet.get("schema_specific_probe_ready") is not True:
        failures.append("schema_specific_probe_not_ready")
    if packet.get("missing_required_schema_keys") != []:
        failures.append("schema_probe_has_missing_required_keys")
    if missing_props:
        failures.extend(f"missing_required_component_prop:{field}" for field in missing_props)
    if candidate.get("read_only") is not True:
        failures.append("candidate_not_read_only")
    ok = not failures
    return {
        "ok": ok,
        "preflight_version": LATEST_PREDICTION_SUMMARY_WIDGET_PROPS_BINDING_PREFLIGHT_VERSION,
        "source_schema_probe_version": LATEST_PREDICTION_SUMMARY_WIDGET_SCHEMA_PROBE_VERSION,
        "widget_family_id": WIDGET_FAMILY_ID,
        "source_packet_id": SOURCE_PACKET_ID,
        "mount_zone_id": MOUNT_ZONE_ID,
        "mount_slot_id": MOUNT_SLOT_ID,
        "props_binding_preflight_state": "latest_prediction_summary_widget_props_candidate_ready_render_deferred" if ok else "latest_prediction_summary_widget_props_candidate_blocked",
        "props_candidate": candidate,
        "props_candidate_key_count": len(candidate_keys),
        "required_component_props": list(REQUIRED_COMPONENT_PROPS),
        "missing_required_component_props": missing_props,
        "schema_required_keys": list(REQUIRED_SUMMARY_SCHEMA_KEYS),
        "schema_probe_row_count": int(packet.get("schema_probe_row_count") or 0),
        "missing_required_schema_keys": list(packet.get("missing_required_schema_keys") or []) if packet else [],
        "validation_failures": failures,
        "read_only": True,
        "non_executing": True,
        "latest_prediction_summary_widget_props_binding_preflight_only": True,
        "props_candidate_ready": ok,
        "props_contract_complete": not missing_props,
        "props_value_binding_deferred": True,
        "real_payload_values_bound": False,
        "widget_props_binding_allowed": False,
        "widget_props_bound_to_component": False,
        "render_invocation_allowed": False,
        "real_prediction_widget_rendering_allowed": False,
        "actual_source_read_invoked_by_props_preflight": False,
        "actual_source_read_allowed_by_props_preflight": False,
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
