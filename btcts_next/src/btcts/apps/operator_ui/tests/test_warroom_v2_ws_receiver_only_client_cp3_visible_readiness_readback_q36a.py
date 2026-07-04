# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_ws_receiver_only_client_cp3_visible_readiness_readback_q36a.py
# desc: PS-Q36A guards for CP3 visible readiness metadata readback. No raw surface packet, no socket, no send.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

REPO_ROOT = Path(__file__).resolve().parents[6]

from btcts.apps.operator_ui.prediction_warroom.v2.transport.ws_receiver_only_client_cp3_visible_readiness_readback import build_warroom_v2_ws_receiver_only_client_cp3_visible_readiness_readback_packet  # noqa: E402
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q36A_WARROOM_V2_WEBSOCKET_RECEIVER_ONLY_CLIENT_CP3_VISIBLE_READINESS_READBACK_NO_SEND_2026-07-04.md"

def test_q36a_reads_visible_readiness_metadata_only() -> None:
    packet = build_warroom_v2_ws_receiver_only_client_cp3_visible_readiness_readback_packet({"packet_kind": "warroom_v2_ws_receiver_only_client_cp3_minimal_visible_readiness_surface_packet", "cp3_visible_readiness_visible_now": True, "visible_readiness_markdown": "x", "receiver_visible_readiness_label": "cp1_ready"}, allow_visible_readiness_readback=True)
    assert packet["cp3_visible_readiness_readback_ready"] is True
    assert packet["visible_readiness_markdown_present"] is True
    assert packet["raw_surface_packet_returned"] is False
    assert "not_sending_external_messages=true" in DOC.read_text(encoding="utf-8-sig")
