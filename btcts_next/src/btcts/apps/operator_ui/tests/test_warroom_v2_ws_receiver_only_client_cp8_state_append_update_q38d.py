# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_ws_receiver_only_client_cp8_state_append_update_q38d.py
# desc: PS-Q38D guards CP8 state append/update; sanitized bounded caller-state only.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

REPO_ROOT = Path(__file__).resolve().parents[6]

from btcts.apps.operator_ui.prediction_warroom.v2.transport.ws_receiver_only_client_cp8_state_append_update import apply_warroom_v2_ws_receiver_only_client_cp8_state_append_update  # noqa: E402

DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q38D_WARROOM_V2_WEBSOCKET_RECEIVER_ONLY_CLIENT_CP8_STATE_APPEND_UPDATE_NO_SEND_2026-07-05.md"


def test_q38d_appends_sanitized_metadata_and_drops_raw_payload() -> None:
    gate = {"packet_kind": "warroom_v2_ws_receiver_only_client_cp8_controlled_state_write_gate_packet", "controlled_state_write_ready": True}
    state = {}
    packet = apply_warroom_v2_ws_receiver_only_client_cp8_state_append_update(state, {"topic": "book", "sequence": 1, "raw_payload": {"secret": "x"}}, gate, allow_state_update=True)
    assert packet["state_append_update_ready"] is True
    assert packet["raw_payload_dropped"] is True
    assert "raw_payload" not in state["latest_incoming_metadata"]
    assert state["received_message_count"] == 1
    assert packet["raw_payload_returned"] is False
    assert "state_append_update_ready=true" in DOC.read_text(encoding="utf-8-sig")
