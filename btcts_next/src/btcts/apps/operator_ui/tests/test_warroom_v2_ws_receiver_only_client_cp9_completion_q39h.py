# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_ws_receiver_only_client_cp9_completion_q39h.py
# desc: PS-Q39H guards CP9 completion handoff to CP10 danger-zone; no-connect/no-send remains enforced.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

REPO_ROOT = Path(__file__).resolve().parents[6]

from btcts.apps.operator_ui.prediction_warroom.v2.transport.ws_receiver_only_client_cp9_completion import build_warroom_v2_ws_receiver_only_client_cp9_completion_packet  # noqa: E402
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q39H_WARROOM_V2_WEBSOCKET_RECEIVER_ONLY_CLIENT_CP9_COMPLETION_NO_SEND_2026-07-05.md"

def test_q39h_completion_hands_off_to_cp10_danger_zone() -> None:
    guard = {"packet_kind": "warroom_v2_ws_receiver_only_client_cp9_no_control_visible_guard_packet", "cp9_no_control_visible_guard_ready": True}
    packet = build_warroom_v2_ws_receiver_only_client_cp9_completion_packet(guard, allow_cp9_completion=True)
    assert packet["cp9_completed"] is True
    assert packet["cp9_completion_commit_ready"] is True
    assert packet["next_checkpoint"] == "CP10_reconnect_heartbeat_backpressure"
    assert packet["cp10_is_danger_zone"] is True
    assert packet["client_sends_messages"] is False
    assert "cp9_completed=true" in DOC.read_text(encoding="utf-8-sig")
