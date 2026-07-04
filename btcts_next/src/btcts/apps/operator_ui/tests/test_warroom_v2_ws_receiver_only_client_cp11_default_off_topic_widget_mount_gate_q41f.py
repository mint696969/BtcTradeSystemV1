# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_ws_receiver_only_client_cp11_default_off_topic_widget_mount_gate_q41f.py
# desc: PS-Q41F guards CP11 default-off topic widget mount gate; no page change.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

REPO_ROOT = Path(__file__).resolve().parents[6]

from btcts.apps.operator_ui.prediction_warroom.v2.transport.ws_receiver_only_client_cp11_default_off_topic_widget_mount_gate import build_warroom_v2_ws_receiver_only_client_cp11_default_off_topic_widget_mount_gate_packet as fn  # noqa: E402
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q41F_WARROOM_V2_WEBSOCKET_RECEIVER_ONLY_CLIENT_CP11_DEFAULT_OFF_TOPIC_WIDGET_MOUNT_GATE_NO_SEND_2026-07-05.md"

def test_default_off_topic_widget_mount_gate_q41f_safe_no_send() -> None:
    render = {'packet_kind': 'warroom_v2_ws_receiver_only_client_cp11_read_only_topic_render_packet', 'read_only_topic_render_packet_ready': True}
    packet = fn(render, allow_mount_gate=True)
    assert packet['topic_widget_mount_default_enabled'] is False
    assert packet['warroom_page_modified'] is False
    assert packet["default_off_topic_widget_mount_gate_ready"] is True
    assert packet["next_checkpoint"] == "CP11_no_control_topic_widget_guard"
    assert packet["topic_widgets_read_only"] is True
    assert packet["topic_subscription_requested"] is False
    assert packet["topic_subscribe_invoked"] is False
    assert packet["client_sends_messages"] is False
    assert packet["send_disabled"] is True
    assert "default_off_topic_widget_mount_gate_ready=true" in DOC.read_text(encoding="utf-8-sig")
