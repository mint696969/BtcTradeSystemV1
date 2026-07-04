# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_ws_receiver_only_client_cp10_danger_zone_no_action_guard_q40g.py
# desc: PS-Q40G guards CP10 danger-zone no-action proof; catches runtime action flags.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

REPO_ROOT = Path(__file__).resolve().parents[6]

from btcts.apps.operator_ui.prediction_warroom.v2.transport.ws_receiver_only_client_cp10_danger_zone_no_action_guard import build_warroom_v2_ws_receiver_only_client_cp10_danger_zone_no_action_guard_packet  # noqa: E402
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q40G_WARROOM_V2_WEBSOCKET_RECEIVER_ONLY_CLIENT_CP10_DANGER_ZONE_NO_ACTION_GUARD_NO_SEND_2026-07-05.md"

def test_q40g_guard_passes_clean_readback_and_catches_reconnect() -> None:
    readback = {"packet_kind": "warroom_v2_ws_receiver_only_client_cp10_lifecycle_state_readback_packet", "lifecycle_state_readback_ready": True, "not_sending_external_messages": True, "send_disabled": True}
    packet = build_warroom_v2_ws_receiver_only_client_cp10_danger_zone_no_action_guard_packet(readback, allow_guard=True)
    assert packet["danger_zone_no_action_guard_ready"] is True
    bad = dict(readback, reconnect_invoked=True)
    blocked = build_warroom_v2_ws_receiver_only_client_cp10_danger_zone_no_action_guard_packet(bad, allow_guard=True)
    assert blocked["danger_zone_no_action_guard_ready"] is False
    assert "reconnect_invoked" in blocked["guard_failures"]
    assert "danger_zone_no_action_guard_ready=true" in DOC.read_text(encoding="utf-8-sig")
