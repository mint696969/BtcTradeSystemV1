# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_market_snapshot_read_model_data_quality_q34a.py
# desc: PS-Q34A guards for market_snapshot_strip read-model data quality diagnostics. Default-off/no-socket/read-only.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.apps.operator_ui.prediction_warroom.panels.warroom_v2.market_snapshot_read_model import build_warroom_v2_market_snapshot_dhot_read_model  # noqa: E402
from btcts.apps.operator_ui.prediction_warroom.panels.warroom_v2.market_snapshot_strip import build_warroom_v2_market_snapshot_strip_packet  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[6]
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q34A_WARROOM_V2_MARKET_SNAPSHOT_STRIP_READ_MODEL_DATA_QUALITY_DIAGNOSTICS_DEFAULT_OFF_NO_SOCKET_2026-07-04.md"
RENDERER_DIR = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/warroom_v2"
WARROOM_PAGE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py"


def _row(*, bid: float = 100.0, ask: float = 101.0, spread: float = 1.0) -> dict[str, object]:
    return {
        "symbol_raw": "FX_BTC_JPY",
        "collector_ts": "2099-01-01T00:00:00Z",
        "best_bid": bid,
        "best_ask": ask,
        "spread": spread,
        "mid_price": (bid + ask) / 2.0,
        "trust_state": "trusted",
        "interpretation_bucket": "allow_structural_use",
        "continuity_state": "continuous",
        "imbalance_summary": {"near_size_imbalance": 0.1},
        "near_zone_liquidity_summary": {"bid_size_total": 1.0, "ask_size_total": 2.0},
    }


def test_q34a_read_model_marks_normal_book_quality_ok_without_transport() -> None:
    packet = build_warroom_v2_market_snapshot_dhot_read_model(row=_row(), diagnostics={"preferred_row_freshness": "LIVE", "preferred_row_age_sec": 1.0})
    quality = packet["data_quality_diagnostics"]
    assert packet["read_model_version"] == "prediction_warroom.v2.market_snapshot_read_model.ps_q34a.v1"
    assert quality["bid_ask_crossed"] is False
    assert quality["spread_sign_valid"] is True
    assert quality["spread_matches_best_bid_ask"] is True
    assert quality["market_data_quality_state"] == "OK"
    assert packet["raw_values"]["market_data_quality_state"] == "OK"
    assert packet["display_values"]["market_data_quality_state"] == "OK"
    assert packet["runtime_connected"] is False
    assert packet["push_connected"] is False
    assert packet["would_send_to_broker"] is False


def test_q34a_read_model_exposes_crossed_book_and_negative_spread_from_dhot_shape() -> None:
    packet = build_warroom_v2_market_snapshot_dhot_read_model(row=_row(bid=10077924.0, ask=10077346.0, spread=-578.0), diagnostics={"preferred_row_freshness": "LIVE"})
    quality = packet["data_quality_diagnostics"]
    assert quality["best_bid"] == 10077924.0
    assert quality["best_ask"] == 10077346.0
    assert quality["reported_spread"] == -578.0
    assert quality["computed_spread"] == -578.0
    assert quality["bid_ask_crossed"] is True
    assert quality["spread_sign_valid"] is False
    assert quality["spread_matches_best_bid_ask"] is True
    assert quality["market_data_quality_state"] == "CROSSED_BOOK"
    assert packet["raw_values"]["bid_ask_crossed"] is True
    assert packet["raw_values"]["spread_sign_valid"] is False
    assert packet["display_values"]["data_quality"] == "CROSSED_BOOK"


def test_q34a_read_model_marks_spread_sign_invalid_without_hiding_values() -> None:
    packet = build_warroom_v2_market_snapshot_dhot_read_model(row=_row(bid=100.0, ask=101.0, spread=-1.0), diagnostics={})
    quality = packet["data_quality_diagnostics"]
    assert quality["bid_ask_crossed"] is False
    assert quality["spread_sign_valid"] is False
    assert quality["spread_matches_best_bid_ask"] is False
    assert quality["market_data_quality_state"] == "SPREAD_SIGN_INVALID"
    assert packet["raw_values"]["spread"] == -1.0
    assert packet["display_values"]["spread"].startswith("-1")


def test_q34a_market_snapshot_strip_carries_diagnostics_without_changing_field_contract() -> None:
    source = build_warroom_v2_market_snapshot_dhot_read_model(row=_row(bid=100.0, ask=99.0, spread=-1.0), diagnostics={})
    strip = build_warroom_v2_market_snapshot_strip_packet(source_packet=source)
    assert strip["field_count"] == 12
    assert "market_data_quality_state" not in strip["field_keys"]
    assert strip["data_quality_diagnostics"]["bid_ask_crossed"] is True
    assert strip["market_data_quality_state"] == "CROSSED_BOOK"
    assert strip["data_quality_badge_only"] is True
    assert strip["runtime_connected"] is False
    assert strip["push_connected"] is False
    assert strip["would_send_to_broker"] is False


def test_q34a_doc_and_renderer_files_preserve_no_socket_page_mount_boundary() -> None:
    text = DOC.read_text(encoding="utf-8-sig")
    assert "bid_ask_crossed_diagnostic=true" in text
    assert "spread_sign_valid_diagnostic=true" in text
    assert "not_opening_socket=true" in text
    assert "not_modifying_warroom_page=true" in text
    page = WARROOM_PAGE.read_text(encoding="utf-8-sig")
    assert "market_snapshot_read_model_data_quality_q34a" not in page
    assert "bid_ask_crossed" not in page
    forbidden = ("send_to_broker(", "append_ledger(", "ledger.append(", "write_runtime_artifact(", "write_prediction_artifact(", "write_status_artifact(", "websocket.", "sse.")
    for path in RENDERER_DIR.glob("*.py"):
        body = path.read_text(encoding="utf-8-sig")
        assert len(body.splitlines()) <= 120, f"renderer file too large: {path}"
        for token in forbidden:
            assert token not in body, f"forbidden token {token!r} found in {path}"
