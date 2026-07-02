# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_chart_readability_q29u.py
# desc: PS-Q29U guards for WarRoom v2 chart readability views.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.apps.operator_ui.prediction_warroom.panels.warroom_v2.chart_review_panel import build_warroom_v2_chart_review_panel_packet  # noqa: E402
from btcts.apps.operator_ui.prediction_warroom.panels.warroom_v2.market_chart_read_model import build_warroom_v2_market_chart_read_model  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[6]
RENDERER_DIR = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/warroom_v2"
CHART_PANEL = RENDERER_DIR / "chart_review_panel.py"
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q29U_WARROOM_V2_CHART_READABILITY_2026-07-02.md"


def _rows() -> list[dict]:
    return [
        {"collector_ts": "2026-07-02T00:00:00Z", "best_bid": 100.0, "best_ask": 102.0, "spread": 2.0, "mid_price": 101.0},
        {"collector_ts": "2026-07-02T00:00:01Z", "best_bid": 101.0, "best_ask": 103.0, "spread": 2.0, "mid_price": 102.0},
        {"collector_ts": "2026-07-02T00:00:02Z", "best_bid": 102.0, "best_ask": 104.0, "spread": 2.0, "mid_price": 103.0},
    ]


def test_q29u_packet_declares_chart_readability_mode_without_transport() -> None:
    chart = build_warroom_v2_market_chart_read_model(rows=_rows(), timeframe="5m")
    packet = build_warroom_v2_chart_review_panel_packet(timeframe="5m", chart_series_packet=chart)
    assert packet["chart_readability_mode"] == "price_and_bps"
    assert packet["actual_chart_series_bound"] is True
    assert packet["push_connected"] is False
    assert packet["websocket_enabled"] is False
    assert packet["sse_enabled"] is False
    assert packet["would_send_to_broker"] is False


def test_q29u_chart_panel_has_price_bps_and_range_metric_views() -> None:
    text = CHART_PANEL.read_text(encoding="utf-8-sig")
    assert "mid_change_bps" in text
    assert "spread_bps" in text
    assert "Change %" in text
    assert "Range %" in text
    assert text.count("st.line_chart") >= 2
    assert "price + bps views" in text


def test_q29u_renderer_files_remain_small_and_non_executing() -> None:
    forbidden = ("send_to_broker(", "append_ledger(", "ledger.append(", "write_runtime_artifact(", "write_prediction_artifact(", "write_status_artifact(", "websocket.", "sse.")
    for path in RENDERER_DIR.glob("*.py"):
        text = path.read_text(encoding="utf-8-sig")
        assert len(text.splitlines()) <= 120, f"renderer file is too large: {path}"
        for token in forbidden:
            assert token not in text, f"forbidden token {token!r} found in {path}"


def test_q29u_doc_records_readability_boundary() -> None:
    text = DOC.read_text(encoding="utf-8-sig")
    assert "chart_readability_mode=price_and_bps" in text
    assert "mid_change_bps_view=true" in text
    assert "spread_bps_view=true" in text
    assert "push_connected=false" in text
    assert "would_send_to_broker=false" in text
