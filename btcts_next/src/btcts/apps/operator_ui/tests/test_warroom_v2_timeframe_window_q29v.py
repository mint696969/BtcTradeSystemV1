# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_timeframe_window_q29v.py
# desc: PS-Q29V guards for WarRoom v2 timeframe-aware chart windows.

from __future__ import annotations

import json
import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.apps.operator_ui.prediction_warroom.panels.warroom_v2.chart_review_panel import build_warroom_v2_chart_review_panel_packet  # noqa: E402
from btcts.apps.operator_ui.prediction_warroom.panels.warroom_v2.market_chart_read_model import build_warroom_v2_market_chart_read_model, chart_window_rows_for_timeframe  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[6]
RENDERER_DIR = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/warroom_v2"
CHART_PANEL = RENDERER_DIR / "chart_review_panel.py"
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q29V_WARROOM_V2_TIMEFRAME_WINDOW_2026-07-02.md"


def _rows(n: int = 100) -> list[dict]:
    return [{"collector_ts": f"2026-07-02T00:{i//60:02d}:{i%60:02d}Z", "best_bid": 100.0 + i, "best_ask": 102.0 + i, "spread": 2.0, "mid_price": 101.0 + i} for i in range(n)]


def test_q29v_timeframe_maps_to_bounded_row_windows() -> None:
    assert chart_window_rows_for_timeframe("1m") == 60
    assert chart_window_rows_for_timeframe("5m") == 240
    assert chart_window_rows_for_timeframe("15m") == 720
    assert chart_window_rows_for_timeframe("1h") == 1440
    assert chart_window_rows_for_timeframe("1d") == 2880
    assert chart_window_rows_for_timeframe("unknown") == 240


def test_q29v_chart_read_model_applies_timeframe_window_to_rows() -> None:
    packet = build_warroom_v2_market_chart_read_model(rows=_rows(100), timeframe="1m")
    assert packet["chart_window"] == {"timeframe": "1m", "row_limit": 60, "window_policy": "bounded_recent_rows"}
    assert packet["chart_row_count"] == 60
    assert packet["range_summary"]["row_count"] == 60
    assert packet["push_connected"] is False


def test_q29v_chart_packet_embeds_chart_window_in_json_and_markdown() -> None:
    chart = build_warroom_v2_market_chart_read_model(rows=_rows(100), timeframe="1m")
    packet = build_warroom_v2_chart_review_panel_packet(timeframe="1m", chart_series_packet=chart)
    payload = json.loads(packet["json_preview"])
    assert packet["timeframe_window_binding"] is True
    assert packet["chart_window"]["row_limit"] == 60
    assert payload["chart_window"]["timeframe"] == "1m"
    assert "chart_window: 1m / row_limit=60" in packet["markdown_preview"]
    assert packet["push_connected"] is False


def test_q29v_chart_panel_displays_window_caption() -> None:
    text = CHART_PANEL.read_text(encoding="utf-8-sig")
    assert "timeframe-aware window" in text
    assert "chart window:" in text
    assert "row_limit" in text
    assert "timeframe_window_binding" in text


def test_q29v_renderer_files_remain_small_and_non_executing() -> None:
    forbidden = ("send_to_broker(", "append_ledger(", "ledger.append(", "write_runtime_artifact(", "write_prediction_artifact(", "write_status_artifact(", "websocket.", "sse.")
    for path in RENDERER_DIR.glob("*.py"):
        text = path.read_text(encoding="utf-8-sig")
        assert len(text.splitlines()) <= 120, f"renderer file is too large: {path}"
        for token in forbidden:
            assert token not in text, f"forbidden token {token!r} found in {path}"


def test_q29v_doc_records_timeframe_window_boundary() -> None:
    text = DOC.read_text(encoding="utf-8-sig")
    assert "timeframe_window_binding=true" in text
    assert "1m_row_limit=60" in text
    assert "1d_row_limit=2880" in text
    assert "push_connected=false" in text
    assert "would_send_to_broker=false" in text
