# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_rt_polish3_cockpit.py
# desc: Verifies WarRoom v2 RT polish3 cockpit modules: market strip, improved guidance, chart scale, copy packet, and page orchestration.

from __future__ import annotations

import json
import sys

import pandas as pd
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

REPO_ROOT = Path(__file__).resolve().parents[6]
PAGE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/warroom_v2_page.py"
RT_UI = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/rt_ui"
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_WARROOM_V2_RT_POLISH3_COCKPIT_2026-07-05.md"

from btcts.apps.operator_ui.prediction_warroom.v2.rt_ui.copy_packet_view import build_gpt_copy_packet, render_gpt_copy_packet  # noqa: E402
from btcts.apps.operator_ui.prediction_warroom.v2.rt_ui.inference_guidance_view import build_inference_guidance_packet  # noqa: E402
from btcts.apps.operator_ui.prediction_warroom.v2.rt_ui.market_strip_view import build_market_strip_packet  # noqa: E402
from btcts.apps.operator_ui.views.warroom_v2_page import build_warroom_v2_page_mount_packet  # noqa: E402
from btcts.apps.operator_ui.prediction_warroom.v2.rt_ui.interactive_chart import build_interactive_candle_records, build_interactive_chart_html, build_chart_selection_copy_request, normalize_interactive_overlay_layers  # noqa: E402


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



class _CopyPacketFakeExpander:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


class _CopyPacketFakeStreamlit:
    def __init__(self) -> None:
        self.captions: list[str] = []
        self.text_areas: list[dict[str, object]] = []
        self.expander_titles: list[str] = []

    def expander(self, title: str, expanded: bool = False):
        self.expander_titles.append(title)
        return _CopyPacketFakeExpander()

    def caption(self, text: object) -> None:
        self.captions.append(str(text))

    def text_area(self, label: str, value: str, height: int | None = None):
        self.text_areas.append({"label": label, "value": value, "height": height})
        return value


