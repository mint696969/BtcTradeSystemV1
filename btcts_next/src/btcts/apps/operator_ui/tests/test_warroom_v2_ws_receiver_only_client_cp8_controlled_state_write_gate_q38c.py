# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_ws_receiver_only_client_cp8_controlled_state_write_gate_q38c.py
# desc: PS-Q38C guards CP8 controlled state write gate; caller-provided state and explicit allow required.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

REPO_ROOT = Path(__file__).resolve().parents[6]

from btcts.apps.operator_ui.prediction_warroom.v2.transport.ws_receiver_only_client_cp8_controlled_state_write_gate import build_warroom_v2_ws_receiver_only_client_cp8_controlled_state_write_gate_packet  # noqa: E402

DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q38C_WARROOM_V2_WEBSOCKET_RECEIVER_ONLY_CLIENT_CP8_CONTROLLED_STATE_WRITE_GATE_NO_SEND_2026-07-05.md"


def test_q38c_requires_explicit_allow_and_caller_state() -> None:
    schema = {"packet_kind": "warroom_v2_ws_receiver_only_client_cp8_incoming_metadata_state_schema_packet", "incoming_metadata_state_schema_ready": True}
    packet = build_warroom_v2_ws_receiver_only_client_cp8_controlled_state_write_gate_packet(schema, allow_controlled_state_write=True, target_state_is_caller_provided=True)
    assert packet["controlled_state_write_ready"] is True
    blocked = build_warroom_v2_ws_receiver_only_client_cp8_controlled_state_write_gate_packet(schema, allow_controlled_state_write=True)
    assert blocked["controlled_state_write_ready"] is False
    assert "controlled_state_write_ready=true" in DOC.read_text(encoding="utf-8-sig")
