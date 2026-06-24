# path: ./btcts_next/src/btcts/apps/operator_ui/components/prediction_widgets/latest_prediction_summary_widget.py
# desc: PS-Q17S read-only skeleton for latest_prediction_summary_widget. Pure data only; no Streamlit import, no D-hot read, no refresh, no writes, no WarRoom page mutation.

from __future__ import annotations

from typing import Any, Mapping

from ._shared import build_read_only_prediction_widget_skeleton_packet, default_skeleton_props

WIDGET_FAMILY_ID = "latest_prediction_summary_widget"
SOURCE_PACKET_ID = "latest_prediction_source_review_packet"
MOUNT_ZONE_ID = "prediction_overview_zone"
MOUNT_SLOT_ID = "latest_prediction_summary_widget_slot"
COMPONENT_MODULE_PATH = "btcts.apps.operator_ui.components.prediction_widgets.latest_prediction_summary_widget"
COMPONENT_FUNCTION_NAME = "render_latest_prediction_summary_widget"


def build_latest_prediction_summary_widget_props(props: Mapping[str, Any] | Any | None = None) -> dict[str, Any]:
    base = default_skeleton_props(
        widget_family_id=WIDGET_FAMILY_ID,
        source_packet_id=SOURCE_PACKET_ID,
        mount_zone_id=MOUNT_ZONE_ID,
        mount_slot_id=MOUNT_SLOT_ID,
    )
    if props is None:
        return base
    if hasattr(props, "to_dict"):
        converted = props.to_dict()
        extra = converted if isinstance(converted, Mapping) else {}
    else:
        extra = props if isinstance(props, Mapping) else {}
    return {**base, **dict(extra)}


def render_latest_prediction_summary_widget(props: Mapping[str, Any] | Any | None = None) -> dict[str, Any]:
    return build_read_only_prediction_widget_skeleton_packet(
        widget_family_id=WIDGET_FAMILY_ID,
        source_packet_id=SOURCE_PACKET_ID,
        mount_zone_id=MOUNT_ZONE_ID,
        mount_slot_id=MOUNT_SLOT_ID,
        component_module_path=COMPONENT_MODULE_PATH,
        component_function_name=COMPONENT_FUNCTION_NAME,
        props=build_latest_prediction_summary_widget_props(props),
    )


REAL_RENDER_PROTOTYPE_GATE_STATE = "still_disabled_real_render_prototype_blocked"
REAL_RENDER_PROTOTYPE_REQUIRED_FLAGS = (
    "requested_enable_real_render",
    "implementation_gate_open",
    "manual_ui_review_passed",
    "rollback_plan_ready",
)
REAL_RENDER_PROTOTYPE_FALSE_BOUNDARIES = (
    "real_prediction_widget_rendering_allowed",
    "real_prediction_widget_render_invoked",
    "streamlit_real_widget_render_invoked",
    "component_runtime_binding_allowed",
    "component_props_bound_to_runtime",
    "runtime_artifact_write_allowed",
    "status_artifact_write_allowed",
    "parameter_apply_allowed",
    "parameter_staging_write_allowed",
    "ledger_append_allowed",
    "autotrade_trigger_allowed",
    "broker_private_api_allowed",
    "would_send_to_broker",
)


def _flag(value: Any) -> bool:
    return bool(value)


def build_latest_prediction_summary_widget_real_render_prototype_packet(
    props: Mapping[str, Any] | Any | None = None,
    *,
    requested_enable_real_render: bool = False,
    implementation_gate_open: bool = False,
    manual_ui_review_passed: bool = False,
    rollback_plan_ready: bool = False,
) -> dict[str, Any]:
    """Return a still-disabled real-render prototype contract packet.

    PS-Q18AS intentionally keeps rendering disabled even when flags are supplied.
    A later implementation gate must replace this blocked prototype after review.
    """
    skeleton = render_latest_prediction_summary_widget(props)
    flags = {
        "requested_enable_real_render": _flag(requested_enable_real_render),
        "implementation_gate_open": _flag(implementation_gate_open),
        "manual_ui_review_passed": _flag(manual_ui_review_passed),
        "rollback_plan_ready": _flag(rollback_plan_ready),
    }
    blockers = ["ps_q18as_still_disabled_prototype_only"]
    if flags["requested_enable_real_render"]:
        blockers.append("real_render_request_seen_but_blocked_by_ps_q18as")
    if not flags["implementation_gate_open"]:
        blockers.append("implementation_gate_not_open")
    if not flags["manual_ui_review_passed"]:
        blockers.append("manual_ui_review_not_passed")
    if not flags["rollback_plan_ready"]:
        blockers.append("rollback_plan_not_ready")
    blockers.append("separate_future_implementation_gate_required")
    packet: dict[str, Any] = {
        "ok": True,
        "prototype_version": "prediction_warroom.latest_prediction_summary_widget.q18as_still_disabled_real_render_prototype.v1",
        "prototype_state": REAL_RENDER_PROTOTYPE_GATE_STATE,
        "source_widget": "btcts_next/src/btcts/apps/operator_ui/components/prediction_widgets/latest_prediction_summary_widget.py",
        "widget_family_id": WIDGET_FAMILY_ID,
        "current_render_function": COMPONENT_FUNCTION_NAME,
        "current_render_function_behavior": "returns_read_only_skeleton_packet",
        "skeleton_component_state": skeleton.get("component_state"),
        "skeleton_packet_preserved": skeleton.get("component_state") == "read_only_component_skeleton_render_disabled",
        "required_flags": list(REAL_RENDER_PROTOTYPE_REQUIRED_FLAGS),
        "flags": flags,
        "prototype_blockers": blockers,
        "prototype_blocker_count": len(blockers),
        "rollback_target": "read_only_component_skeleton_render_disabled",
        "rollback_action": "use render_latest_prediction_summary_widget skeleton packet path",
        "manual_ui_review_required_before_enablement": True,
        "future_implementation_gate_required": True,
        "real_rendering_enabled": False,
        "streamlit_import_required_by_this_slice": False,
        "streamlit_import_present_by_this_slice": False,
        "component_runtime_binding_enabled": False,
        "operator_summary_ja": "PS-Q18AS は latest_prediction_summary_widget の real-render prototype contract だけを追加します。実レンダリングはまだ無効です。",
        "recommended_next_slice": "implementation-gate review packet or WarRoom observation cleanup; keep real rendering disabled until explicitly approved",
    }
    packet.update({key: False for key in REAL_RENDER_PROTOTYPE_FALSE_BOUNDARIES})
    return packet
