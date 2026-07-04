# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_ws_receiver_only_client_cp9_read_only_render_packet_q39d.py
# desc: PS-Q39D guards CP9 read-only render packet; no Streamlit import/callable/control.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

REPO_ROOT = Path(__file__).resolve().parents[6]

from btcts.apps.operator_ui.prediction_warroom.v2.transport.ws_receiver_only_client_cp9_read_only_render_packet import build_warroom_v2_ws_receiver_only_client_cp9_read_only_render_packet  # noqa: E402
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q39D_WARROOM_V2_WEBSOCKET_RECEIVER_ONLY_CLIENT_CP9_READ_ONLY_RENDER_PACKET_NO_SEND_2026-07-05.md"
MODULE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/ws_receiver_only_client_cp9_read_only_render_packet.py"

def test_q39d_render_packet_is_metadata_only_no_streamlit() -> None:
    rows = {"packet_kind": "warroom_v2_ws_receiver_only_client_cp9_panel_row_shaping_packet", "panel_row_shaping_ready": True, "panel_rows": [{"topic": "book"}], "panel_row_count": 1}
    packet = build_warroom_v2_ws_receiver_only_client_cp9_read_only_render_packet(rows, allow_render_packet=True)
    assert packet["read_only_render_packet_ready"] is True
    assert packet["render_callable_returned"] is False
    assert packet["streamlit_imported"] is False
    assert "import streamlit" not in MODULE.read_text(encoding="utf-8-sig")
    assert "read_only_render_packet_ready=true" in DOC.read_text(encoding="utf-8-sig")
