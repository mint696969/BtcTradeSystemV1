# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_push_widgets_wp6_independent_widget_update_pipeline.py
# desc: WP6 verifies independent push-to-render pipeline with registry-driven read-only render packets and no page/socket/send side effects.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

REPO_ROOT = Path(__file__).resolve().parents[6]

from btcts.apps.operator_ui.prediction_warroom.v2.push_widgets.wp6_independent_widget_update_pipeline import build_wp6_independent_widget_update_pipeline_packet, run_independent_widget_update_pipeline  # noqa: E402

DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_WARROOM_MANUAL_TRADE_SUPPORT_PUSH_WIDGET_WP6_INDEPENDENT_WIDGET_UPDATE_PIPELINE_2026-07-05.md"


def test_wp6_packet_marks_pipeline_ready_and_safe() -> None:
    packet = build_wp6_independent_widget_update_pipeline_packet()
    assert packet["wp6_completed"] is True
    assert packet["next_checkpoint"] == "WP7_Per_widget_freshness_stale_heartbeat_error"
    assert packet["independent_widget_update_pipeline_ready"] is True
    assert packet["push_to_router_to_state_to_render_ready"] is True
    assert packet["render_packet_generation_ready"] is True
    assert packet["per_widget_render_packet_ready"] is True
    assert packet["updated_widget_ids"] == ["market_depth_widget", "recent_trades_widget"]
    assert packet["render_packets"]["market_depth_widget"]["read_only"] is True
    assert packet["render_packets"]["market_depth_widget"]["controls_added"] is False
    assert packet["websocket_opened"] is False
    assert packet["websocket_send_enabled"] is False
    assert packet["broker_send_enabled"] is False
    assert packet["warroom_page_mount_added"] is False
    assert "wp6_completed=true" in DOC.read_text(encoding="utf-8-sig")


def test_wp6_pipeline_keeps_unrelated_widgets_not_started() -> None:
    packet = run_independent_widget_update_pipeline([
        {"topic_key": "market.depth", "value": {"bid": 1, "raw_payload": {"x": 1}}, "received_at_ms": 100, "sequence": 4},
    ])
    assert packet["updated_widget_ids"] == ["market_depth_widget"]
    assert packet["render_packets"]["market_depth_widget"]["sequence"] == 4
    assert packet["render_packets"]["recent_trades_widget"]["freshness_label"] == "not_started"
    rows = packet["render_packets"]["market_depth_widget"]["rows"]
    assert rows[0]["raw_payload_rendered"] is False
    assert "raw_payload" not in rows[0]["value"]


def test_wp6_unsafe_message_does_not_block_safe_message() -> None:
    packet = run_independent_widget_update_pipeline([
        {"topic_key": "market.depth", "value": {"bid": 1}, "received_at_ms": 100, "send_requested": True},
        {"topic_key": "market.trades", "value": {"last": 2}, "received_at_ms": 101, "sequence": 2},
    ])
    assert packet["updated_widget_ids"] == ["recent_trades_widget"]
    assert packet["render_packets"]["market_depth_widget"]["sequence"] == 0
    assert packet["render_packets"]["recent_trades_widget"]["sequence"] == 2
