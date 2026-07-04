# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_ws_receiver_only_client_cp10_backpressure_policy_schema_q40d.py
# desc: PS-Q40D guards CP10 backpressure policy schema; metadata only and no runtime queue.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

REPO_ROOT = Path(__file__).resolve().parents[6]

from btcts.apps.operator_ui.prediction_warroom.v2.transport.ws_receiver_only_client_cp10_backpressure_policy_schema import build_warroom_v2_ws_receiver_only_client_cp10_backpressure_policy_schema_packet  # noqa: E402
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q40D_WARROOM_V2_WEBSOCKET_RECEIVER_ONLY_CLIENT_CP10_BACKPRESSURE_POLICY_SCHEMA_NO_SEND_2026-07-05.md"

def test_q40d_backpressure_policy_is_metadata_only() -> None:
    heartbeat = {"packet_kind": "warroom_v2_ws_receiver_only_client_cp10_heartbeat_policy_schema_packet", "heartbeat_policy_schema_ready": True}
    packet = build_warroom_v2_ws_receiver_only_client_cp10_backpressure_policy_schema_packet(heartbeat, allow_backpressure_policy_schema=True)
    assert packet["backpressure_policy_schema_ready"] is True
    assert packet["runtime_backpressure_allowed"] is False
    assert packet["backpressure_runtime_started"] is False
    assert "backpressure_policy_schema_ready=true" in DOC.read_text(encoding="utf-8-sig")
