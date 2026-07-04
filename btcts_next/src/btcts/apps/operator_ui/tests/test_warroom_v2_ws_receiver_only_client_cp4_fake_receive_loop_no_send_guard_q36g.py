# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_ws_receiver_only_client_cp4_fake_receive_loop_no_send_guard_q36g.py
# desc: PS-Q36G guards for CP4 fake receive loop no-send boundary. No broker/order/ledger/prediction/classifier send.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

REPO_ROOT = Path(__file__).resolve().parents[6]

from btcts.apps.operator_ui.prediction_warroom.v2.transport.ws_receiver_only_client_cp4_fake_receive_loop_no_send_guard import build_warroom_v2_ws_receiver_only_client_cp4_fake_receive_loop_no_send_guard_packet  # noqa: E402
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q36G_WARROOM_V2_WEBSOCKET_RECEIVER_ONLY_CLIENT_CP4_FAKE_RECEIVE_LOOP_NO_SEND_GUARD_NO_SEND_2026-07-04.md"

def test_q36g_accepts_only_no_send_readback() -> None:
    packet = build_warroom_v2_ws_receiver_only_client_cp4_fake_receive_loop_no_send_guard_packet({"packet_kind": "warroom_v2_ws_receiver_only_client_cp4_fake_receive_loop_readback_packet", "readback_ready": True, "raw_payload_returned": False, "socket_opened": False, "client_sends_messages": False, "external_message_send_enabled": False, "send_disabled": True, "message_count": 3}, allow_no_send_guard=True)
    assert packet["no_send_guard_ready"] is True
    assert packet["would_send_to_broker"] is False
    assert packet["prediction_inference_invoked"] is False
    assert "no_send_guard_ready=true" in DOC.read_text(encoding="utf-8-sig")
