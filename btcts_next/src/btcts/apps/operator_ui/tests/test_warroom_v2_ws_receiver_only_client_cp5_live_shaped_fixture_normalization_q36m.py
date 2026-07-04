# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_ws_receiver_only_client_cp5_live_shaped_fixture_normalization_q36m.py
# desc: PS-Q36M guards for CP5 live-shaped fixture normalization. Local fixture only; no network, no socket, no send.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

REPO_ROOT = Path(__file__).resolve().parents[6]

from btcts.apps.operator_ui.prediction_warroom.v2.transport.ws_receiver_only_client_cp5_live_shaped_fixture_normalization import build_warroom_v2_ws_receiver_only_client_cp5_live_shaped_fixture_normalization_packet  # noqa: E402

DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q36M_WARROOM_V2_WEBSOCKET_RECEIVER_ONLY_CLIENT_CP5_LIVE_SHAPED_FIXTURE_NORMALIZATION_NO_SEND_2026-07-04.md"


def test_q36m_normalizes_local_live_shaped_fixture_only() -> None:
    packet = build_warroom_v2_ws_receiver_only_client_cp5_live_shaped_fixture_normalization_packet({"packet_kind": "warroom_v2_ws_receiver_only_client_cp5_message_normalizer_core_packet", "cp5_message_normalizer_core_ready": True}, allow_live_shaped_fixture_normalization=True)
    assert packet["live_shaped_fixture_normalization_ready"] is True
    assert packet["fixture_source"] == "local_only"
    assert packet["message_count"] == 2
    assert packet["external_network_used"] is False
    assert "fixture_source=local_only" in DOC.read_text(encoding="utf-8-sig")
