# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_ws_receiver_only_client_lightweight_state_drain_preview_q33d.py
# desc: PS-Q33D guards for receiver-only client lightweight state drain preview. Default-off/no-socket/no-mutation.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.apps.operator_ui.prediction_warroom.v2 import (  # noqa: E402
    build_warroom_v2_ws_receiver_only_client_lightweight_state_drain_preview_contract,
    build_warroom_v2_ws_receiver_only_client_lightweight_state_drain_preview_packet,
)

REPO_ROOT = Path(__file__).resolve().parents[6]
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q33D_WARROOM_V2_WEBSOCKET_RECEIVER_ONLY_CLIENT_LIGHTWEIGHT_STATE_DRAIN_PREVIEW_DEFAULT_OFF_NO_SOCKET_2026-07-03.md"
TRANSPORT_DIR = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport"
WARROOM_PAGE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py"


def _drain_packet_ready() -> dict[str, object]:
    messages = [
        {"topic": "warroom.market.snapshot", "widget_id": "market_snapshot_strip", "sequence": 1},
        {"topic": "warroom.position.summary", "widget_id": "position_summary_strip", "sequence": 2},
    ]
    return {
        "receive_buffer_drain_allowed_for_next_slice": True,
        "drain_contract_status": "receive_buffer_drain_ready_for_next_slice_no_socket",
        "drain_preview_count": len(messages),
        "drain_preview_messages": messages,
        "receive_buffer_drain_allowed_effective": False,
        "messages_drained_now": 0,
        "state_mutated": False,
        "session_state_write_allowed": False,
        "socket_opened": False,
        "client_started": False,
        "client_sends_messages": False,
    }


def test_q33d_contract_defines_default_off_preview_only_boundary() -> None:
    packet = build_warroom_v2_ws_receiver_only_client_lightweight_state_drain_preview_contract()
    assert packet["preview_kind"] == "warroom_v2_ws_receiver_only_client_lightweight_state_drain_preview_default_off_no_socket"
    assert packet["lightweight_state_update_requested_default"] is False
    assert packet["operator_lightweight_state_ack_default"] is False
    assert packet["lightweight_state_drain_preview_status_default"] == "lightweight_state_drain_preview_hidden_default"
    assert packet["lightweight_state_drain_preview_status_ready"] == "lightweight_state_drain_preview_ready_for_next_slice_no_socket"
    assert packet["candidate_state_update_is_preview_only"] is True
    assert packet["lightweight_state_update_allowed_effective"] is False
    assert packet["candidate_state_update_applied"] is False
    assert packet["messages_committed_now"] == 0
    assert packet["state_mutated"] is False
    assert packet["socket_opened"] is False
    assert packet["client_started"] is False


def test_q33d_default_packet_stays_hidden_and_does_not_preview_or_mutate() -> None:
    packet = build_warroom_v2_ws_receiver_only_client_lightweight_state_drain_preview_packet()
    assert packet["packet_kind"] == "warroom_v2_ws_receiver_only_client_lightweight_state_drain_preview_packet"
    assert packet["lightweight_state_drain_preview_status"] == "lightweight_state_drain_preview_hidden_default"
    assert packet["lightweight_state_update_requested"] is False
    assert packet["operator_lightweight_state_ack"] is False
    assert packet["receive_buffer_drain_ready_for_next_slice"] is False
    assert packet["lightweight_state_preview_count"] == 0
    assert packet["candidate_state_update_preview"]["message_count"] == 0
    assert packet["lightweight_state_drain_allowed_for_next_slice"] is False
    assert packet["lightweight_state_update_allowed_effective"] is False
    assert packet["state_mutated"] is False
    assert packet["websocket_enabled"] is False


def test_q33d_ready_requires_request_ack_and_q33c_drain_but_still_preview_only() -> None:
    blocked_ack = build_warroom_v2_ws_receiver_only_client_lightweight_state_drain_preview_packet(
        receive_buffer_drain_packet=_drain_packet_ready(),
        lightweight_state_update_requested=True,
        operator_lightweight_state_ack=False,
    )
    assert blocked_ack["lightweight_state_drain_preview_status"] == "lightweight_state_drain_preview_blocked_operator_ack_required"
    blocked_drain = build_warroom_v2_ws_receiver_only_client_lightweight_state_drain_preview_packet(
        lightweight_state_update_requested=True,
        operator_lightweight_state_ack=True,
    )
    assert blocked_drain["lightweight_state_drain_preview_status"] == "lightweight_state_drain_preview_blocked_drain_contract_required"
    ready = build_warroom_v2_ws_receiver_only_client_lightweight_state_drain_preview_packet(
        receive_buffer_drain_packet=_drain_packet_ready(),
        lightweight_state_update_requested=True,
        operator_lightweight_state_ack=True,
        max_preview_items=1,
    )
    assert ready["lightweight_state_drain_preview_status"] == "lightweight_state_drain_preview_ready_for_next_slice_no_socket"
    assert ready["source_drain_preview_count"] == 2
    assert ready["lightweight_state_preview_count"] == 1
    candidate = ready["candidate_state_update_preview"]
    assert candidate["candidate_kind"] == "future_lightweight_receiver_state_update_preview"
    assert candidate["message_count"] == 1
    assert candidate["latest_topic"] == "warroom.market.snapshot"
    assert candidate["latest_sequence"] == 1
    assert ready["lightweight_state_drain_allowed_for_next_slice"] is True
    assert ready["lightweight_state_update_allowed_effective"] is False
    assert ready["candidate_state_update_applied"] is False
    assert ready["messages_committed_now"] == 0
    assert ready["state_mutated"] is False
    assert ready["session_state_write_allowed"] is False
    assert ready["socket_opened"] is False
    assert ready["client_started"] is False
    assert ready["client_sends_messages"] is False
    assert ready["would_send_to_broker"] is False


def test_q33d_doc_and_warroom_page_preserve_no_ui_boundary() -> None:
    text = DOC.read_text(encoding="utf-8-sig")
    assert "preview_kind=warroom_v2_ws_receiver_only_client_lightweight_state_drain_preview_default_off_no_socket" in text
    assert "lightweight_state_update_requested_default=false" in text
    assert "operator_lightweight_state_ack_default=false" in text
    assert "not_mutating_session_state=true" in text
    assert "not_opening_socket=true" in text
    page = WARROOM_PAGE.read_text(encoding="utf-8-sig")
    assert "ws_receiver_only_client_lightweight_state_drain_preview" not in page
    assert "lightweight_state_drain_preview_ready_for_next_slice_no_socket" not in page
    assert "Lightweight state drain" not in page
    assert 'st.checkbox("WS' not in page
    assert 'st.button("WS' not in page


def test_q33d_transport_modules_preserve_no_socket_order_prediction_boundary() -> None:
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
