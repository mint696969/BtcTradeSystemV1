# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_rt_polish3_cockpit.py
# desc: Verifies WarRoom v2 RT polish3 cockpit modules: market strip, improved guidance, chart scale, copy packet, and page orchestration.

from __future__ import annotations

import json
import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

REPO_ROOT = Path(__file__).resolve().parents[6]
PAGE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/warroom_v2_page.py"
RT_UI = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/rt_ui"
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_WARROOM_V2_RT_POLISH3_COCKPIT_2026-07-05.md"

from btcts.apps.operator_ui.prediction_warroom.v2.rt_ui.copy_packet_view import build_gpt_copy_packet  # noqa: E402
from btcts.apps.operator_ui.prediction_warroom.v2.rt_ui.inference_guidance_view import build_inference_guidance_packet  # noqa: E402
from btcts.apps.operator_ui.prediction_warroom.v2.rt_ui.market_strip_view import build_market_strip_packet  # noqa: E402
from btcts.apps.operator_ui.views.warroom_v2_page import build_warroom_v2_page_mount_packet  # noqa: E402


def _widgets_packet() -> dict[str, object]:
    row_depth = {"topic_key": "market.depth", "updated_at_ms": 1, "sequence": 1, "value": {"symbol": "FX_BTC_JPY", "best_bid": 100.0, "best_ask": 101.0, "spread": 1.0, "market_uid": "bitflyer.fx.FX_BTC_JPY", "source": "dhot_unified_market_state"}}
    row_spread = {"topic_key": "market.spread", "updated_at_ms": 1, "sequence": 1, "value": {"symbol": "FX_BTC_JPY", "spread": 1.0, "spread_bps": 1.0, "source": "dhot_unified_market_state"}}
    row_life = {"topic_key": "receiver.lifecycle", "updated_at_ms": 1, "sequence": 1, "value": {"status": "receiving", "last_event_ts": "2026-07-05T04:11:21Z"}}
    return {"live_widget_count": 4, "render_packets": {"market_depth_widget": {"rows": [row_depth]}, "spread_liquidity_widget": {"rows": [row_spread]}, "receiver_lifecycle_widget": {"rows": [row_life]}}}


def test_market_strip_extracts_dhot_values() -> None:
    packet = build_market_strip_packet(_widgets_packet())
    assert packet["symbol"] == "FX_BTC_JPY"
    assert packet["best_bid"] == 100.0
    assert packet["best_ask"] == 101.0
    assert packet["spread_bps"] == 1.0
    assert packet["receiver_status"] == "receiving"
    assert packet["broker_send_enabled"] is False


def test_guidance_and_copy_packet_are_read_only() -> None:
    chart = {"chart_row_count": 2, "stale_row_count": 0, "chart_rows": [{"topic_key": "market.depth", "updated_at_ms": 1, "price": 100.0, "value_label": "best_bid=100.0, best_ask=101.0, spread_bps=1.0", "freshness_label": "live"}]}
    widgets = _widgets_packet()
    market = build_market_strip_packet(widgets)
    guidance = build_inference_guidance_packet(chart, widgets)
    text = build_gpt_copy_packet(market_strip=market, guidance=guidance, chart_packet=chart, cards_packet={"cards": []})
    payload = json.loads(text)
    assert payload["schema_version"] == "warroom_gpt_review_packet.v1"
    assert payload["market"]["symbol"] == "FX_BTC_JPY"
    assert payload["safety"]["broker_send_enabled"] is False
    assert guidance["observational_scenario_only"] is True
    assert guidance["prediction_invoked"] is False


def test_page_uses_cockpit_modules_and_mount_marker() -> None:
    page = PAGE.read_text(encoding="utf-8-sig")
    assert "build_market_strip_packet" in page
    assert "build_gpt_copy_packet" in page
    assert "Realtime widget details" in page
    assert "rt_polish3_cockpit_layout_ready" in page
    packet = build_warroom_v2_page_mount_packet(runtime_status={"receiver_runtime_started": True}, bridge_packet={"messages_applied": 6}, display_source="live")
    assert packet["rt_polish3_cockpit_layout_ready"] is True
    assert packet["broker_send_enabled"] is False


def test_modules_and_doc_markers() -> None:
    assert (RT_UI / "market_strip_view.py").exists()
    assert (RT_UI / "copy_packet_view.py").exists()
    chart_text = (RT_UI / "chart_view.py").read_text(encoding="utf-8-sig")
    assert "zero=False" in chart_text
    doc = DOC.read_text(encoding="utf-8-sig")
    assert "warroom_v2_rt_polish3_cockpit_done=true" in doc
    assert "gpt_review_copy_packet_added=true" in doc
