# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_push_widgets_rt_live_receiver_bridge.py
# desc: RT0-RT6 verifies actual live observation runtime path, state/session_state/page packets, freshness, and no-action guards.

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Mapping

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

REPO_ROOT = Path(__file__).resolve().parents[6]
PAGE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py"
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_WARROOM_PUSH_WIDGET_RT0_RT6_LIVE_OBSERVATION_RUNTIME_2026-07-05.md"

from btcts.apps.operator_ui.prediction_warroom.v2.push_widgets.rt_live_receiver_bridge import WARROOM_RT_LIVE_ENDPOINT_STATE_KEY, WARROOM_RT_LIVE_RUNTIME_STATUS_STATE_KEY, ensure_warroom_push_widget_live_observation_runtime, apply_warroom_push_widget_rt_live_receiver_bridge_to_session_state  # noqa: E402
from btcts.apps.operator_ui.prediction_warroom.v2.push_widgets.wp9_warroom_page_mount import WARROOM_WP9_PAGE_MOUNT_SESSION_STATE_KEY  # noqa: E402
from btcts.apps.operator_ui.prediction_warroom.v2.push_widgets.wp12_bottom_chart_layout import WARROOM_WP12_BOTTOM_CHART_SESSION_STATE_KEY  # noqa: E402
from btcts.apps.operator_ui.prediction_warroom.v2.push_widgets.wp13_prediction_card_connection import WARROOM_WP13_PREDICTION_CARD_SESSION_STATE_KEY  # noqa: E402


def _messages() -> list[dict[str, object]]:
    return [
        {"topic": "market.depth", "value": {"best_bid": 100.0, "best_ask": 101.0}, "ts_ms": 1000, "sequence": 1},
        {"topic_key": "market.trades", "value": {"last_price": 100.5}, "received_at_ms": 1010, "sequence": 1},
        {"topic_key": "market.spread", "value": {"spread_bps": 9.9}, "received_at_ms": 1020, "sequence": 1},
        {"topic_key": "market.liquidity", "value": {"depth_score": 0.8}, "received_at_ms": 1021, "sequence": 2},
        {"topic_key": "receiver.lifecycle", "value": {"status": "receiving"}, "received_at_ms": 1030, "sequence": 1},
        {"topic_key": "warroom.summary", "value": {"summary": "live bridge ok"}, "received_at_ms": 1040, "sequence": 1},
        {"topic_key": "warroom.alerts", "value": {"alert_count": 0}, "received_at_ms": 1041, "sequence": 2},
    ]


def fake_connect(endpoint: str, config: Mapping[str, Any]) -> dict[str, Any]:
    return {"opened": True, "messages": _messages(), "endpoint": endpoint, "config_keys": sorted(config)}


def test_rt0_rt6_runtime_drains_receiver_messages_and_updates_all_warroom_packets() -> None:
    state: dict[str, Any] = {WARROOM_RT_LIVE_ENDPOINT_STATE_KEY: "ws://example.invalid/push"}
    status = ensure_warroom_push_widget_live_observation_runtime(state, connect_fn=fake_connect, runtime_key="test_rt0_rt6", runtime_config={"x": 1})
    assert status["receiver_runtime_started"] is True
    for _ in range(20):
        status = ensure_warroom_push_widget_live_observation_runtime(state, connect_fn=fake_connect, runtime_key="test_rt0_rt6", runtime_config={"x": 1})
        if status["drained_message_count"] == 7:
            break
    assert status["drained_message_count"] == 7
    packet = apply_warroom_push_widget_rt_live_receiver_bridge_to_session_state(state, now_ms=1100)
    assert packet["rt0_live_receiver_runtime_started"] is True
    assert packet["rt1_live_receiver_source_to_router_bridge_ready"] is True
    assert packet["rt2_received_websocket_message_to_state_store_apply_ready"] is True
    assert packet["rt3_session_state_lightweight_state_reflection_ready"] is True
    assert packet["rt4_warroom_auto_refresh_observation_ready"] is True
    assert packet["rt5_live_freshness_stale_error_observation_ready"] is True
    assert packet["rt6_no_send_broker_order_boundary_ready"] is True
    assert state[WARROOM_WP9_PAGE_MOUNT_SESSION_STATE_KEY]["live_widget_count"] == 5
    assert state[WARROOM_WP12_BOTTOM_CHART_SESSION_STATE_KEY]["chart_row_count"] == 7
    assert state[WARROOM_WP13_PREDICTION_CARD_SESSION_STATE_KEY]["prediction_card_count"] == 3
    assert packet["websocket_send_enabled"] is False
    assert packet["broker_send_enabled"] is False
    assert packet["prediction_invoked"] is False
    assert packet["classifier_invoked"] is False


def test_rt_runtime_idle_without_endpoint_and_page_doc_markers() -> None:
    state: dict[str, Any] = {}
    status = ensure_warroom_push_widget_live_observation_runtime(state)
    assert status["receiver_runtime_configured"] is False
    assert state[WARROOM_RT_LIVE_RUNTIME_STATUS_STATE_KEY]["endpoint_url_present"] is False
    page = PAGE.read_text(encoding="utf-8-sig")
    assert "ensure_warroom_push_widget_live_observation_runtime" in page
    assert "_refresh_warroom_push_widget_rt_live_bridge" in page
    assert "st.session_state.get(WARROOM_WP9_PAGE_MOUNT_SESSION_STATE_KEY)" in page
    doc = DOC.read_text(encoding="utf-8-sig")
    assert "rt0_live_receiver_runtime_started=true" in doc
    assert "rt6_no_send_broker_order_boundary_ready=true" in doc
