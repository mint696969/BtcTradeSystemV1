# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_ws_receiver_only_client_cp9_default_off_mount_gate_q39e.py
# desc: PS-Q39E guards CP9 default-off mount gate; no actual page mount.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

REPO_ROOT = Path(__file__).resolve().parents[6]

from btcts.apps.operator_ui.prediction_warroom.v2.transport.ws_receiver_only_client_cp9_default_off_mount_gate import build_warroom_v2_ws_receiver_only_client_cp9_default_off_mount_gate_packet  # noqa: E402
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q39E_WARROOM_V2_WEBSOCKET_RECEIVER_ONLY_CLIENT_CP9_DEFAULT_OFF_MOUNT_GATE_NO_SEND_2026-07-05.md"

def test_q39e_default_off_mount_gate_does_not_mount_now() -> None:
    render = {"packet_kind": "warroom_v2_ws_receiver_only_client_cp9_read_only_render_packet", "read_only_render_packet_ready": True}
    packet = build_warroom_v2_ws_receiver_only_client_cp9_default_off_mount_gate_packet(render, allow_default_off_mount_gate=True)
    assert packet["default_off_mount_gate_ready"] is True
    assert packet["panel_mount_default_enabled"] is False
    assert packet["panel_mount_requested_now"] is False
    assert packet["warroom_page_modified"] is False
    assert "default_off_mount_gate_ready=true" in DOC.read_text(encoding="utf-8-sig")
