# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_ws_receiver_only_client_receive_buffer_drain_contract_q33c.py
# desc: PS-Q33C guards for receiver-only client receive-buffer drain contract. Default-off/no-socket/no-send.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.apps.operator_ui.prediction_warroom.v2 import (  # noqa: E402
    build_warroom_v2_ws_display_client_receive_buffer,
    build_warroom_v2_ws_receiver_only_client_hidden_state_packet,
    build_warroom_v2_ws_receiver_only_client_receive_buffer_drain_contract,
    build_warroom_v2_ws_receiver_only_client_receive_buffer_drain_packet,
)

REPO_ROOT = Path(__file__).resolve().parents[6]
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q33C_WARROOM_V2_WEBSOCKET_RECEIVER_ONLY_CLIENT_RECEIVE_BUFFER_DRAIN_CONTRACT_DEFAULT_OFF_NO_SOCKET_2026-07-03.md"
TRANSPORT_DIR = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport"
WARROOM_PAGE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py"


def _message(sequence: int = 1) -> dict[str, object]:
    return {
        "message_type": "warroom_v2_widget_update",
        "payload_kind": "widget_update_event_envelope",
        "topic": "warroom.market.snapshot",
        "widget_id": "market_snapshot_strip",
        "sequence": sequence,
        "generated_at": "2026-07-03T00:00:00Z",
        "ui_patch_unit": "widget_dom_region",
        "broad_page_reload_required": False,
        "envelope": {"topic": "warroom.market.snapshot", "widget_id": "market_snapshot_strip", "sequence": sequence},
        "json_payload": "{}",
    }


def _ready_hidden_state() -> dict[str, object]:
    gate = {
        "receiver_client_enable_allowed_for_next_slice": True,
        "receiver_enable_gate_status": "receiver_enable_gate_ready_for_next_slice_no_socket",
        "socket_opened": False,
        "client_started": False,
        "client_sends_messages": False,
    }
    return build_warroom_v2_ws_receiver_only_client_hidden_state_packet(receiver_enable_gate_packet=gate)


def test_q33c_contract_defines_default_off_drain_preview_only_boundary() -> None:
    packet = build_warroom_v2_ws_receiver_only_client_receive_buffer_drain_contract()
    assert packet["drain_kind"] == "warroom_v2_ws_receiver_only_client_receive_buffer_drain_contract_default_off_no_socket"
    assert packet["drain_requested_default"] is False
    assert packet["operator_drain_ack_default"] is False
    assert packet["drain_contract_status_default"] == "receive_buffer_drain_hidden_default"
    assert packet["drain_contract_status_ready"] == "receive_buffer_drain_ready_for_next_slice_no_socket"
    assert packet["drain_contract_is_preview_only"] is True
    assert packet["receive_buffer_drain_allowed_effective"] is False
    assert packet["messages_drained_now"] == 0
    assert packet["state_mutated"] is False
    assert packet["socket_opened"] is False
    assert packet["client_started"] is False
    assert packet["client_sends_messages"] is False


def test_q33c_default_packet_stays_hidden_and_does_not_drain() -> None:
    packet = build_warroom_v2_ws_receiver_only_client_receive_buffer_drain_packet()
    assert packet["packet_kind"] == "warroom_v2_ws_receiver_only_client_receive_buffer_drain_packet"
    assert packet["drain_contract_status"] == "receive_buffer_drain_hidden_default"
    assert packet["drain_requested"] is False
    assert packet["operator_drain_ack"] is False
    assert packet["receiver_hidden_state_ready_for_next_slice"] is False
    assert packet["drain_preview_count"] == 0
    assert packet["receive_buffer_drain_allowed_for_next_slice"] is False
    assert packet["receive_buffer_drain_allowed_effective"] is False
    assert packet["messages_drained_now"] == 0
    assert packet["state_mutated"] is False
    assert packet["websocket_enabled"] is False


def test_q33c_ready_requires_request_ack_and_hidden_state_but_still_preview_only() -> None:
    buffer_packet = build_warroom_v2_ws_display_client_receive_buffer(messages=[_message(1), _message(2)])
    blocked_ack = build_warroom_v2_ws_receiver_only_client_receive_buffer_drain_packet(
        receiver_hidden_state_packet=_ready_hidden_state(),
        receive_buffer_packet=buffer_packet,
        drain_requested=True,
        operator_drain_ack=False,
    )
    assert blocked_ack["drain_contract_status"] == "receive_buffer_drain_blocked_operator_ack_required"
    blocked_state = build_warroom_v2_ws_receiver_only_client_receive_buffer_drain_packet(
        receive_buffer_packet=buffer_packet,
        drain_requested=True,
        operator_drain_ack=True,
    )
    assert blocked_state["drain_contract_status"] == "receive_buffer_drain_blocked_receiver_hidden_state_required"
    ready = build_warroom_v2_ws_receiver_only_client_receive_buffer_drain_packet(
        receiver_hidden_state_packet=_ready_hidden_state(),
        receive_buffer_packet=buffer_packet,
        drain_requested=True,
        operator_drain_ack=True,
        max_drain_items=1,
    )
    assert ready["drain_contract_status"] == "receive_buffer_drain_ready_for_next_slice_no_socket"
    assert ready["receive_buffer_message_count"] == 2
    assert ready["drain_preview_count"] == 1
    assert ready["drain_preview_messages"][0]["topic"] == "warroom.market.snapshot"
    assert ready["receive_buffer_drain_allowed_for_next_slice"] is True
    assert ready["receive_buffer_drain_allowed_effective"] is False
    assert ready["messages_drained_now"] == 0
    assert ready["state_mutated"] is False
    assert ready["socket_opened"] is False
    assert ready["client_started"] is False
    assert ready["client_sends_messages"] is False
    assert ready["would_send_to_broker"] is False


def test_q33c_doc_and_warroom_page_preserve_no_ui_boundary() -> None:
    text = DOC.read_text(encoding="utf-8-sig")
    assert "drain_kind=warroom_v2_ws_receiver_only_client_receive_buffer_drain_contract_default_off_no_socket" in text
    assert "drain_requested_default=false" in text
    assert "operator_drain_ack_default=false" in text
    assert "not_mutating_session_state=true" in text
    assert "not_opening_socket=true" in text
    page = WARROOM_PAGE.read_text(encoding="utf-8-sig")
    assert "ws_receiver_only_client_receive_buffer_drain" not in page
    assert "receive_buffer_drain_ready_for_next_slice_no_socket" not in page
    assert "Drain WS buffer" not in page
    assert 'st.checkbox("WS' not in page
    assert 'st.button("WS' not in page


def test_q33c_transport_modules_preserve_no_socket_order_prediction_boundary() -> None:
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
