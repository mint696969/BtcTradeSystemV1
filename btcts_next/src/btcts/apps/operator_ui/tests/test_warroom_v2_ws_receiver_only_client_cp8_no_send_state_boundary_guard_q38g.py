# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_ws_receiver_only_client_cp8_no_send_state_boundary_guard_q38g.py
# desc: PS-Q38G guards CP8 no-send state boundary; no socket/network/send/UI/broker/prediction/classifier.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

REPO_ROOT = Path(__file__).resolve().parents[6]

from btcts.apps.operator_ui.prediction_warroom.v2.transport.ws_receiver_only_client_cp8_no_send_state_boundary_guard import build_warroom_v2_ws_receiver_only_client_cp8_no_send_state_boundary_guard_packet  # noqa: E402

DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q38G_WARROOM_V2_WEBSOCKET_RECEIVER_ONLY_CLIENT_CP8_NO_SEND_STATE_BOUNDARY_GUARD_NO_SEND_2026-07-05.md"


def test_q38g_guard_passes_clean_bridge_and_catches_send() -> None:
    bridge = {"packet_kind": "warroom_v2_ws_receiver_only_client_cp8_preflight_to_state_bridge_packet", "live_incoming_state_flow_ready": True, "not_sending_external_messages": True, "send_disabled": True}
    packet = build_warroom_v2_ws_receiver_only_client_cp8_no_send_state_boundary_guard_packet(bridge, allow_guard=True)
    assert packet["cp8_no_send_state_boundary_guard_ready"] is True
    bad = dict(bridge, client_sends_messages=True)
    blocked = build_warroom_v2_ws_receiver_only_client_cp8_no_send_state_boundary_guard_packet(bad, allow_guard=True)
    assert blocked["cp8_no_send_state_boundary_guard_ready"] is False
    assert "client_sends_messages" in blocked["guard_failures"]
    assert "cp8_no_send_state_boundary_guard_ready=true" in DOC.read_text(encoding="utf-8-sig")
