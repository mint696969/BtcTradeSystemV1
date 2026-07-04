# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_ws_receiver_only_client_cp6_live_adapter_contract_q36r.py
# desc: PS-Q36R guards for CP6 live adapter contract. Contract only; no socket, no send.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

REPO_ROOT = Path(__file__).resolve().parents[6]

DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q36R_WARROOM_V2_WEBSOCKET_RECEIVER_ONLY_CLIENT_CP6_LIVE_ADAPTER_CONTRACT_NO_SEND_2026-07-04.md"

from btcts.apps.operator_ui.prediction_warroom.v2.transport.ws_receiver_only_client_cp6_live_adapter_contract import build_warroom_v2_ws_receiver_only_client_cp6_live_adapter_contract, build_warroom_v2_ws_receiver_only_client_cp6_live_adapter_contract_packet  # noqa: E402


def test_q36r_contract_ready_from_cp5_completion() -> None:
    contract = build_warroom_v2_ws_receiver_only_client_cp6_live_adapter_contract()
    assert contract["schema_contract_defined"] is True
    assert contract["adapter_factory_added"] is False
    packet = build_warroom_v2_ws_receiver_only_client_cp6_live_adapter_contract_packet({"packet_kind": "warroom_v2_ws_receiver_only_client_cp5_completion_packet", "cp5_completion_commit_ready": True}, allow_cp6_contract=True)
    assert packet["cp6_live_adapter_contract_ready"] is True
    assert packet["socket_opened"] is False
    assert "cp6_live_adapter_contract_ready=true" in DOC.read_text(encoding="utf-8-sig")
