# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_chart_review_market_snapshot_contract_q29q.py
# desc: PS-Q29Q guards for WarRoom v2 market snapshot and chart review contract.

from __future__ import annotations

import json
import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.apps.operator_ui.prediction_warroom.panels.warroom_v2 import (  # noqa: E402
    build_warroom_v2_chart_review_panel_packet,
    build_warroom_v2_market_snapshot_strip_packet,
)
from btcts.apps.operator_ui.prediction_warroom.panels.warroom_v2_shell_preview_panel import build_warroom_v2_shell_preview_panel_packet  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[6]
RENDERER_DIR = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/warroom_v2"
PANEL = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/warroom_v2_shell_preview_panel.py"
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q29Q_WARROOM_V2_CHART_REVIEW_MARKET_SNAPSHOT_CONTRACT_2026-07-02.md"


def test_q29q_shell_packet_mounts_snapshot_above_cards_and_chart_at_bottom() -> None:
    packet = build_warroom_v2_shell_preview_panel_packet()
    assert packet["market_snapshot_strip_above_prediction_cards"] is True
    assert packet["chart_review_panel_bottom"] is True
    assert packet["market_snapshot_strip"]["placement"] == "above_prediction_cards"
    assert packet["chart_review_panel"]["placement"] == "bottom_of_warroom_v2"
    assert packet["push_ready"] is True
    assert packet["auto_refresh_ready"] is True
    assert packet["data_connected"] is False
    assert packet["runtime_connected"] is False
    assert packet["push_connected"] is False


def test_q29q_render_order_is_top_snapshot_cards_scenario_debug_chart() -> None:
    text = PANEL.read_text(encoding="utf-8-sig")
    calls = {
        "top": text.index("    render_warroom_v2_top_bar("),
        "snapshot": text.index("    render_warroom_v2_market_snapshot_strip("),
        "cards": text.index("    render_warroom_v2_prediction_cards("),
        "scenario": text.index("    render_warroom_v2_scenario_area("),
        "debug": text.index("    render_warroom_v2_debug_preview("),
        "chart": text.index("    render_warroom_v2_chart_review_panel("),
    }
    assert calls["top"] < calls["snapshot"] < calls["cards"] < calls["scenario"] < calls["debug"] < calls["chart"]
    assert len(text.splitlines()) <= 90


def test_q29q_market_snapshot_fields_cover_manual_trade_reference_baseline() -> None:
    packet = build_warroom_v2_market_snapshot_strip_packet()
    assert packet["field_count"] == 12
    for key in ("market", "ltp", "best_bid", "best_ask", "spread", "data_age_sec", "data_state", "change_1m_pct", "change_5m_pct", "change_15m_pct", "change_1h_pct", "invalidation_watch"):
        assert key in packet["field_keys"]
    assert packet["data_state"] == "NO_DATA"
    assert packet["invalidation_watch"] == "NO_DATA"
    assert "board_imbalance" in packet["secondary_ready_fields"]
    assert "trade_density" in packet["secondary_ready_fields"]
    assert packet["freshness_badge_only"] is True
    assert packet["price_neutral_display"] is True
    assert packet["push_ready"] is True
    assert packet["push_connected"] is False


def test_q29q_chart_review_packet_has_markdown_json_and_structured_empty_layers() -> None:
    packet = build_warroom_v2_chart_review_panel_packet(timeframe="15m")
    payload = json.loads(packet["json_preview"])
    assert packet["schema_version"] == "warroom_chart_review.v1"
    assert packet["selected_timeframe"] == "15m"
    assert payload["selection"] == {"clicked_at": None, "range_start": None, "range_end": None}
    assert payload["annotations"] == {"predictions": [], "orderbook": [], "orders": [], "manual": []}
    assert payload["market_snapshot"]["data_state"] == "NO_DATA"
    assert payload["safety"]["read_only"] is True
    assert payload["safety"]["runtime_connected"] is False
    assert "# WarRoom Chart Review Packet" in packet["markdown_preview"]
    assert "## Market Snapshot" in packet["markdown_preview"]
    assert packet["copy_for_gpt_ready"] is True
    assert packet["push_ready"] is True
    assert packet["data_connected"] is False


def test_q29q_files_are_small_and_side_effect_free() -> None:
    forbidden = (
        "D:" + "\\",
        "E:" + "\\",
        "build_market_regime_source_snapshot(",
        "classify_market_regime_feature_bundle(",
        "send_to_broker(",
        "append_ledger(",
        "ledger.append(",
        "write_runtime_artifact(",
        "write_prediction_artifact(",
        "write_status_artifact(",
        "websocket.",
        "sse.",
    )
    for path in RENDERER_DIR.glob("*.py"):
        text = path.read_text(encoding="utf-8-sig")
        assert len(text.splitlines()) <= 120, f"renderer file is too large: {path}"
        for token in forbidden:
            assert token not in text, f"forbidden token {token!r} found in {path}"


def test_q29q_doc_records_push_staging_and_non_goals() -> None:
    text = DOC.read_text(encoding="utf-8-sig")
    assert "market_snapshot_strip_above_prediction_cards=true" in text
    assert "chart_review_panel_bottom=true" in text
    assert "push_ready=true" in text
    assert "auto_refresh_ready=true" in text
    assert "push_connected=false" in text
    assert "data_connected=false" in text
    assert "not_connecting_dhot=true" in text
    assert "not_enabling_websocket=true" in text
    assert "not_touching_autotrade_broker_ledger_mode_parameter=true" in text
