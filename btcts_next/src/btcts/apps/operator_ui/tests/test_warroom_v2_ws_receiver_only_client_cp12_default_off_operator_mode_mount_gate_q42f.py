# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_ws_receiver_only_client_cp12_default_off_operator_mode_mount_gate_q42f.py
# desc: PS-Q42F guards CP12 cp12_default_off_operator_mode_mount_gate no-send danger-zone behavior.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

REPO_ROOT = Path(__file__).resolve().parents[6]

from btcts.apps.operator_ui.prediction_warroom.v2.transport.ws_receiver_only_client_cp12_default_off_operator_mode_mount_gate import build_warroom_v2_ws_receiver_only_client_cp12_default_off_operator_mode_mount_gate_packet as fn  # noqa: E402

DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q42F_WARROOM_V2_WEBSOCKET_RECEIVER_ONLY_CLIENT_CP12_DEFAULT_OFF_OPERATOR_MODE_MOUNT_GATE_NO_SEND_2026-07-05.md"


def test_default_off_operator_mode_mount_gate_q42f_safe_no_action_no_send() -> None:
    previous = {"packet_kind": "warroom_v2_ws_receiver_only_client_cp12_live_mode_dry_run_readiness_evaluator_packet"}
    previous["live_mode_dry_run_readiness_evaluator_ready"] = True
    packet = fn(previous, allow_default_off_operator_mode_mount_gate=True)
    assert packet["default_off_operator_mode_mount_gate_ready"] is True
    assert packet["next_checkpoint"] == "CP12_operator_facing_no_action_guard"
    assert packet["cp12_is_danger_zone"] is True
    assert packet["operator_facing_live_mode_dry_run_only"] is True
    assert packet["operator_live_mode_enabled"] is False
    assert packet["operator_action_controls_added"] is False
    assert packet["socket_opened"] is False
    assert packet["client_sends_messages"] is False
    assert packet["send_disabled"] is True
    assert "default_off_operator_mode_mount_gate_ready=true" in DOC.read_text(encoding="utf-8-sig")
