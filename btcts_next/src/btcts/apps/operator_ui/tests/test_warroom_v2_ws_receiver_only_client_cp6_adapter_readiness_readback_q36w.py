# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_ws_receiver_only_client_cp6_adapter_readiness_readback_q36w.py
# desc: PS-Q36W guards for CP6 adapter readiness/readback. Metadata readback only; no session keys, no socket, no send.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

REPO_ROOT = Path(__file__).resolve().parents[6]

DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q36W_WARROOM_V2_WEBSOCKET_RECEIVER_ONLY_CLIENT_CP6_ADAPTER_READINESS_READBACK_NO_SEND_2026-07-04.md"

from btcts.apps.operator_ui.prediction_warroom.v2.transport.ws_receiver_only_client_cp6_adapter_readiness_readback import build_warroom_v2_ws_receiver_only_client_cp6_adapter_readiness_readback_packet  # noqa: E402


def test_q36w_reads_adapter_readiness_without_exposing_keys() -> None:
    descriptor = {"packet_kind": "warroom_v2_ws_receiver_only_client_cp6_redacted_connection_descriptor_packet", "redacted_connection_descriptor_ready": True}
    factory = {"packet_kind": "warroom_v2_ws_receiver_only_client_cp6_no_connect_adapter_factory_packet", "no_connect_adapter_factory_ready": True}
    buffer = {"packet_kind": "warroom_v2_ws_receiver_only_client_cp6_bounded_local_receive_buffer_packet", "bounded_local_receive_buffer_ready": True, "buffer_count": 1, "latest_envelope": {"topic": "fake.heartbeat"}}
    packet = build_warroom_v2_ws_receiver_only_client_cp6_adapter_readiness_readback_packet(descriptor, no_connect_adapter_factory_packet=factory, bounded_local_receive_buffer_packet=buffer, allow_adapter_readiness_readback=True)
    assert packet["adapter_readiness_readback_ready"] is True
    assert packet["session_state_keys_returned"] is False
    assert packet["latest_envelope"]["topic"] == "fake.heartbeat"
    assert "adapter_readiness_readback_ready=true" in DOC.read_text(encoding="utf-8-sig")
