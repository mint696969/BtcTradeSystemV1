# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_push_widgets_wp7_widget_health_freshness.py
# desc: WP7 verifies per-widget freshness, stale, heartbeat, error, slow state, and no action side effects.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

REPO_ROOT = Path(__file__).resolve().parents[6]

from btcts.apps.operator_ui.prediction_warroom.v2.push_widgets.wp7_widget_health_freshness import build_wp7_widget_health_freshness_packet, run_widget_health_freshness_pipeline  # noqa: E402

DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_WARROOM_MANUAL_TRADE_SUPPORT_PUSH_WIDGET_WP7_WIDGET_HEALTH_FRESHNESS_2026-07-05.md"


def test_wp7_packet_marks_health_layer_ready_and_safe() -> None:
    packet = build_wp7_widget_health_freshness_packet()
    assert packet["wp7_completed"] is True
    assert packet["next_checkpoint"] == "WP8_First_real_push_widget_set"
    assert packet["per_widget_freshness_ready"] is True
    assert packet["per_widget_stale_ready"] is True
    assert packet["per_widget_heartbeat_ready"] is True
    assert packet["per_widget_error_ready"] is True
    assert packet["health_enriched_render_packets_ready"] is True
    assert packet["render_packets"]["market_depth_widget"]["freshness_label"] == "stale"
    assert packet["render_packets"]["recent_trades_widget"]["freshness_label"] == "live"
    assert packet["websocket_send_enabled"] is False
    assert packet["broker_send_enabled"] is False
    assert packet["warroom_page_mount_added"] is False
    assert "wp7_completed=true" in DOC.read_text(encoding="utf-8-sig")


def test_wp7_health_is_isolated_per_widget() -> None:
    packet = run_widget_health_freshness_pipeline([
        {"topic_key": "market.depth", "value": {"bid": 1}, "received_at_ms": 1000, "sequence": 2},
        {"topic_key": "market.trades", "value": {"last": 2}, "received_at_ms": 5900, "sequence": 3},
    ], now_ms=6200, errors_by_widget={"market_depth_widget": "decode_error"})
    assert packet["render_packets"]["market_depth_widget"]["health"]["state"] == "error"
    assert packet["render_packets"]["market_depth_widget"]["health"]["error_reason"] == "decode_error"
    assert packet["render_packets"]["recent_trades_widget"]["health"]["state"] == "live"
    assert packet["render_packets"]["recent_trades_widget"]["error"] is False


def test_wp7_not_started_widget_stays_read_only_and_not_started() -> None:
    packet = run_widget_health_freshness_pipeline([
        {"topic_key": "market.depth", "value": {"bid": 1}, "received_at_ms": 1000, "sequence": 1},
    ], now_ms=1001)
    summary = packet["render_packets"]["summary_alerts_widget"]
    assert summary["freshness_label"] == "not_started"
    assert summary["health"]["age_ms"] is None
    assert summary["read_only"] is True
    assert summary["controls_added"] is False
