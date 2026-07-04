# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_ws_receiver_only_client_cp10_heartbeat_policy_schema_q40c.py
# desc: PS-Q40C guards CP10 heartbeat policy schema; metadata only and no heartbeat send/receive.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

REPO_ROOT = Path(__file__).resolve().parents[6]

from btcts.apps.operator_ui.prediction_warroom.v2.transport.ws_receiver_only_client_cp10_heartbeat_policy_schema import build_warroom_v2_ws_receiver_only_client_cp10_heartbeat_policy_schema_packet  # noqa: E402
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q40C_WARROOM_V2_WEBSOCKET_RECEIVER_ONLY_CLIENT_CP10_HEARTBEAT_POLICY_SCHEMA_NO_SEND_2026-07-05.md"

def test_q40c_heartbeat_policy_does_not_send_or_receive() -> None:
    reconnect = {"packet_kind": "warroom_v2_ws_receiver_only_client_cp10_reconnect_policy_schema_packet", "reconnect_policy_schema_ready": True}
    packet = build_warroom_v2_ws_receiver_only_client_cp10_heartbeat_policy_schema_packet(reconnect, allow_heartbeat_policy_schema=True)
    assert packet["heartbeat_policy_schema_ready"] is True
    assert packet["runtime_heartbeat_allowed"] is False
    assert packet["heartbeat_sent"] is False
    assert packet["heartbeat_received"] is False
    assert "heartbeat_policy_schema_ready=true" in DOC.read_text(encoding="utf-8-sig")
