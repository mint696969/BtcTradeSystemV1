# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/shell_preview.py
# desc: WarRoom v2 shell preview packet builder. Contract-only; not mounted into the Operator UI yet.

from __future__ import annotations

from typing import Any

from .layout_policy import build_warroom_v2_layout_policy
from .placeholder_read_models import build_warroom_v2_placeholder_read_models_packet
from .safety import warroom_v2_safety_flags
from .topics import build_warroom_v2_widget_topic_catalog

WARROOM_V2_SHELL_PREVIEW_VERSION = "prediction_warroom.v2.shell_preview.ps_q29b.v1"


def _group_widget_ids_by_zone(widgets: list[dict[str, Any]]) -> dict[str, list[str]]:
    zones: dict[str, list[str]] = {}
    for row in widgets:
        zones.setdefault(str(row["zone"]), []).append(str(row["widget_id"]))
    return zones


def build_warroom_v2_shell_preview_packet(*, generated_at: str = "") -> dict[str, Any]:
    layout = build_warroom_v2_layout_policy()
    topic_catalog = build_warroom_v2_widget_topic_catalog()
    placeholders = build_warroom_v2_placeholder_read_models_packet(generated_at=generated_at)
    widgets = list(layout["widgets"])
    zones = _group_widget_ids_by_zone(widgets)
    packet: dict[str, Any] = {
        "ok": True,
        "shell_preview_version": WARROOM_V2_SHELL_PREVIEW_VERSION,
        "generated_at": generated_at,
        "warroom_v2_shell_preview_only": True,
        "warroom_v2_page_added": False,
        "warroom_v2_route_added": False,
        "warroom_legacy_retained_as_reference": True,
        "app_navigation_changed": False,
        "legacy_warroom_page_changed": False,
        "layout": layout,
        "topic_catalog": topic_catalog,
        "placeholder_read_models": placeholders,
        "zones": zones,
        "top_zone_widget_ids": zones.get("top", []),
        "prediction_card_widget_ids": zones.get("prediction_cards", []),
        "scenario_widget_ids": zones.get("scenario", []),
        "prediction_cards_before_scenario": True,
        "debug_default_collapsed": bool(layout.get("debug_default_collapsed")),
        "widget_update_unit": "topic",
        "runtime_connected": False,
        "push_connected": False,
        "websocket_enabled": False,
        "sse_enabled": False,
        "page_owns_artifact_scanning": False,
        "page_owns_cache_invalidation": False,
        "page_owns_classifier_invocation": False,
        "page_owns_transport_source": False,
        "streamlit_required": False,
    }
    packet.update(warroom_v2_safety_flags())
    return packet
