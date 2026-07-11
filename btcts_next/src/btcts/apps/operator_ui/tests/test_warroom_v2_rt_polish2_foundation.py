# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_rt_polish2_foundation.py
# desc: Verifies WarRoom v2 RT polish2 foundation: live/retained/waiting packet policy, no sample fallback, trade strip, and scenario guidance.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

REPO_ROOT = Path(__file__).resolve().parents[6]
PAGE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/warroom_v2_page.py"
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_WARROOM_V2_RT_POLISH2_FOUNDATION_2026-07-05.md"

from btcts.apps.operator_ui.prediction_warroom.v2.rt_ui.inference_guidance_view import build_inference_guidance_packet  # noqa: E402
from btcts.apps.operator_ui.prediction_warroom.v2.rt_ui.live_packets import select_or_build_rt_display_packets  # noqa: E402
from btcts.apps.operator_ui.views.warroom_v2_page import build_warroom_v2_page_mount_packet  # noqa: E402


def test_waiting_packets_suppress_wp_sample_fallback() -> None:
    state: dict[str, object] = {}
    packets = select_or_build_rt_display_packets(state, {"live_receiver_bridge_idle": True, "messages_applied": 0})
    assert packets["source"]["display_source"] == "waiting"
    assert packets["source"]["fallback_sample_suppressed"] is True
    assert packets["chart"]["chart_rows"] == []
    assert packets["widgets"]["render_packets"] == {}
    assert "BTC_JPY" not in str(packets)
    assert "100.5" not in str(packets)


def test_live_packets_are_retained_and_reused_when_next_render_is_idle() -> None:
    live_chart = {"version": "warroom.manual_trade_support.push_widgets.rt0_rt6.test", "packet_kind": "warroom_push_widget_rt_live_bottom_chart_packet", "chart_rows": [{"topic_key": "market.trades", "updated_at_ms": 1, "price": 101.0, "value_label": "last_price=101.0", "freshness_label": "live"}], "chart_row_count": 1, "overlay_count": 0, "stale_row_count": 0}
    state = {
        "warroom_push_widget_wp9_page_mount_packet": {"version": live_chart["version"], "packet_kind": "warroom_push_widget_rt_live_page_mount_packet", "render_packets": {}, "widget_count": 0, "live_widget_count": 0},
        "warroom_push_widget_wp11_top_layout_packet": {"version": live_chart["version"], "packet_kind": "warroom_push_widget_rt_live_top_layout_packet", "groups": []},
        "warroom_push_widget_wp12_bottom_chart_packet": live_chart,
        "warroom_push_widget_wp13_prediction_card_packet": {"version": live_chart["version"], "packet_kind": "warroom_push_widget_rt_live_prediction_card_packet", "cards": []},
    }
    first = select_or_build_rt_display_packets(state, {"messages_applied": 1})
    assert first["source"]["display_source"] == "live"
    state.pop("warroom_push_widget_wp12_bottom_chart_packet")
    second = select_or_build_rt_display_packets(state, {"live_receiver_bridge_idle": True, "messages_applied": 0})
    assert second["source"]["display_source"] == "retained"
    assert second["chart"]["chart_rows"][0]["price"] == 101.0


def test_inference_guidance_is_observational_and_read_only() -> None:
    packet = build_inference_guidance_packet({"display_source": "live", "chart_rows": [{"price": 100.0, "value_label": "best_bid=100.0"}, {"price": 101.0, "value_label": "last_price=101.0"}]}, {"live_widget_count": 4})
    assert packet["observational_scenario_only"] is True
    assert packet["scenario"] == "upside pressure watch"
    assert packet["prediction_invoked"] is False
    assert packet["classifier_invoked"] is False
    assert packet["broker_send_enabled"] is False


def test_page_order_and_mount_packet_markers() -> None:
    page = PAGE.read_text(encoding="utf-8-sig")
    assert 'render_compact_section_label(st, index=1, title="Market strip"' in page
    assert 'render_compact_section_label(st, index=2, title="Trade strip"' in page
    assert 'render_compact_section_label(st, index=3, title="Inference scenario guidance"' in page
    assert 'render_compact_section_label(st, index=4, title="Prediction cards"' in page
    assert 'render_compact_section_label(st, index=5, title="Bottom chart"' in page
    assert "build_wp12_bottom_chart_layout_packet" not in page
    packet = build_warroom_v2_page_mount_packet(runtime_status={"receiver_runtime_started": True}, bridge_packet={"messages_applied": 0}, display_source="waiting")
    assert packet["rt_polish2_live_retention_ready"] is True
    assert packet["fallback_sample_suppressed"] is True


def test_doc_markers() -> None:
    doc = DOC.read_text(encoding="utf-8-sig")
    assert "warroom_v2_rt_polish2_foundation_done=true" in doc
    assert "fallback_sample_suppressed=true" in doc
    assert "inference_scenario_guidance_lane_added=true" in doc
