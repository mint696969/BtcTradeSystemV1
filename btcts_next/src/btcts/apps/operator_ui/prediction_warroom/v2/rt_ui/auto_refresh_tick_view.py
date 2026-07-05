# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/rt_ui/auto_refresh_tick_view.py
# desc: WarRoom v2 cockpit auto-refresh tick. Uses sidebar refresh settings to trigger a safe browser rerun/reload for live observation.

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Mapping

import streamlit.components.v1 as components

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
        "source": "operator_sidebar",
        "transport_kind": "browser_timer_reload",
        "target": "warroom_v2_realtime_cockpit",
        "last_rendered_at": _now_iso(),
        "page_reload_enabled": enabled,
        "read_only": True,
        "websocket_send_enabled": False,
        "broker_send_enabled": False,
        "order_intent_submitted": False,
        "prediction_invoked": False,
        "classifier_invoked": False,
    }


def _timer_html(interval_ms: int) -> str:
    # Reload only the browser page. No network send, broker action, order action, prediction, or classifier invocation is performed.
    return f"""
<script>
(function() {{
  const intervalMs = {int(interval_ms)};
  const key = 'warroom_v2_rt_cockpit_auto_refresh_last_reload_ms';
  const now = Date.now();
  const last = Number(window.sessionStorage.getItem(key) || '0');
  const wait = Math.max(250, intervalMs - Math.max(0, now - last));
  window.setTimeout(function() {{
    window.sessionStorage.setItem(key, String(Date.now()));
    window.parent.location.reload();
  }}, wait);
}})();
</script>
"""


def render_cockpit_auto_refresh_tick(packet: Mapping[str, Any], st_api: Any) -> dict[str, Any]:
    enabled = bool(packet.get("auto_refresh_enabled"))
    interval_ms = _bounded_interval(packet.get("interval_ms"))
    if enabled:
        components.html(_timer_html(interval_ms), height=0)
    st_api.caption(
        " / ".join(
            [
                f"cockpit_auto_refresh={'on' if enabled else 'off'}",
                f"interval_ms={interval_ms}",
                "transport=browser_timer_reload",
                "broker_send_enabled=false",
                "prediction_invoked=false",
            ]
        )
    )
    return {"ok": True, "auto_refresh_tick_rendered": True, "auto_refresh_enabled": enabled, "interval_ms": interval_ms, "page_reload_enabled": enabled, "read_only": True}
