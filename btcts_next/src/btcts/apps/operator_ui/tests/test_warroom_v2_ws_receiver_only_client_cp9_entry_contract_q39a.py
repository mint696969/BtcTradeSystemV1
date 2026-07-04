# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_ws_receiver_only_client_cp9_entry_contract_q39a.py
# desc: PS-Q39A guards CP9 entry after CP8 completion; read-only/default-off/no-send.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

REPO_ROOT = Path(__file__).resolve().parents[6]

from btcts.apps.operator_ui.prediction_warroom.v2.transport.ws_receiver_only_client_cp9_entry_contract import build_warroom_v2_ws_receiver_only_client_cp9_entry_contract_packet  # noqa: E402
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q39A_WARROOM_V2_WEBSOCKET_RECEIVER_ONLY_CLIENT_CP9_ENTRY_CONTRACT_NO_SEND_2026-07-05.md"

def test_q39a_entry_requires_cp8_completion() -> None:
    cp8 = {"packet_kind": "warroom_v2_ws_receiver_only_client_cp8_completion_packet", "cp8_completed": True, "cp8_completion_commit_ready": True}
    packet = build_warroom_v2_ws_receiver_only_client_cp9_entry_contract_packet(cp8, allow_cp9_entry=True)
    assert packet["cp9_entry_ready"] is True
    assert packet["visible_stream_panel_read_only"] is True
    assert packet["panel_mount_default_enabled"] is False
    assert packet["send_disabled"] is True
    assert "cp9_entry_ready=true" in DOC.read_text(encoding="utf-8-sig")
