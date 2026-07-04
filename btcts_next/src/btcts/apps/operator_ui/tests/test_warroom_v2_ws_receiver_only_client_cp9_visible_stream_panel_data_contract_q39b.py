# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_ws_receiver_only_client_cp9_visible_stream_panel_data_contract_q39b.py
# desc: PS-Q39B guards CP9 visible stream panel data contract; safe fields only.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

REPO_ROOT = Path(__file__).resolve().parents[6]

from btcts.apps.operator_ui.prediction_warroom.v2.transport.ws_receiver_only_client_cp9_visible_stream_panel_data_contract import build_warroom_v2_ws_receiver_only_client_cp9_visible_stream_panel_data_contract_packet  # noqa: E402
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q39B_WARROOM_V2_WEBSOCKET_RECEIVER_ONLY_CLIENT_CP9_VISIBLE_STREAM_PANEL_DATA_CONTRACT_NO_SEND_2026-07-05.md"

def test_q39b_contract_excludes_raw_and_secret_fields() -> None:
    entry = {"packet_kind": "warroom_v2_ws_receiver_only_client_cp9_entry_contract_packet", "cp9_entry_ready": True}
    packet = build_warroom_v2_ws_receiver_only_client_cp9_visible_stream_panel_data_contract_packet(entry, allow_data_contract=True)
    assert packet["visible_stream_panel_data_contract_ready"] is True
    assert "raw_payload" not in packet["safe_panel_fields"]
    assert "endpoint" not in packet["safe_panel_fields"]
    assert packet["operator_action_controls_added"] is False
    assert "visible_stream_panel_data_contract_ready=true" in DOC.read_text(encoding="utf-8-sig")
