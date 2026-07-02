# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/warroom_v2/auto_refresh_control.py
# desc: WarRoom v2 browser-timer auto refresh control. No WebSocket/SSE/push transport or execution behavior.

from __future__ import annotations

from typing import Any

import streamlit as st
import streamlit.components.v1 as components

WARROOM_V2_AUTO_REFRESH_CONTROL_RENDERER_VERSION = "prediction_warroom.v2.auto_refresh_control.ps_q29t.v1"
DEFAULT_INTERVAL_MS = 2000
MIN_INTERVAL_MS = 1000
MAX_INTERVAL_MS = 60000


def _bounded_interval(value: int | float | None) -> int:
    try:
        raw = int(value or DEFAULT_INTERVAL_MS)
    except Exception:
        raw = DEFAULT_INTERVAL_MS
    return max(MIN_INTERVAL_MS, min(MAX_INTERVAL_MS, raw))


def build_warroom_v2_auto_refresh_control_packet(*, enabled: bool = False, interval_ms: int = DEFAULT_INTERVAL_MS) -> dict[str, Any]:
    bounded = _bounded_interval(interval_ms)
    return {
        "ok": True,
        "renderer_version": WARROOM_V2_AUTO_REFRESH_CONTROL_RENDERER_VERSION,
        "placement": "below_top_bar_above_market_snapshot",
        "transport_kind": "browser_timer_polling",
        "auto_refresh_available": True,
        "auto_refresh_enabled": bool(enabled),
        "auto_refresh_enabled_default": False,
        "interval_ms": bounded,
        "min_interval_ms": MIN_INTERVAL_MS,
        "max_interval_ms": MAX_INTERVAL_MS,
        "refresh_targets": ["market_snapshot_strip", "prediction_cards", "chart_review_panel"],
        "push_ready": True,
        "auto_refresh_ready": True,
        "runtime_connected": False,
        "push_connected": False,
        "websocket_enabled": False,
        "sse_enabled": False,
        "scheduler_enabled": False,
        "producer_enabled": False,
        "display_only": True,
        "read_only": True,
        "would_send_to_broker": False,
    }


def _inject_browser_timer(interval_ms: int) -> None:
    components.html(
        f"""
        <script>
        const intervalMs = {int(interval_ms)};
        window.setTimeout(function() {{ window.parent.location.reload(); }}, intervalMs);
        </script>
        """,
        height=0,
    )


def render_warroom_v2_auto_refresh_control() -> dict[str, Any]:
    with st.expander("Auto refresh / 高頻度更新", expanded=False):
        enabled = st.checkbox("Enable browser-timer auto refresh", value=False, key="warroom_v2_auto_refresh_enabled")
        interval_ms = st.number_input(
            "Refresh interval ms",
            min_value=MIN_INTERVAL_MS,
            max_value=MAX_INTERVAL_MS,
            value=DEFAULT_INTERVAL_MS,
            step=500,
            key="warroom_v2_auto_refresh_interval_ms",
        )
        packet = build_warroom_v2_auto_refresh_control_packet(enabled=bool(enabled), interval_ms=int(interval_ms))
        st.caption("browser timer polling only / push_connected=false / websocket=false / sse=false")
        if packet["auto_refresh_enabled"]:
            _inject_browser_timer(int(packet["interval_ms"]))
        return packet
