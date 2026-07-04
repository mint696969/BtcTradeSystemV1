# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_ws_receiver_only_client_cp7_entry_contract_q37a.py
# desc: PS-Q37A guards CP7 entry contract after CP6 completion; no socket, no network, no send.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

REPO_ROOT = Path(__file__).resolve().parents[6]

from btcts.apps.operator_ui.prediction_warroom.v2.transport.ws_receiver_only_client_cp7_entry_contract import build_warroom_v2_ws_receiver_only_client_cp7_entry_contract_packet  # noqa: E402

DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q37A_WARROOM_V2_WEBSOCKET_RECEIVER_ONLY_CLIENT_CP7_ENTRY_CONTRACT_NO_SEND_2026-07-05.md"


def test_q37a_entry_requires_cp6_completion_and_stays_no_connect() -> None:
    cp6 = {"packet_kind": "warroom_v2_ws_receiver_only_client_cp6_completion_packet", "cp6_completed": True, "cp6_completion_commit_ready": True}
    packet = build_warroom_v2_ws_receiver_only_client_cp7_entry_contract_packet(cp6, allow_cp7_entry=True)
    assert packet["cp7_entry_ready"] is True
    assert packet["next_checkpoint"] == "CP7_dry_run_approval_gate"
    assert packet["socket_opened"] is False
    assert packet["external_network_used"] is False
    assert packet["send_disabled"] is True
    assert "cp7_entry_ready=true" in DOC.read_text(encoding="utf-8-sig")


def test_q37a_blocks_without_explicit_entry_allowance() -> None:
    cp6 = {"packet_kind": "warroom_v2_ws_receiver_only_client_cp6_completion_packet", "cp6_completed": True, "cp6_completion_commit_ready": True}
    packet = build_warroom_v2_ws_receiver_only_client_cp7_entry_contract_packet(cp6)
    assert packet["cp7_entry_ready"] is False
