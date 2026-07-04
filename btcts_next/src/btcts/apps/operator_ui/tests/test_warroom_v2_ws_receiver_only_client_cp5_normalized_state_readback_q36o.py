# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_ws_receiver_only_client_cp5_normalized_state_readback_q36o.py
# desc: PS-Q36O guards for CP5 normalized state write/readback. Metadata-only target state; no socket, no send.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

REPO_ROOT = Path(__file__).resolve().parents[6]

from btcts.apps.operator_ui.prediction_warroom.v2.transport.ws_receiver_only_client_cp5_normalized_state_readback import STATE_KEY, apply_warroom_v2_ws_receiver_only_client_cp5_normalized_state_write, build_warroom_v2_ws_receiver_only_client_cp5_normalized_state_readback_packet  # noqa: E402

DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q36O_WARROOM_V2_WEBSOCKET_RECEIVER_ONLY_CLIENT_CP5_NORMALIZED_STATE_READBACK_NO_SEND_2026-07-04.md"


def test_q36o_writes_and_reads_normalized_metadata() -> None:
    fake = {"packet_kind": "warroom_v2_ws_receiver_only_client_cp5_fake_source_normalization_packet", "normalized_messages": [{"topic": "fake.heartbeat", "source_kind": "cp4_fake_source", "normalized_ok": True, "message_kind": "heartbeat"}]}
    state: dict[str, object] = {}
    write = apply_warroom_v2_ws_receiver_only_client_cp5_normalized_state_write(state, fake_source_normalization_packet=fake, allow_normalized_state_write=True)
    readback = build_warroom_v2_ws_receiver_only_client_cp5_normalized_state_readback_packet(state, state_key=STATE_KEY, allow_normalized_state_readback=True)
    assert write["target_state_mutated"] is True
    assert readback["normalized_state_readback_ready"] is True
    assert readback["latest_normalized_message"]["topic"] == "fake.heartbeat"
    assert "normalized_state_readback_ready=true" in DOC.read_text(encoding="utf-8-sig")