def test_guidance_and_copy_packet_are_read_only() -> None:
    chart = {"chart_row_count": 2, "stale_row_count": 0, "chart_rows": [{"topic_key": "market.depth", "updated_at_ms": 1, "price": 100.0, "value_label": "best_bid=100.0, best_ask=101.0, spread_bps=1.0", "freshness_label": "live"}]}
    widgets = _widgets_packet()
    market = build_market_strip_packet(widgets)
    guidance = build_inference_guidance_packet(chart, widgets)
    chart_render_summary = {
        "gpt_review_chart_snapshot": {
            "schema_version": "warroom_chart_gpt_review_snapshot.v2_light_pointer",
            "display_mode": "Live",
            "viewport_label": "15分",
            "viewport_minutes": 15,
            "history_rows": 819,
            "visible_rows": 813,
            "latest": {"ts": "2026-07-05T14:16:27Z", "price": 10103617.0, "role": "last", "freshness_label": "dhot_bootstrap"},
            "x_domain": {"start": "2026-07-05T14:01:27Z", "end": "2026-07-05T14:16:27Z", "latest_anchored": True},
            "candle_summary": {"rows": 16, "closed": 15, "forming": 1, "source": "non_ui_warroom_chart_series", "true_trade_ohlcv_connected": False},
            "dhot_bootstrap": {"ok": True, "source_path": "D:/btc_ts_hot/data/market_data/exchange=bitflyer/symbol=FX_BTC_JPY/type=market.trade/date=2026-07-05/part-00001.jsonl", "rows_returned": 813, "tail_bytes": 2000000, "max_rows": 900},
            "trust_boundary": {"chart_logic_owner": "btcts.prediction.warroom_chart_series", "ui_role": "render_only", "input_source": "retained_market_state_rows_plus_dhot_market_trade_bootstrap", "latest_candle_may_change": True, "closed_candles_should_not_change_in_session": True, "official_exchange_ohlc_connected": False, "manual_review_only": True},
            "sample_preview": {"visible_price_rows_tail": [{"heavy": "not copied into final packet"}]},
        }
    }
    text = build_gpt_copy_packet(market_strip=market, guidance=guidance, chart_packet=chart, cards_packet={"cards": []}, chart_render_summary=chart_render_summary)
    payload = json.loads(text)
    assert payload["schema_version"] == "warroom_gpt_review_packet.2026_07_05.v3_action_plan"
    assert payload["market"]["symbol"] == "FX_BTC_JPY"
    selected = payload["operator_focus"]["selected_chart_range"]
    assert selected["schema_version"] == "warroom_chart_analysis_request.v1"
    assert selected["history_rows"] == 819
    assert selected["dhot_bootstrap"]["rows_returned"] == 813
    assert selected["analysis_target"]["scope"] == "currently selected WarRoom chart viewport"
    assert selected["analysis_target"]["time_range"]["start"] == "2026-07-05T14:01:27Z"
    assert selected["data_access_hints"]["hot_data_root"] == "D:/btc_ts_hot"
    assert selected["data_access_hints"]["cold_data_root"] == "E:/btc_ts"
    assert selected["data_access_hints"]["primary_market_trade_path"].endswith("part-00001.jsonl")
    actions = selected["data_access_hints"]["recommended_actions"]
    assert [action["tool"] for action in actions] == ["data_latest", "data_slice", "repo_read_batch"]
    trade_action = actions[1]
    assert trade_action["args"]["path"].endswith("part-00001.jsonl")
    assert trade_action["args"]["date_from"] == "2026-07-05"
    assert trade_action["args"]["time_from"] == "14:01:27"
    assert trade_action["args"]["time_to"] == "14:16:27"
    assert trade_action["args"]["max_lines"] == 200
    assert trade_action["args"]["max_bytes"] == 60000
    assert selected["copy_weight_policy"]["embedded_raw_rows"] is False
    assert selected["copy_weight_policy"]["embedded_visible_price_rows"] is False
    serialized = json.dumps(payload, ensure_ascii=False)
    assert "sample_preview" not in serialized
    assert "visible_price_rows_tail" not in serialized
    assert "heavy" not in serialized
    assert payload["safety"]["broker_send_enabled"] is False
    assert payload["safety"]["prediction_invoked"] is False
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
    assert (RT_UI / "interactive_chart" / "renderer.py").exists()
    assert (RT_UI / "interactive_chart" / "html_builder.py").exists()
    assert (RT_UI / "interactive_chart" / "overlays.py").exists()
    assert not (RT_UI / "interactive_chart" / "html_assets.py").exists()
    assert (RT_UI / "interactive_chart" / "frontend_assets" / "styles.py").exists()
    assert (RT_UI / "interactive_chart" / "frontend_assets" / "selection_js.py").exists()
    assert (RT_UI / "interactive_chart" / "frontend_assets" / "overlay_js.py").exists()
    assert (RT_UI / "interactive_chart" / "frontend_assets" / "boot_js.py").exists()
    chart_text = (RT_UI / "chart_view.py").read_text(encoding="utf-8-sig")
    assert "zero=False" in chart_text
    assert "render_interactive_candle_chart" in chart_text
    assert "_build_board_band_overlay_layers" in chart_text
    doc = DOC.read_text(encoding="utf-8-sig")
    assert "warroom_v2_rt_polish3_cockpit_done=true" in doc
    assert "gpt_review_copy_packet_added=true" in doc



def test_interactive_chart_package_builds_selection_copy_surface() -> None:
    frame = pd.DataFrame(
        [
            {"ts": "2026-07-05T14:00:00Z", "open": 100.0, "high": 105.0, "low": 99.0, "close": 103.0, "candle_status": "closed", "source_role": "last"},
            {"ts": "2026-07-05T14:01:00Z", "open": 103.0, "high": 108.0, "low": 102.0, "close": 104.0, "candle_status": "forming", "source_role": "last"},
        ]
    )
    candles = build_interactive_candle_records(frame)
    assert len(candles) == 2
    assert candles[0]["time_utc"] == "2026-07-05T14:00:00Z"
    assert candles[0]["time_jst"].startswith("2026-07-05T23:00:00")
    packet = build_chart_selection_copy_request(
        mode="1分足",
        selection_type="range",
        start_candle=candles[0],
        end_candle=candles[1],
        candle_count=2,
        visible_candle_count=120,
        chart_context={"primary_market_trade_path": "D:/btc_ts_hot/data/market_data/example.jsonl"},
    )
    assert packet["timeframe"] == "1m"
    assert packet["selected_range"]["candle_count"] == 2
    assert packet["source"]["primary_market_trade_path"].endswith("example.jsonl")
    assert packet["safety"]["broker_send_enabled"] is False
    html = build_interactive_chart_html(candles=candles, mode="1分足", chart_context=packet["source"], visible_candle_count=120)
    assert "lightweight-charts" in html
    assert "この範囲をGPTへコピー" in html
    assert "navigator.clipboard.writeText" in html
    assert "packet-preview" in html
    assert "自動コピー不可: 下のJSONをCtrl+Cで手動コピー" in html
    assert "selectPreviewForManualCopy" in html
    assert "renderOverlayLayers" in html
    assert "renderMarkerOverlay" in html
    assert "future_space_is_visual_blank_only" in html


