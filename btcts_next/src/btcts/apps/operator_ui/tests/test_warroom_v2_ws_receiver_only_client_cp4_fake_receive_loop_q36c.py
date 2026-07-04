# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_ws_receiver_only_client_cp4_fake_receive_loop_q36c.py
# desc: PS-Q36C guards for CP4 fake receive loop contract only. No fake source/write/readback yet; no socket, no send.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

REPO_ROOT = Path(__file__).resolve().parents[6]

from btcts.apps.operator_ui.prediction_warroom.v2.transport.ws_receiver_only_client_cp4_fake_receive_loop import build_warroom_v2_ws_receiver_only_client_cp4_fake_receive_loop_contract, build_warroom_v2_ws_receiver_only_client_cp4_fake_receive_loop_contract_packet  # noqa: E402
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q36C_WARROOM_V2_WEBSOCKET_RECEIVER_ONLY_CLIENT_CP4_FAKE_RECEIVE_LOOP_CONTRACT_NO_SEND_2026-07-04.md"
PAGE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py"

def test_q36c_is_contract_only_no_fake_source_or_write() -> None:
    contract = build_warroom_v2_ws_receiver_only_client_cp4_fake_receive_loop_contract()
    assert contract["contract_only"] is True
    assert contract["fake_receive_loop_contract_defined"] is True
    assert contract["external_network_used"] is False

def test_q36c_contract_ready_from_cp3_handoff() -> None:
    packet = build_warroom_v2_ws_receiver_only_client_cp4_fake_receive_loop_contract_packet({"packet_kind": "warroom_v2_ws_receiver_only_client_cp3_close_handoff_packet", "cp4_fake_receive_loop_ready": True}, allow_fake_receive_loop_contract=True)
    assert packet["cp4_fake_receive_loop_contract_ready"] is True
    assert packet["fake_receive_loop_enabled"] is True
    assert packet["client_sends_messages"] is False
    assert "contract_only=true" in DOC.read_text(encoding="utf-8-sig")
    assert "ws_receiver_only_client_cp4_fake_receive_loop" not in PAGE.read_text(encoding="utf-8-sig")
