# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/rt_ui/auto_refresh_tick_view.py
# desc: WarRoom v2 cockpit auto-refresh metadata. Sidebar-driven Streamlit fragment refresh; page reload disabled.

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Mapping

DEFAULT_INTERVAL_MS = 3000
MIN_INTERVAL_MS = 1000
MAX_INTERVAL_MS = 60000


def _bounded_interval(value: object) -> int:
    try:
        raw = int(value or DEFAULT_INTERVAL_MS)
    except Exception:
        raw = DEFAULT_INTERVAL_MS
    return max(MIN_INTERVAL_MS, min(MAX_INTERVAL_MS, raw))


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def fragment_run_every(packet: Mapping[str, Any]) -> str | None:
    if not bool(packet.get("auto_refresh_enabled")):
        return None
    interval_ms = _bounded_interval(packet.get("interval_ms"))
    return f"{max(1, int(interval_ms / 1000))}s"


def build_cockpit_auto_refresh_packet(session_state: Mapping[str, Any]) -> dict[str, Any]:
    enabled = bool(session_state.get("ui_auto_refresh", False))
    try:
        interval_sec = int(session_state.get("ui_refresh_interval", DEFAULT_INTERVAL_MS // 1000) or 0)
    except Exception:
        interval_sec = DEFAULT_INTERVAL_MS // 1000
    interval_ms = _bounded_interval(interval_sec * 1000)
    return {
        "ok": True,
        "packet_kind": "warroom_v2_rt_cockpit_auto_refresh_tick_packet",
        "auto_refresh_enabled": enabled,
        "interval_ms": interval_ms,
        "fragment_run_every": f"{max(1, int(interval_ms / 1000))}s" if enabled else None,
        "source": "operator_sidebar",
        "transport_kind": "streamlit_fragment_refresh",
        "target": "warroom_v2_realtime_cockpit_body",
        "last_rendered_at": _now_iso(),
        "page_reload_enabled": False,
        "fragment_refresh_enabled": enabled,
        "read_only": True,
        "websocket_send_enabled": False,
        "broker_send_enabled": False,
        "order_intent_submitted": False,
        "prediction_invoked": False,
        "classifier_invoked": False,
    }


def render_cockpit_auto_refresh_tick(packet: Mapping[str, Any], st_api: Any) -> dict[str, Any]:
    enabled = bool(packet.get("auto_refresh_enabled"))
    interval_ms = _bounded_interval(packet.get("interval_ms"))
    st_api.caption(
        " / ".join(
            [
                f"cockpit_auto_refresh={'on' if enabled else 'off'}",
                f"interval_ms={interval_ms}",
                "transport=streamlit_fragment_refresh",
                "page_reload_enabled=false",
                "broker_send_enabled=false",
                "prediction_invoked=false",
            ]
        )
    )
    return {"ok": True, "auto_refresh_tick_rendered": True, "auto_refresh_enabled": enabled, "interval_ms": interval_ms, "page_reload_enabled": False, "fragment_refresh_enabled": enabled, "read_only": True}
