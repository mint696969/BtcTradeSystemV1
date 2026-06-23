# path: ./btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_latest_prediction_summary_widget_render_disabled_packet_validation.py
# desc: PS-Q18G pure-data validation for latest_prediction_summary_widget render-disabled skeleton packet. Supplies Q18E props candidate to the render-disabled packet builder only; no Streamlit render, no source read, no D-hot discovery, no refresh, no writes.

from __future__ import annotations

from typing import Any, Mapping

from btcts.apps.operator_ui.components.prediction_widgets._shared import PREDICTION_WARROOM_WIDGET_COMPONENT_SKELETON_VERSION, REQUIRED_COMPONENT_PROPS
from btcts.apps.operator_ui.components.prediction_widgets.latest_prediction_summary_widget import COMPONENT_FUNCTION_NAME, COMPONENT_MODULE_PATH, MOUNT_SLOT_ID, MOUNT_ZONE_ID, SOURCE_PACKET_ID, WIDGET_FAMILY_ID, render_latest_prediction_summary_widget
from btcts.apps.operator_ui.components.prediction_warroom_latest_prediction_summary_widget_props_binding_preflight import LATEST_PREDICTION_SUMMARY_WIDGET_PROPS_BINDING_PREFLIGHT_VERSION

LATEST_PREDICTION_SUMMARY_WIDGET_RENDER_DISABLED_PACKET_VALIDATION_VERSION = "prediction_warroom_latest_prediction_summary_widget_render_disabled_packet_validation.ps_q18g.v1"


def _as_mapping(value: Any) -> Mapping[str, Any]:
    if hasattr(value, "to_dict"):
        converted = value.to_dict()
        return converted if isinstance(converted, Mapping) else {}
    return value if isinstance(value, Mapping) else {}


def _safe_list(value: Any) -> list[str]:
    if isinstance(value, (list, tuple)):
        return [str(item) for item in value]
    if value:
        return [str(value)]
    return []


def build_latest_prediction_summary_widget_render_disabled_packet_validation(*, supplied_props_preflight_packet: Mapping[str, Any] | Any | None = None) -> dict[str, Any]:
    preflight = _as_mapping(supplied_props_preflight_packet)
    candidate = _as_mapping(preflight.get("props_candidate"))
    failures: list[str] = []
    component_packet: dict[str, Any] = {}
    packet_builder_invoked = False

    if preflight.get("preflight_version") != LATEST_PREDICTION_SUMMARY_WIDGET_PROPS_BINDING_PREFLIGHT_VERSION:
        failures.append("props_preflight_version_mismatch")
    if preflight.get("ok") is not True:
        failures.append("props_preflight_packet_not_ok")
    if preflight.get("props_candidate_ready") is not True:
        failures.append("props_candidate_not_ready")
    if preflight.get("props_contract_complete") is not True:
        failures.append("props_contract_not_complete")
    if preflight.get("missing_required_component_props") != []:
        failures.append("missing_required_component_props_present")
    for field in REQUIRED_COMPONENT_PROPS:
        if field not in candidate:
            failures.append(f"candidate_missing_required_component_prop:{field}")
    if not failures:
        packet_builder_invoked = True
        component_packet = render_latest_prediction_summary_widget(props=candidate)

    component_failures: list[str] = []
    if packet_builder_invoked:
        if component_packet.get("component_version") != PREDICTION_WARROOM_WIDGET_COMPONENT_SKELETON_VERSION:
            component_failures.append("component_version_mismatch")
        if component_packet.get("component_state") != "read_only_component_skeleton_render_disabled":
            component_failures.append("component_state_not_render_disabled")
        expected = {
            "widget_family_id": WIDGET_FAMILY_ID,
            "source_packet_id": SOURCE_PACKET_ID,
            "mount_zone_id": MOUNT_ZONE_ID,
            "mount_slot_id": MOUNT_SLOT_ID,
            "component_module_path": COMPONENT_MODULE_PATH,
            "component_function_name": COMPONENT_FUNCTION_NAME,
        }
        for key, value in expected.items():
            if component_packet.get(key) != value:
                component_failures.append(f"component_{key}_mismatch")
        if component_packet.get("missing_props") != []:
            component_failures.append("component_missing_props_present")
        if component_packet.get("source_generated_at") != "schema_verified_value_not_bound":
            component_failures.append("component_source_generated_at_should_remain_placeholder")
        if component_packet.get("source_artifact_ref") != "schema_verified_value_not_bound":
            component_failures.append("component_source_artifact_ref_should_remain_placeholder")
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
    ok = not failures and packet_builder_invoked
    return {
        "ok": ok,
        "validation_version": LATEST_PREDICTION_SUMMARY_WIDGET_RENDER_DISABLED_PACKET_VALIDATION_VERSION,
        "source_preflight_version": LATEST_PREDICTION_SUMMARY_WIDGET_PROPS_BINDING_PREFLIGHT_VERSION,
        "component_skeleton_version": PREDICTION_WARROOM_WIDGET_COMPONENT_SKELETON_VERSION,
        "widget_family_id": WIDGET_FAMILY_ID,
        "source_packet_id": SOURCE_PACKET_ID,
        "mount_zone_id": MOUNT_ZONE_ID,
        "mount_slot_id": MOUNT_SLOT_ID,
        "component_module_path": COMPONENT_MODULE_PATH,
        "component_function_name": COMPONENT_FUNCTION_NAME,
        "validation_state": "latest_prediction_summary_widget_render_disabled_packet_valid" if ok else "latest_prediction_summary_widget_render_disabled_packet_blocked",
        "component_packet_builder_invoked": packet_builder_invoked,
        "component_packet_valid": bool(packet_builder_invoked and not component_failures),
        "component_packet_state": str(component_packet.get("component_state") or ""),
        "component_missing_props": list(component_packet.get("missing_props") or []) if component_packet else [],
        "component_fallback_reason_codes": _safe_list(component_packet.get("fallback_reason_codes")) if component_packet else [],
        "component_source_generated_at": str(component_packet.get("source_generated_at") or "") if component_packet else "",
        "component_source_artifact_ref": str(component_packet.get("source_artifact_ref") or "") if component_packet else "",
        "validation_failures": failures,
        "component_packet": component_packet,
        "read_only": True,
        "non_executing": True,
        "latest_prediction_summary_widget_render_disabled_packet_validation_only": True,
        "render_disabled_component_packet_validation_only": True,
        "component_skeleton_packet_only": True,
        "props_candidate_supplied_to_packet_builder": packet_builder_invoked,
        "props_value_binding_deferred": True,
        "real_payload_values_bound": False,
        "streamlit_render_allowed": False,
        "streamlit_render_invoked": False,
        "real_prediction_widget_rendering_allowed": False,
        "component_runtime_binding_allowed": False,
        "warroom_page_mutation_allowed": False,
        "warroom_widget_rendering_allowed": False,
        "warroom_ui_trigger_enabled": False,
        "actual_source_read_invoked_by_validation": False,
        "actual_source_read_allowed_by_validation": False,
        "payload_reparse_allowed": False,
        "source_discovery_allowed": False,
        "d_hot_directory_scan_allowed": False,
        "d_hot_actual_read_allowed": False,
        "freshness_checked_against_d_hot": False,
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
