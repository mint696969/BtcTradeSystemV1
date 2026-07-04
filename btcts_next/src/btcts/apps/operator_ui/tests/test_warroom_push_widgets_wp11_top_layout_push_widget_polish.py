# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_push_widgets_wp11_top_layout_push_widget_polish.py
# desc: WP11 verifies top layout push-widget polish groups and WarRoom page mount markers.

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

REPO_ROOT = Path(__file__).resolve().parents[6]
PAGE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py"
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_WARROOM_MANUAL_TRADE_SUPPORT_PUSH_WIDGET_WP11_TOP_LAYOUT_PUSH_WIDGET_POLISH_2026-07-05.md"

from btcts.apps.operator_ui.prediction_warroom.v2.push_widgets.wp11_top_layout_push_widget_polish import build_wp11_top_layout_push_widget_polish_packet, render_wp11_top_layout_polish  # noqa: E402


class FakeStreamlit:
    def __init__(self) -> None:
        self.captions: list[str] = []
        self.frames: list[Any] = []

    def caption(self, value: object) -> None:
        self.captions.append(str(value))

    def dataframe(self, value: object, width: object | None = None) -> None:
        self.frames.append({"value": value, "width": width})


def test_wp11_packet_marks_top_layout_ready_and_safe() -> None:
    packet = build_wp11_top_layout_push_widget_polish_packet()
    assert packet["wp11_completed"] is True
    assert packet["next_checkpoint"] == "WP12_Bottom_chart_layout"
    assert packet["top_layout_push_widget_polish_ready"] is True
    assert packet["top_information_groups_ready"] is True
    assert packet["market_status_group_ready"] is True
    assert packet["freshness_connection_group_ready"] is True
    assert packet["manual_decision_context_group_ready"] is True
    assert packet["risk_cues_group_ready"] is True
    assert packet["group_count"] == 4
    assert packet["base_widget_count"] == 5
    assert packet["live_widget_count"] == 5
    assert packet["websocket_opened"] is False
    assert packet["websocket_send_enabled"] is False
    assert packet["broker_send_enabled"] is False
    assert "wp11_completed=true" in DOC.read_text(encoding="utf-8-sig")


def test_wp11_render_adapter_renders_four_read_only_groups() -> None:
    fake = FakeStreamlit()
    result = render_wp11_top_layout_polish(build_wp11_top_layout_push_widget_polish_packet(), fake)
    assert result["rendered_group_count"] == 4
    assert result["read_only"] is True
    assert result["controls_added"] is False
    assert len(fake.frames) == 1
    assert any("top layout" in line for line in fake.captions)


def test_wp11_warroom_page_contains_top_layout_mount_markers() -> None:
    text = PAGE.read_text(encoding="utf-8-sig")
    assert "build_wp11_top_layout_push_widget_polish_packet" in text
    assert "render_wp11_top_layout_polish" in text
    assert "_render_warroom_push_widget_top_layout_wp11" in text
    assert 'with render_warroom_focus_section("push_widget_top_layout")' in text
