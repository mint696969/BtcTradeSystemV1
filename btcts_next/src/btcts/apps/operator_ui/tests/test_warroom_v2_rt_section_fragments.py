# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_rt_section_fragments.py
# desc: Verifies WarRoom v2 cockpit refresh is split into section fragments instead of one full-body fragment.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

REPO_ROOT = Path(__file__).resolve().parents[6]
PAGE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/warroom_v2_page.py"
AUTO = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/rt_ui/auto_refresh_tick_view.py"
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_WARROOM_V2_RT_SECTION_FRAGMENTS_2026-07-05.md"

from btcts.apps.operator_ui.prediction_warroom.v2.rt_ui.auto_refresh_tick_view import build_cockpit_auto_refresh_packet  # noqa: E402
from btcts.apps.operator_ui.views.warroom_v2_page import build_warroom_v2_page_mount_packet  # noqa: E402


def test_refresh_uses_section_fragments_not_full_body_fragment() -> None:
    page = PAGE.read_text(encoding="utf-8-sig")
    assert "_render_section_fragment" in page
    assert "_build_cockpit_snapshot" in page
    assert "rt_section_fragment_refresh_ready" in page
    assert "rt_chart_engine_polling_ready" in page
    assert "rt_chart_fragment_refresh_disabled" in page
    assert "_render_section_fragment(\"chart\"" not in page
    assert "_render_warroom_v2_cockpit_body" not in page
    assert "_render_warroom_v2_cockpit_fragment" not in page
    assert "window.parent.location.reload" not in page


def test_auto_refresh_transport_marks_section_fragments() -> None:
    packet = build_cockpit_auto_refresh_packet({"ui_auto_refresh": True, "ui_refresh_interval": 3})
    assert packet["transport_kind"] == "streamlit_section_fragment_refresh"
    assert packet["section_fragment_refresh_enabled"] is True
    assert packet["page_reload_enabled"] is False


def test_page_mount_packet_section_fragment_and_no_action() -> None:
    packet = build_warroom_v2_page_mount_packet(runtime_status={"receiver_runtime_started": True, "socket_opened": True, "receive_loop_started": True}, bridge_packet={"messages_applied": 12}, display_source="live")
    assert packet["rt_section_fragment_refresh_ready"] is True
    assert packet["rt_chart_engine_polling_ready"] is True
    assert packet["rt_chart_fragment_refresh_disabled"] is True
    assert packet["page_reload_enabled"] is False
    assert packet["broker_send_enabled"] is False
    assert packet["order_intent_submitted"] is False
    assert packet["prediction_invoked"] is False
    assert packet["classifier_invoked"] is False


def test_doc_markers() -> None:
    doc = DOC.read_text(encoding="utf-8-sig")
    assert "warroom_v2_rt_section_fragments_done=true" in doc
    assert "full_body_fragment_removed=true" in doc
    assert "section_fragment_refresh_enabled=true" in doc
