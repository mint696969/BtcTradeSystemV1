# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_ws_receiver_only_client_cp11_entry_contract_q41a.py
# desc: PS-Q41A guards CP11 entry after CP10 completion; read-only/default-off/no-send.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

REPO_ROOT = Path(__file__).resolve().parents[6]

from btcts.apps.operator_ui.prediction_warroom.v2.transport.ws_receiver_only_client_cp11_entry_contract import build_warroom_v2_ws_receiver_only_client_cp11_entry_contract_packet as fn  # noqa: E402
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q41A_WARROOM_V2_WEBSOCKET_RECEIVER_ONLY_CLIENT_CP11_ENTRY_CONTRACT_NO_SEND_2026-07-05.md"

def test_entry_contract_q41a_safe_no_send() -> None:
    cp10 = {'packet_kind': 'warroom_v2_ws_receiver_only_client_cp10_completion_packet', 'cp10_completed': True, 'cp10_completion_commit_ready': True}
    packet = fn(cp10, allow_cp11_entry=True)
    assert packet["cp11_entry_ready"] is True
    assert packet["next_checkpoint"] == "CP11_topic_registry_schema"
    assert packet["topic_widgets_read_only"] is True
    assert packet["topic_subscription_requested"] is False
    assert packet["topic_subscribe_invoked"] is False
    assert packet["client_sends_messages"] is False
    assert packet["send_disabled"] is True
    assert "cp11_entry_ready=true" in DOC.read_text(encoding="utf-8-sig")
