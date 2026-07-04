# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_push_widgets_wp13_prediction_card_connection.py
# desc: WP13 verifies prediction card connection to push-widget/chart context without prediction/classifier/broker/order side effects.

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

REPO_ROOT = Path(__file__).resolve().parents[6]
PAGE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py"
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_WARROOM_MANUAL_TRADE_SUPPORT_PUSH_WIDGET_WP13_PREDICTION_CARD_CONNECTION_2026-07-05.md"

from btcts.apps.operator_ui.prediction_warroom.v2.push_widgets.wp13_prediction_card_connection import build_wp13_prediction_card_connection_packet, render_wp13_prediction_card_connection  # noqa: E402


class FakeStreamlit:
    def __init__(self) -> None:
        self.captions: list[str] = []
        self.frames: list[Any] = []

    def caption(self, value: object) -> None:
        self.captions.append(str(value))

    def dataframe(self, value: object, width: object | None = None) -> None:
        self.frames.append({"value": value, "width": width})


def test_wp13_packet_marks_prediction_card_connection_complete_and_safe() -> None:
    packet = build_wp13_prediction_card_connection_packet()
    assert packet["wp13_completed"] is True
    assert packet["roadmap_completed"] is True
    assert packet["next_checkpoint"] == "WP13_DONE_CC_and_operator_acceptance"
    assert packet["prediction_card_connection_ready"] is True
    assert packet["prediction_card_update_ready"] is True
    assert packet["prediction_card_no_action_boundary_ready"] is True
    assert packet["prediction_invocation_guard_ready"] is True
    assert packet["classifier_invocation_guard_ready"] is True
    assert packet["prediction_card_count"] == 3
    assert packet["bottom_chart_row_count"] == 7
    assert packet["websocket_send_enabled"] is False
    assert packet["broker_send_enabled"] is False
    assert packet["order_intent_submitted"] is False
    assert packet["prediction_invoked"] is False
    assert packet["classifier_invoked"] is False
    assert "wp13_completed=true" in DOC.read_text(encoding="utf-8-sig")


def test_wp13_render_adapter_is_read_only_and_no_invocation() -> None:
    fake = FakeStreamlit()
    result = render_wp13_prediction_card_connection(build_wp13_prediction_card_connection_packet(), fake)
    assert result["rendered_prediction_card_count"] == 3
    assert result["read_only"] is True
    assert result["controls_added"] is False
    assert result["prediction_invoked"] is False
    assert result["classifier_invoked"] is False
    assert len(fake.frames) == 1
    assert any("prediction cards" in line for line in fake.captions)


def test_wp13_warroom_page_contains_prediction_card_mount_markers() -> None:
    text = PAGE.read_text(encoding="utf-8-sig")
    assert "build_wp13_prediction_card_connection_packet" in text
    assert "render_wp13_prediction_card_connection" in text
    assert "_render_warroom_push_widget_prediction_card_wp13" in text
    assert 'with render_warroom_focus_section("push_widget_prediction_cards")' in text
