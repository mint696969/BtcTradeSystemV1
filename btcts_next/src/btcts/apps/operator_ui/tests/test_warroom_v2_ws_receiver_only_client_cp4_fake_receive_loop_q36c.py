# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_ws_receiver_only_client_cp4_fake_receive_loop_q36c.py
# desc: PS-Q36C guards for CP4 fake receive loop completion. Local fake messages only; no network, no socket, no send.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.apps.operator_ui.prediction_warroom.v2.transport.ws_receiver_only_client_cp4_fake_receive_loop import (  # noqa: E402
    WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_CP4_FAKE_RECEIVE_LOOP_STATE_KEY,
    apply_warroom_v2_ws_receiver_only_client_cp4_fake_receive_loop,
    build_warroom_v2_ws_receiver_only_client_cp4_fake_receive_loop_contract,
)

REPO_ROOT = Path(__file__).resolve().parents[6]
MODULE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/ws_receiver_only_client_cp4_fake_receive_loop.py"
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q36C_WARROOM_V2_WEBSOCKET_RECEIVER_ONLY_CLIENT_CP4_FAKE_RECEIVE_LOOP_COMPLETION_NO_SEND_2026-07-04.md"
WARROOM_PAGE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py"


def _cp3() -> dict[str, object]:
    return {"packet_kind": "warroom_v2_ws_receiver_only_client_cp3_visible_readiness_packet", "cp3_visible_readiness_visible_now": True}


def test_q36c_contract_is_fake_receive_loop_no_network_no_send() -> None:
    packet = build_warroom_v2_ws_receiver_only_client_cp4_fake_receive_loop_contract()
    assert packet["state_key"] == WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_CP4_FAKE_RECEIVE_LOOP_STATE_KEY
    assert packet["fake_receive_loop"] is True
    assert packet["fake_messages_only"] is True
    assert packet["external_network_used"] is False
    assert packet["socket_opened"] is False
    assert packet["send_disabled"] is True


def test_q36c_blocks_without_allow_cp3_or_target_state() -> None:
    assert apply_warroom_v2_ws_receiver_only_client_cp4_fake_receive_loop({}, cp3_visible_readiness_packet=_cp3())["fake_receive_loop_status"] == "receiver_only_client_cp4_fake_receive_loop_blocked_allow_required"
    assert apply_warroom_v2_ws_receiver_only_client_cp4_fake_receive_loop({}, allow_fake_receive_loop=True)["fake_receive_loop_status"] == "receiver_only_client_cp4_fake_receive_loop_blocked_cp3_visible_readiness_required"
    assert apply_warroom_v2_ws_receiver_only_client_cp4_fake_receive_loop(None, cp3_visible_readiness_packet=_cp3(), allow_fake_receive_loop=True)["fake_receive_loop_status"] == "receiver_only_client_cp4_fake_receive_loop_blocked_target_state_required"


def test_q36c_applies_fake_messages_to_target_state_and_readback_metadata() -> None:
    state: dict[str, object] = {}
    packet = apply_warroom_v2_ws_receiver_only_client_cp4_fake_receive_loop(state, cp3_visible_readiness_packet=_cp3(), allow_fake_receive_loop=True)
    assert packet["fake_receive_loop_applied"] is True
    assert packet["cp4_completed"] is True
    assert packet["message_count"] == 3
    assert packet["latest_message"]["topic"] == "fake.heartbeat"
    assert WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_CP4_FAKE_RECEIVE_LOOP_STATE_KEY in state
    assert state[WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_CP4_FAKE_RECEIVE_LOOP_STATE_KEY]["message_count"] == 3
    assert "price" not in str(packet["latest_message"])
    assert packet["raw_payload_returned"] is False


def test_q36c_module_doc_and_page_preserve_no_send_boundary() -> None:
    module = MODULE.read_text(encoding="utf-8-sig")
    doc = DOC.read_text(encoding="utf-8-sig")
    page = WARROOM_PAGE.read_text(encoding="utf-8-sig")
    assert "cp4_completed=true" in doc
    assert "fake_messages_only=true" in doc
    assert "external_network_used=false" in doc
    assert "not_sending_external_messages=true" in doc
    assert "ws_receiver_only_client_cp4_fake_receive_loop" not in page
    for token in ("import streamlit", "from streamlit", "import websockets", "from websockets", "websocket.", "send_to_broker(", "submit_order(", "append_ledger(", "run_prediction(", "invoke_classifier(", "D:" + chr(92), "E:" + chr(92)):
        assert token not in module