def test_interactive_chart_overlay_layers_are_read_only_and_renderable() -> None:
    layers = normalize_interactive_overlay_layers(
        [
            {
                "layer_id": "prediction_flow_preview",
                "label": "予測流動線 preview",
                "kind": "line",
                "color": "#7c3aed",
                "points": [
                    {"ts": "2026-07-05T14:00:00Z", "value": 100.0},
                    {"ts": "2026-07-05T14:01:00Z", "value": 101.0},
                ],
            }
        ]
    )
    assert layers[0]["layer_id"] == "prediction_flow_preview"
    assert layers[0]["kind"] == "line"
    assert layers[0]["read_only"] is True
    assert layers[0]["prediction_invoked"] is False
    marker_layers = normalize_interactive_overlay_layers(
        [
            {
                "layer_id": "execution_points",
                "kind": "marker",
                "markers": [{"ts": "2026-07-05T14:00:00Z", "text": "約定", "shape": "circle"}],
            },
            {"layer_id": "board_depth_band", "kind": "board_band"},
        ]
    )
    assert marker_layers[0]["kind"] == "marker"
    assert marker_layers[0]["broker_send_enabled"] is False
    assert marker_layers[1]["kind"] == "board_band"
    assert marker_layers[1]["reserved_for_future"] is True
    assert marker_layers[1]["rendered_now"] is False
    board_layers = normalize_interactive_overlay_layers(
        [
            {
                "layer_id": "warroom_board_bid_ask_band",
                "kind": "board_band",
                "points": [
                    {"ts": "2026-07-05T14:00:00Z", "bid": 100.0, "ask": 101.0},
                    {"ts": "2026-07-05T14:01:00Z", "bid": 100.5, "ask": 101.5},
                ],
            }
        ]
    )
    assert board_layers[0]["kind"] == "board_band"
    assert board_layers[0]["rendered_now"] is True
    assert board_layers[0]["points"][0]["mid"] == 100.5
    html = build_interactive_chart_html(candles=[{"time": 1, "open": 1, "high": 1, "low": 1, "close": 1, "time_utc": "1970-01-01T00:00:01Z", "time_jst": "1970-01-01T09:00:01+09:00", "candle_index": 0}], mode="1分足", chart_context={"overlay_layers": layers + marker_layers + board_layers})
    assert "prediction_flow_preview" in html
    assert "execution_points" in html
    assert "board_depth_band" in html
    assert "warroom_board_bid_ask_band" in html
    assert "renderMarkerOverlay" in html
    assert "renderBoardBandOverlay" in html
    assert "renderOverlayLayers(chart, series);" in html



def test_gpt_copy_packet_render_shows_copy_range_guidance() -> None:
    text = json.dumps(
        {
            "schema_version": "warroom_gpt_review_packet.2026_07_05.v3_action_plan",
            "operator_focus": {
                "selected_chart_range": {
                    "history_rows": 813,
                    "visible_rows": 813,
                    "x_domain": {
                        "start": "2026-07-05T18:20:37Z",
                        "end": "2026-07-05T18:35:37Z",
                    },
                    "dhot_bootstrap": {
                        "source_path": "D:/btc_ts_hot/data/market_data/exchange=bitflyer/symbol=FX_BTC_JPY/type=market.trade/date=2026-07-05",
                    },
                }
            },
        },
        ensure_ascii=False,
    )
    fake = _CopyPacketFakeStreamlit()
    result = render_gpt_copy_packet(text, fake)
    assert result["copy_packet_rendered"] is True
    assert result["copy_status_summary"].startswith("GPTコピー準備:")
    assert fake.expander_titles == ["GPTへコピーするチャート範囲"]
    assert any("GPTコピー準備:" in line for line in fake.captions)
    assert any("GPTコピー対象範囲: 2026-07-05T18:20:37Z ～ 2026-07-05T18:35:37Z" in line for line in fake.captions)
    assert any("rows: history=813 / visible=813" in line for line in fake.captions)
    assert any("D-hot source:" in line for line in fake.captions)
    assert fake.text_areas[0]["label"] == "GPTに貼る軽量リクエスト"
