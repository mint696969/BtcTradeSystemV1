# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_ws_receiver_only_client_cp5_fake_source_normalization_q36l.py
# desc: PS-Q36L guards for CP5 fake source normalization. CP4 fake summaries only; no socket, no send.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

REPO_ROOT = Path(__file__).resolve().parents[6]

from btcts.apps.operator_ui.prediction_warroom.v2.transport.ws_receiver_only_client_cp5_fake_source_normalization import build_warroom_v2_ws_receiver_only_client_cp5_fake_source_normalization_packet  # noqa: E402

DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q36L_WARROOM_V2_WEBSOCKET_RECEIVER_ONLY_CLIENT_CP5_FAKE_SOURCE_NORMALIZATION_NO_SEND_2026-07-04.md"


def test_q36l_normalizes_cp4_fake_summaries() -> None:
    source = {"packet_kind": "warroom_v2_ws_receiver_only_client_cp4_fake_message_source_packet", "fake_message_source_ready": True, "fake_message_summaries": [{"topic": "fake.btc.tick", "symbol": "BTC", "sequence": 1}, {"topic": "fake.heartbeat", "symbol": "BTC", "sequence": 2}]}
    core = {"packet_kind": "warroom_v2_ws_receiver_only_client_cp5_message_normalizer_core_packet", "cp5_message_normalizer_core_ready": True}
    packet = build_warroom_v2_ws_receiver_only_client_cp5_fake_source_normalization_packet(source, normalizer_core_packet=core, allow_fake_source_normalization=True)
    assert packet["fake_source_normalization_ready"] is True
    assert packet["normalized_ok_count"] == 2
    assert packet["normalized_messages"][-1]["message_kind"] == "heartbeat"
    assert "fake_source_normalization_ready=true" in DOC.read_text(encoding="utf-8-sig")
