# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_dhot_market_snapshot_binding_q29r.py
# desc: PS-Q29R guards for WarRoom v2 D-hot read-only market snapshot binding.

from __future__ import annotations

import json
import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.apps.operator_ui.prediction_warroom.panels.warroom_v2.chart_review_panel import build_warroom_v2_chart_review_panel_packet  # noqa: E402
from btcts.apps.operator_ui.prediction_warroom.panels.warroom_v2.market_snapshot_read_model import build_warroom_v2_market_snapshot_dhot_read_model  # noqa: E402
from btcts.apps.operator_ui.prediction_warroom.panels.warroom_v2.market_snapshot_strip import build_warroom_v2_market_snapshot_strip_packet  # noqa: E402
from btcts.apps.operator_ui.prediction_warroom.panels.warroom_v2_shell_preview_panel import build_warroom_v2_shell_preview_panel_packet  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[6]
RENDERER_DIR = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/warroom_v2"
PANEL = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/warroom_v2_shell_preview_panel.py"
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q29R_WARROOM_V2_DHOT_MARKET_SNAPSHOT_BINDING_2026-07-02.md"


def _source() -> dict:
    row = {"symbol_raw": "FX_BTC_JPY", "collector_ts": "2099-01-01T00:00:00Z", "best_bid": 9764512.0, "best_ask": 9765366.0, "spread": 854.0, "mid_price": 9764939.0, "trust_state": "trusted", "interpretation_bucket": "allow_structural_use", "continuity_state": "continuous", "imbalance_summary": {"near_size_imbalance": 0.24}, "near_zone_liquidity_summary": {"bid_size_total": 3.36, "ask_size_total": 2.04}}
    diag = {"preferred_row_freshness": "LIVE", "preferred_row_age_sec": 2.5, "latest_part_exists": True}
    return build_warroom_v2_market_snapshot_dhot_read_model(row=row, diagnostics=diag)


def test_q29r_dhot_read_model_maps_market_overview_to_manual_trade_fields() -> None:
    source = _source()
    assert source["ok"] is True and source["explicit_dhot_read_only_binding"] is True
    assert source["data_connected"] is True and source["runtime_connected"] is False and source["push_connected"] is False
    assert source["would_send_to_broker"] is False
    raw, display = source["raw_values"], source["display_values"]
    assert raw["market"] == "BTC-FX-JPY"
    assert raw["best_bid"] == 9764512.0 and raw["best_ask"] == 9765366.0
    assert raw["spread_bps"] is not None and raw["board_imbalance"] == 0.24
    assert display["data_state"] == "LIVE" and display["spread"].endswith("bps")


def test_q29r_market_snapshot_strip_uses_dhot_source_without_push() -> None:
    packet = build_warroom_v2_market_snapshot_strip_packet(source_packet=_source())
    values = {field["key"]: field["value"] for field in packet["fields"]}
    assert packet["data_connected"] is True and packet["placeholder_only"] is False
    assert values["market"] == "BTC-FX-JPY"
    assert values["best_bid"] == "9,764,512" and values["best_ask"] == "9,765,366"
    assert values["data_state"] == "LIVE"
    assert packet["push_connected"] is False and packet["runtime_connected"] is False


def test_q29r_chart_review_packet_embeds_current_market_snapshot_read_only() -> None:
    packet = build_warroom_v2_chart_review_panel_packet(timeframe="5m", source_packet=_source())
    payload = json.loads(packet["json_preview"])
    assert packet["data_connected"] is True and packet["chart_placeholder_only"] is True
    assert payload["market_snapshot"]["best_bid"] == 9764512.0
    assert payload["market_snapshot"]["best_ask"] == 9765366.0
    assert payload["market_snapshot"]["data_state"] == "LIVE"
    assert payload["safety"]["read_only"] is True and payload["safety"]["push_connected"] is False


def test_q29r_default_packet_remains_q29q_compatible_but_can_accept_dhot_source() -> None:
    default = build_warroom_v2_shell_preview_panel_packet()
    connected = build_warroom_v2_shell_preview_panel_packet(source_packet=_source())
    assert default["data_connected"] is False
    assert connected["data_connected"] is True
    assert connected["market_snapshot_strip"]["data_connected"] is True
    assert connected["chart_review_panel"]["data_connected"] is True


def test_q29r_panel_wires_render_path_to_dhot_source() -> None:
    text = PANEL.read_text(encoding="utf-8-sig")
    assert "source = build_warroom_v2_market_snapshot_dhot_read_model()" in text
    assert "build_warroom_v2_shell_preview_panel_packet(page_mount_packet=page_mount_packet, source_packet=source)" in text
    assert "render_warroom_v2_market_snapshot_strip(source_packet=source)" in text
    assert "render_warroom_v2_chart_review_panel(source_packet=source)" in text


def test_q29r_renderer_files_remain_small_and_non_executing() -> None:
    forbidden = ("send_to_broker(", "append_ledger(", "ledger.append(", "write_runtime_artifact(", "write_prediction_artifact(", "write_status_artifact(", "websocket.", "sse.")
    for path in RENDERER_DIR.glob("*.py"):
        text = path.read_text(encoding="utf-8-sig")
        assert len(text.splitlines()) <= 120, f"renderer file is too large: {path}"
        for token in forbidden:
            assert token not in text, f"forbidden token {token!r} found in {path}"


def test_q29r_doc_records_read_only_binding_boundary() -> None:
    text = DOC.read_text(encoding="utf-8-sig")
    assert "dhot_market_snapshot_read_only_binding=true" in text
    assert "market_snapshot_values_bound=true" in text
    assert "chart_packet_market_snapshot_bound=true" in text
    assert "push_connected=false" in text
    assert "not_enabling_websocket=true" in text
    assert "would_send_to_broker=false" in text
