# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_ws_display_client_observation_q32b.py
# desc: PS-Q32B guards for hidden session_state WS display client observation. No socket open and no UI mount.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.apps.operator_ui.prediction_warroom.v2 import (  # noqa: E402
    WARROOM_V2_WS_DISPLAY_CLIENT_OBSERVATION_STATE_KEY,
    build_warroom_v2_ws_display_client_observation_contract,
    build_warroom_v2_ws_display_client_observation_packet,
)

REPO_ROOT = Path(__file__).resolve().parents[6]
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q32B_WARROOM_V2_WS_DISPLAY_CLIENT_OBSERVATION_TO_HIDDEN_SESSION_STATE_NO_SOCKET_OPEN_2026-07-03.md"
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


def test_q32b_contract_is_hidden_state_for_ws_display_client() -> None:
    packet = build_warroom_v2_ws_display_client_observation_contract()
    assert packet["state_key"] == WARROOM_V2_WS_DISPLAY_CLIENT_OBSERVATION_STATE_KEY
    assert packet["observation_kind"] == "warroom_v2_hidden_ws_display_client_observation_packet"
    assert packet["current_small_goal"] == "warroom_tab_ws_push_realtime_update_and_japanese_readability"
    assert packet["websocket_display_push_main_path"] is True
    assert packet["ui_receiver_side"] is True
    assert packet["server_to_warroom_ui"] is True
    assert packet["socket_open_requested"] is False
    assert packet["socket_opened"] is False
    assert packet["client_started"] is False
    assert packet["client_sends_messages"] is False
    assert packet["order_intent_submitted"] is False


def test_q32b_default_streamlit_path_records_empty_no_socket_client_state() -> None:
    packet = build_warroom_v2_ws_display_client_observation_packet(fragment_summary={"fragment_widget_count": 9})
    assert packet["packet_kind"] == "warroom_v2_ws_display_client_observation_packet"
    assert packet["default_streamlit_message_count"] == 0
    assert packet["received_message_count"] == 0
    assert packet["dropped_count"] == 0
    assert packet["subscriptions_count"] >= 10
    assert packet["socket_open_requested"] is False
    assert packet["socket_opened"] is False
    assert packet["client_started"] is False
    assert packet["client_sends_messages"] is False
    assert packet["streamlit_render_allowed"] is False
    assert packet["would_send_to_broker"] is False


def test_q32b_observation_can_hold_client_buffer_without_starting_client() -> None:
    packet = build_warroom_v2_ws_display_client_observation_packet(messages=[_message(), _message("x.y", "bad", 2)])
    assert packet["default_streamlit_message_count"] == 2
    assert packet["received_message_count"] == 1
    assert packet["dropped_count"] == 1
    client_packet = packet["ws_display_client_packet"]
    assert client_packet["receive_buffer_packet"]["messages"][0]["topic"] == "warroom.market.snapshot"
    assert client_packet["receive_buffer_packet"]["messages"][0]["received_over_ws_now"] is False
    assert client_packet["socket_opened"] is False
    assert client_packet["client_started"] is False
    assert client_packet["client_sends_messages"] is False
    assert packet["all_messages_are_display_targets"] is True
    assert packet["all_messages_no_broad_page_reload"] is True


def test_q32b_warroom_page_records_hidden_ws_client_observation_state_only() -> None:
    text = WARROOM_PAGE.read_text(encoding="utf-8-sig")
    assert "WARROOM_V2_WS_DISPLAY_CLIENT_OBSERVATION_STATE_KEY" in text
    assert "warroom_v2_ws_display_client_observation_q32b" in text
    assert "build_warroom_v2_ws_display_client_observation_packet" in text
    assert "st.session_state[WARROOM_V2_WS_DISPLAY_CLIENT_OBSERVATION_STATE_KEY]" in text
    assert "build_warroom_v2_ws_display_client_packet" not in text
    assert "WARROOM_V2_WS_DISPLAY_CLIENT_VERSION" not in text
    forbidden_visible_labels = (
        "WS display client observation",
        "WebSocket display client observation",
        "Run WS display client",
        "Enable WS display client",
    )
    for label in forbidden_visible_labels:
        assert label not in text


def test_q32b_doc_modules_preserve_no_side_effect_boundary() -> None:
    text = DOC.read_text(encoding="utf-8-sig")
    assert "state_key=warroom_v2_ws_display_client_observation_q32b" in text
    assert "client_started=false" in text
    assert "not_opening_socket=true" in text
    assert "not_using_polling_fallback=true" in text
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
