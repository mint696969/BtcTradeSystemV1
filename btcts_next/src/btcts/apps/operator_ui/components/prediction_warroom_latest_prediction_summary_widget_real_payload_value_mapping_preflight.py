# path: ./btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_latest_prediction_summary_widget_real_payload_value_mapping_preflight.py
# desc: PS-Q18I pure-data real decoded-payload value mapping preflight for latest_prediction_summary_widget. Uses supplied decoded payload only; no file read, no D-hot discovery, no component bind, no widget render, no refresh, no writes.

from __future__ import annotations

from typing import Any, Mapping

from btcts.apps.operator_ui.components.prediction_widgets._shared import REQUIRED_COMPONENT_PROPS
from btcts.apps.operator_ui.components.prediction_widgets.latest_prediction_summary_widget import MOUNT_SLOT_ID, MOUNT_ZONE_ID, SOURCE_PACKET_ID, WIDGET_FAMILY_ID, build_latest_prediction_summary_widget_props
from btcts.apps.operator_ui.components.prediction_warroom_latest_prediction_summary_widget_props_binding_preflight import LATEST_PREDICTION_SUMMARY_WIDGET_PROPS_BINDING_PREFLIGHT_VERSION

LATEST_PREDICTION_SUMMARY_WIDGET_REAL_PAYLOAD_VALUE_MAPPING_PREFLIGHT_VERSION = "prediction_warroom_latest_prediction_summary_widget_real_payload_value_mapping_preflight.ps_q18i.v1"
REQUIRED_REAL_PAYLOAD_VALUE_KEYS = (
    "prediction_run_id",
    "generated_at",
    "market_uid",
    "source_artifact_ref",
)


def _as_mapping(value: Any) -> Mapping[str, Any]:
    if hasattr(value, "to_dict"):
        converted = value.to_dict()
        return converted if isinstance(converted, Mapping) else {}
    return value if isinstance(value, Mapping) else {}


def _clean_text(value: Any) -> str:
    if value is None:
        return ""
    return str(value)


def build_latest_prediction_summary_widget_real_payload_value_mapping_candidate(
    *,
    supplied_props_preflight_packet: Mapping[str, Any] | Any | None = None,
    supplied_decoded_payload: Mapping[str, Any] | Any | None = None,
) -> dict[str, Any]:
    preflight = _as_mapping(supplied_props_preflight_packet)
    payload = _as_mapping(supplied_decoded_payload)
    base_candidate = _as_mapping(preflight.get("props_candidate"))
    prediction_run_id = _clean_text(payload.get("prediction_run_id"))
    generated_at = _clean_text(payload.get("generated_at"))
    market_uid = _clean_text(payload.get("market_uid"))
    source_artifact_ref = _clean_text(payload.get("source_artifact_ref"))
    fallback_reasons = list(base_candidate.get("fallback_reason_codes") or [])
    fallback_reasons.append("ps_q18i_real_payload_values_mapped_render_still_disabled")
    return build_latest_prediction_summary_widget_props(
        {
            **dict(base_candidate),
            "widget_family_id": WIDGET_FAMILY_ID,
            "source_packet_id": SOURCE_PACKET_ID,
            "mount_zone_id": MOUNT_ZONE_ID,
            "mount_slot_id": MOUNT_SLOT_ID,
            "source_generated_at": generated_at,
            "source_artifact_ref": source_artifact_ref,
            "release_gate_state": "real_payload_value_mapping_preflight_only_render_disabled",
            "fallback_reason_codes": fallback_reasons,
            "operator_summary_ja": f"latest_prediction_summary_widget real payload value mapping preflight: run={prediction_run_id} / market={market_uid} / generated_at={generated_at}。実 widget render / refresh / write はまだ行いません。",
            "read_only": True,
            "prediction_run_id": prediction_run_id,
            "generated_at": generated_at,
            "market_uid": market_uid,
            "real_payload_value_mapping_preflight_only": True,
            "props_value_binding_deferred": False,
            "real_payload_values_bound_to_props_candidate": True,
            "real_widget_rendering_deferred": True,
        }
    )


