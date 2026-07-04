# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_ws_receiver_only_client_cp7_forbidden_behavior_guard_q37g.py
# desc: PS-Q37G guards CP7 forbidden behavior proof; no socket/network/send/broker/prediction/classifier.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

REPO_ROOT = Path(__file__).resolve().parents[6]

from btcts.apps.operator_ui.prediction_warroom.v2.transport.ws_receiver_only_client_cp7_forbidden_behavior_guard import build_warroom_v2_ws_receiver_only_client_cp7_forbidden_behavior_guard_packet  # noqa: E402

DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q37G_WARROOM_V2_WEBSOCKET_RECEIVER_ONLY_CLIENT_CP7_FORBIDDEN_BEHAVIOR_GUARD_NO_SEND_2026-07-05.md"


def test_q37g_guard_passes_clean_preflight_and_catches_socket_open() -> None:
    preflight = {"packet_kind": "warroom_v2_ws_receiver_only_client_cp7_dry_run_preflight_packet", "dry_run_preflight_ready": True, "not_sending_external_messages": True, "send_disabled": True}
    packet = build_warroom_v2_ws_receiver_only_client_cp7_forbidden_behavior_guard_packet(preflight, allow_guard=True)
    assert packet["cp7_forbidden_behavior_guard_ready"] is True
    assert packet["guard_failures"] == []
    bad = dict(preflight, socket_opened=True)
    blocked = build_warroom_v2_ws_receiver_only_client_cp7_forbidden_behavior_guard_packet(bad, allow_guard=True)
    assert blocked["cp7_forbidden_behavior_guard_ready"] is False
    assert "socket_opened" in blocked["guard_failures"]
    assert "cp7_forbidden_behavior_guard_ready=true" in DOC.read_text(encoding="utf-8-sig")
