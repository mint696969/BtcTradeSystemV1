# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_market_snapshot_data_quality_badge_policy_q34b.py
# desc: PS-Q34B guards for market_snapshot_strip data-quality badge policy metadata. Default-off/no-socket/read-only.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.apps.operator_ui.prediction_warroom.panels.warroom_v2.market_snapshot_read_model import build_warroom_v2_market_snapshot_dhot_read_model  # noqa: E402
from btcts.apps.operator_ui.prediction_warroom.panels.warroom_v2.market_snapshot_strip import build_warroom_v2_market_snapshot_strip_packet  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[6]
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q34B_WARROOM_V2_MARKET_SNAPSHOT_STRIP_DATA_QUALITY_BADGE_POLICY_DEFAULT_OFF_NO_SOCKET_2026-07-04.md"
STRIP = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/warroom_v2/market_snapshot_strip.py"
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
    }


def _strip_for(*, bid: float = 100.0, ask: float = 101.0, spread: float = 1.0) -> dict[str, object]:
    source = build_warroom_v2_market_snapshot_dhot_read_model(row=_row(bid=bid, ask=ask, spread=spread), diagnostics={"preferred_row_freshness": "LIVE"})
    return build_warroom_v2_market_snapshot_strip_packet(source_packet=source)


def test_q34b_ok_quality_policy_is_default_hidden_normal_badge_metadata() -> None:
    strip = _strip_for()
    policy = strip["data_quality_badge_policy"]
    assert strip["renderer_version"] == "prediction_warroom.v2.market_snapshot_strip_renderer.ps_q34b.v1"
    assert strip["data_quality_badge_policy_version"] == "prediction_warroom.v2.market_snapshot_data_quality_badge_policy.ps_q34b.v1"
    assert strip["market_data_quality_state"] == "OK"
    assert policy["state"] == "OK"
    assert policy["severity"] == "normal"
    assert policy["label_ja"] == "板品質: 正常"
    assert policy["badge_visible_default"] is False
    assert policy["badge_render_allowed_default"] is False
    assert policy["streamlit_badge_invoked"] is False
    assert policy["would_block_trading"] is False
    assert strip["runtime_connected"] is False
    assert strip["push_connected"] is False
    assert strip["would_send_to_broker"] is False


def test_q34b_crossed_book_policy_is_danger_but_metadata_only() -> None:
    strip = _strip_for(bid=10077924.0, ask=10077346.0, spread=-578.0)
    policy = strip["data_quality_badge_policy"]
    assert strip["market_data_quality_state"] == "CROSSED_BOOK"
    assert policy["state"] == "CROSSED_BOOK"
    assert policy["severity"] == "danger"
    assert policy["badge_token"] == "crossed_book"
    assert policy["label_ja"] == "板品質: 交差"
    assert policy["operator_guidance_ja"] == "参考表示のみ。売買判断へ直結しない。"
    assert policy["badge_visible_default"] is False
    assert policy["streamlit_badge_invoked"] is False
    assert strip["data_quality_badge_only"] is True


def test_q34b_spread_sign_and_mismatch_policy_are_warning_metadata() -> None:
    invalid = _strip_for(bid=100.0, ask=101.0, spread=-1.0)["data_quality_badge_policy"]
    mismatch = _strip_for(bid=100.0, ask=101.0, spread=3.0)["data_quality_badge_policy"]
    assert invalid["state"] == "SPREAD_SIGN_INVALID"
    assert invalid["severity"] == "warning"
    assert invalid["badge_token"] == "spread_sign_invalid"
    assert mismatch["state"] == "SPREAD_MISMATCH"
    assert mismatch["severity"] == "warning"
    assert mismatch["badge_token"] == "spread_mismatch"
    assert invalid["badge_visible_default"] is False
    assert mismatch["badge_render_allowed_default"] is False


def test_q34b_strip_field_contract_and_diagnostics_metadata_stay_read_only() -> None:
    strip = _strip_for(bid=100.0, ask=99.0, spread=-1.0)
    assert strip["field_count"] == 12
    assert "data_quality_badge_policy" not in strip["field_keys"]
    assert "market_data_quality_state" not in strip["field_keys"]
    assert strip["data_quality_badge_policy"]["visual_policy_only"] is True
    assert strip["data_quality_badge_policy"]["streamlit_badge_invoked"] is False
    assert strip["websocket_enabled"] is False
    assert strip["sse_enabled"] is False
    assert strip["runtime_connected"] is False
    assert strip["push_connected"] is False
    assert strip["would_send_to_broker"] is False


def test_q34b_doc_and_renderer_files_preserve_no_page_mount_socket_boundary() -> None:
    doc = DOC.read_text(encoding="utf-8-sig")
    assert "data_quality_badge_policy_default_visible=false" in doc
    assert "badge_render_allowed_default=false" in doc
    assert "not_modifying_warroom_page=true" in doc
    assert "not_opening_socket=true" in doc
    page = WARROOM_PAGE.read_text(encoding="utf-8-sig")
    assert "market_snapshot_data_quality_badge_policy_q34b" not in page
    assert "板品質: 交差" not in page
    strip_text = STRIP.read_text(encoding="utf-8-sig")
    assert "st.badge" not in strip_text
    assert "st.error" not in strip_text
    forbidden = ("send_to_broker(", "append_ledger(", "ledger.append(", "write_runtime_artifact(", "write_prediction_artifact(", "write_status_artifact(", "websocket.", "sse.")
    for path in RENDERER_DIR.glob("*.py"):
        body = path.read_text(encoding="utf-8-sig")
        assert len(body.splitlines()) <= 120, f"renderer file too large: {path}"
        for token in forbidden:
            assert token not in body, f"forbidden token {token!r} found in {path}"
