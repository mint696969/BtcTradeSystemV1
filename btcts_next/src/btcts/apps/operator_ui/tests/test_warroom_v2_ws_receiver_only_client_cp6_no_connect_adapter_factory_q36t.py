# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_ws_receiver_only_client_cp6_no_connect_adapter_factory_q36t.py
# desc: PS-Q36T guards for CP6 no-connect adapter factory. Adapter shell only; no socket, no send.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

REPO_ROOT = Path(__file__).resolve().parents[6]

DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q36T_WARROOM_V2_WEBSOCKET_RECEIVER_ONLY_CLIENT_CP6_NO_CONNECT_ADAPTER_FACTORY_NO_SEND_2026-07-04.md"

from btcts.apps.operator_ui.prediction_warroom.v2.transport.ws_receiver_only_client_cp6_no_connect_adapter_factory import build_warroom_v2_ws_receiver_only_client_cp6_no_connect_adapter_factory_packet  # noqa: E402


def test_q36t_adapter_shell_never_connects_or_sends() -> None:
    descriptor = {"packet_kind": "warroom_v2_ws_receiver_only_client_cp6_redacted_connection_descriptor_packet", "redacted_connection_descriptor_ready": True, "endpoint_value_returned": False, "token_value_returned": False, "callable_values_returned": False}
    packet = build_warroom_v2_ws_receiver_only_client_cp6_no_connect_adapter_factory_packet(descriptor, allow_no_connect_adapter_factory=True)
    assert packet["no_connect_adapter_factory_ready"] is True
    assert packet["adapter_shell"]["adapter_opens_socket"] is False
    assert packet["adapter_shell"]["adapter_sends_messages"] is False
    assert "adapter_opens_socket=false" in DOC.read_text(encoding="utf-8-sig")
