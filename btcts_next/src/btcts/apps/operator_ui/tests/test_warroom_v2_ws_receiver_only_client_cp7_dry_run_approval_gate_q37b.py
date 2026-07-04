# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_ws_receiver_only_client_cp7_dry_run_approval_gate_q37b.py
# desc: PS-Q37B guards CP7 dry-run approval gate; explicit non-secret label, no socket, no send.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

REPO_ROOT = Path(__file__).resolve().parents[6]

from btcts.apps.operator_ui.prediction_warroom.v2.transport.ws_receiver_only_client_cp7_dry_run_approval_gate import REQUIRED_APPROVAL_LABEL, build_warroom_v2_ws_receiver_only_client_cp7_dry_run_approval_gate_packet  # noqa: E402

DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q37B_WARROOM_V2_WEBSOCKET_RECEIVER_ONLY_CLIENT_CP7_DRY_RUN_APPROVAL_GATE_NO_SEND_2026-07-05.md"


def test_q37b_requires_ack_and_non_secret_label() -> None:
    entry = {"packet_kind": "warroom_v2_ws_receiver_only_client_cp7_entry_contract_packet", "cp7_entry_ready": True}
    packet = build_warroom_v2_ws_receiver_only_client_cp7_dry_run_approval_gate_packet(entry, operator_dry_run_ack=True, approval_label=REQUIRED_APPROVAL_LABEL)
    assert packet["dry_run_approval_ready"] is True
    assert packet["approval_token_value_returned"] is False
    assert packet["secret_exposure"] is False
    assert packet["socket_opened"] is False
    assert "dry_run_approval_ready=true" in DOC.read_text(encoding="utf-8-sig")


def test_q37b_blocks_bad_label() -> None:
    entry = {"packet_kind": "warroom_v2_ws_receiver_only_client_cp7_entry_contract_packet", "cp7_entry_ready": True}
    packet = build_warroom_v2_ws_receiver_only_client_cp7_dry_run_approval_gate_packet(entry, operator_dry_run_ack=True, approval_label="WRONG")
    assert packet["dry_run_approval_ready"] is False
