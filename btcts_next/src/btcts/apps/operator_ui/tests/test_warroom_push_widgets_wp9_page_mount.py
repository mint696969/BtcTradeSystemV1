# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_push_widgets_wp9_page_mount.py
# desc: WP9 verifies WarRoom page mount adapter and page integration markers without socket/send/broker/order side effects.

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

REPO_ROOT = Path(__file__).resolve().parents[6]
PAGE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py"
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_WARROOM_MANUAL_TRADE_SUPPORT_PUSH_WIDGET_WP9_PAGE_MOUNT_2026-07-05.md"

from btcts.apps.operator_ui.prediction_warroom.v2.push_widgets.wp9_warroom_page_mount import build_wp9_warroom_page_mount_packet, render_wp9_push_widget_mount  # noqa: E402


class FakeStreamlit:
    def __init__(self) -> None:
        self.captions: list[str] = []
        self.frames: list[Any] = []

    def caption(self, value: object) -> None:
        self.captions.append(str(value))

    def dataframe(self, value: object, width: object | None = None) -> None:
        self.frames.append({"value": value, "width": width})


def test_wp9_packet_marks_page_mount_ready_and_safe() -> None:
    packet = build_wp9_warroom_page_mount_packet()
    assert packet["wp9_completed"] is True
    assert packet["next_checkpoint"] == "WP10_Widget_extension_contract"
    assert packet["warroom_page_mount_ready"] is True
    assert packet["warroom_page_mount_added"] is True
    assert packet["registry_driven_page_mount_ready"] is True
    assert packet["widget_count"] == 5
    assert packet["render_packet_count"] == 5
    assert packet["live_widget_count"] == 5
    assert packet["websocket_opened"] is False
    assert packet["websocket_send_enabled"] is False
    assert packet["broker_send_enabled"] is False
    assert packet["order_intent_submitted"] is False
    assert "wp9_completed=true" in DOC.read_text(encoding="utf-8-sig")


def test_wp9_render_adapter_renders_all_widgets_read_only() -> None:
    fake = FakeStreamlit()
    result = render_wp9_push_widget_mount(build_wp9_warroom_page_mount_packet(), fake)
    assert result["rendered_widget_count"] == 5
    assert result["read_only"] is True
    assert result["controls_added"] is False
    assert len(fake.frames) == 5
    assert any("receive-only" in line for line in fake.captions)


def test_wp9_warroom_page_contains_mount_markers() -> None:
    text = PAGE.read_text(encoding="utf-8-sig")
    assert "build_wp9_warroom_page_mount_packet" in text
    assert "render_wp9_push_widget_mount" in text
    assert "_render_warroom_push_widget_mount_wp9" in text
    assert 'with render_warroom_focus_section("push_widget_grid")' in text
