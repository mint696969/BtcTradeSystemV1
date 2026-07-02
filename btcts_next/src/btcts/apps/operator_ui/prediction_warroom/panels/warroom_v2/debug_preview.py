# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/warroom_v2/debug_preview.py
# desc: Compact debug renderer for WarRoom v2 shell preview metadata. Display-only; no live data ownership.

from __future__ import annotations

from typing import Any

import streamlit as st

WARROOM_V2_DEBUG_PREVIEW_RENDERER_VERSION = "prediction_warroom.v2.debug_preview_renderer.ps_q29n.v1"


def _shell_read_models(shell: dict[str, Any]) -> list[dict[str, Any]]:
    placeholders = dict(shell.get("placeholder_read_models") or {})
    return list(placeholders.get("read_models") or shell.get("read_models") or [])


def build_warroom_v2_debug_preview_packet(packet: dict[str, Any], shell: dict[str, Any]) -> dict[str, Any]:
    models = _shell_read_models(shell)
    zones: dict[str, int] = {}
    for model in models:
        zone = str(dict(model.get("payload", {})).get("zone", "unknown"))
        zones[zone] = zones.get(zone, 0) + 1
    return {
        "ok": True,
        "renderer_version": WARROOM_V2_DEBUG_PREVIEW_RENDERER_VERSION,
        "compact_debug_preview": True,
        "expanded_by_default": False,
        "display_only": True,
        "placeholder_only": True,
        "panel_version": packet.get("panel_version", ""),
        "shell_preview_version": shell.get("shell_preview_version", ""),
        "widget_update_unit": shell.get("widget_update_unit", "widget"),
        "model_count": len(models),
        "zones": zones,
        "runtime_connected": False,
        "push_connected": False,
        "would_send_to_broker": False,
    }


def render_warroom_v2_debug_preview(packet: dict[str, Any], shell: dict[str, Any]) -> dict[str, Any]:
    preview = build_warroom_v2_debug_preview_packet(packet, shell)
    with st.expander("Debug / compact preview", expanded=False):
        st.caption("placeholder-only / display-only / no runtime or push connection")
        st.json({
            "renderer_version": preview["renderer_version"],
            "panel_version": preview["panel_version"],
            "shell_preview_version": preview["shell_preview_version"],
            "widget_update_unit": preview["widget_update_unit"],
            "model_count": preview["model_count"],
            "zones": preview["zones"],
            "runtime_connected": preview["runtime_connected"],
            "push_connected": preview["push_connected"],
        })
    return preview
