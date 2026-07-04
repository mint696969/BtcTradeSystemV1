# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_ws_receiver_only_client_cp4_fake_receive_loop_state_write_q36e.py
# desc: PS-Q36E guards for CP4 fake receive loop state write. Target state metadata only; no socket, no send.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

REPO_ROOT = Path(__file__).resolve().parents[6]

from btcts.apps.operator_ui.prediction_warroom.v2.transport.ws_receiver_only_client_cp4_fake_receive_loop_state_write import STATE_KEY, apply_warroom_v2_ws_receiver_only_client_cp4_fake_receive_loop_state_write  # noqa: E402
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q36E_WARROOM_V2_WEBSOCKET_RECEIVER_ONLY_CLIENT_CP4_FAKE_RECEIVE_LOOP_STATE_WRITE_NO_SEND_2026-07-04.md"

def test_q36e_writes_summary_metadata_to_target_state() -> None:
    state: dict[str, object] = {}
    source = {"packet_kind": "warroom_v2_ws_receiver_only_client_cp4_fake_message_source_packet", "fake_message_source_ready": True, "fake_message_summaries": [{"topic": "fake.heartbeat", "sequence": 1}]}
    packet = apply_warroom_v2_ws_receiver_only_client_cp4_fake_receive_loop_state_write(state, fake_message_source_packet=source, allow_state_write=True)
    assert packet["state_write_ready"] is True
    assert packet["target_state_mutated"] is True
    assert state[STATE_KEY]["message_count"] == 1
    assert packet["raw_payload_returned"] is False
    assert "target_state_mutated=true" in DOC.read_text(encoding="utf-8-sig")
