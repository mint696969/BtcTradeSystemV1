# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_ws_receiver_only_client_cp6_no_connect_no_send_guard_q36x.py
# desc: PS-Q36X guards for CP6 no-connect/no-send boundary. No endpoint/token/callable/socket/send.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

REPO_ROOT = Path(__file__).resolve().parents[6]

DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q36X_WARROOM_V2_WEBSOCKET_RECEIVER_ONLY_CLIENT_CP6_NO_CONNECT_NO_SEND_GUARD_NO_SEND_2026-07-04.md"

from btcts.apps.operator_ui.prediction_warroom.v2.transport.ws_receiver_only_client_cp6_no_connect_no_send_guard import build_warroom_v2_ws_receiver_only_client_cp6_no_connect_no_send_guard_packet  # noqa: E402


def test_q36x_guard_accepts_only_no_connect_no_send_readback() -> None:
    readback = {"packet_kind": "warroom_v2_ws_receiver_only_client_cp6_adapter_readiness_readback_packet", "adapter_readiness_readback_ready": True, "buffer_count": 1, "endpoint_value_returned": False, "token_value_returned": False, "callable_values_returned": False, "socket_opened": False, "client_sends_messages": False, "external_message_send_enabled": False, "send_disabled": True}
    packet = build_warroom_v2_ws_receiver_only_client_cp6_no_connect_no_send_guard_packet(readback, allow_cp6_no_connect_no_send_guard=True)
    assert packet["cp6_no_connect_no_send_guard_ready"] is True
    assert packet["secret_exposure"] is False
    assert packet["would_send_to_broker"] is False
    assert "cp6_no_connect_no_send_guard_ready=true" in DOC.read_text(encoding="utf-8-sig")
