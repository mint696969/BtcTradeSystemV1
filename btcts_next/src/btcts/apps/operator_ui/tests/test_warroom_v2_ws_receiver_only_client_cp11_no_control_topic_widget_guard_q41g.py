# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_ws_receiver_only_client_cp11_no_control_topic_widget_guard_q41g.py
# desc: PS-Q41G guards CP11 no-control topic widget proof; catches subscription/control flags.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

REPO_ROOT = Path(__file__).resolve().parents[6]

from btcts.apps.operator_ui.prediction_warroom.v2.transport.ws_receiver_only_client_cp11_no_control_topic_widget_guard import build_warroom_v2_ws_receiver_only_client_cp11_no_control_topic_widget_guard_packet as fn  # noqa: E402
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q41G_WARROOM_V2_WEBSOCKET_RECEIVER_ONLY_CLIENT_CP11_NO_CONTROL_TOPIC_WIDGET_GUARD_NO_SEND_2026-07-05.md"

def test_no_control_topic_widget_guard_q41g_safe_no_send() -> None:
    gate = {'packet_kind': 'warroom_v2_ws_receiver_only_client_cp11_default_off_topic_widget_mount_gate_packet', 'default_off_topic_widget_mount_gate_ready': True, 'not_sending_external_messages': True, 'send_disabled': True}
    packet = fn(gate, allow_guard=True)
    assert packet['no_control_topic_widget_guard_ready'] is True
    blocked = fn(dict(gate, topic_subscription_requested=True), allow_guard=True)
    assert blocked['no_control_topic_widget_guard_ready'] is False
    assert 'topic_subscription_requested' in blocked['guard_failures']
    assert packet["no_control_topic_widget_guard_ready"] is True
    assert packet["next_checkpoint"] == "CP11_completion"
    assert packet["topic_widgets_read_only"] is True
    assert packet["topic_subscription_requested"] is False
    assert packet["topic_subscribe_invoked"] is False
    assert packet["client_sends_messages"] is False
    assert packet["send_disabled"] is True
    assert "no_control_topic_widget_guard_ready=true" in DOC.read_text(encoding="utf-8-sig")
