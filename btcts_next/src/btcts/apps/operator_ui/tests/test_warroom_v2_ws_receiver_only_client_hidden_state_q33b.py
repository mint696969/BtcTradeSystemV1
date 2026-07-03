# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_ws_receiver_only_client_hidden_state_q33b.py
# desc: PS-Q33B guards for receiver-only client hidden state. Default-off/no-socket/no-send.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.apps.operator_ui.prediction_warroom.v2 import (  # noqa: E402
    WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_HIDDEN_STATE_KEY,
    build_warroom_v2_ws_display_client_observation_packet,
    build_warroom_v2_ws_receiver_only_client_enable_gate_packet,
    build_warroom_v2_ws_receiver_only_client_hidden_state_contract,
    build_warroom_v2_ws_receiver_only_client_hidden_state_packet,
)

REPO_ROOT = Path(__file__).resolve().parents[6]
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q33B_WARROOM_V2_WEBSOCKET_RECEIVER_ONLY_CLIENT_HIDDEN_STATE_DEFAULT_OFF_NO_SOCKET_2026-07-03.md"
TRANSPORT_DIR = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport"
WARROOM_PAGE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py"


def test_q33b_contract_defines_hidden_receiver_state_default_off() -> None:
    packet = build_warroom_v2_ws_receiver_only_client_hidden_state_contract()
    assert packet["state_key"] == WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_HIDDEN_STATE_KEY
    assert packet["state_kind"] == "warroom_v2_ws_receiver_only_client_hidden_state_packet"
    assert packet["receiver_state_default"] == "receiver_hidden_state_default_off"
    assert packet["hidden_session_state_recorded"] is True
    assert packet["warroom_page_modified"] is True
    assert packet["visible_controls_added"] is False
    assert packet["receiver_enabled_effective"] is False
    assert packet["socket_opened"] is False
    assert packet["client_started"] is False
    assert packet["client_sends_messages"] is False
    assert packet["order_intent_submitted"] is False


def test_q33b_default_packet_records_observation_only_state_without_socket() -> None:
    packet = build_warroom_v2_ws_receiver_only_client_hidden_state_packet(fragment_summary={"fragment_widget_count": 9})
    assert packet["packet_kind"] == "warroom_v2_ws_receiver_only_client_hidden_state_packet"
    assert packet["receiver_state_status"] == "receiver_hidden_state_default_off"
    assert packet["receiver_client_enable_allowed_for_next_slice"] is False
    assert packet["receiver_client_enable_allowed_effective"] is False
    assert packet["receiver_enabled_effective"] is False
    assert packet["received_message_count"] == 0
    assert packet["dropped_count"] == 0
    assert packet["socket_open_requested"] is False
    assert packet["socket_opened"] is False
    assert packet["client_started"] is False
    assert packet["client_sends_messages"] is False
    assert packet["websocket_enabled"] is False


def test_q33b_ready_gate_can_be_reflected_as_next_slice_only_not_effective() -> None:
    gate = build_warroom_v2_ws_receiver_only_client_enable_gate_packet()
    gate["receiver_client_enable_allowed_for_next_slice"] = True
    gate["receiver_enable_gate_status"] = "receiver_enable_gate_ready_for_next_slice_no_socket"
    observation = build_warroom_v2_ws_display_client_observation_packet(fragment_summary={"fragment_widget_count": 9}, messages=[])
    packet = build_warroom_v2_ws_receiver_only_client_hidden_state_packet(
        fragment_summary={"fragment_widget_count": 9},
        ws_display_client_observation_packet=observation,
        receiver_enable_gate_packet=gate,
    )
    assert packet["receiver_state_status"] == "receiver_hidden_state_ready_for_next_slice_no_socket"
    assert packet["receiver_client_enable_allowed_for_next_slice"] is True
    assert packet["receiver_client_enable_allowed_effective"] is False
    assert packet["receiver_enabled_effective"] is False
    assert packet["socket_opened"] is False
    assert packet["client_started"] is False
    assert packet["client_sends_messages"] is False
    assert packet["would_send_to_broker"] is False


def test_q33b_warroom_page_records_hidden_state_only() -> None:
    text = WARROOM_PAGE.read_text(encoding="utf-8-sig")
    assert "WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_HIDDEN_STATE_KEY" in text
    assert "warroom_v2_ws_receiver_only_client_hidden_state_q33b" in text
    assert "build_warroom_v2_ws_receiver_only_client_hidden_state_packet" in text
    assert "st.session_state[WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_HIDDEN_STATE_KEY]" in text
    assert "receiver_hidden_state_ready_for_next_slice_no_socket" not in text
    assert "WebSocket receiver" not in text
    assert "Enable WS receiver" not in text
    assert 'st.checkbox("WS' not in text
    assert 'st.button("WS' not in text


def test_q33b_doc_modules_preserve_no_socket_order_prediction_boundary() -> None:
    text = DOC.read_text(encoding="utf-8-sig")
    assert "state_key=warroom_v2_ws_receiver_only_client_hidden_state_q33b" in text
    assert "hidden_session_state_recorded=true" in text
    assert "not_opening_socket=true" in text
    assert "not_starting_client=true" in text
    forbidden = (
        "import streamlit", "from streamlit", "websocket.", "sse.", "polling_loop(", "browser_timer_reload(",
        "send_to_broker(", "submit_order(", "append_ledger(", "write_runtime_artifact(", "write_prediction_artifact(",
        "run_prediction(", "invoke_classifier(", "st.write(", "st.metric(", "st.caption(", "st.markdown(", "D:" + chr(92), "E:" + chr(92),
    )
    for path in TRANSPORT_DIR.glob("*.py"):
        body = path.read_text(encoding="utf-8-sig")
        assert len(body.splitlines()) <= 220, f"transport file too large: {path}"
        for token in forbidden:
            assert token not in body, f"forbidden token {token!r} found in {path}"
