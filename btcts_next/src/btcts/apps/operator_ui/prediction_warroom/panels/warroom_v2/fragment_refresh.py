# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/warroom_v2/fragment_refresh.py
# desc: WarRoom v2 Streamlit fragment refresh helper. No WebSocket/SSE/server push or execution behavior.

from __future__ import annotations

from typing import Any, Callable

import streamlit as st

WARROOM_V2_FRAGMENT_REFRESH_VERSION = "prediction_warroom.v2.fragment_refresh.ps_q29y.v1"


def fragment_interval_sec_from_ms(interval_ms: int | float | None) -> int:
    try:
        ms = int(interval_ms or 0)
    except Exception:
        ms = 0
    return max(1, int(round(ms / 1000.0))) if ms else 2


def build_warroom_v2_fragment_refresh_packet(*, refresh_packet: dict[str, Any] | None = None) -> dict[str, Any]:
    packet = dict(refresh_packet or {})
    enabled = bool(packet.get("auto_refresh_enabled"))
    interval_sec = fragment_interval_sec_from_ms(packet.get("interval_ms"))
    fragment_supported = callable(getattr(st, "fragment", None))
    return {
        "ok": True,
        "fragment_refresh_version": WARROOM_V2_FRAGMENT_REFRESH_VERSION,
        "effective_transport_kind": "streamlit_fragment_polling",
        "fragment_refresh_available": fragment_supported,
        "fragment_refresh_enabled": bool(enabled and fragment_supported),
        "page_reload_enabled": False,
        "browser_timer_reload_enabled": False,
        "interval_sec": interval_sec,
        "refresh_targets": ["market_snapshot_strip", "chart_review_panel"],
        "runtime_connected": False,
        "push_connected": False,
        "websocket_enabled": False,
        "sse_enabled": False,
        "scheduler_enabled": False,
        "producer_enabled": False,
        "read_only": True,
        "display_only": True,
        "would_send_to_broker": False,
    }


def render_warroom_v2_fragment_refresh_block(
    *,
    label: str,
    render_body: Callable[[], None],
    refresh_packet: dict[str, Any] | None = None,
) -> dict[str, Any]:
    packet = build_warroom_v2_fragment_refresh_packet(refresh_packet=refresh_packet)
    if not packet["fragment_refresh_enabled"]:
        render_body()
        return packet

    fragment = getattr(st, "fragment")

    @fragment(run_every=f"{int(packet['interval_sec'])}s")
    def _fragment_runner() -> None:
        render_body()

    _fragment_runner()
    packet["fragment_label"] = label
    return packet
