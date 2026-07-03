# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_ws_display_connection_status_observation_q32d.py
# desc: PS-Q32D guards for hidden session_state WS display connection status observation. No UI mount and no socket open.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.apps.operator_ui.prediction_warroom.v2 import (  # noqa: E402
    WARROOM_V2_WS_DISPLAY_CONNECTION_STATUS_OBSERVATION_STATE_KEY,
    build_warroom_v2_ws_display_connection_status_observation_contract,
    build_warroom_v2_ws_display_connection_status_observation_packet,
)

REPO_ROOT = Path(__file__).resolve().parents[6]
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q32D_WARROOM_V2_WS_DISPLAY_CONNECTION_STATUS_OBSERVATION_TO_HIDDEN_SESSION_STATE_NO_UI_MOUNT_2026-07-03.md"
TRANSPORT_DIR = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport"
WARROOM_PAGE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py"


def _message(topic: str = "warroom.market.snapshot", widget_id: str = "market_snapshot_strip", sequence: int = 1) -> dict[str, object]:
    return {
        "message_type": "warroom_v2_widget_update",
        "payload_kind": "widget_update_event_envelope",
        "topic": topic,
        "widget_id": widget_id,
        "sequence": sequence,
        "generated_at": "2026-07-03T00:00:00Z",
        "ui_patch_unit": "widget_dom_region",
        "broad_page_reload_required": False,
        "envelope": {"topic": topic, "widget_id": widget_id, "sequence": sequence},
        "json_payload": "{}",
    }


def test_q32d_contract_is_hidden_state_for_ws_connection_status() -> None:
    packet = build_warroom_v2_ws_display_connection_status_observation_contract()
    assert packet["state_key"] == WARROOM_V2_WS_DISPLAY_CONNECTION_STATUS_OBSERVATION_STATE_KEY
    assert packet["observation_kind"] == "warroom_v2_hidden_ws_display_connection_status_observation_packet"
    assert packet["current_small_goal"] == "warroom_tab_ws_push_realtime_update_and_japanese_readability"
    assert packet["warroom_status_line_allowed_later"] is True
    assert packet["warroom_status_line_visible_now"] is False
    assert packet["warroom_status_line_mounted_now"] is False
    assert packet["compact_status_only"] is True
    assert packet["socket_opened"] is False
    assert packet["client_started"] is False
    assert packet["order_intent_submitted"] is False


def test_q32d_default_hidden_status_is_japanese_no_socket_open() -> None:
    packet = build_warroom_v2_ws_display_connection_status_observation_packet(fragment_summary={"fragment_widget_count": 9})
    assert packet["packet_kind"] == "warroom_v2_ws_display_connection_status_observation_packet"
    assert packet["status_code"] == "ws_not_started_no_socket_open"
    assert packet["transport_state_ja"] == "WS未接続（準備中）"
    assert packet["data_freshness_ja"] == "未接続のため未取得"
    assert packet["last_update_age_ja"] == "未接続"
    assert packet["received_message_count"] == 0
    assert packet["dropped_count"] == 0
    assert "表示契約のみ確認中" in packet["operator_guidance_ja"]
    assert packet["status_line_visible_now"] is False
    assert packet["status_line_mounted_now"] is False
    assert packet["socket_opened"] is False


def test_q32d_observation_can_hold_counts_without_mounting_status_line() -> None:
    packet = build_warroom_v2_ws_display_connection_status_observation_packet(messages=[_message(), _message("x.y", "bad", 2)])
    assert packet["status_code"] == "ws_not_started_no_socket_open"
    assert packet["received_message_count"] == 1
    assert packet["dropped_count"] == 1
    assert packet["status_line"]["received_message_count"] == 1
    assert packet["status_line"]["dropped_count"] == 1
    assert packet["ws_display_connection_status_packet"]["packet_kind"] == "warroom_v2_ws_display_connection_status_packet"
    assert packet["status_line_allowed_in_warroom_later"] is True
    assert packet["status_line_visible_now"] is False
    assert packet["status_line_mounted_now"] is False
    assert packet["client_started"] is False


def test_q32d_warroom_page_records_hidden_status_observation_state_only() -> None:
    text = WARROOM_PAGE.read_text(encoding="utf-8-sig")
    assert "WARROOM_V2_WS_DISPLAY_CONNECTION_STATUS_OBSERVATION_STATE_KEY" in text
    assert "warroom_v2_ws_display_connection_status_observation_q32d" in text
    assert "build_warroom_v2_ws_display_connection_status_observation_packet" in text
    assert "st.session_state[WARROOM_V2_WS_DISPLAY_CONNECTION_STATUS_OBSERVATION_STATE_KEY]" in text
    assert "build_warroom_v2_ws_display_connection_status_packet" not in text
    assert "WARROOM_V2_WS_DISPLAY_CONNECTION_STATUS_VERSION" not in text
    forbidden_visible_labels = (
        "WS未接続（準備中）",
        "WS display connection status",
        "WebSocket connection status",
        "Enable WS connection status",
    )
    for label in forbidden_visible_labels:
        assert label not in text


def test_q32d_doc_modules_preserve_no_side_effect_boundary() -> None:
    text = DOC.read_text(encoding="utf-8-sig")
    assert "state_key=warroom_v2_ws_display_connection_status_observation_q32d" in text
    assert "default_status_code=ws_not_started_no_socket_open" in text
    assert "warroom_status_line_visible_now=false" in text
    assert "not_opening_socket=true" in text
    assert "not_mounting_status_line_into_warroom=true" in text
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
