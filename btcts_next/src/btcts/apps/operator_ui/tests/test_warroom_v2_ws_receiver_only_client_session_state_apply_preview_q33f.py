# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_ws_receiver_only_client_session_state_apply_preview_q33f.py
# desc: PS-Q33F guards for receiver-only client session_state apply preview. Default-off/no-socket/no-mutation.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.apps.operator_ui.prediction_warroom.v2 import (  # noqa: E402
    WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_SESSION_STATE_APPLY_PREVIEW_KEY,
    build_warroom_v2_ws_receiver_only_client_session_state_apply_preview_contract,
    build_warroom_v2_ws_receiver_only_client_session_state_apply_preview_packet,
)

REPO_ROOT = Path(__file__).resolve().parents[6]
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q33F_WARROOM_V2_WEBSOCKET_RECEIVER_ONLY_CLIENT_SESSION_STATE_APPLY_PREVIEW_DEFAULT_OFF_NO_SOCKET_2026-07-03.md"
TRANSPORT_DIR = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport"
WARROOM_PAGE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py"


def _apply_gate_ready() -> dict[str, object]:
    candidate = {
        "candidate_kind": "future_lightweight_receiver_state_update_preview",
        "message_count": 1,
        "topics": ["warroom.market.snapshot"],
        "latest_topic": "warroom.market.snapshot",
        "latest_widget_id": "market_snapshot_strip",
        "latest_sequence": 11,
        "messages": [{"topic": "warroom.market.snapshot", "widget_id": "market_snapshot_strip", "sequence": 11}],
        "preview_only": True,
        "applied_now": False,
    }
    return {
        "lightweight_state_apply_allowed_for_next_slice": True,
        "lightweight_state_apply_gate_status": "lightweight_state_apply_gate_ready_for_next_slice_no_socket",
        "candidate_state_update_preview": candidate,
        "lightweight_state_apply_allowed_effective": False,
        "candidate_state_update_applied": False,
        "messages_committed_now": 0,
        "state_mutated": False,
        "session_state_write_allowed": False,
        "socket_opened": False,
        "client_started": False,
        "client_sends_messages": False,
    }


def test_q33f_contract_defines_default_off_session_state_preview_boundary() -> None:
    packet = build_warroom_v2_ws_receiver_only_client_session_state_apply_preview_contract()
    assert packet["preview_kind"] == "warroom_v2_ws_receiver_only_client_session_state_apply_preview_default_off_no_socket"
    assert packet["session_state_target_key"] == WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_SESSION_STATE_APPLY_PREVIEW_KEY
    assert packet["session_state_apply_preview_requested_default"] is False
    assert packet["operator_session_state_apply_preview_ack_default"] is False
    assert packet["session_state_apply_preview_status_default"] == "session_state_apply_preview_hidden_default"
    assert packet["session_state_apply_preview_status_ready"] == "session_state_apply_preview_ready_for_next_slice_no_socket"
    assert packet["session_state_write_allowed_effective"] is False
    assert packet["session_state_write_applied"] is False
    assert packet["session_state_mutated"] is False
    assert packet["state_mutated"] is False
    assert packet["socket_opened"] is False


def test_q33f_default_packet_stays_hidden_and_does_not_write() -> None:
    packet = build_warroom_v2_ws_receiver_only_client_session_state_apply_preview_packet()
    assert packet["packet_kind"] == "warroom_v2_ws_receiver_only_client_session_state_apply_preview_packet"
    assert packet["session_state_apply_preview_status"] == "session_state_apply_preview_hidden_default"
    assert packet["session_state_apply_preview_requested"] is False
    assert packet["operator_session_state_apply_preview_ack"] is False
    assert packet["lightweight_state_apply_gate_ready_for_next_slice"] is False
    assert packet["session_state_write_preview"] == {}
    assert packet["session_state_apply_preview_allowed_for_next_slice"] is False
    assert packet["session_state_write_allowed_effective"] is False
    assert packet["session_state_write_applied"] is False
    assert packet["session_state_mutated"] is False
    assert packet["websocket_enabled"] is False


