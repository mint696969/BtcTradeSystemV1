# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_ws_receiver_only_client_cp8_incoming_metadata_state_schema_q38b.py
# desc: PS-Q38B guards CP8 incoming metadata state schema; bounded metadata only and no raw payload.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

REPO_ROOT = Path(__file__).resolve().parents[6]

from btcts.apps.operator_ui.prediction_warroom.v2.transport.ws_receiver_only_client_cp8_incoming_metadata_state_schema import build_warroom_v2_ws_receiver_only_client_cp8_incoming_metadata_state_schema_packet  # noqa: E402

DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q38B_WARROOM_V2_WEBSOCKET_RECEIVER_ONLY_CLIENT_CP8_INCOMING_METADATA_STATE_SCHEMA_NO_SEND_2026-07-05.md"


def test_q38b_schema_is_bounded_metadata_only() -> None:
    entry = {"packet_kind": "warroom_v2_ws_receiver_only_client_cp8_entry_contract_packet", "cp8_entry_ready": True}
    packet = build_warroom_v2_ws_receiver_only_client_cp8_incoming_metadata_state_schema_packet(entry, allow_schema=True)
    assert packet["incoming_metadata_state_schema_ready"] is True
    assert "raw_payload" not in packet["allowed_metadata_fields"]
    assert packet["bounded_metadata_state"] is True
    assert "incoming_metadata_state_schema_ready=true" in DOC.read_text(encoding="utf-8-sig")
