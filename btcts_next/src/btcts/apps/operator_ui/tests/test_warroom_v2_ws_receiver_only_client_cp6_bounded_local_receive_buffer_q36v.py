# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_ws_receiver_only_client_cp6_bounded_local_receive_buffer_q36v.py
# desc: PS-Q36V guards for CP6 bounded local receive buffer metadata. No receive loop, no socket, no send.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

REPO_ROOT = Path(__file__).resolve().parents[6]

DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q36V_WARROOM_V2_WEBSOCKET_RECEIVER_ONLY_CLIENT_CP6_BOUNDED_LOCAL_RECEIVE_BUFFER_NO_SEND_2026-07-04.md"

from btcts.apps.operator_ui.prediction_warroom.v2.transport.ws_receiver_only_client_cp6_bounded_local_receive_buffer import build_warroom_v2_ws_receiver_only_client_cp6_bounded_local_receive_buffer_packet  # noqa: E402


def test_q36v_buffers_metadata_with_bound() -> None:
    envelope = {"packet_kind": "warroom_v2_ws_receiver_only_client_cp6_normalized_adapter_envelope_packet", "adapter_envelope_ready": True, "adapter_envelope": {"topic": "fake.heartbeat", "sequence": 3}}
    packet = build_warroom_v2_ws_receiver_only_client_cp6_bounded_local_receive_buffer_packet(envelope, existing_envelopes=[{"topic": "old"}], max_buffer_size=1, allow_bounded_buffer=True)
    assert packet["bounded_local_receive_buffer_ready"] is True
    assert packet["buffer_count"] == 1
    assert packet["latest_envelope"]["topic"] == "fake.heartbeat"
    assert packet["receive_loop_started"] is False
    assert packet["endpoint_value_returned"] is False
    assert packet["token_value_returned"] is False
    assert packet["callable_values_returned"] is False
    assert "receive_loop_started=false" in DOC.read_text(encoding="utf-8-sig")
