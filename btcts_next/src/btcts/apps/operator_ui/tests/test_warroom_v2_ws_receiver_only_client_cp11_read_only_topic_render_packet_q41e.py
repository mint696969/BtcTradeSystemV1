# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_ws_receiver_only_client_cp11_read_only_topic_render_packet_q41e.py
# desc: PS-Q41E guards CP11 read-only topic render packet; no Streamlit/callable/control.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

REPO_ROOT = Path(__file__).resolve().parents[6]

from btcts.apps.operator_ui.prediction_warroom.v2.transport.ws_receiver_only_client_cp11_read_only_topic_render_packet import build_warroom_v2_ws_receiver_only_client_cp11_read_only_topic_render_packet as fn  # noqa: E402
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q41E_WARROOM_V2_WEBSOCKET_RECEIVER_ONLY_CLIENT_CP11_READ_ONLY_TOPIC_RENDER_PACKET_NO_SEND_2026-07-05.md"

def test_read_only_topic_render_packet_q41e_safe_no_send() -> None:
    rows = {'packet_kind': 'warroom_v2_ws_receiver_only_client_cp11_topic_widget_row_shaping_packet', 'topic_widget_row_shaping_ready': True, 'topic_widget_rows': [{'topic': 'book'}]}
    packet = fn(rows, allow_render_packet=True)
    assert packet['streamlit_imported'] is False
    assert packet['render_callable_returned'] is False
    assert packet["read_only_topic_render_packet_ready"] is True
    assert packet["next_checkpoint"] == "CP11_default_off_topic_widget_mount_gate"
    assert packet["topic_widgets_read_only"] is True
    assert packet["topic_subscription_requested"] is False
    assert packet["topic_subscribe_invoked"] is False
    assert packet["client_sends_messages"] is False
    assert packet["send_disabled"] is True
    assert "read_only_topic_render_packet_ready=true" in DOC.read_text(encoding="utf-8-sig")
