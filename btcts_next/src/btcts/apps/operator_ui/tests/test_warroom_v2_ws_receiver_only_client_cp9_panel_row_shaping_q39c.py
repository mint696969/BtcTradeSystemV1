# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_ws_receiver_only_client_cp9_panel_row_shaping_q39c.py
# desc: PS-Q39C guards CP9 panel row shaping; metadata-only rows from CP8 readback.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

REPO_ROOT = Path(__file__).resolve().parents[6]

from btcts.apps.operator_ui.prediction_warroom.v2.transport.ws_receiver_only_client_cp9_panel_row_shaping import build_warroom_v2_ws_receiver_only_client_cp9_panel_row_shaping_packet  # noqa: E402
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q39C_WARROOM_V2_WEBSOCKET_RECEIVER_ONLY_CLIENT_CP9_PANEL_ROW_SHAPING_NO_SEND_2026-07-05.md"

def test_q39c_shapes_safe_rows_only() -> None:
    contract = {"packet_kind": "warroom_v2_ws_receiver_only_client_cp9_visible_stream_panel_data_contract_packet", "visible_stream_panel_data_contract_ready": True}
    readback = {"packet_kind": "warroom_v2_ws_receiver_only_client_cp8_state_readback_packet", "state_readback_ready": True, "recent_incoming_metadata": [{"topic": "book", "sequence": 1, "raw_payload": {"blocked": True}}]}
    packet = build_warroom_v2_ws_receiver_only_client_cp9_panel_row_shaping_packet(contract, readback, allow_row_shaping=True)
    assert packet["panel_row_shaping_ready"] is True
    assert packet["panel_row_count"] == 1
    assert "raw_payload" not in packet["panel_rows"][0]
    assert packet["panel_rows_metadata_only"] is True
    assert "panel_row_shaping_ready=true" in DOC.read_text(encoding="utf-8-sig")
