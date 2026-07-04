# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_push_widgets_wp8_first_real_push_widget_set.py
# desc: WP8 verifies first real push widget set updates all initial widgets through health-enriched read-only render packets.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

REPO_ROOT = Path(__file__).resolve().parents[6]

from btcts.apps.operator_ui.prediction_warroom.v2.push_widgets.wp8_first_real_push_widget_set import build_first_real_push_widget_messages, build_wp8_first_real_push_widget_set_packet  # noqa: E402

DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_WARROOM_MANUAL_TRADE_SUPPORT_PUSH_WIDGET_WP8_FIRST_REAL_PUSH_WIDGET_SET_2026-07-05.md"


def test_wp8_packet_updates_all_initial_widgets_and_stays_safe() -> None:
    packet = build_wp8_first_real_push_widget_set_packet()
    assert packet["wp8_completed"] is True
    assert packet["next_checkpoint"] == "WP9_WarRoom_page_mount_for_push_widgets"
    assert packet["first_real_push_widget_set_ready"] is True
    assert packet["all_initial_widgets_update_from_push_ready"] is True
    assert packet["message_count"] == 7
    assert packet["widget_count"] == 5
    assert packet["live_widget_count"] == 5
    assert set(packet["live_widget_ids"]) == {"market_depth_widget", "recent_trades_widget", "spread_liquidity_widget", "receiver_lifecycle_widget", "summary_alerts_widget"}
    assert all(item["read_only"] is True for item in packet["render_packets"].values())
    assert all(item["controls_added"] is False for item in packet["render_packets"].values())
    assert packet["websocket_opened"] is False
    assert packet["websocket_send_enabled"] is False
    assert packet["broker_send_enabled"] is False
    assert packet["warroom_page_mount_added"] is False
    assert "wp8_completed=true" in DOC.read_text(encoding="utf-8-sig")


def test_wp8_message_builders_do_not_emit_raw_or_secret_fields() -> None:
    messages = build_first_real_push_widget_messages()
    assert [message["topic_key"] for message in messages] == ["market.depth", "market.trades", "market.spread", "market.liquidity", "receiver.lifecycle", "warroom.summary", "warroom.alerts"]
    for message in messages:
        assert "raw_payload" not in message["value"]
        assert "endpoint" not in message["value"]
        assert "token" not in message["value"]
        assert "callable" not in message["value"]


def test_wp8_spread_liquidity_and_summary_widgets_hold_multiple_topics() -> None:
    packet = build_wp8_first_real_push_widget_set_packet()
    spread_rows = packet["render_packets"]["spread_liquidity_widget"]["rows"]
    summary_rows = packet["render_packets"]["summary_alerts_widget"]["rows"]
    assert {row["topic_key"] for row in spread_rows} == {"market.spread", "market.liquidity"}
    assert {row["topic_key"] for row in summary_rows} == {"warroom.summary", "warroom.alerts"}
