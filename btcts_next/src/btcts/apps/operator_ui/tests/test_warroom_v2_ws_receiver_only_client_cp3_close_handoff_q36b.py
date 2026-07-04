# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_ws_receiver_only_client_cp3_close_handoff_q36b.py
# desc: PS-Q36B guards for CP3 close handoff to CP4 fake receive loop. No socket, no send.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

REPO_ROOT = Path(__file__).resolve().parents[6]

from btcts.apps.operator_ui.prediction_warroom.v2.transport.ws_receiver_only_client_cp3_close_handoff import build_warroom_v2_ws_receiver_only_client_cp3_close_handoff_packet  # noqa: E402
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q36B_WARROOM_V2_WEBSOCKET_RECEIVER_ONLY_CLIENT_CP3_CLOSE_HANDOFF_NO_SEND_2026-07-04.md"

def test_q36b_declares_cp3_complete_and_handoff_to_cp4() -> None:
    packet = build_warroom_v2_ws_receiver_only_client_cp3_close_handoff_packet({"packet_kind": "warroom_v2_ws_receiver_only_client_cp3_visible_readiness_readback_packet", "cp3_visible_readiness_readback_ready": True}, allow_cp3_close_handoff=True)
    assert packet["cp3_completed"] is True
    assert packet["cp4_fake_receive_loop_ready"] is True
    assert packet["next_checkpoint"] == "CP4_fake_receive_loop_contract"
    assert "not_sending_external_messages=true" in DOC.read_text(encoding="utf-8-sig")
