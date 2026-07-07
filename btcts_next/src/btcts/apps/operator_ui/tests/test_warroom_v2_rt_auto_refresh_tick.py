# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_rt_auto_refresh_tick.py
# desc: Verifies WarRoom v2 realtime cockpit auto-refresh tick is sidebar-driven, fragment-based, and safe.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

REPO_ROOT = Path(__file__).resolve().parents[6]
PAGE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/warroom_v2_page.py"
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_WARROOM_V2_RT_AUTO_REFRESH_TICK_2026-07-05.md"
AUTO_REFRESH = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/rt_ui/auto_refresh_tick_view.py"

from btcts.apps.operator_ui.prediction_warroom.v2.rt_ui.auto_refresh_tick_view import build_cockpit_auto_refresh_packet, fragment_run_every, render_cockpit_auto_refresh_tick  # noqa: E402


class FakeStreamlit:
    def __init__(self) -> None:
        self.captions: list[str] = []

    def caption(self, value: object) -> None:
        self.captions.append(str(value))


def test_auto_refresh_packet_uses_sidebar_state_and_no_action_boundary() -> None:
    packet = build_cockpit_auto_refresh_packet({"ui_auto_refresh": True, "ui_refresh_interval": 3})
    assert packet["auto_refresh_enabled"] is True
    assert packet["interval_ms"] == 3000
    assert packet["fragment_run_every"] == "3s"
    assert packet["transport_kind"] == "streamlit_section_fragment_refresh"
    assert packet["page_reload_enabled"] is False
    assert packet["fragment_refresh_enabled"] is True
    assert packet["section_fragment_refresh_enabled"] is True
    assert packet["websocket_send_enabled"] is False
    assert packet["broker_send_enabled"] is False
    assert packet["order_intent_submitted"] is False
    assert packet["prediction_invoked"] is False
    assert packet["classifier_invoked"] is False


def test_fragment_run_every_is_bounded_and_no_browser_reload_timer_remains() -> None:
    assert fragment_run_every({"auto_refresh_enabled": True, "interval_ms": 3000}) == "3s"
    assert fragment_run_every({"auto_refresh_enabled": False, "interval_ms": 3000}) is None
    assert fragment_run_every({"auto_refresh_enabled": True, "interval_ms": 100}) == "1s"

    source = AUTO_REFRESH.read_text(encoding="utf-8-sig")
    assert "def _timer_html" not in source
    assert "window.parent.location.reload" not in source
    assert "streamlit_section_fragment_refresh" in source
    forbidden = ["fetch(", "new WebSocket", ".send(", "broker_private"]
    assert not any(token in source for token in forbidden)
    assert "order_intent_submitted" in source
    assert "broker_send_enabled" in source
    assert "prediction_invoked" in source


def test_render_cockpit_auto_refresh_tick_is_diagnostics_only_and_safe() -> None:
    fake = FakeStreamlit()
    packet = build_cockpit_auto_refresh_packet({"ui_auto_refresh": True, "ui_refresh_interval": 3})
    result = render_cockpit_auto_refresh_tick(packet, fake)
    assert result["auto_refresh_tick_rendered"] is True
    assert result["page_reload_enabled"] is False
    assert result["section_fragment_refresh_enabled"] is True
    assert result["read_only"] is True
    assert fake.captions
    assert "cockpit_auto_refresh=on" in fake.captions[0]
    assert "page_reload_enabled=false" in fake.captions[0]
    assert "broker_send_enabled=false" in fake.captions[0]
    assert "prediction_invoked=false" in fake.captions[0]


def test_warroom_page_mounts_auto_refresh_tick_and_doc_markers() -> None:
    page = PAGE.read_text(encoding="utf-8-sig")
    assert "build_cockpit_auto_refresh_packet" in page
    assert "render_cockpit_auto_refresh_tick" in page
    assert "auto_refresh_packet" in page
    assert "fragment_run_every(auto_refresh_packet)" in page
    doc = DOC.read_text(encoding="utf-8-sig")
    assert "warroom_v2_rt_auto_refresh_tick_done=true" in doc
