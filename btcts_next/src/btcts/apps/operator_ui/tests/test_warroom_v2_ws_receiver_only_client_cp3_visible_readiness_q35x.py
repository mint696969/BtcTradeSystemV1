# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_ws_receiver_only_client_cp3_visible_readiness_q35x.py
# desc: PS-Q35X guards for CP3 visible readiness on compact badge. No controls, no socket, no send.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.apps.operator_ui.prediction_warroom.v2.transport.ws_receiver_only_client_cp1_completion import build_warroom_v2_ws_receiver_only_client_cp1_completion_packet  # noqa: E402
from btcts.apps.operator_ui.prediction_warroom.v2.transport.ws_receiver_only_client_cp3_visible_readiness import (  # noqa: E402
    WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_CP3_VISIBLE_READINESS_STATE_KEY,
    build_warroom_v2_ws_receiver_only_client_cp3_visible_readiness_contract,
    build_warroom_v2_ws_receiver_only_client_cp3_visible_readiness_packet,
)

REPO_ROOT = Path(__file__).resolve().parents[6]
MODULE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/ws_receiver_only_client_cp3_visible_readiness.py"
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q35X_WARROOM_V2_WEBSOCKET_RECEIVER_ONLY_CLIENT_CP3_VISIBLE_READINESS_NO_SEND_2026-07-04.md"
WARROOM_PAGE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py"


def _badge() -> dict[str, object]:
    return {"compact_status_badge_visible_now": True, "compact_badge_markdown": "`WS Receiver` mount ready · state=present · readback=ready · msgs=0 · no socket/send"}


def _cp1() -> dict[str, object]:
    return build_warroom_v2_ws_receiver_only_client_cp1_completion_packet({"packet_kind": "warroom_v2_ws_receiver_only_client_cp1_readiness_gate_packet", "cp1_readiness_gate_ready": True, "cp1_done_candidate": True}, allow_cp1_completion=True)


def test_q35x_contract_is_visible_readiness_no_send() -> None:
    packet = build_warroom_v2_ws_receiver_only_client_cp3_visible_readiness_contract()
    assert packet["state_key"] == WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_CP3_VISIBLE_READINESS_STATE_KEY
    assert packet["selected_visible_surface"] == "compact_status_badge"
    assert packet["visible_controls_added"] is False
    assert packet["warroom_page_modified"] is True
    assert packet["send_disabled"] is True


def test_q35x_adds_cp1_ready_label_to_existing_badge() -> None:
    packet = build_warroom_v2_ws_receiver_only_client_cp3_visible_readiness_packet(compact_badge_packet=_badge(), cp1_completion_packet=_cp1(), allow_visible_readiness=True)
    assert packet["cp3_visible_readiness_visible_now"] is True
    assert packet["cp1_completed"] is True
    assert packet["receiver_visible_readiness_label"] == "cp1_ready"
    assert packet["visible_readiness_markdown"].endswith("readiness=cp1_ready · live=off")
    assert packet["visible_controls_added"] is False
    assert packet["socket_opened"] is False


def test_q35x_page_patches_existing_badge_without_extra_markdown_call() -> None:
    page = WARROOM_PAGE.read_text(encoding="utf-8-sig")
    assert "ws_receiver_only_client_cp3_visible_readiness" in page
    assert "WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_CP3_VISIBLE_READINESS_SOURCE_STATE_KEY" in page
    assert 'badge_packet["compact_badge_markdown"] = str(cp3_visible_readiness_packet.get("visible_readiness_markdown") or badge_packet.get("compact_badge_markdown") or "")' in page
    assert page.count('st.markdown(str(badge_packet.get("compact_badge_markdown") or ""))') == 1


def test_q35x_doc_and_module_preserve_no_send_boundary() -> None:
    module = MODULE.read_text(encoding="utf-8-sig")
    doc = DOC.read_text(encoding="utf-8-sig")
    assert "visible_readiness_display_enabled=true" in doc
    assert "live_stream_enabled=false" in doc
    assert "not_sending_external_messages=true" in doc
    for token in ("import streamlit", "from streamlit", "import websockets", "send_to_broker(", "submit_order(", "append_ledger(", "run_prediction(", "invoke_classifier(", "D:" + chr(92), "E:" + chr(92)):
        assert token not in module
