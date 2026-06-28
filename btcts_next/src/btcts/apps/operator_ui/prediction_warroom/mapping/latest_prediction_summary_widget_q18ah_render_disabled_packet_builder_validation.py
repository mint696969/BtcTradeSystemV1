# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/mapping/latest_prediction_summary_widget_q18ah_render_disabled_packet_builder_validation.py
# desc: PS-Q18AH retired render-disabled packet builder validation for legacy latest_prediction_summary_widget mapped props. Kept no-render/no-refresh/no-write after PS-Q23J manifest-first display default.

from __future__ import annotations

from typing import Any, Mapping

from btcts.apps.operator_ui.components.prediction_widgets._shared import (
    PREDICTION_WARROOM_WIDGET_COMPONENT_SKELETON_VERSION,
    REQUIRED_COMPONENT_PROPS,
)
from btcts.apps.operator_ui.components.prediction_widgets.latest_prediction_summary_widget import (
    COMPONENT_FUNCTION_NAME,
    COMPONENT_MODULE_PATH,
    MOUNT_SLOT_ID,
    MOUNT_ZONE_ID,
    SOURCE_PACKET_ID,
    WIDGET_FAMILY_ID,
    render_latest_prediction_summary_widget,
)
from btcts.apps.operator_ui.prediction_warroom.mapping.latest_prediction_summary_widget_q18ag_payload_to_props_mapping_preflight import (
    LATEST_PREDICTION_SUMMARY_WIDGET_Q18AG_PAYLOAD_TO_PROPS_MAPPING_PREFLIGHT_ACK,
    LATEST_PREDICTION_SUMMARY_WIDGET_Q18AG_PAYLOAD_TO_PROPS_MAPPING_PREFLIGHT_VERSION,
    build_latest_prediction_summary_widget_q18ag_payload_to_props_mapping_preflight_packet,
)

LATEST_PREDICTION_SUMMARY_WIDGET_Q18AH_RENDER_DISABLED_PACKET_BUILDER_VALIDATION_VERSION = "prediction_warroom.latest_prediction_summary_widget.q18ah_render_disabled_packet_builder_validation.v1"
LATEST_PREDICTION_SUMMARY_WIDGET_Q18AH_RENDER_DISABLED_PACKET_BUILDER_VALIDATION_ACK = "PS_Q18AH_VALIDATE_RENDER_DISABLED_PACKET_BUILDER_ONLY"
LATEST_PREDICTION_SUMMARY_WIDGET_Q18AH_RENDER_DISABLED_PACKET_BUILDER_VALIDATION_STATE = "render_disabled_component_skeleton_packet_valid_no_streamlit_no_refresh"

TRUE_BOUNDARIES = (
    "read_only",
    "non_executing",
    "display_only",
    "render_disabled_packet_builder_validation_only",
    "q18ag_payload_to_props_mapping_consumed",
    "props_contract_complete",
    "props_candidate_supplied_to_packet_builder",
    "render_disabled_packet_builder_invoked",
    "component_skeleton_packet_built",
    "component_packet_valid",
    "mapped_values_visible_in_component_packet",
    "component_packet_render_disabled",
)

FALSE_BOUNDARIES = (
    "actual_source_read_allowed",
    "actual_source_read_invoked",
    "payload_reparse_allowed",
    "component_runtime_binding_allowed",
    "component_props_bound_to_runtime",
    "real_prediction_widget_rendering_allowed",
    "real_prediction_widget_render_invoked",
    "streamlit_render_allowed",
    "streamlit_render_invoked",
    "warroom_page_mutation_allowed",
    "warroom_mount_patch_allowed",
    "refresh_invocation_allowed",
    "scheduler_enabled",
    "runtime_artifact_write_allowed",
    "status_artifact_write_allowed",
    "parameter_apply_allowed",
    "parameter_staging_write_allowed",
    "approval_or_authorization_allowed",
    "ledger_append_allowed",
    "autotrade_trigger_allowed",
    "broker_private_api_allowed",
    "would_write_runtime_artifact",
    "would_send_to_broker",
)


def _as_mapping(value: Any) -> Mapping[str, Any]:
    if hasattr(value, "to_dict"):
        converted = value.to_dict()
        return converted if isinstance(converted, Mapping) else {}
    return value if isinstance(value, Mapping) else {}