def test_q33f_ready_requires_request_ack_and_q33e_gate_but_still_preview_only() -> None:
    blocked_ack = build_warroom_v2_ws_receiver_only_client_session_state_apply_preview_packet(
        lightweight_state_apply_gate_packet=_apply_gate_ready(),
        session_state_apply_preview_requested=True,
        operator_session_state_apply_preview_ack=False,
    )
    assert blocked_ack["session_state_apply_preview_status"] == "session_state_apply_preview_blocked_operator_ack_required"
    blocked_gate = build_warroom_v2_ws_receiver_only_client_session_state_apply_preview_packet(
        session_state_apply_preview_requested=True,
        operator_session_state_apply_preview_ack=True,
    )
    assert blocked_gate["session_state_apply_preview_status"] == "session_state_apply_preview_blocked_apply_gate_required"
    ready = build_warroom_v2_ws_receiver_only_client_session_state_apply_preview_packet(
        lightweight_state_apply_gate_packet=_apply_gate_ready(),
        session_state_apply_preview_requested=True,
        operator_session_state_apply_preview_ack=True,
    )
    assert ready["session_state_apply_preview_status"] == "session_state_apply_preview_ready_for_next_slice_no_socket"
    assert ready["candidate_message_count"] == 1
    preview = ready["session_state_write_preview"]
    assert preview["target_key"] == WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_SESSION_STATE_APPLY_PREVIEW_KEY
    assert preview["message_count"] == 1
    assert preview["latest_topic"] == "warroom.market.snapshot"
    assert preview["latest_sequence"] == 11
    assert preview["preview_only"] is True
    assert preview["write_applied_now"] is False
    assert ready["session_state_apply_preview_allowed_for_next_slice"] is True
    assert ready["session_state_write_allowed_effective"] is False
    assert ready["session_state_write_applied"] is False
    assert ready["session_state_mutated"] is False
    assert ready["state_mutated"] is False
    assert ready["messages_committed_now"] == 0
    assert ready["socket_opened"] is False
    assert ready["client_started"] is False
    assert ready["client_sends_messages"] is False
    assert ready["would_send_to_broker"] is False


def test_q33f_doc_and_warroom_page_preserve_no_ui_boundary() -> None:
    text = DOC.read_text(encoding="utf-8-sig")
    assert "session_state_apply_preview_kind=warroom_v2_ws_receiver_only_client_session_state_apply_preview_default_off_no_socket" in text
    assert "session_state_apply_preview_requested_default=false" in text
    assert "operator_session_state_apply_preview_ack_default=false" in text
    assert "not_mutating_session_state=true" in text
    assert "not_opening_socket=true" in text
    page = WARROOM_PAGE.read_text(encoding="utf-8-sig")
    assert "ws_receiver_only_client_session_state_apply_preview" not in page
    assert "session_state_apply_preview_ready_for_next_slice_no_socket" not in page
    assert "session_state apply preview" not in page
    assert 'st.checkbox("WS' not in page
    assert 'st.button("WS' not in page


def test_q33f_transport_modules_preserve_no_socket_order_prediction_boundary() -> None:
    forbidden = (
        "import streamlit", "from streamlit", "websocket.", "sse.", "polling_loop(", "browser_timer_reload(",
        "send_to_broker(", "submit_order(", "append_ledger(", "write_runtime_artifact(", "write_prediction_artifact(",
        "run_prediction(", "invoke_classifier(", "st.write(", "st.metric(", "st.caption(", "st.markdown(", "D:" + chr(92), "E:" + chr(92),
    )
    for path in TRANSPORT_DIR.glob("*.py"):
        body = path.read_text(encoding="utf-8-sig")
        assert len(body.splitlines()) <= 220, f"transport file too large: {path}"
        for token in forbidden:
            assert token not in body, f"forbidden token {token!r} found in {path}"
