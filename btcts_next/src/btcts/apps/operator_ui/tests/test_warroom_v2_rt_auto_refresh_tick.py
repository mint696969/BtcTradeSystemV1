# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_rt_auto_refresh_tick.py
# desc: Verifies WarRoom v2 realtime cockpit auto-refresh tick is sidebar-driven and safe.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

REPO_ROOT = Path(__file__).resolve().parents[6]
PAGE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/warroom_v2_page.py"
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_WARROOM_V2_RT_AUTO_REFRESH_TICK_2026-07-05.md"

from btcts.apps.operator_ui.prediction_warroom.v2.rt_ui.auto_refresh_tick_view import build_cockpit_auto_refresh_packet, _timer_html  # noqa: E402


def test_auto_refresh_packet_uses_sidebar_state_and_no_action_boundary() -> None:
    packet = build_cockpit_auto_refresh_packet({"ui_auto_refresh": True, "ui_refresh_interval": 3})
    assert packet["auto_refresh_enabled"] is True
    assert packet["interval_ms"] == 3000
    assert packet["page_reload_enabled"] is True
    assert packet["websocket_send_enabled"] is False
    assert packet["broker_send_enabled"] is False
    assert packet["order_intent_submitted"] is False
    assert packet["prediction_invoked"] is False
    assert packet["classifier_invoked"] is False


def test_timer_html_is_browser_reload_only() -> None:
    html = _timer_html(3000)
    assert "window.parent.location.reload" in html
    assert "sessionStorage" in html
    forbidden = ["fetch(", "WebSocket", "send(", "broker", "order", "prediction", "classifier"]
    assert not any(token in html for token in forbidden)


def test_warroom_page_mounts_auto_refresh_tick_and_doc_markers() -> None:
    page = PAGE.read_text(encoding="utf-8-sig")
    assert "build_cockpit_auto_refresh_packet" in page
    assert "render_cockpit_auto_refresh_tick" in page
    assert "auto_refresh_packet" in page
    doc = DOC.read_text(encoding="utf-8-sig")
    assert "warroom_v2_rt_auto_refresh_tick_done=true" in doc
    assert "sidebar_auto_refresh_drives_cockpit_reload=true" in doc
