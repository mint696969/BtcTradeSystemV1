# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_ws_receiver_only_client_cp3_visible_readiness_implementation_gate_q35y.py
# desc: PS-Q35Y guards for CP3 visible readiness implementation gate. Display metadata allowlist only; no socket, no send.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

REPO_ROOT = Path(__file__).resolve().parents[6]

from btcts.apps.operator_ui.prediction_warroom.v2.transport.ws_receiver_only_client_cp3_visible_readiness_implementation_gate import build_warroom_v2_ws_receiver_only_client_cp3_visible_readiness_implementation_gate_packet  # noqa: E402

MODULE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/ws_receiver_only_client_cp3_visible_readiness_implementation_gate.py"
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q35Y_WARROOM_V2_WEBSOCKET_RECEIVER_ONLY_CLIENT_CP3_VISIBLE_READINESS_IMPLEMENTATION_GATE_NO_SEND_2026-07-04.md"


def _proposal() -> dict[str, object]:
    return {"packet_kind": "warroom_v2_ws_receiver_only_client_cp3_visible_readiness_proposal_packet", "cp3_visible_readiness_proposal_ready": True, "cp1_completed": True, "receiver_visible_readiness_label": "cp1_ready"}


def test_q35y_gates_visible_metadata_allowlist() -> None:
    packet = build_warroom_v2_ws_receiver_only_client_cp3_visible_readiness_implementation_gate_packet(_proposal(), allow_implementation_gate=True)
    assert packet["cp3_visible_readiness_implementation_gate_ready"] is True
    assert packet["display_metadata_allowed"] is True
    assert packet["receiver_visible_readiness_label"] == "cp1_ready"
    assert packet["visible_controls_added"] is False


def test_q35y_doc_and_module_no_page_no_send() -> None:
    module = MODULE.read_text(encoding="utf-8-sig")
    doc = DOC.read_text(encoding="utf-8-sig")
    assert "display_metadata_allowlist=true" in doc
    assert "warroom_page_modified=false" in doc
    assert "not_sending_external_messages=true" in doc
    for token in ("import streamlit", "from streamlit", "import websockets", "send_to_broker(", "submit_order(", "append_ledger(", "run_prediction(", "invoke_classifier("):
        assert token not in module
