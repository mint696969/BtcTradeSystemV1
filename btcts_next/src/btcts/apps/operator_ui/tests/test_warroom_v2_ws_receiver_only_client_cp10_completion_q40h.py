# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_ws_receiver_only_client_cp10_completion_q40h.py
# desc: PS-Q40H guards CP10 completion handoff to CP11 topic widgets; dry-run/no-action/no-send remains enforced.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

REPO_ROOT = Path(__file__).resolve().parents[6]

from btcts.apps.operator_ui.prediction_warroom.v2.transport.ws_receiver_only_client_cp10_completion import build_warroom_v2_ws_receiver_only_client_cp10_completion_packet  # noqa: E402
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q40H_WARROOM_V2_WEBSOCKET_RECEIVER_ONLY_CLIENT_CP10_COMPLETION_NO_SEND_2026-07-05.md"

def test_q40h_completion_hands_off_to_cp11_topic_widgets() -> None:
    guard = {"packet_kind": "warroom_v2_ws_receiver_only_client_cp10_danger_zone_no_action_guard_packet", "danger_zone_no_action_guard_ready": True}
    packet = build_warroom_v2_ws_receiver_only_client_cp10_completion_packet(guard, allow_cp10_completion=True)
    assert packet["cp10_completed"] is True
    assert packet["cp10_completion_commit_ready"] is True
    assert packet["next_checkpoint"] == "CP11_topic_widgets"
    assert packet["reconnect_invoked"] is False
    assert packet["heartbeat_sent"] is False
    assert packet["backpressure_runtime_started"] is False
    assert "cp10_completed=true" in DOC.read_text(encoding="utf-8-sig")
