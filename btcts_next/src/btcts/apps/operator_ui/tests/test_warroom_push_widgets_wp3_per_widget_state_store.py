# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_push_widgets_wp3_per_widget_state_store.py
# desc: WP3 verifies independent per-widget state store, bounded buffers, raw-payload drop, and no-send boundary.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

REPO_ROOT = Path(__file__).resolve().parents[6]

from btcts.apps.operator_ui.prediction_warroom.v2.push_widgets.wp3_per_widget_state_store import apply_widget_state_update, build_initial_widget_state_store, build_wp3_state_store_packet  # noqa: E402

DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_WARROOM_MANUAL_TRADE_SUPPORT_PUSH_WIDGET_WP3_PER_WIDGET_STATE_STORE_2026-07-05.md"


def test_wp3_packet_marks_state_store_ready_and_safe() -> None:
    packet = build_wp3_state_store_packet()
    assert packet["wp3_completed"] is True
    assert packet["next_checkpoint"] == "WP4_Receive_only_WebSocket_push_router"
    assert packet["per_widget_state_store_ready"] is True
    assert packet["independent_widget_state_ready"] is True
    assert packet["bounded_buffers_ready"] is True
    assert packet["raw_payload_drop_ready"] is True
    assert packet["widget_count"] == 6
    assert packet["websocket_send_enabled"] is False
    assert packet["broker_send_enabled"] is False
    assert packet["order_intent_submitted"] is False
    assert "wp3_completed=true" in DOC.read_text(encoding="utf-8-sig")


def test_wp3_update_isolated_to_target_widget_and_drops_raw_payload() -> None:
    store = build_initial_widget_state_store()
    updated = apply_widget_state_update(store, topic_key="market.depth", value={"best_bid": 100, "raw_payload": {"secret": "x"}}, updated_at_ms=123, sequence=7)
    depth = updated["widgets"]["market_depth_widget"]
    trades = updated["widgets"]["recent_trades_widget"]
    assert depth["sequence"] == 7
    assert depth["snapshots"]["market.depth"]["value"] == {"best_bid": 100}
    assert "raw_payload" not in depth["snapshots"]["market.depth"]["value"]
    assert trades["sequence"] == 0
    assert store["widgets"]["market_depth_widget"]["sequence"] == 0


def test_wp3_unknown_topic_does_not_mutate_widgets() -> None:
    store = build_initial_widget_state_store()
    updated = apply_widget_state_update(store, topic_key="unknown.topic", value={"x": 1}, updated_at_ms=999)
    assert updated["widgets"] == store["widgets"]
    assert updated["unknown_topic_errors"] == [{"topic_key": "unknown.topic", "reason": "unknown_topic"}]
