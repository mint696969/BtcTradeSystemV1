# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_ws_receiver_only_client_cp8_preflight_to_state_bridge_q38f.py
# desc: PS-Q38F guards CP8 preflight-to-state bridge; CP7 completion plus state readback without receive loop.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

REPO_ROOT = Path(__file__).resolve().parents[6]

from btcts.apps.operator_ui.prediction_warroom.v2.transport.ws_receiver_only_client_cp8_preflight_to_state_bridge import build_warroom_v2_ws_receiver_only_client_cp8_preflight_to_state_bridge_packet  # noqa: E402

DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q38F_WARROOM_V2_WEBSOCKET_RECEIVER_ONLY_CLIENT_CP8_PREFLIGHT_TO_STATE_BRIDGE_NO_SEND_2026-07-05.md"


def test_q38f_bridge_links_cp7_completion_to_state_readback() -> None:
    cp7 = {"packet_kind": "warroom_v2_ws_receiver_only_client_cp7_completion_packet", "cp7_completed": True}
    readback = {"packet_kind": "warroom_v2_ws_receiver_only_client_cp8_state_readback_packet", "state_readback_ready": True}
    packet = build_warroom_v2_ws_receiver_only_client_cp8_preflight_to_state_bridge_packet(cp7, readback, allow_bridge=True)
    assert packet["preflight_to_state_bridge_ready"] is True
    assert packet["live_incoming_state_flow_ready"] is True
    assert packet["receive_loop_started"] is False
    assert "preflight_to_state_bridge_ready=true" in DOC.read_text(encoding="utf-8-sig")
