# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_ws_receiver_only_client_lightweight_state_target_write_actual_q33l.py
# desc: PS-Q33L guards for receiver-only client lightweight-state first actual target write. Default-off/operator-gated/no-socket.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.apps.operator_ui.prediction_warroom.v2 import (  # noqa: E402
    apply_warroom_v2_ws_receiver_only_client_lightweight_state_target_write_actual,
    build_warroom_v2_ws_receiver_only_client_lightweight_state_target_write_actual_contract,
)

REPO_ROOT = Path(__file__).resolve().parents[6]
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q33L_WARROOM_V2_WEBSOCKET_RECEIVER_ONLY_CLIENT_LIGHTWEIGHT_STATE_TARGET_WRITE_FIRST_ACTUAL_DEFAULT_OFF_NO_SOCKET_2026-07-04.md"
TRANSPORT_DIR = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport"
WARROOM_PAGE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py"


def _target_write_gate_ready() -> dict[str, object]:
    value_preview = {
        "value_kind": "receiver_only_lightweight_state_value_preview",
        "target_key": "warroom_v2_ws_receiver_only_client_lightweight_state_q33f_preview",
        "message_count": 1,
        "latest_topic": "warroom.market.snapshot",
        "latest_widget_id": "market_snapshot_strip",
        "latest_sequence": 31,
        "topics": ["warroom.market.snapshot"],
        "messages": [{"topic": "warroom.market.snapshot", "widget_id": "market_snapshot_strip", "sequence": 31}],
        "receiver_only": True,
        "preview_only": True,
        "target_write_applied_now": False,
        "state_mutated_now": False,
    }
    return {
        "target_write_gate_allowed_for_next_slice": True,
        "target_write_gate_status": "lightweight_state_target_write_gate_ready_for_next_slice_no_socket",
        "target_lightweight_state_write_candidate": value_preview,
        "target_lightweight_state_value_preview": value_preview,
        "target_write_allowed_effective": False,
        "target_session_state_write_allowed_effective": False,
        "target_session_state_write_applied": False,
        "target_session_state_mutated": False,
        "state_mutated": False,
        "socket_opened": False,
        "client_started": False,
        "client_sends_messages": False,
    }


def test_q33l_contract_defines_first_actual_target_write_boundary() -> None:
    packet = build_warroom_v2_ws_receiver_only_client_lightweight_state_target_write_actual_contract()
    assert packet["target_write_actual_kind"] == "warroom_v2_ws_receiver_only_client_lightweight_state_target_write_first_actual_default_off_no_socket"
    assert packet["lightweight_state_target_write_actual_requested_default"] is False
    assert packet["operator_lightweight_state_target_write_actual_ack_default"] is False
    assert packet["target_write_actual_status_default"] == "lightweight_state_target_write_actual_hidden_default"
    assert packet["target_write_actual_status_applied"] == "lightweight_state_target_write_actual_applied_no_socket"
    assert packet["target_write_actual_capability"] is True
    assert packet["actual_target_session_state_write_default"] is False
    assert packet["target_write_actual_target"] == "provided_mutable_session_state_mapping_only"
    assert packet["target_write_actual_checks_gate_ready"] is True
    assert packet["target_write_actual_checks_target_key"] is True
    assert packet["target_write_actual_checks_message_count"] is True
    assert packet["target_write_actual_checks_preview_only"] is True
    assert packet["warroom_page_modified"] is False
    assert packet["visible_controls_added"] is False
    assert packet["socket_opened"] is False


def test_q33l_default_call_does_not_write_or_mutate_state() -> None:
    state = {"existing": {"ok": True}}
    packet = apply_warroom_v2_ws_receiver_only_client_lightweight_state_target_write_actual(state)
    assert packet["packet_kind"] == "warroom_v2_ws_receiver_only_client_lightweight_state_target_write_actual_result_packet"
    assert packet["target_write_actual_status"] == "lightweight_state_target_write_actual_hidden_default"
    assert packet["lightweight_state_target_write_actual_requested"] is False
    assert packet["operator_lightweight_state_target_write_actual_ack"] is False
    assert packet["actual_target_session_state_write"] is False
    assert packet["target_write_allowed_effective"] is False
    assert packet["target_session_state_write_allowed_effective"] is False
    assert packet["target_session_state_write_applied"] is False
    assert packet["target_session_state_mutated"] is False
    assert packet["state_mutated"] is False
    assert packet["messages_committed_now"] == 0
    assert state == {"existing": {"ok": True}}
    assert packet["socket_opened"] is False
    assert packet["websocket_enabled"] is False


