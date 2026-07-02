# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/warroom_v2/debug_preview.py
# desc: Collapsed debug renderer for WarRoom v2 shell preview metadata.

from __future__ import annotations

from typing import Any

import streamlit as st

WARROOM_V2_DEBUG_PREVIEW_RENDERER_VERSION = "prediction_warroom.v2.debug_preview_renderer.ps_q29d.v1"


def render_warroom_v2_debug_preview(packet: dict[str, Any], shell: dict[str, Any]) -> None:
    with st.expander("Debug / raw preview packet", expanded=False):
        st.json({
            "panel_version": packet["panel_version"],
            "shell_preview_version": shell["shell_preview_version"],
            "widget_update_unit": shell["widget_update_unit"],
            "runtime_connected": shell["runtime_connected"],
            "push_connected": shell["push_connected"],
        })
