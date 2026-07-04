# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_ws_receiver_only_client_cp5_no_send_traceability_guard_q36p.py
# desc: PS-Q36P guards for CP5 no-send traceability. Normalized readback must stay metadata-only and no-send.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

REPO_ROOT = Path(__file__).resolve().parents[6]

from btcts.apps.operator_ui.prediction_warroom.v2.transport.ws_receiver_only_client_cp5_no_send_traceability_guard import build_warroom_v2_ws_receiver_only_client_cp5_no_send_traceability_guard_packet  # noqa: E402

DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q36P_WARROOM_V2_WEBSOCKET_RECEIVER_ONLY_CLIENT_CP5_NO_SEND_TRACEABILITY_GUARD_NO_SEND_2026-07-04.md"


def test_q36p_accepts_only_no_send_normalized_readback() -> None:
    readback = {"packet_kind": "warroom_v2_ws_receiver_only_client_cp5_normalized_state_readback_packet", "normalized_state_readback_ready": True, "message_count": 5, "invalid_message_count": 2, "raw_payload_returned": False, "socket_opened": False, "client_sends_messages": False, "external_message_send_enabled": False, "send_disabled": True}
    packet = build_warroom_v2_ws_receiver_only_client_cp5_no_send_traceability_guard_packet(readback, allow_cp5_no_send_guard=True)
    assert packet["cp5_no_send_guard_ready"] is True
    assert packet["would_send_to_broker"] is False
    assert packet["classifier_invoked"] is False
    assert "cp5_no_send_guard_ready=true" in DOC.read_text(encoding="utf-8-sig")
