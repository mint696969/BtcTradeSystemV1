# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_push_widgets_wp12_bottom_chart_layout.py
# desc: WP12 verifies bottom chart layout adapter, overlays, stale handling, and WarRoom page mount markers.

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

REPO_ROOT = Path(__file__).resolve().parents[6]
PAGE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py"
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_WARROOM_MANUAL_TRADE_SUPPORT_PUSH_WIDGET_WP12_BOTTOM_CHART_LAYOUT_2026-07-05.md"

from btcts.apps.operator_ui.prediction_warroom.v2.push_widgets.wp12_bottom_chart_layout import build_wp12_bottom_chart_layout_packet, render_wp12_bottom_chart_layout  # noqa: E402


class FakeStreamlit:
    def __init__(self) -> None:
        self.captions: list[str] = []
        self.frames: list[Any] = []

    def caption(self, value: object) -> None:
        self.captions.append(str(value))

    def dataframe(self, value: object, width: object | None = None) -> None:
        self.frames.append({"value": value, "width": width})


def test_wp12_packet_marks_bottom_chart_ready_and_safe() -> None:
    packet = build_wp12_bottom_chart_layout_packet()
    assert packet["wp12_completed"] is True
    assert packet["next_checkpoint"] == "WP13_Prediction_card_connection_and_updates"
    assert packet["bottom_chart_layout_ready"] is True
    assert packet["bottom_chart_data_adapter_ready"] is True
    assert packet["bottom_chart_overlay_ready"] is True
    assert packet["bottom_chart_refresh_cadence_ready"] is True
    assert packet["bottom_chart_stale_handling_ready"] is True
    assert packet["chart_row_count"] == 7
    assert packet["overlay_count"] == 4
    assert packet["stale_row_count"] == 0
    assert packet["rate_limit_respected"] is True
    assert packet["websocket_send_enabled"] is False
    assert packet["broker_send_enabled"] is False
    assert packet["order_intent_submitted"] is False
    assert "wp12_completed=true" in DOC.read_text(encoding="utf-8-sig")


def test_wp12_render_adapter_is_read_only() -> None:
    fake = FakeStreamlit()
    result = render_wp12_bottom_chart_layout(build_wp12_bottom_chart_layout_packet(), fake)
    assert result["rendered_chart_rows"] == 7
    assert result["rendered_overlays"] == 4
    assert result["read_only"] is True
    assert result["controls_added"] is False
    assert len(fake.frames) == 2
    assert any("bottom chart" in line for line in fake.captions)


def test_wp12_warroom_page_contains_bottom_chart_mount_markers() -> None:
    text = PAGE.read_text(encoding="utf-8-sig")
    assert "build_wp12_bottom_chart_layout_packet" in text
    assert "render_wp12_bottom_chart_layout" in text
    assert "_render_warroom_push_widget_bottom_chart_wp12" in text
    assert 'with render_warroom_focus_section("push_widget_bottom_chart")' in text