def build_latest_prediction_summary_widget_real_payload_value_mapping_preflight_packet(
    *,
    supplied_props_preflight_packet: Mapping[str, Any] | Any | None = None,
    supplied_decoded_payload: Mapping[str, Any] | Any | None = None,
) -> dict[str, Any]:
    preflight = _as_mapping(supplied_props_preflight_packet)
    payload = _as_mapping(supplied_decoded_payload)
    mapped_candidate = build_latest_prediction_summary_widget_real_payload_value_mapping_candidate(
        supplied_props_preflight_packet=preflight,
        supplied_decoded_payload=payload,
    )
    failures: list[str] = []
    missing_payload_keys = [key for key in REQUIRED_REAL_PAYLOAD_VALUE_KEYS if key not in payload or payload.get(key) in (None, "")]
    missing_component_props = [field for field in REQUIRED_COMPONENT_PROPS if field not in mapped_candidate]
    if preflight.get("preflight_version") != LATEST_PREDICTION_SUMMARY_WIDGET_PROPS_BINDING_PREFLIGHT_VERSION:
        failures.append("props_preflight_version_mismatch")
    if preflight.get("ok") is not True:
        failures.append("props_preflight_packet_not_ok")
    if preflight.get("props_candidate_ready") is not True:
        failures.append("props_candidate_not_ready")
    if preflight.get("props_contract_complete") is not True:
        failures.append("props_contract_not_complete")
    if preflight.get("missing_required_component_props") != []:
        failures.append("source_preflight_missing_required_component_props_present")
    if not payload:
        failures.append("decoded_payload_missing")
    failures.extend(f"missing_required_payload_value:{key}" for key in missing_payload_keys)
    failures.extend(f"mapped_candidate_missing_required_component_prop:{field}" for field in missing_component_props)
    if mapped_candidate.get("source_generated_at") != _clean_text(payload.get("generated_at")):
        failures.append("generated_at_not_mapped_to_source_generated_at")
    if mapped_candidate.get("source_artifact_ref") != _clean_text(payload.get("source_artifact_ref")):
        failures.append("source_artifact_ref_not_mapped")
    if mapped_candidate.get("read_only") is not True:
        failures.append("mapped_candidate_not_read_only")
    ok = not failures
    return {
        "ok": ok,
        "mapping_preflight_version": LATEST_PREDICTION_SUMMARY_WIDGET_REAL_PAYLOAD_VALUE_MAPPING_PREFLIGHT_VERSION,
        "source_preflight_version": LATEST_PREDICTION_SUMMARY_WIDGET_PROPS_BINDING_PREFLIGHT_VERSION,
        "widget_family_id": WIDGET_FAMILY_ID,
        "source_packet_id": SOURCE_PACKET_ID,
        "mount_zone_id": MOUNT_ZONE_ID,
        "mount_slot_id": MOUNT_SLOT_ID,
        "mapping_state": "latest_prediction_summary_widget_real_payload_values_mapped_render_deferred" if ok else "latest_prediction_summary_widget_real_payload_value_mapping_blocked",
        "required_real_payload_value_keys": list(REQUIRED_REAL_PAYLOAD_VALUE_KEYS),
        "missing_required_payload_value_keys": missing_payload_keys,
        "required_component_props": list(REQUIRED_COMPONENT_PROPS),
        "missing_required_component_props": missing_component_props,
        "mapped_props_candidate": mapped_candidate,
        "mapped_props_candidate_key_count": len(set(mapped_candidate)),
        "mapped_prediction_run_id": mapped_candidate.get("prediction_run_id"),
        "mapped_market_uid": mapped_candidate.get("market_uid"),
        "mapped_source_generated_at": mapped_candidate.get("source_generated_at"),
        "mapped_source_artifact_ref": mapped_candidate.get("source_artifact_ref"),
        "validation_failures": failures,
        "read_only": True,
        "non_executing": True,
        "latest_prediction_summary_widget_real_payload_value_mapping_preflight_only": True,
        "decoded_payload_supplied": bool(payload),
        "decoded_payload_values_mapped_to_props_candidate": ok,
        "props_contract_complete": not missing_component_props,
        "props_value_binding_deferred": False if ok else True,
        "real_payload_values_bound_to_props_candidate": ok,
        "real_payload_values_bound_to_component": False,
        "component_props_binding_allowed": False,
        "component_props_bound_to_component": False,
        "component_runtime_binding_allowed": False,
        "streamlit_render_allowed": False,
        "streamlit_render_invoked": False,
        "render_invocation_allowed": False,
        "real_prediction_widget_rendering_allowed": False,
        "actual_source_read_invoked_by_mapping": False,
        "actual_source_read_allowed_by_mapping": False,
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
        "signal_reliability_claim_allowed": False,
        "parameter_candidate_reliability_claim_allowed": False,
        "parameter_tuning_allowed": False,
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
