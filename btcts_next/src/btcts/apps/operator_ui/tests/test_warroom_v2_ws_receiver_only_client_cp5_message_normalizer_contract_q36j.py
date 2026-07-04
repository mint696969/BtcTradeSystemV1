# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_ws_receiver_only_client_cp5_message_normalizer_contract_q36j.py
# desc: PS-Q36J guards for CP5 message normalizer contract. Schema contract only; no network, no socket, no send.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

REPO_ROOT = Path(__file__).resolve().parents[6]

from btcts.apps.operator_ui.prediction_warroom.v2.transport.ws_receiver_only_client_cp5_message_normalizer_contract import build_warroom_v2_ws_receiver_only_client_cp5_message_normalizer_contract, build_warroom_v2_ws_receiver_only_client_cp5_message_normalizer_contract_packet  # noqa: E402

DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q36J_WARROOM_V2_WEBSOCKET_RECEIVER_ONLY_CLIENT_CP5_MESSAGE_NORMALIZER_CONTRACT_NO_SEND_2026-07-04.md"


def test_q36j_contract_is_schema_only_no_send() -> None:
    contract = build_warroom_v2_ws_receiver_only_client_cp5_message_normalizer_contract()
    assert contract["schema_contract_defined"] is True
    assert contract["normalizer_core_added"] is False
    assert contract["warroom_page_modified"] is False
    assert contract["send_disabled"] is True


def test_q36j_ready_from_cp4_close_handoff() -> None:
    packet = build_warroom_v2_ws_receiver_only_client_cp5_message_normalizer_contract_packet({"packet_kind": "warroom_v2_ws_receiver_only_client_cp4_close_handoff_packet", "cp4_close_ready": True}, allow_cp5_contract=True)
    assert packet["cp5_message_normalizer_contract_ready"] is True
    assert packet["next_checkpoint"] == "CP5_normalizer_core"
    assert "schema_contract_defined=true" in DOC.read_text(encoding="utf-8-sig")
