# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_realtime_japanese_read_surface_q31x.py
# desc: PS-Q31X guards for WarRoom v2 realtime Japanese read surface WS display target contract. No socket and no UI mount.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.apps.operator_ui.prediction_warroom.v2 import (  # noqa: E402
    build_warroom_v2_realtime_japanese_read_surface_contract,
    build_warroom_v2_realtime_japanese_read_surface_packet,
)

REPO_ROOT = Path(__file__).resolve().parents[6]
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q31X_WARROOM_V2_REALTIME_JAPANESE_READ_SURFACE_WS_DISPLAY_TARGET_CONTRACT_2026-07-03.md"
TRANSPORT_DIR = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport"
WARROOM_PAGE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py"


def test_q31x_contract_records_current_small_goal_and_ws_first_update_target() -> None:
    packet = build_warroom_v2_realtime_japanese_read_surface_contract()
    assert packet["current_small_goal"] == "warroom_tab_ws_push_realtime_update_and_japanese_readability"
    assert packet["websocket_display_push_required"] is True
    assert packet["bidirectional_websocket_premise"] is True
    assert packet["read_model_push_plane"] == "server_to_warroom_ui"
    assert packet["japanese_readable_now_target"] is True
    assert packet["manual_trading_information_board"] is True
    assert packet["prediction_enrichment_deferred"] is True
    assert packet["trading_logic_deferred"] is True
    assert packet["browser_timer_polling_is_legacy_compat_only"] is True
    assert packet["websocket_enabled"] is False
    assert packet["order_intent_submitted"] is False


def test_q31x_packet_has_japanese_reading_order_for_current_warroom_tab() -> None:
    packet = build_warroom_v2_realtime_japanese_read_surface_packet()
    assert packet["packet_kind"] == "warroom_v2_realtime_japanese_read_surface_packet"
    assert packet["reading_order_labels_ja"] == [
        "地合い・安全境界",
        "現在価格・板・鮮度",
        "予測カード",
        "シナリオ日本語要約",
        "チャート確認",
        "操作判断メモ",
    ]
    assert packet["all_targets_have_ja_label"] is True
    assert packet["all_targets_are_ws_display_push_targets"] is True
    assert packet["japanese_readable_now_target"] is True


def test_q31x_display_targets_cover_market_prediction_scenario_and_chart() -> None:
    packet = build_warroom_v2_realtime_japanese_read_surface_packet()
    topics = set(packet["target_topics"])
    assert "warroom.current_state" in topics
    assert "warroom.alerts" in topics
    assert "warroom.safety" in topics
    assert packet["market_snapshot_topic"] == "warroom.market.snapshot"
    assert packet["chart_review_topic"] == "warroom.chart.review"
    assert packet["scenario_ja_topic"] == "warroom.prediction.scenario_ja"
    assert len(packet["prediction_card_topics"]) >= 7
    labels = {row["topic"]: row["label_ja"] for row in packet["targets"]}
    assert labels["warroom.market.snapshot"] == "現在価格・板・鮮度"
    assert labels["warroom.prediction.market_regime"] == "地合い予測"
    assert labels["warroom.prediction.scenario_ja"] == "シナリオ日本語要約"


def test_q31x_no_new_polling_or_ui_mount_is_introduced() -> None:
    packet = build_warroom_v2_realtime_japanese_read_surface_packet()
    assert packet["browser_timer_polling_is_legacy_compat_only"] is True
    assert packet["browser_timer_reload_replacement_target"] is True
    assert packet["no_new_polling_fallback"] is True
    assert packet["no_browser_timer_reload_introduced"] is True
    assert packet["streamlit_render_allowed"] is False
    assert packet["warroom_page_ui_switch"] is False
    assert packet["websocket_enabled"] is False
    assert packet["socket_opened"] is False
    assert packet["external_message_send_enabled"] is False
    assert packet["would_send_to_broker"] is False


def test_q31x_doc_modules_and_warroom_page_preserve_no_side_effect_boundary() -> None:
    text = DOC.read_text(encoding="utf-8-sig")
    assert "current_small_goal=warroom_tab_ws_push_realtime_update_and_japanese_readability" in text
    assert "websocket_display_push_required=true" in text
    assert "japanese_readable_now_target=true" in text
    assert "prediction_enrichment_deferred=true" in text
    assert "trading_logic_deferred=true" in text
    assert "browser_timer_polling_is_legacy_compat_only=true" in text
    assert "not_using_polling_fallback=true" in text
    assert "not_using_browser_timer_reload=true" in text
    page = WARROOM_PAGE.read_text(encoding="utf-8-sig")
    assert "build_warroom_v2_realtime_japanese_read_surface_packet" not in page
    assert "WARROOM_V2_REALTIME_READ_SURFACE_VERSION" not in page
    forbidden = (
        "import streamlit",
        "from streamlit",
        "websocket.",
        "sse.",
        "polling_loop(",
        "browser_timer_reload(",
        "send_to_broker(",
        "submit_order(",
        "append_ledger(",
        "write_runtime_artifact(",
        "write_prediction_artifact(",
        "run_prediction(",
        "invoke_classifier(",
        "st.write(",
        "st.metric(",
        "st.caption(",
        "D:" + chr(92),
        "E:" + chr(92),
    )
    for path in TRANSPORT_DIR.glob("*.py"):
        body = path.read_text(encoding="utf-8-sig")
        assert len(body.splitlines()) <= 220, f"transport file too large: {path}"
        for token in forbidden:
            assert token not in body, f"forbidden token {token!r} found in {path}"
