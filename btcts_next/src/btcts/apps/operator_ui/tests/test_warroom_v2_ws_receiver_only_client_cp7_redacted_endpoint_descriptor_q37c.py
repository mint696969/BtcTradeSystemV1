# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_ws_receiver_only_client_cp7_redacted_endpoint_descriptor_q37c.py
# desc: PS-Q37C guards CP7 redacted endpoint descriptor; no endpoint/token/callable values returned.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

REPO_ROOT = Path(__file__).resolve().parents[6]

from btcts.apps.operator_ui.prediction_warroom.v2.transport.ws_receiver_only_client_cp7_redacted_endpoint_descriptor import build_warroom_v2_ws_receiver_only_client_cp7_redacted_endpoint_descriptor_packet  # noqa: E402

DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q37C_WARROOM_V2_WEBSOCKET_RECEIVER_ONLY_CLIENT_CP7_REDACTED_ENDPOINT_DESCRIPTOR_NO_SEND_2026-07-05.md"


def test_q37c_returns_configured_booleans_only() -> None:
    gate = {"packet_kind": "warroom_v2_ws_receiver_only_client_cp7_dry_run_approval_gate_packet", "dry_run_approval_ready": True}
    packet = build_warroom_v2_ws_receiver_only_client_cp7_redacted_endpoint_descriptor_packet(gate, endpoint_configured=True, token_configured=True, connect_callable_configured=True, allow_descriptor=True)
    assert packet["redacted_endpoint_descriptor_ready"] is True
    assert packet["endpoint_configured"] is True
    assert packet["endpoint_value_returned"] is False
    assert packet["token_value_returned"] is False
    assert packet["callable_values_returned"] is False
    assert "redacted_endpoint_descriptor_ready=true" in DOC.read_text(encoding="utf-8-sig")
