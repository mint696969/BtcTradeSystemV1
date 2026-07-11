# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_dhot_chart_series_binding_q29s.py
# desc: PS-Q29S guards for WarRoom v2 D-hot read-only chart series binding.

from __future__ import annotations

import json
import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.apps.operator_ui.prediction_warroom.panels.warroom_v2.chart_review_panel import build_warroom_v2_chart_review_panel_packet  # noqa: E402
from btcts.apps.operator_ui.prediction_warroom.panels.warroom_v2.market_chart_read_model import build_warroom_v2_market_chart_read_model  # noqa: E402
from btcts.apps.operator_ui.prediction_warroom.panels.warroom_v2.market_snapshot_read_model import build_warroom_v2_market_snapshot_dhot_read_model  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[6]
SERVICE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/market_state_service.py"
RENDERER_DIR = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/warroom_v2"
CHART_PANEL = RENDERER_DIR / "chart_review_panel.py"
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q29S_WARROOM_V2_DHOT_CHART_SERIES_BINDING_2026-07-02.md"


def _rows() -> list[dict]:
    return [
        {"collector_ts": "2026-07-02T00:00:00Z", "best_bid": 100.0, "best_ask": 102.0, "spread": 2.0, "mid_price": 101.0, "trust_state": "trusted", "continuity_state": "continuous", "interpretation_bucket": "allow_structural_use"},
        {"collector_ts": "2026-07-02T00:00:01Z", "best_bid": 101.0, "best_ask": 103.0, "spread": 2.0, "mid_price": 102.0, "trust_state": "trusted", "continuity_state": "continuous", "interpretation_bucket": "allow_structural_use"},
        {"collector_ts": "2026-07-02T00:00:02Z", "best_bid": 102.0, "best_ask": 104.0, "spread": 2.0, "mid_price": 103.0, "trust_state": "trusted", "continuity_state": "continuous", "interpretation_bucket": "allow_structural_use"},
    ]


def test_q29s_chart_read_model_builds_price_series_and_range_summary() -> None:
    packet = build_warroom_v2_market_chart_read_model(rows=_rows(), timeframe="5m")
    assert packet["chart_series_connected"] is True
    assert packet["actual_chart_series_bound"] is True
    assert packet["chart_row_count"] == 3
    assert packet["chart_rows"][0]["mid_price"] == 101.0
    assert packet["range_summary"]["open"] == 101.0
    assert packet["range_summary"]["close"] == 103.0
    assert packet["range_summary"]["change_pct"] is not None
    assert packet["push_connected"] is False
    assert packet["would_send_to_broker"] is False


def test_q29s_chart_review_packet_embeds_range_summary_and_keeps_safety() -> None:
    chart = build_warroom_v2_market_chart_read_model(rows=_rows(), timeframe="5m")
    source = build_warroom_v2_market_snapshot_dhot_read_model(row=_rows()[-1], diagnostics={"preferred_row_freshness": "LIVE", "preferred_row_age_sec": 1})
    packet = build_warroom_v2_chart_review_panel_packet(timeframe="5m", source_packet=source, chart_series_packet=chart)
    payload = json.loads(packet["json_preview"])
    assert packet["actual_chart_series_bound"] is True
    assert packet["chart_placeholder_only"] is False
    assert payload["range_summary"]["row_count"] == 3
    assert payload["range_summary"]["high"] == 103.0
    assert payload["market_snapshot"]["best_bid"] == 102.0
    assert payload["safety"]["read_only"] is True
    assert packet["push_connected"] is False


def test_q29s_market_state_service_exposes_bounded_recent_rows_public_api() -> None:
    text = SERVICE.read_text(encoding="utf-8-sig")
    assert "def load_recent_market_states(" in text
    assert "read_jsonl_tail_from_parts(latest_part.parent" in text
    assert "max_lines=max_lines" in text
    assert "max_bytes=max_bytes" in text
    assert "from btcts.core.sharded_jsonl import latest_part_path, read_jsonl_tail_from_parts" in text


def test_q29s_chart_panel_renders_line_chart_from_read_only_series() -> None:
    text = CHART_PANEL.read_text(encoding="utf-8-sig")
    assert "build_warroom_v2_market_chart_read_model" in text
    assert "st.line_chart" in text
    assert "chart_series_connected" in text
    assert "actual_chart_series_bound" in text
    assert "push_connected" in text


def test_q29s_renderer_files_remain_small_and_non_executing() -> None:
    forbidden = ("send_to_broker(", "append_ledger(", "ledger.append(", "write_runtime_artifact(", "write_prediction_artifact(", "write_status_artifact(", "websocket.", "sse.")
    for path in RENDERER_DIR.glob("*.py"):
        text = path.read_text(encoding="utf-8-sig")
        assert len(text.splitlines()) <= 120, f"renderer file is too large: {path}"
        for token in forbidden:
            assert token not in text, f"forbidden token {token!r} found in {path}"


def test_q29s_doc_records_chart_series_binding_boundary() -> None:
    text = DOC.read_text(encoding="utf-8-sig")
    assert "dhot_chart_series_read_only_binding=true" in text
    assert "actual_chart_series_bound=true" in text
    assert "push_connected=false" in text
    assert "not_enabling_websocket=true" in text
    assert "would_send_to_broker=false" in text
