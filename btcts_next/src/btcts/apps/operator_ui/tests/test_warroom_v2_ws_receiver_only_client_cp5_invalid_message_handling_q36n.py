# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_ws_receiver_only_client_cp5_invalid_message_handling_q36n.py
# desc: PS-Q36N guards for CP5 invalid message handling. Error metadata only; no socket, no send.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

REPO_ROOT = Path(__file__).resolve().parents[6]

from btcts.apps.operator_ui.prediction_warroom.v2.transport.ws_receiver_only_client_cp5_invalid_message_handling import build_warroom_v2_ws_receiver_only_client_cp5_invalid_message_handling_packet  # noqa: E402

DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q36N_WARROOM_V2_WEBSOCKET_RECEIVER_ONLY_CLIENT_CP5_INVALID_MESSAGE_HANDLING_NO_SEND_2026-07-04.md"


def test_q36n_marks_invalid_messages_without_dropping() -> None:
    packet = build_warroom_v2_ws_receiver_only_client_cp5_invalid_message_handling_packet({"packet_kind": "warroom_v2_ws_receiver_only_client_cp5_message_normalizer_core_packet", "cp5_message_normalizer_core_ready": True}, allow_invalid_message_handling=True)
    assert packet["invalid_message_handling_ready"] is True
    assert packet["invalid_message_count"] >= 2
    assert packet["dropped_count"] == 0
    assert "invalid_message_count=true" in DOC.read_text(encoding="utf-8-sig")
