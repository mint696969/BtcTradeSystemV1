# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_ws_receiver_only_client_session_state_apply_hidden_record_q33g.py
# desc: PS-Q33G guards for receiver-only client session_state apply hidden record. Default-off/no-socket/no-target-state-mutation.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.apps.operator_ui.prediction_warroom.v2 import (  # noqa: E402
    WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_SESSION_STATE_APPLY_HIDDEN_RECORD_KEY,
    build_warroom_v2_ws_receiver_only_client_session_state_apply_hidden_record_contract,
    build_warroom_v2_ws_receiver_only_client_session_state_apply_hidden_record_packet,
)

REPO_ROOT = Path(__file__).resolve().parents[6]
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q33G_WARROOM_V2_WEBSOCKET_RECEIVER_ONLY_CLIENT_SESSION_STATE_APPLY_HIDDEN_RECORD_DEFAULT_OFF_NO_SOCKET_2026-07-03.md"
TRANSPORT_DIR = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport"
WARROOM_PAGE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py"


def _preview_ready() -> dict[str, object]:
    write_preview = {
        "write_preview_kind": "future_streamlit_session_state_write_preview",
        "target_key": "warroom_v2_ws_receiver_only_client_lightweight_state_q33f_preview",
        "value_kind": "receiver_only_lightweight_state_update_preview",
        "message_count": 1,
        "latest_topic": "warroom.market.snapshot",
        "latest_widget_id": "market_snapshot_strip",
        "latest_sequence": 13,
        "topics": ["warroom.market.snapshot"],
        "messages": [{"topic": "warroom.market.snapshot", "widget_id": "market_snapshot_strip", "sequence": 13}],
        "preview_only": True,
        "write_applied_now": False,
    }
    return {
        "session_state_apply_preview_allowed_for_next_slice": True,
        "session_state_apply_preview_status": "session_state_apply_preview_ready_for_next_slice_no_socket",
        "session_state_write_preview": write_preview,
        "session_state_write_allowed_effective": False,
        "session_state_write_applied": False,
        "session_state_mutated": False,
        "state_mutated": False,
        "socket_opened": False,
        "client_started": False,
        "client_sends_messages": False,
    }


def test_q33g_contract_defines_hidden_record_boundary() -> None:
    packet = build_warroom_v2_ws_receiver_only_client_session_state_apply_hidden_record_contract()
    assert packet["hidden_record_key"] == WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_SESSION_STATE_APPLY_HIDDEN_RECORD_KEY
    assert packet["hidden_record_kind"] == "warroom_v2_ws_receiver_only_client_session_state_apply_hidden_record_default_off_no_socket"
    assert packet["session_state_apply_hidden_record_requested_default"] is False
    assert packet["operator_session_state_apply_hidden_record_ack_default"] is False
    assert packet["hidden_record_status_default"] == "session_state_apply_hidden_record_hidden_default"
    assert packet["hidden_record_session_state_recorded"] is True
    assert packet["warroom_page_modified"] is True
    assert packet["visible_controls_added"] is False
    assert packet["hidden_record_is_not_target_lightweight_state_write"] is True
    assert packet["target_session_state_write_allowed_effective"] is False
    assert packet["target_session_state_write_applied"] is False
    assert packet["socket_opened"] is False


def test_q33g_default_packet_records_hidden_default_without_target_write() -> None:
    packet = build_warroom_v2_ws_receiver_only_client_session_state_apply_hidden_record_packet(fragment_summary={"fragment_widget_count": 9})
    assert packet["packet_kind"] == "warroom_v2_ws_receiver_only_client_session_state_apply_hidden_record_packet"
    assert packet["hidden_record_status"] == "session_state_apply_hidden_record_hidden_default"
    assert packet["hidden_record_session_state_recorded"] is True
    assert packet["hidden_record_allowed_for_next_slice"] is False
    assert packet["session_state_write_preview"] == {}
    assert packet["fragment_summary"]["fragment_widget_count"] == 9
    assert packet["target_session_state_write_allowed_effective"] is False
    assert packet["target_session_state_write_applied"] is False
    assert packet["target_session_state_mutated"] is False
    assert packet["state_mutated"] is False
    assert packet["websocket_enabled"] is False


def test_q33g_ready_requires_request_ack_and_q33f_preview_but_still_no_target_write() -> None:
    blocked_ack = build_warroom_v2_ws_receiver_only_client_session_state_apply_hidden_record_packet(
        session_state_apply_preview_packet=_preview_ready(),
        session_state_apply_hidden_record_requested=True,
        operator_session_state_apply_hidden_record_ack=False,
    )
    assert blocked_ack["hidden_record_status"] == "session_state_apply_hidden_record_blocked_operator_ack_required"
    blocked_preview = build_warroom_v2_ws_receiver_only_client_session_state_apply_hidden_record_packet(
        session_state_apply_hidden_record_requested=True,
        operator_session_state_apply_hidden_record_ack=True,
    )
    assert blocked_preview["hidden_record_status"] == "session_state_apply_hidden_record_blocked_preview_required"
    ready = build_warroom_v2_ws_receiver_only_client_session_state_apply_hidden_record_packet(
        session_state_apply_preview_packet=_preview_ready(),
        session_state_apply_hidden_record_requested=True,
        operator_session_state_apply_hidden_record_ack=True,
    )
    assert ready["hidden_record_status"] == "session_state_apply_hidden_record_ready_for_next_slice_no_socket"
    assert ready["hidden_record_allowed_for_next_slice"] is True
    assert ready["session_state_write_preview"]["message_count"] == 1
    assert ready["session_state_write_preview"]["latest_sequence"] == 13
    assert ready["target_session_state_key"] == "warroom_v2_ws_receiver_only_client_lightweight_state_q33f_preview"
    assert ready["target_session_state_write_allowed_effective"] is False
    assert ready["target_session_state_write_applied"] is False
    assert ready["target_session_state_mutated"] is False
    assert ready["state_mutated"] is False
    assert ready["messages_committed_now"] == 0
    assert ready["socket_opened"] is False
    assert ready["client_started"] is False
    assert ready["client_sends_messages"] is False
    assert ready["would_send_to_broker"] is False


def test_q33g_warroom_page_records_hidden_record_only() -> None:
    page = WARROOM_PAGE.read_text(encoding="utf-8-sig")
    assert "WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_SESSION_STATE_APPLY_HIDDEN_RECORD_KEY" in page
    assert "warroom_v2_ws_receiver_only_client_session_state_apply_hidden_record_q33g" in page
    assert "build_warroom_v2_ws_receiver_only_client_session_state_apply_hidden_record_packet" in page
    assert "st.session_state[WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_SESSION_STATE_APPLY_HIDDEN_RECORD_KEY]" in page
    assert "session_state_apply_hidden_record_ready_for_next_slice_no_socket" not in page
    assert "Session state apply" not in page
    assert 'st.checkbox("WS' not in page
    assert 'st.button("WS' not in page


def test_q33g_doc_modules_preserve_no_socket_order_prediction_boundary() -> None:
    text = DOC.read_text(encoding="utf-8-sig")
    assert "hidden_record_key=warroom_v2_ws_receiver_only_client_session_state_apply_hidden_record_q33g" in text
    assert "hidden_record_session_state_recorded=true" in text
    assert "not_writing_target_lightweight_state=true" in text
    assert "not_opening_socket=true" in text
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
