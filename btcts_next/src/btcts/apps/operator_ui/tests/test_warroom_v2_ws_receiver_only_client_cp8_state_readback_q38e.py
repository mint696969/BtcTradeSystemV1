# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_ws_receiver_only_client_cp8_state_readback_q38e.py
# desc: PS-Q38E guards CP8 state readback; returns sanitized metadata summary only.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

REPO_ROOT = Path(__file__).resolve().parents[6]

from btcts.apps.operator_ui.prediction_warroom.v2.transport.ws_receiver_only_client_cp8_state_readback import build_warroom_v2_ws_receiver_only_client_cp8_state_readback_packet  # noqa: E402

DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q38E_WARROOM_V2_WEBSOCKET_RECEIVER_ONLY_CLIENT_CP8_STATE_READBACK_NO_SEND_2026-07-05.md"


def test_q38e_readback_is_metadata_only() -> None:
    update = {"packet_kind": "warroom_v2_ws_receiver_only_client_cp8_state_append_update_packet", "state_append_update_ready": True}
    state = {"cp8_state_flow_ready": True, "received_message_count": 1, "dropped_count": 1, "latest_incoming_metadata": {"topic": "book"}, "recent_incoming_metadata": [{"topic": "book"}]}
    packet = build_warroom_v2_ws_receiver_only_client_cp8_state_readback_packet(state, update, allow_readback=True)
    assert packet["state_readback_ready"] is True
    assert packet["latest_incoming_metadata"] == {"topic": "book"}
    assert packet["raw_payload_returned"] is False
    assert "state_readback_ready=true" in DOC.read_text(encoding="utf-8-sig")
