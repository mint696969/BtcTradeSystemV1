# path: ./btcts_next/src/btcts/apps/operator_ui/components/prediction_widgets/warning_blocker_widget.py
# desc: PS-Q17S read-only skeleton for warning_blocker_widget. Pure data only; no Streamlit import, no D-hot read, no refresh, no writes, no WarRoom page mutation.

from __future__ import annotations

from typing import Any, Mapping

from ._shared import build_read_only_prediction_widget_skeleton_packet, default_skeleton_props

WIDGET_FAMILY_ID = "warning_blocker_widget"
SOURCE_PACKET_ID = "tier0_source_quality_gate_packet"
MOUNT_ZONE_ID = "prediction_overview_zone"
MOUNT_SLOT_ID = "warning_blocker_widget_slot"
COMPONENT_MODULE_PATH = "btcts.apps.operator_ui.components.prediction_widgets.warning_blocker_widget"
COMPONENT_FUNCTION_NAME = "render_warning_blocker_widget"


def build_warning_blocker_widget_props(props: Mapping[str, Any] | Any | None = None) -> dict[str, Any]:
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


def render_warning_blocker_widget(props: Mapping[str, Any] | Any | None = None) -> dict[str, Any]:
    return build_read_only_prediction_widget_skeleton_packet(
        widget_family_id=WIDGET_FAMILY_ID,
        source_packet_id=SOURCE_PACKET_ID,
        mount_zone_id=MOUNT_ZONE_ID,
        mount_slot_id=MOUNT_SLOT_ID,
        component_module_path=COMPONENT_MODULE_PATH,
        component_function_name=COMPONENT_FUNCTION_NAME,
        props=build_warning_blocker_widget_props(props),
    )
