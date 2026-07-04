# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_ws_receiver_only_client_cp8_entry_contract_q38a.py
# desc: PS-Q38A guards CP8 entry contract after CP7 completion; no socket, no network, no send.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

REPO_ROOT = Path(__file__).resolve().parents[6]

from btcts.apps.operator_ui.prediction_warroom.v2.transport.ws_receiver_only_client_cp8_entry_contract import build_warroom_v2_ws_receiver_only_client_cp8_entry_contract_packet  # noqa: E402

DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q38A_WARROOM_V2_WEBSOCKET_RECEIVER_ONLY_CLIENT_CP8_ENTRY_CONTRACT_NO_SEND_2026-07-05.md"


def test_q38a_entry_requires_cp7_completion() -> None:
    cp7 = {"packet_kind": "warroom_v2_ws_receiver_only_client_cp7_completion_packet", "cp7_completed": True, "cp7_completion_commit_ready": True}
    packet = build_warroom_v2_ws_receiver_only_client_cp8_entry_contract_packet(cp7, allow_cp8_entry=True)
    assert packet["cp8_entry_ready"] is True
    assert packet["next_checkpoint"] == "CP8_incoming_metadata_state_schema"
    assert packet["socket_opened"] is False
    assert packet["send_disabled"] is True
    assert "cp8_entry_ready=true" in DOC.read_text(encoding="utf-8-sig")
