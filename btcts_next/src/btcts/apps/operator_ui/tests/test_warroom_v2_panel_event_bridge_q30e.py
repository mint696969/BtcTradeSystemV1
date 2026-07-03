# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_panel_event_bridge_q30e.py
# desc: PS-Q30E guards for adapting WarRoom v2 panel packets into read-model event bridge payloads.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.apps.operator_ui.prediction_warroom.panels.warroom_v2 import (  # noqa: E402
    WARROOM_V2_PANEL_EVENT_BRIDGE_ADAPTER_VERSION,
    build_warroom_v2_chart_review_panel_packet,
    build_warroom_v2_market_snapshot_strip_packet,
    build_warroom_v2_panel_event_bridge_packet,
    chart_review_event_payload_from_panel_packet,
    market_snapshot_event_payload_from_strip_packet,
)
from btcts.apps.operator_ui.prediction_warroom.panels.warroom_v2_shell_preview_panel import build_warroom_v2_shell_preview_panel_packet  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[6]
RENDERER_DIR = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/warroom_v2"
SHELL = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/warroom_v2_shell_preview_panel.py"
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q30E_WARROOM_V2_PANEL_EVENT_BRIDGE_2026-07-02.md"


def test_q30e_market_snapshot_packet_adapts_to_event_payload() -> None:
    packet = build_warroom_v2_market_snapshot_strip_packet(source_packet={"data_connected": True, "display_values": {"market": "BTC-FX-JPY", "ltp": "9,900,000", "data_state": "LIVE"}, "raw_values": {"ltp": 9900000}})
    payload = market_snapshot_event_payload_from_strip_packet(packet)
    assert payload["payload_schema"] == "warroom.market_snapshot_strip.event_payload.v1"
    assert payload["market"] == "BTC-FX-JPY"
    assert payload["fields"]["ltp"] == "9,900,000"
    assert payload["raw_values"] == {"ltp": 9900000}
    assert payload["would_send_to_broker"] is False


def test_q30e_chart_review_packet_adapts_to_event_payload() -> None:
    packet = build_warroom_v2_chart_review_panel_packet(timeframe="5m", source_packet={"data_connected": True, "raw_values": {"ltp": 1}}, chart_series_packet={"chart_series_connected": True, "chart_rows": [{"x": 1}], "range_summary": {"row_count": 1}, "chart_window": {"timeframe": "5m", "row_limit": 240, "window_policy": "bounded_recent_rows"}})
    payload = chart_review_event_payload_from_panel_packet(packet)
    assert payload["payload_schema"] == "warroom.chart_review_panel.event_payload.v1"
    assert payload["selected_timeframe"] == "5m"
    assert payload["chart_row_count"] == 1
    assert payload["range_summary"]["row_count"] == 1
    assert payload["would_send_to_broker"] is False


def test_q30e_panel_event_bridge_builds_both_events_without_transport() -> None:
    market = build_warroom_v2_market_snapshot_strip_packet(source_packet={"data_connected": True, "display_values": {"ltp": "1"}, "raw_values": {"ltp": 1}})
    chart = build_warroom_v2_chart_review_panel_packet(chart_series_packet={"chart_series_connected": False})
    packet = build_warroom_v2_panel_event_bridge_packet(market_snapshot_packet=market, chart_review_packet=chart, generated_at="2026-07-02T12:00:00Z")
    assert packet["panel_event_bridge_adapter_version"] == WARROOM_V2_PANEL_EVENT_BRIDGE_ADAPTER_VERSION
    assert packet["market_snapshot_event"]["topic"] == "warroom.market.snapshot"
    assert packet["chart_review_event"]["topic"] == "warroom.chart.review"
    assert packet["market_snapshot_event"]["envelope"]["ui_patch_unit"] == "widget_dom_region"
    assert packet["transport_implemented_now"] is False
    assert packet["bridge_reads_dhot"] is False
    assert packet["would_send_to_broker"] is False


def test_q30e_shell_panel_packet_includes_event_bridge_without_ui_decoration() -> None:
    packet = build_warroom_v2_shell_preview_panel_packet(source_packet={"data_connected": True, "display_values": {"ltp": "1"}, "raw_values": {"ltp": 1}})
    assert packet["panel_packet_event_bridge_bound"] is True
    assert packet["read_model_event_bridge"]["market_snapshot_event"]["topic"] == "warroom.market.snapshot"
    text = SHELL.read_text(encoding="utf-8-sig")
    assert "read_model_event_bridge" in text
    assert "render_warroom_v2_market_snapshot_strip(source_packet=source)" in text
    assert "render_warroom_v2_chart_review_panel(source_packet=source)" in text
    assert "st.caption(\"Event bridge" not in text


def test_q30e_renderer_files_remain_small_and_non_executing() -> None:
    forbidden = ("send_to_broker(", "append_ledger(", "ledger.append(", "write_runtime_artifact(", "write_prediction_artifact(", "write_status_artifact(", "websocket.", "sse.")
    for path in RENDERER_DIR.glob("*.py"):
        text = path.read_text(encoding="utf-8-sig")
        assert len(text.splitlines()) <= 120, f"renderer file is too large: {path}"
        for token in forbidden:
            assert token not in text, f"forbidden token {token!r} found in {path}"


def test_q30e_doc_records_panel_event_bridge_boundary() -> None:
    text = DOC.read_text(encoding="utf-8-sig")
    assert "panel_packet_event_bridge=true" in text
    assert "input_kind=existing_panel_packets" in text
    assert "output_kind=read_model_event_bridge_packet" in text
    assert "transport_implemented_now=false" in text
    assert "would_send_to_broker=false" in text
