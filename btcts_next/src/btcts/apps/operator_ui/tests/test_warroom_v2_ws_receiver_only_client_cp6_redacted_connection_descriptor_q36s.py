# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_ws_receiver_only_client_cp6_redacted_connection_descriptor_q36s.py
# desc: PS-Q36S guards for CP6 redacted connection descriptor. No endpoint/token/callable exposure.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

REPO_ROOT = Path(__file__).resolve().parents[6]

DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q36S_WARROOM_V2_WEBSOCKET_RECEIVER_ONLY_CLIENT_CP6_REDACTED_CONNECTION_DESCRIPTOR_NO_SEND_2026-07-04.md"

from btcts.apps.operator_ui.prediction_warroom.v2.transport.ws_receiver_only_client_cp6_redacted_connection_descriptor import build_warroom_v2_ws_receiver_only_client_cp6_redacted_connection_descriptor_packet  # noqa: E402


def test_q36s_descriptor_is_redacted() -> None:
    packet = build_warroom_v2_ws_receiver_only_client_cp6_redacted_connection_descriptor_packet({"packet_kind": "warroom_v2_ws_receiver_only_client_cp6_live_adapter_contract_packet", "cp6_live_adapter_contract_ready": True}, allow_descriptor=True)
    assert packet["redacted_connection_descriptor_ready"] is True
    assert packet["endpoint_value_returned"] is False
    assert packet["token_value_returned"] is False
    assert packet["callable_values_returned"] is False
    assert "secret_exposure=false" in DOC.read_text(encoding="utf-8-sig")
