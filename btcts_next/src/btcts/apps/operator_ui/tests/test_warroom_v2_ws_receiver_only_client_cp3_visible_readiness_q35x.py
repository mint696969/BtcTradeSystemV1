# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_ws_receiver_only_client_cp3_visible_readiness_q35x.py
# desc: PS-Q35X guards for CP3 visible readiness proposal. Proposal metadata only; no page, no socket, no send.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

REPO_ROOT = Path(__file__).resolve().parents[6]

from btcts.apps.operator_ui.prediction_warroom.v2.transport.ws_receiver_only_client_cp1_completion import build_warroom_v2_ws_receiver_only_client_cp1_completion_packet  # noqa: E402
from btcts.apps.operator_ui.prediction_warroom.v2.transport.ws_receiver_only_client_cp3_visible_readiness import build_warroom_v2_ws_receiver_only_client_cp3_visible_readiness_contract, build_warroom_v2_ws_receiver_only_client_cp3_visible_readiness_packet  # noqa: E402

MODULE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/ws_receiver_only_client_cp3_visible_readiness.py"
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q35X_WARROOM_V2_WEBSOCKET_RECEIVER_ONLY_CLIENT_CP3_VISIBLE_READINESS_NO_SEND_2026-07-04.md"


def _cp1() -> dict[str, object]:
    return build_warroom_v2_ws_receiver_only_client_cp1_completion_packet({"packet_kind": "warroom_v2_ws_receiver_only_client_cp1_readiness_gate_packet", "cp1_readiness_gate_ready": True, "cp1_done_candidate": True}, allow_cp1_completion=True)


def test_q35x_is_proposal_only_not_page_surface() -> None:
    contract = build_warroom_v2_ws_receiver_only_client_cp3_visible_readiness_contract()
    assert contract["proposal_only"] is True
    assert contract["warroom_page_modified"] is False
    assert contract["send_disabled"] is True


def test_q35x_builds_ready_proposal_from_cp1_completion() -> None:
    packet = build_warroom_v2_ws_receiver_only_client_cp3_visible_readiness_packet(cp1_completion_packet=_cp1(), allow_visible_readiness_proposal=True)
    assert packet["packet_kind"] == "warroom_v2_ws_receiver_only_client_cp3_visible_readiness_proposal_packet"
    assert packet["cp3_visible_readiness_proposal_ready"] is True
    assert packet["receiver_visible_readiness_label"] == "cp1_ready"
    assert packet["live_stream_enabled"] is False


def test_q35x_doc_and_module_are_no_send_no_page() -> None:
    module = MODULE.read_text(encoding="utf-8-sig")
    doc = DOC.read_text(encoding="utf-8-sig")
    assert "proposal_only=true" in doc
    assert "warroom_page_modified=false" in doc
    assert "not_sending_external_messages=true" in doc
    for token in ("import streamlit", "from streamlit", "import websockets", "send_to_broker(", "submit_order(", "append_ledger(", "run_prediction(", "invoke_classifier("):
        assert token not in module