def _clean(value: Any) -> str:
    return "" if value is None else str(value)


def build_latest_prediction_summary_widget_q18ah_render_disabled_packet_builder_validation_packet(
    *,
    supplied_q18ag_payload_to_props_mapping_packet: Mapping[str, Any] | Any | None = None,
    execute_packet_builder_validation: bool = False,
    explicit_ack: str = "",
) -> dict[str, Any]:
    mapping = _as_mapping(supplied_q18ag_payload_to_props_mapping_packet)
    if not mapping:
        mapping = build_latest_prediction_summary_widget_q18ag_payload_to_props_mapping_preflight_packet(
            execute_mapping_preflight=True,
            explicit_ack=LATEST_PREDICTION_SUMMARY_WIDGET_Q18AG_PAYLOAD_TO_PROPS_MAPPING_PREFLIGHT_ACK,
        )
    failures: list[str] = []
    component_failures: list[str] = []
    props_candidate = _as_mapping(mapping.get("props_candidate"))
    component_packet: dict[str, Any] = {}
    packet_builder_invoked = False
    execution_allowed = bool(execute_packet_builder_validation and explicit_ack == LATEST_PREDICTION_SUMMARY_WIDGET_Q18AH_RENDER_DISABLED_PACKET_BUILDER_VALIDATION_ACK)

    if mapping.get("mapping_preflight_version") != LATEST_PREDICTION_SUMMARY_WIDGET_Q18AG_PAYLOAD_TO_PROPS_MAPPING_PREFLIGHT_VERSION:
        failures.append("q18ag_mapping_preflight_version_mismatch")
    if mapping.get("ok") is not True:
        failures.append("q18ag_mapping_packet_not_ok")
    if mapping.get("props_contract_complete") is not True:
        failures.append("q18ag_props_contract_not_complete")
    if not props_candidate:
        failures.append("props_candidate_missing")
    for field in REQUIRED_COMPONENT_PROPS:
        if field not in props_candidate:
            failures.append(f"props_candidate_missing_required_component_prop:{field}")
    if not execute_packet_builder_validation:
        failures.append("execute_packet_builder_validation_false")
    if explicit_ack != LATEST_PREDICTION_SUMMARY_WIDGET_Q18AH_RENDER_DISABLED_PACKET_BUILDER_VALIDATION_ACK:
        failures.append("explicit_ack_missing_or_mismatch")

    if execution_allowed and not failures:
        packet_builder_invoked = True
        component_packet = render_latest_prediction_summary_widget(props=props_candidate)
        expected = {
            "component_version": PREDICTION_WARROOM_WIDGET_COMPONENT_SKELETON_VERSION,
            "component_state": "read_only_component_skeleton_render_disabled",
            "widget_family_id": WIDGET_FAMILY_ID,
            "source_packet_id": SOURCE_PACKET_ID,
            "mount_zone_id": MOUNT_ZONE_ID,
            "mount_slot_id": MOUNT_SLOT_ID,
            "component_module_path": COMPONENT_MODULE_PATH,
            "component_function_name": COMPONENT_FUNCTION_NAME,
            "source_generated_at": _clean(mapping.get("mapped_generated_at")),
            "source_artifact_ref": "hot://prediction/latest_manifest.json",
        }
        for key, value in expected.items():
            if component_packet.get(key) != value:
                component_failures.append(f"component_{key}_mismatch")
        if component_packet.get("missing_props") != []:
            component_failures.append("component_missing_props_present")
        for key in ("read_only", "non_executing", "component_skeleton_only", "fallback_component_only", "display_packet_only"):
            if component_packet.get(key) is not True:
                component_failures.append(f"component_true_boundary_missing:{key}")
        for key in (
            "warroom_page_mutation_allowed",
            "warroom_page_import_patch_allowed",
            "warroom_mount_patch_allowed",
            "component_import_allowed_by_warroom_page",
            "streamlit_render_allowed",
            "streamlit_render_invoked",
            "actual_source_read_allowed",
            "actual_source_read_attempted",
            "d_hot_actual_read_allowed",
            "refresh_invocation_allowed",
            "scheduler_enabled",
            "runtime_artifact_write_allowed",
            "status_artifact_write_allowed",
            "confidence_increase_allowed",
            "parameter_apply_allowed",
            "parameter_staging_write_allowed",
            "approval_or_authorization_allowed",
            "ledger_append_allowed",
            "autotrade_trigger_allowed",
            "broker_private_api_allowed",
            "would_write_runtime_artifact",
            "would_write_collector_state",
            "would_send_to_broker",
        ):
            if component_packet.get(key) is not False:
                component_failures.append(f"component_false_boundary_not_false:{key}")
    failures.extend(component_failures)
    ok = bool(execution_allowed and packet_builder_invoked and component_packet and not failures)
    packet: dict[str, Any] = {
        "ok": ok,
        "validation_version": LATEST_PREDICTION_SUMMARY_WIDGET_Q18AH_RENDER_DISABLED_PACKET_BUILDER_VALIDATION_VERSION,
        "validation_ack": LATEST_PREDICTION_SUMMARY_WIDGET_Q18AH_RENDER_DISABLED_PACKET_BUILDER_VALIDATION_ACK,
        "source_mapping_preflight_version": LATEST_PREDICTION_SUMMARY_WIDGET_Q18AG_PAYLOAD_TO_PROPS_MAPPING_PREFLIGHT_VERSION,
        "component_skeleton_version": PREDICTION_WARROOM_WIDGET_COMPONENT_SKELETON_VERSION,
        "validation_state": LATEST_PREDICTION_SUMMARY_WIDGET_Q18AH_RENDER_DISABLED_PACKET_BUILDER_VALIDATION_STATE if ok else "render_disabled_packet_builder_validation_blocked",
        "widget_family_id": WIDGET_FAMILY_ID,
        "source_packet_id": SOURCE_PACKET_ID,
        "mount_zone_id": MOUNT_ZONE_ID,
        "mount_slot_id": MOUNT_SLOT_ID,
        "component_module_path": COMPONENT_MODULE_PATH,
        "component_function_name": COMPONENT_FUNCTION_NAME,
        "mapped_generated_at": _clean(mapping.get("mapped_generated_at")),
        "mapped_record_count": int(mapping.get("record_count") or 0),
        "mapped_first_record_family": _clean(mapping.get("mapped_first_record_family")),
        "mapped_first_record_horizon_sec": _clean(mapping.get("mapped_first_record_horizon_sec")),
        "mapped_first_record_primary_label": _clean(mapping.get("mapped_first_record_primary_label")),
        "mapped_first_record_score": _clean(mapping.get("mapped_first_record_score")),
        "props_contract_complete": mapping.get("props_contract_complete") is True,
        "props_candidate_supplied_to_packet_builder": bool(props_candidate and execution_allowed),
        "render_disabled_packet_builder_invoked": packet_builder_invoked,
        "component_skeleton_packet_built": bool(component_packet),
        "component_packet_valid": bool(component_packet and not component_failures),
        "component_packet_render_disabled": component_packet.get("component_state") == "read_only_component_skeleton_render_disabled" if component_packet else False,
        "mapped_values_visible_in_component_packet": bool(component_packet and component_packet.get("source_generated_at") == _clean(mapping.get("mapped_generated_at"))),
        "component_packet_state": _clean(component_packet.get("component_state")) if component_packet else "",
        "component_source_generated_at": _clean(component_packet.get("source_generated_at")) if component_packet else "",
        "component_source_artifact_ref": _clean(component_packet.get("source_artifact_ref")) if component_packet else "",
        "component_missing_props": list(component_packet.get("missing_props") or []) if component_packet else [],
        "component_packet": component_packet,
        "validation_failures": failures,
        "recommended_next_slice": "WarRoom render-disabled packet status/value panel mount with no refresh, or bounded auto-refresh preflight if mounting is already adequate.",
        "human_interpretation": "PS-Q18AH passes the mapped props candidate through the read-only skeleton packet builder and verifies the resulting render-disabled component packet. It does not perform Streamlit rendering, component runtime binding, WarRoom mount patching, refresh, writes, AutoTrade, or broker calls.",
    }
    packet.update({key: ok for key in TRUE_BOUNDARIES})
    packet.update({key: False for key in FALSE_BOUNDARIES})
    packet["read_only"] = True
    packet["non_executing"] = True
    packet["display_only"] = True
    packet["render_disabled_packet_builder_validation_only"] = True
    packet["q18ag_payload_to_props_mapping_consumed"] = mapping.get("ok") is True
    packet["props_contract_complete"] = mapping.get("props_contract_complete") is True
    return packet
