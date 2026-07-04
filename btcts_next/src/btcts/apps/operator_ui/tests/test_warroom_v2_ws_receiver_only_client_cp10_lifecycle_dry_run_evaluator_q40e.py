# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_ws_receiver_only_client_cp10_lifecycle_dry_run_evaluator_q40e.py
# desc: PS-Q40E guards CP10 lifecycle dry-run evaluator; recommends metadata without runtime action.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

REPO_ROOT = Path(__file__).resolve().parents[6]

from btcts.apps.operator_ui.prediction_warroom.v2.transport.ws_receiver_only_client_cp10_lifecycle_dry_run_evaluator import build_warroom_v2_ws_receiver_only_client_cp10_lifecycle_dry_run_evaluator_packet  # noqa: E402
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q40E_WARROOM_V2_WEBSOCKET_RECEIVER_ONLY_CLIENT_CP10_LIFECYCLE_DRY_RUN_EVALUATOR_NO_SEND_2026-07-05.md"

def test_q40e_dry_run_evaluates_without_runtime_action() -> None:
    backpressure = {"packet_kind": "warroom_v2_ws_receiver_only_client_cp10_backpressure_policy_schema_packet", "backpressure_policy_schema_ready": True, "max_pending_messages_metadata": 100, "drop_policy_metadata": "drop_oldest_metadata_only"}
    packet = build_warroom_v2_ws_receiver_only_client_cp10_lifecycle_dry_run_evaluator_packet(backpressure, {"pending_message_count": 90, "last_seen_age_ms": 20000}, allow_dry_run_evaluator=True)
    assert packet["lifecycle_dry_run_evaluator_ready"] is True
    assert packet["dry_run_backpressure_warning"] is True
    assert packet["dry_run_reconnect_recommended_metadata"] is True
    assert packet["runtime_action_executed"] is False
    assert packet["reconnect_invoked"] is False
    assert "lifecycle_dry_run_evaluator_ready=true" in DOC.read_text(encoding="utf-8-sig")
