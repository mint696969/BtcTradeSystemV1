# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_ws_receiver_only_client_cp11_completion_q41h.py
# desc: PS-Q41H guards CP11 completion handoff to CP12 danger-zone; no-connect/no-send remains enforced.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

REPO_ROOT = Path(__file__).resolve().parents[6]

from btcts.apps.operator_ui.prediction_warroom.v2.transport.ws_receiver_only_client_cp11_completion import build_warroom_v2_ws_receiver_only_client_cp11_completion_packet as fn  # noqa: E402
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q41H_WARROOM_V2_WEBSOCKET_RECEIVER_ONLY_CLIENT_CP11_COMPLETION_NO_SEND_2026-07-05.md"

def test_completion_q41h_safe_no_send() -> None:
    guard = {'packet_kind': 'warroom_v2_ws_receiver_only_client_cp11_no_control_topic_widget_guard_packet', 'no_control_topic_widget_guard_ready': True}
    packet = fn(guard, allow_cp11_completion=True)
    assert packet['cp12_is_danger_zone'] is True
    assert packet["cp11_completed"] is True
    assert packet["next_checkpoint"] == "CP12_operator_facing_live_receiver_mode"
    assert packet["topic_widgets_read_only"] is True
    assert packet["topic_subscription_requested"] is False
    assert packet["topic_subscribe_invoked"] is False
    assert packet["client_sends_messages"] is False
    assert packet["send_disabled"] is True
    assert "cp11_completed=true" in DOC.read_text(encoding="utf-8-sig")
