# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_ws_receiver_only_client_cp13_danger_zone_entry_contract_q43a.py
# desc: PS-Q43A guards CP13 cp13_danger_zone_entry_contract no-action/no-send danger-zone behavior.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

REPO_ROOT = Path(__file__).resolve().parents[6]

from btcts.apps.operator_ui.prediction_warroom.v2.transport.ws_receiver_only_client_cp13_danger_zone_entry_contract import build_warroom_v2_ws_receiver_only_client_cp13_danger_zone_entry_contract_packet as fn  # noqa: E402

DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q43A_WARROOM_V2_WEBSOCKET_RECEIVER_ONLY_CLIENT_CP13_DANGER_ZONE_ENTRY_CONTRACT_NO_SEND_2026-07-05.md"


def test_danger_zone_entry_contract_q43a_safe_no_broadcast_no_send() -> None:
    previous = {"packet_kind": "warroom_v2_ws_receiver_only_client_cp12_completion_packet"}
    previous["cp12_completed"] = True
    previous["cp12_completion_commit_ready"] = True
    packet = fn(previous, allow_cp13_entry=True)
    assert packet["cp13_entry_ready"] is True
    assert packet["next_checkpoint"] == "CP13_high_visibility_delivery_policy_schema"
    assert packet["cp13_is_danger_zone"] is True
    assert packet["high_visibility_realtime_delivery_dry_run_only"] is True
    assert packet["high_visibility_delivery_enabled"] is False
    assert packet["broadcast_invoked"] is False
    assert packet["publish_invoked"] is False
    assert packet["socket_opened"] is False
    assert packet["external_network_used"] is False
    assert packet["client_sends_messages"] is False
    assert packet["send_disabled"] is True
    assert "cp13_entry_ready=true" in DOC.read_text(encoding="utf-8-sig")
