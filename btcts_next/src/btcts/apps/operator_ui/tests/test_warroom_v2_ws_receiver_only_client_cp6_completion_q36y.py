# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_ws_receiver_only_client_cp6_completion_q36y.py
# desc: PS-Q36Y guards for CP6 completion. Full no-connect live adapter preparation closes before CP7.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

REPO_ROOT = Path(__file__).resolve().parents[6]

DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q36Y_WARROOM_V2_WEBSOCKET_RECEIVER_ONLY_CLIENT_CP6_COMPLETION_NO_SEND_2026-07-04.md"

from btcts.apps.operator_ui.prediction_warroom.v2.transport.ws_receiver_only_client_cp6_completion import build_warroom_v2_ws_receiver_only_client_cp6_completion_packet  # noqa: E402


def test_q36y_completion_after_no_connect_no_send_guard() -> None:
    guard = {"packet_kind": "warroom_v2_ws_receiver_only_client_cp6_no_connect_no_send_guard_packet", "cp6_no_connect_no_send_guard_ready": True}
    packet = build_warroom_v2_ws_receiver_only_client_cp6_completion_packet(guard, allow_cp6_completion=True)
    assert packet["cp6_completed"] is True
    assert packet["cp6_completion_commit_ready"] is True
    assert packet["next_checkpoint"] == "CP7_gated_receiver_dry_run_preflight_no_send"
    assert packet["socket_opened"] is False
    assert "cp6_completed=true" in DOC.read_text(encoding="utf-8-sig")
