# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_ws_receiver_only_client_cp4_fake_receive_loop_readback_q36f.py
# desc: PS-Q36F guards for CP4 fake receive loop metadata readback. No raw payload, no socket, no send.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

REPO_ROOT = Path(__file__).resolve().parents[6]

from btcts.apps.operator_ui.prediction_warroom.v2.transport.ws_receiver_only_client_cp4_fake_receive_loop_readback import build_warroom_v2_ws_receiver_only_client_cp4_fake_receive_loop_readback_packet  # noqa: E402
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q36F_WARROOM_V2_WEBSOCKET_RECEIVER_ONLY_CLIENT_CP4_FAKE_RECEIVE_LOOP_READBACK_NO_SEND_2026-07-04.md"

def test_q36f_reads_message_count_and_latest_metadata() -> None:
    state = {"k": {"packet_kind": "warroom_v2_ws_receiver_only_client_cp4_fake_receive_loop_state_record", "message_count": 2, "latest_message": {"topic": "fake.heartbeat"}}}
    packet = build_warroom_v2_ws_receiver_only_client_cp4_fake_receive_loop_readback_packet(state, state_write_key="k", allow_readback=True)
    assert packet["readback_ready"] is True
    assert packet["message_count"] == 2
    assert packet["latest_message"]["topic"] == "fake.heartbeat"
    assert packet["session_state_keys_returned"] is False
    assert "message_count_readback=true" in DOC.read_text(encoding="utf-8-sig")
