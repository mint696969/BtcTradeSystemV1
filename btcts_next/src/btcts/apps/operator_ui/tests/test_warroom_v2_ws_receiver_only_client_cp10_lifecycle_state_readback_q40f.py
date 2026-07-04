# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_ws_receiver_only_client_cp10_lifecycle_state_readback_q40f.py
# desc: PS-Q40F guards CP10 lifecycle state readback; summary metadata only and no raw payload.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

REPO_ROOT = Path(__file__).resolve().parents[6]

from btcts.apps.operator_ui.prediction_warroom.v2.transport.ws_receiver_only_client_cp10_lifecycle_state_readback import build_warroom_v2_ws_receiver_only_client_cp10_lifecycle_state_readback_packet  # noqa: E402
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q40F_WARROOM_V2_WEBSOCKET_RECEIVER_ONLY_CLIENT_CP10_LIFECYCLE_STATE_READBACK_NO_SEND_2026-07-05.md"

def test_q40f_readback_is_metadata_only_no_action() -> None:
    evaluator = {"packet_kind": "warroom_v2_ws_receiver_only_client_cp10_lifecycle_dry_run_evaluator_packet", "lifecycle_dry_run_evaluator_ready": True, "dry_run_stale_state_detected": True, "dry_run_backpressure_warning": True, "dry_run_reconnect_recommended_metadata": True}
    packet = build_warroom_v2_ws_receiver_only_client_cp10_lifecycle_state_readback_packet(evaluator, allow_state_readback=True)
    assert packet["lifecycle_state_readback_ready"] is True
    assert packet["lifecycle_summary"]["mode"] == "dry_run_no_action"
    assert packet["runtime_action_executed"] is False
    assert packet["raw_payload_returned"] is False
    assert "lifecycle_state_readback_ready=true" in DOC.read_text(encoding="utf-8-sig")
