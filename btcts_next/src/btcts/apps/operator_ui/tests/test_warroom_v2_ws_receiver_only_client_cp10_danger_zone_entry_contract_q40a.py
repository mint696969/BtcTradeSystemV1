# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_ws_receiver_only_client_cp10_danger_zone_entry_contract_q40a.py
# desc: PS-Q40A guards CP10 danger-zone entry after CP9 completion; dry-run/no-action/no-send.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

REPO_ROOT = Path(__file__).resolve().parents[6]

from btcts.apps.operator_ui.prediction_warroom.v2.transport.ws_receiver_only_client_cp10_danger_zone_entry_contract import build_warroom_v2_ws_receiver_only_client_cp10_danger_zone_entry_contract_packet  # noqa: E402
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q40A_WARROOM_V2_WEBSOCKET_RECEIVER_ONLY_CLIENT_CP10_DANGER_ZONE_ENTRY_CONTRACT_NO_SEND_2026-07-05.md"

def test_q40a_entry_requires_cp9_completion_and_stays_no_action() -> None:
    cp9 = {"packet_kind": "warroom_v2_ws_receiver_only_client_cp9_completion_packet", "cp9_completed": True, "cp9_completion_commit_ready": True}
    packet = build_warroom_v2_ws_receiver_only_client_cp10_danger_zone_entry_contract_packet(cp9, allow_cp10_entry=True)
    assert packet["cp10_entry_ready"] is True
    assert packet["cp10_is_danger_zone"] is True
    assert packet["runtime_actions_allowed_now"] is False
    assert packet["reconnect_invoked"] is False
    assert packet["send_disabled"] is True
    assert "cp10_entry_ready=true" in DOC.read_text(encoding="utf-8-sig")
