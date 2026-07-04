# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_ws_receiver_only_client_cp5_message_normalizer_core_q36k.py
# desc: PS-Q36K guards for CP5 pure message normalizer core. Metadata normalization only; no socket, no send.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

REPO_ROOT = Path(__file__).resolve().parents[6]

from btcts.apps.operator_ui.prediction_warroom.v2.transport.ws_receiver_only_client_cp5_message_normalizer_core import build_warroom_v2_ws_receiver_only_client_cp5_message_normalizer_core_packet, normalize_warroom_v2_ws_receiver_only_client_cp5_message  # noqa: E402

DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q36K_WARROOM_V2_WEBSOCKET_RECEIVER_ONLY_CLIENT_CP5_MESSAGE_NORMALIZER_CORE_NO_SEND_2026-07-04.md"


def test_q36k_normalizes_tick_metadata() -> None:
    msg = normalize_warroom_v2_ws_receiver_only_client_cp5_message({"topic": "fake.btc.tick", "symbol": "BTC", "sequence": "7"}, source_kind="unit", allow_normalize=True)
    assert msg["normalized_ok"] is True
    assert msg["message_kind"] == "tick"
    assert msg["sequence"] == 7
    assert msg["raw_payload_returned"] is False


def test_q36k_core_packet_ready_from_contract() -> None:
    packet = build_warroom_v2_ws_receiver_only_client_cp5_message_normalizer_core_packet({"packet_kind": "warroom_v2_ws_receiver_only_client_cp5_message_normalizer_contract_packet", "cp5_message_normalizer_contract_ready": True}, allow_core_normalization=True)
    assert packet["cp5_message_normalizer_core_ready"] is True
    assert packet["sample_normalized_message"]["normalized_ok"] is True
    assert "normalized_ok=true" in DOC.read_text(encoding="utf-8-sig")