def test_q33l_blocked_paths_do_not_mutate_state() -> None:
    state = {}
    blocked_ack = apply_warroom_v2_ws_receiver_only_client_lightweight_state_target_write_actual(
        state,
        target_write_gate_packet=_target_write_gate_ready(),
        lightweight_state_target_write_actual_requested=True,
        operator_lightweight_state_target_write_actual_ack=False,
    )
    assert blocked_ack["target_write_actual_status"] == "lightweight_state_target_write_actual_blocked_operator_ack_required"
    assert state == {}
    blocked_gate = apply_warroom_v2_ws_receiver_only_client_lightweight_state_target_write_actual(
        state,
        lightweight_state_target_write_actual_requested=True,
        operator_lightweight_state_target_write_actual_ack=True,
    )
    assert blocked_gate["target_write_actual_status"] == "lightweight_state_target_write_actual_blocked_target_write_gate_required"
    assert state == {}
    bad_gate = dict(_target_write_gate_ready())
    bad_gate["target_lightweight_state_write_candidate"] = {"target_key": "", "message_count": 0, "preview_only": True}
    blocked_value = apply_warroom_v2_ws_receiver_only_client_lightweight_state_target_write_actual(
        state,
        target_write_gate_packet=bad_gate,
        lightweight_state_target_write_actual_requested=True,
        operator_lightweight_state_target_write_actual_ack=True,
    )
    assert blocked_value["target_write_actual_status"] == "lightweight_state_target_write_actual_blocked_target_value_preview_required"
    assert state == {}


def test_q33l_ready_request_ack_gate_writes_only_target_key_without_socket() -> None:
    state = {"unrelated": {"keep": True}}
    packet = apply_warroom_v2_ws_receiver_only_client_lightweight_state_target_write_actual(
        state,
        target_write_gate_packet=_target_write_gate_ready(),
        lightweight_state_target_write_actual_requested=True,
        operator_lightweight_state_target_write_actual_ack=True,
    )
    target_key = "warroom_v2_ws_receiver_only_client_lightweight_state_q33f_preview"
    assert packet["target_write_actual_status"] == "lightweight_state_target_write_actual_applied_no_socket"
    assert packet["actual_target_session_state_write"] is True
    assert packet["target_write_allowed_effective"] is True
    assert packet["target_session_state_write_allowed_effective"] is True
    assert packet["target_session_state_write_applied"] is True
    assert packet["target_session_state_mutated"] is True
    assert packet["state_mutated"] is True
    assert packet["messages_committed_now"] == 1
    assert packet["target_session_state_key"] == target_key
    assert packet["target_message_count"] == 1
    assert packet["target_latest_topic"] == "warroom.market.snapshot"
    assert packet["target_latest_widget_id"] == "market_snapshot_strip"
    assert packet["target_latest_sequence"] == 31
    assert set(state) == {"unrelated", target_key}
    assert state[target_key]["preview_only"] is True
    assert state[target_key]["message_count"] == 1
    assert packet["written_value_present"] is True
    assert packet["written_value_kind"] == "dict"
    assert packet["socket_opened"] is False
    assert packet["client_started"] is False
    assert packet["client_sends_messages"] is False
    assert packet["external_message_send_enabled"] is False
    assert packet["websocket_enabled"] is False
    assert packet["would_send_to_broker"] is False


def test_q33l_doc_and_warroom_page_preserve_no_ui_runtime_boundary() -> None:
    text = DOC.read_text(encoding="utf-8-sig")
    assert "target_write_actual_kind=warroom_v2_ws_receiver_only_client_lightweight_state_target_write_first_actual_default_off_no_socket" in text
    assert "lightweight_state_target_write_actual_requested_default=false" in text
    assert "operator_lightweight_state_target_write_actual_ack_default=false" in text
    assert "actual_target_session_state_write_default=false" in text
    assert "target_write_actual_target=provided_mutable_session_state_mapping_only" in text
    assert "not_opening_socket=true" in text
    page = WARROOM_PAGE.read_text(encoding="utf-8-sig")
    assert "ws_receiver_only_client_lightweight_state_target_write_actual" not in page
    assert "lightweight_state_target_write_actual_applied_no_socket" not in page
    assert "Target write actual" not in page
    assert 'st.checkbox("WS' not in page
    assert 'st.button("WS' not in page


def test_q33l_transport_modules_preserve_no_socket_order_prediction_boundary() -> None:
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
