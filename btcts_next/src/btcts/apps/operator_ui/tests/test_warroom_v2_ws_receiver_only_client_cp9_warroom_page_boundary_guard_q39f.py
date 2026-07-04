# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_ws_receiver_only_client_cp9_warroom_page_boundary_guard_q39f.py
# desc: PS-Q39F guards CP9 WarRoom page boundary; page remains untouched.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

REPO_ROOT = Path(__file__).resolve().parents[6]

from btcts.apps.operator_ui.prediction_warroom.v2.transport.ws_receiver_only_client_cp9_warroom_page_boundary_guard import build_warroom_v2_ws_receiver_only_client_cp9_warroom_page_boundary_guard_packet  # noqa: E402
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q39F_WARROOM_V2_WEBSOCKET_RECEIVER_ONLY_CLIENT_CP9_WARROOM_PAGE_BOUNDARY_GUARD_NO_SEND_2026-07-05.md"

def test_q39f_page_boundary_guard_keeps_page_unmodified() -> None:
    gate = {"packet_kind": "warroom_v2_ws_receiver_only_client_cp9_default_off_mount_gate_packet", "default_off_mount_gate_ready": True, "warroom_page_modified": False}
    packet = build_warroom_v2_ws_receiver_only_client_cp9_warroom_page_boundary_guard_packet(gate, allow_page_boundary_guard=True)
    assert packet["warroom_page_boundary_guard_ready"] is True
    assert packet["warroom_page_modified"] is False
    assert packet["visible_controls_added"] is False
    assert "warroom_page_boundary_guard_ready=true" in DOC.read_text(encoding="utf-8-sig")
