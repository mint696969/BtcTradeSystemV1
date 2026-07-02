# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/warroom_v2/auto_refresh_control.py
# desc: WarRoom v2 browser-timer auto refresh control. Reads sidebar UI state; no WebSocket/SSE/push transport.

from __future__ import annotations

from typing import Any

import streamlit as st
import streamlit.components.v1 as components

WARROOM_V2_AUTO_REFRESH_CONTROL_RENDERER_VERSION = "prediction_warroom.v2.auto_refresh_control.ps_q29w.v1"
DEFAULT_INTERVAL_MS = 2000
MIN_INTERVAL_MS = 1000
MAX_INTERVAL_MS = 60000


def _bounded_interval(value: int | float | None) -> int:
    try:
        raw = int(value or DEFAULT_INTERVAL_MS)
    except Exception:
        raw = DEFAULT_INTERVAL_MS
    return max(MIN_INTERVAL_MS, min(MAX_INTERVAL_MS, raw))


def sidebar_auto_refresh_settings(*, session_state: Any | None = None) -> dict[str, Any]:
    state = st.session_state if session_state is None else session_state
    enabled = bool(state.get("ui_auto_refresh", False))
    try:
        interval_sec = int(state.get("ui_refresh_interval", DEFAULT_INTERVAL_MS // 1000) or 0)
    except Exception:
        interval_sec = DEFAULT_INTERVAL_MS // 1000
    return {"enabled": enabled, "interval_ms": _bounded_interval(interval_sec * 1000), "source": "operator_sidebar"}


def build_warroom_v2_auto_refresh_control_packet(
    *,
    enabled: bool = False,
    interval_ms: int = DEFAULT_INTERVAL_MS,
    source: str = "local_default",
) -> dict[str, Any]:
    bounded = _bounded_interval(interval_ms)
    return {
        "ok": True,
        "renderer_version": WARROOM_V2_AUTO_REFRESH_CONTROL_RENDERER_VERSION,
        "placement": "below_top_bar_above_market_snapshot",
        "transport_kind": "browser_timer_polling",
        "auto_refresh_available": True,
        "auto_refresh_enabled": bool(enabled),
        "auto_refresh_enabled_default": False,
        "auto_refresh_source": source,
        "sidebar_auto_refresh_consumed": source == "operator_sidebar",
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
    settings = sidebar_auto_refresh_settings()
    packet = build_warroom_v2_auto_refresh_control_packet(
        enabled=bool(settings["enabled"]),
        interval_ms=int(settings["interval_ms"]),
        source=str(settings["source"]),
    )
    with st.expander("Auto refresh / 高頻度更新", expanded=False):
        st.caption("Uses the left sidebar Widget Auto Refresh setting / browser timer polling only")
        c1, c2, c3 = st.columns(3)
        c1.metric("Sidebar", "ON" if packet["auto_refresh_enabled"] else "OFF")
        c2.metric("Interval", f"{int(packet['interval_ms'] / 1000)}s")
        c3.metric("Transport", "browser timer")
        st.caption("push_connected=false / websocket=false / sse=false / would_send_to_broker=false")
    if packet["auto_refresh_enabled"]:
        _inject_browser_timer(int(packet["interval_ms"]))
    return packet
