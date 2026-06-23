# path: ./btcts_next/src/btcts/apps/operator_ui/components/prediction_widgets/_shared.py
# desc: Shared pure-data builder for PS-Q17S read-only Prediction WarRoom widget skeletons. No Streamlit import, no file IO, no D-hot read, no refresh, no writes.

from __future__ import annotations

from typing import Any, Mapping

PREDICTION_WARROOM_WIDGET_COMPONENT_SKELETON_VERSION = "prediction_warroom_widget_component_skeleton.ps_q17s.v1"
REQUIRED_COMPONENT_PROPS = (
    "widget_family_id",
    "source_packet_id",
    "mount_zone_id",
    "mount_slot_id",
    "source_generated_at",
    "source_artifact_ref",
    "release_gate_state",
    "fallback_reason_codes",
    "operator_summary_ja",
    "read_only",
)


def _as_mapping(value: Any) -> Mapping[str, Any]:
    if hasattr(value, "to_dict"):
        converted = value.to_dict()
        return converted if isinstance(converted, Mapping) else {}
    return value if isinstance(value, Mapping) else {}


def _as_reason_codes(value: Any) -> list[str]:
    if isinstance(value, (list, tuple)):
        return [str(item) for item in value]
    if value:
        return [str(value)]
    return []


def default_skeleton_props(*, widget_family_id: str, source_packet_id: str, mount_zone_id: str, mount_slot_id: str) -> dict[str, Any]:
    return {
        "widget_family_id": widget_family_id,
        "source_packet_id": source_packet_id,
        "mount_zone_id": mount_zone_id,
        "mount_slot_id": mount_slot_id,
        "source_generated_at": "",
        "source_artifact_ref": "",
        "release_gate_state": "render_disabled_until_future_source_preflight",
        "fallback_reason_codes": ["ps_q17s_component_skeleton_render_disabled", "actual_source_not_bound"],
        "operator_summary_ja": f"{widget_family_id} は PS-Q17S の read-only skeleton です。まだ WarRoom 表示・実読込・更新は行いません。",
        "read_only": True,
    }


def build_read_only_prediction_widget_skeleton_packet(
    *,
    widget_family_id: str,
    source_packet_id: str,
    mount_zone_id: str,
    mount_slot_id: str,
    component_module_path: str,
    component_function_name: str,
    props: Mapping[str, Any] | Any | None = None,
) -> dict[str, Any]:
    supplied = dict(_as_mapping(props)) if props is not None else {}
    base_props = default_skeleton_props(
        widget_family_id=widget_family_id,
        source_packet_id=source_packet_id,
        mount_zone_id=mount_zone_id,
        mount_slot_id=mount_slot_id,
    )
    merged = {**base_props, **supplied}
    missing_props = [field for field in REQUIRED_COMPONENT_PROPS if field not in merged]
    fallback_reason_codes = _as_reason_codes(merged.get("fallback_reason_codes"))
    if missing_props:
        fallback_reason_codes.extend(f"missing_prop:{field}" for field in missing_props)
    return {
        "component_version": PREDICTION_WARROOM_WIDGET_COMPONENT_SKELETON_VERSION,
        "component_state": "read_only_component_skeleton_render_disabled",
        "widget_family_id": widget_family_id,
        "source_packet_id": str(merged.get("source_packet_id") or source_packet_id),
        "mount_zone_id": str(merged.get("mount_zone_id") or mount_zone_id),
        "mount_slot_id": str(merged.get("mount_slot_id") or mount_slot_id),
        "component_module_path": component_module_path,
        "component_function_name": component_function_name,
        "props_contract_fields": list(REQUIRED_COMPONENT_PROPS),
        "missing_props": missing_props,
        "fallback_reason_codes": fallback_reason_codes,
        "operator_summary_ja": str(merged.get("operator_summary_ja") or ""),
        "source_generated_at": str(merged.get("source_generated_at") or ""),
        "source_artifact_ref": str(merged.get("source_artifact_ref") or ""),
        "release_gate_state": str(merged.get("release_gate_state") or "render_disabled_until_future_source_preflight"),
        "read_only": True,
        "non_executing": True,
        "component_skeleton_only": True,
        "fallback_component_only": True,
        "display_packet_only": True,
        "warroom_page_mutation_allowed": False,
        "warroom_page_import_patch_allowed": False,
        "warroom_mount_patch_allowed": False,
        "component_import_allowed_by_warroom_page": False,
        "streamlit_render_allowed": False,
        "streamlit_render_invoked": False,
        "actual_source_read_allowed": False,
        "actual_source_read_attempted": False,
        "d_hot_actual_read_allowed": False,
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
