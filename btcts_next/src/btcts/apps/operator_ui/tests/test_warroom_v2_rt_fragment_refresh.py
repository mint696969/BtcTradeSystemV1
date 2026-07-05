# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_rt_fragment_refresh.py
# desc: Verifies WarRoom v2 cockpit uses Streamlit fragment refresh instead of browser page reload.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

REPO_ROOT = Path(__file__).resolve().parents[6]
PAGE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/warroom_v2_page.py"
AUTO = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/rt_ui/auto_refresh_tick_view.py"
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_WARROOM_V2_RT_FRAGMENT_REFRESH_2026-07-05.md"

from btcts.apps.operator_ui.prediction_warroom.v2.rt_ui.auto_refresh_tick_view import build_cockpit_auto_refresh_packet, fragment_run_every  # noqa: E402
from btcts.apps.operator_ui.views.warroom_v2_page import build_warroom_v2_page_mount_packet  # noqa: E402


def test_auto_refresh_packet_uses_fragment_not_page_reload() -> None:
    packet = build_cockpit_auto_refresh_packet({"ui_auto_refresh": True, "ui_refresh_interval": 3})
    assert packet["transport_kind"] == "streamlit_fragment_refresh"
    assert packet["fragment_refresh_enabled"] is True
    assert packet["page_reload_enabled"] is False
    assert "browser_timer_reload_enabled" not in packet
    assert fragment_run_every(packet) == "3s"


def test_page_mounts_fragment_body_and_has_no_browser_reload() -> None:
    page = PAGE.read_text(encoding="utf-8-sig")
    assert "_render_warroom_v2_cockpit_fragment" in page
    assert "getattr(st, \"fragment\", None)" in page
    assert "@fragment(run_every=run_every)" in page
    assert "window.parent.location.reload" not in page
    auto = AUTO.read_text(encoding="utf-8-sig")
    assert "window.parent.location.reload" not in auto
    assert "streamlit.components" not in auto
    assert "browser_timer_reload" not in auto


def test_page_mount_packet_marks_fragment_refresh_and_no_action() -> None:
    packet = build_warroom_v2_page_mount_packet(runtime_status={"receiver_runtime_started": True, "socket_opened": True, "receive_loop_started": True}, bridge_packet={"messages_applied": 8}, display_source="live")
    assert packet["rt_fragment_refresh_ready"] is True
    assert packet["page_reload_enabled"] is False
    assert packet["broker_send_enabled"] is False
    assert packet["order_intent_submitted"] is False
    assert packet["prediction_invoked"] is False
    assert packet["classifier_invoked"] is False


def test_doc_markers() -> None:
    doc = DOC.read_text(encoding="utf-8-sig")
    assert "warroom_v2_rt_fragment_refresh_done=true" in doc
    assert "browser_page_reload_removed=true" in doc
    assert "scroll_position_preserved_by_fragment_refresh=true" in doc
