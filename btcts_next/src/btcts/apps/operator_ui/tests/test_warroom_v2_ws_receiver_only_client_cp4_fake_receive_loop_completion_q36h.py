# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_ws_receiver_only_client_cp4_fake_receive_loop_completion_q36h.py
# desc: PS-Q36H guards for CP4 fake receive loop completion packet. Completion only after no-send guard.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

REPO_ROOT = Path(__file__).resolve().parents[6]

from btcts.apps.operator_ui.prediction_warroom.v2.transport.ws_receiver_only_client_cp4_fake_receive_loop_completion import build_warroom_v2_ws_receiver_only_client_cp4_fake_receive_loop_completion_packet  # noqa: E402
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q36H_WARROOM_V2_WEBSOCKET_RECEIVER_ONLY_CLIENT_CP4_FAKE_RECEIVE_LOOP_COMPLETION_PACKET_NO_SEND_2026-07-04.md"

def test_q36h_declares_cp4_completion_from_no_send_guard() -> None:
    packet = build_warroom_v2_ws_receiver_only_client_cp4_fake_receive_loop_completion_packet({"packet_kind": "warroom_v2_ws_receiver_only_client_cp4_fake_receive_loop_no_send_guard_packet", "no_send_guard_ready": True}, allow_cp4_completion=True)
    assert packet["cp4_completed"] is True
    assert packet["cp4_completion_commit_ready"] is True
    assert packet["next_checkpoint"] == "CP5_message_normalizer_no_send"
    assert "cp4_completed=true" in DOC.read_text(encoding="utf-8-sig")
