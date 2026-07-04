# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_ws_receiver_only_client_cp6_normalized_adapter_envelope_q36u.py
# desc: PS-Q36U guards for CP6 normalized adapter envelope. Metadata envelope only; no raw payload.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

REPO_ROOT = Path(__file__).resolve().parents[6]

DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q36U_WARROOM_V2_WEBSOCKET_RECEIVER_ONLY_CLIENT_CP6_NORMALIZED_ADAPTER_ENVELOPE_NO_SEND_2026-07-04.md"

from btcts.apps.operator_ui.prediction_warroom.v2.transport.ws_receiver_only_client_cp6_normalized_adapter_envelope import build_warroom_v2_ws_receiver_only_client_cp6_normalized_adapter_envelope_packet  # noqa: E402


def test_q36u_wraps_cp5_normalized_metadata_only() -> None:
    factory = {"packet_kind": "warroom_v2_ws_receiver_only_client_cp6_no_connect_adapter_factory_packet", "no_connect_adapter_factory_ready": True}
    readback = {"packet_kind": "warroom_v2_ws_receiver_only_client_cp5_normalized_state_readback_packet", "normalized_state_readback_ready": True, "message_count": 7, "latest_normalized_message": {"topic": "fake.heartbeat", "message_kind": "heartbeat", "source_kind": "cp5", "sequence": 3, "normalized_ok": True}}
    packet = build_warroom_v2_ws_receiver_only_client_cp6_normalized_adapter_envelope_packet(factory, cp5_normalized_state_readback_packet=readback, allow_adapter_envelope=True)
    assert packet["adapter_envelope_ready"] is True
    assert packet["adapter_envelope"]["topic"] == "fake.heartbeat"
    assert packet["raw_payload_returned"] is False
    assert packet["endpoint_value_returned"] is False
    assert packet["token_value_returned"] is False
    assert packet["callable_values_returned"] is False
    assert "adapter_envelope_ready=true" in DOC.read_text(encoding="utf-8-sig")
