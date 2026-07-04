# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_ws_receiver_only_client_cp4_fake_message_source_q36d.py
# desc: PS-Q36D guards for CP4 fixed fake message source. Local fake summaries only; no network, no socket, no send.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

REPO_ROOT = Path(__file__).resolve().parents[6]

from btcts.apps.operator_ui.prediction_warroom.v2.transport.ws_receiver_only_client_cp4_fake_message_source import build_warroom_v2_ws_receiver_only_client_cp4_fake_message_source_packet  # noqa: E402
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q36D_WARROOM_V2_WEBSOCKET_RECEIVER_ONLY_CLIENT_CP4_FAKE_MESSAGE_SOURCE_NO_SEND_2026-07-04.md"

def test_q36d_produces_fixed_fake_message_summaries_without_raw_payload() -> None:
    packet = build_warroom_v2_ws_receiver_only_client_cp4_fake_message_source_packet({"packet_kind": "warroom_v2_ws_receiver_only_client_cp4_fake_receive_loop_contract_packet", "cp4_fake_receive_loop_contract_ready": True}, allow_fake_message_source=True)
    assert packet["fake_message_source_ready"] is True
    assert packet["message_count"] == 3
    assert packet["fake_message_summaries"][-1]["topic"] == "fake.heartbeat"
    assert "price" not in str(packet["fake_message_summaries"])
    assert "fake_messages_only=true" in DOC.read_text(encoding="utf-8-sig")
