# path: ./btcts_next/src/btcts/apps/operator_ui/views/warroom_v2_page.py
# desc: Thin WarRoom v2 page shell. Renders shell preview only; no D-hot, classifier, push, or execution behavior.

from __future__ import annotations

import streamlit as st

from btcts.apps.operator_ui.prediction_warroom.panels.warroom_v2_shell_preview_panel import (
    render_warroom_v2_shell_preview_panel,
)

WARROOM_V2_PAGE_SHELL_MOUNT_VERSION = "prediction_warroom.v2.page_shell_mount.ps_q29c.v1"


def build_warroom_v2_page_mount_packet() -> dict:
    return {
        "ok": True,
        "page_shell_mount_version": WARROOM_V2_PAGE_SHELL_MOUNT_VERSION,
        "page_key": "warroom_v2",
        "page_label": "WarRoom v2",
        "legacy_warroom_retained": True,
        "legacy_warroom_route_removed": False,
        "thin_page_shell_only": True,
        "renders_shell_preview_panel": True,
        "runtime_connected": False,
        "push_connected": False,
        "websocket_enabled": False,
        "sse_enabled": False,
        "dhot_read_in_page": False,
        "classifier_invoked_in_page": False,
        "cache_invalidation_in_page": False,
        "scheduler_enabled": False,
        "producer_enabled": False,
        "autotrade_trigger_allowed": False,
        "broker_private_api_allowed": False,
        "ledger_append_allowed": False,
        "mode_apply_allowed": False,
        "parameter_apply_allowed": False,
        "would_send_to_broker": False,
    }


def render():
    packet = build_warroom_v2_page_mount_packet()
    st.header("WarRoom v2 / Prediction Room")
    st.caption(
        "Preview shell only. Widget read models are placeholders; live data and push transport are not connected."
    )
    render_warroom_v2_shell_preview_panel(page_mount_packet=packet)
