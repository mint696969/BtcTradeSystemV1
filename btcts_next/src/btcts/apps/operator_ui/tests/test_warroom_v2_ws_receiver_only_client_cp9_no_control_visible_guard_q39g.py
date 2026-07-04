# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_ws_receiver_only_client_cp9_no_control_visible_guard_q39g.py
# desc: PS-Q39G guards CP9 no-control visible proof; no connect/start/send control.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

REPO_ROOT = Path(__file__).resolve().parents[6]

from btcts.apps.operator_ui.prediction_warroom.v2.transport.ws_receiver_only_client_cp9_no_control_visible_guard import build_warroom_v2_ws_receiver_only_client_cp9_no_control_visible_guard_packet  # noqa: E402
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q39G_WARROOM_V2_WEBSOCKET_RECEIVER_ONLY_CLIENT_CP9_NO_CONTROL_VISIBLE_GUARD_NO_SEND_2026-07-05.md"

def test_q39g_guard_passes_clean_boundary_and_catches_control() -> None:
    boundary = {"packet_kind": "warroom_v2_ws_receiver_only_client_cp9_warroom_page_boundary_guard_packet", "visible_stream_panel_ready": True, "visible_stream_panel_read_only": True, "not_sending_external_messages": True, "send_disabled": True}
    packet = build_warroom_v2_ws_receiver_only_client_cp9_no_control_visible_guard_packet(boundary, allow_guard=True)
    assert packet["cp9_no_control_visible_guard_ready"] is True
    bad = dict(boundary, operator_action_controls_added=True)
    blocked = build_warroom_v2_ws_receiver_only_client_cp9_no_control_visible_guard_packet(bad, allow_guard=True)
    assert blocked["cp9_no_control_visible_guard_ready"] is False
    assert "operator_action_controls_added" in blocked["guard_failures"]
    assert "cp9_no_control_visible_guard_ready=true" in DOC.read_text(encoding="utf-8-sig")
