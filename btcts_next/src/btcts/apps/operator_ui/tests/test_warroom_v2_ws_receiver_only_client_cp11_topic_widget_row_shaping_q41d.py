# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_ws_receiver_only_client_cp11_topic_widget_row_shaping_q41d.py
# desc: PS-Q41D guards CP11 topic widget row shaping; grouped metadata-only rows.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

REPO_ROOT = Path(__file__).resolve().parents[6]

from btcts.apps.operator_ui.prediction_warroom.v2.transport.ws_receiver_only_client_cp11_topic_widget_row_shaping import build_warroom_v2_ws_receiver_only_client_cp11_topic_widget_row_shaping_packet as fn  # noqa: E402
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q41D_WARROOM_V2_WEBSOCKET_RECEIVER_ONLY_CLIENT_CP11_TOPIC_WIDGET_ROW_SHAPING_NO_SEND_2026-07-05.md"

def test_topic_widget_row_shaping_q41d_safe_no_send() -> None:
    contract = {'packet_kind': 'warroom_v2_ws_receiver_only_client_cp11_topic_widget_data_contract_packet', 'topic_widget_data_contract_ready': True}
    render = {'packet_kind': 'warroom_v2_ws_receiver_only_client_cp9_read_only_render_packet', 'read_only_render_packet_ready': True, 'render_rows': [{'topic': 'book', 'sequence': 1, 'summary': 'metadata', 'raw_payload': {'blocked': True}}]}
    packet = fn(contract, render, allow_row_shaping=True)
    assert packet['topic_widget_row_count'] == 1
    assert 'raw_payload' not in packet['topic_widget_rows'][0]
    assert packet["topic_widget_row_shaping_ready"] is True
    assert packet["next_checkpoint"] == "CP11_read_only_topic_render_packet"
    assert packet["topic_widgets_read_only"] is True
    assert packet["topic_subscription_requested"] is False
    assert packet["topic_subscribe_invoked"] is False
    assert packet["client_sends_messages"] is False
    assert packet["send_disabled"] is True
    assert "topic_widget_row_shaping_ready=true" in DOC.read_text(encoding="utf-8-sig")
