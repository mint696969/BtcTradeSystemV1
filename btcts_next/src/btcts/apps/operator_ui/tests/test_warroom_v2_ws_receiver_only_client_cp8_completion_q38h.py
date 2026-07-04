# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_ws_receiver_only_client_cp8_completion_q38h.py
# desc: PS-Q38H guards CP8 completion handoff to CP9 visible stream panel; no-connect/no-send remains enforced.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

REPO_ROOT = Path(__file__).resolve().parents[6]

from btcts.apps.operator_ui.prediction_warroom.v2.transport.ws_receiver_only_client_cp8_completion import build_warroom_v2_ws_receiver_only_client_cp8_completion_packet  # noqa: E402

DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q38H_WARROOM_V2_WEBSOCKET_RECEIVER_ONLY_CLIENT_CP8_COMPLETION_NO_SEND_2026-07-05.md"


def test_q38h_completion_hands_off_to_cp9_no_connect_no_send() -> None:
    guard = {"packet_kind": "warroom_v2_ws_receiver_only_client_cp8_no_send_state_boundary_guard_packet", "cp8_no_send_state_boundary_guard_ready": True}
    packet = build_warroom_v2_ws_receiver_only_client_cp8_completion_packet(guard, allow_cp8_completion=True)
    assert packet["cp8_completed"] is True
    assert packet["cp8_completion_commit_ready"] is True
    assert packet["next_checkpoint"] == "CP9_visible_stream_panel"
    assert packet["socket_opened"] is False
    assert packet["client_sends_messages"] is False
    assert "cp8_completed=true" in DOC.read_text(encoding="utf-8-sig")
