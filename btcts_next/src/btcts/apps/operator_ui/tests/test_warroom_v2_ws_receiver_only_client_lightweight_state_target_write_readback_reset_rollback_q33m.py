# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_ws_receiver_only_client_lightweight_state_target_write_readback_reset_rollback_q33m.py
# desc: PS-Q33M guards for receiver-only client lightweight-state target write readback/reset/rollback diagnostics. Default-off/operator-gated/no-socket.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.apps.operator_ui.prediction_warroom.v2 import (  # noqa: E402
    apply_warroom_v2_ws_receiver_only_client_lightweight_state_target_write_readback_reset_rollback,
    build_warroom_v2_ws_receiver_only_client_lightweight_state_target_write_readback_reset_rollback_contract,
)

REPO_ROOT = Path(__file__).resolve().parents[6]
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q33M_WARROOM_V2_WEBSOCKET_RECEIVER_ONLY_CLIENT_LIGHTWEIGHT_STATE_TARGET_WRITE_READBACK_RESET_ROLLBACK_DEFAULT_OFF_NO_SOCKET_2026-07-04.md"
TRANSPORT_DIR = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport"
WARROOM_PAGE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py"
TARGET_KEY = "warroom_v2_ws_receiver_only_client_lightweight_state_q33f_preview"


def _value(sequence: int = 41) -> dict[str, object]:
    return {
        "value_kind": "receiver_only_lightweight_state_value_preview",
        "target_key": TARGET_KEY,
        "message_count": 1,
        "latest_topic": "warroom.market.snapshot",
        "latest_widget_id": "market_snapshot_strip",
        "latest_sequence": sequence,
        "topics": ["warroom.market.snapshot"],
        "messages": [{"topic": "warroom.market.snapshot", "widget_id": "market_snapshot_strip", "sequence": sequence}],
        "receiver_only": True,
        "preview_only": True,
    }


def _actual_result() -> dict[str, object]:
    return {
        "target_write_actual_status": "lightweight_state_target_write_actual_applied_no_socket",
        "target_session_state_key": TARGET_KEY,
        "actual_target_session_state_write": True,
        "target_session_state_write_applied": True,
        "socket_opened": False,
    }


def test_q33m_contract_defines_readback_reset_rollback_boundary() -> None:
    packet = build_warroom_v2_ws_receiver_only_client_lightweight_state_target_write_readback_reset_rollback_contract()
    assert packet["target_write_readback_reset_rollback_kind"] == "warroom_v2_ws_receiver_only_client_lightweight_state_target_write_readback_reset_rollback_default_off_no_socket"
    assert packet["readback_diagnostic_available"] is True
    assert packet["reset_requested_default"] is False
    assert packet["operator_reset_ack_default"] is False
    assert packet["rollback_requested_default"] is False
    assert packet["operator_rollback_ack_default"] is False
    assert packet["target_write_reset_requires_request_ack"] is True
    assert packet["target_write_rollback_requires_request_ack_and_valid_value"] is True
    assert packet["target_write_readback_target"] == "provided_mutable_session_state_mapping_only"
    assert packet["warroom_page_modified"] is False
    assert packet["visible_controls_added"] is False
    assert packet["socket_opened"] is False


def test_q33m_default_readback_does_not_mutate_state() -> None:
    state = {TARGET_KEY: _value(41), "unrelated": {"keep": True}}
    packet = apply_warroom_v2_ws_receiver_only_client_lightweight_state_target_write_readback_reset_rollback(
        state,
        target_write_actual_result_packet=_actual_result(),
    )
    assert packet["readback_before_present"] is True
    assert packet["readback_after_present"] is True
    assert packet["readback_before_message_count"] == 1
    assert packet["readback_after_message_count"] == 1
    assert packet["reset_status"] == "target_write_reset_hidden_default"
    assert packet["rollback_status"] == "target_write_rollback_hidden_default"
    assert packet["target_session_state_mutated"] is False
    assert packet["state_mutated"] is False
    assert set(state) == {TARGET_KEY, "unrelated"}
    assert packet["socket_opened"] is False
    assert packet["websocket_enabled"] is False


def test_q33m_reset_requires_request_ack_and_existing_target() -> None:
    state = {TARGET_KEY: _value(42)}
    blocked_ack = apply_warroom_v2_ws_receiver_only_client_lightweight_state_target_write_readback_reset_rollback(
        state,
        target_write_actual_result_packet=_actual_result(),
        reset_requested=True,
        operator_reset_ack=False,
    )
    assert blocked_ack["reset_status"] == "target_write_reset_blocked_operator_ack_required"
    assert TARGET_KEY in state
    applied = apply_warroom_v2_ws_receiver_only_client_lightweight_state_target_write_readback_reset_rollback(
        state,
        target_write_actual_result_packet=_actual_result(),
        reset_requested=True,
        operator_reset_ack=True,
    )
    assert applied["reset_status"] == "target_write_reset_applied_no_socket"
    assert applied["reset_applied"] is True
    assert applied["target_session_state_mutated"] is True
    assert applied["messages_removed_now"] == 1
    assert TARGET_KEY not in state
    missing = apply_warroom_v2_ws_receiver_only_client_lightweight_state_target_write_readback_reset_rollback(
        state,
        target_write_actual_result_packet=_actual_result(),
        reset_requested=True,
        operator_reset_ack=True,
    )
    assert missing["reset_status"] == "target_write_reset_blocked_target_missing"
    assert missing["state_mutated"] is False


def test_q33m_rollback_requires_request_ack_valid_value_and_matching_key() -> None:
    state = {}
    blocked_ack = apply_warroom_v2_ws_receiver_only_client_lightweight_state_target_write_readback_reset_rollback(
        state,
        target_write_actual_result_packet=_actual_result(),
        rollback_requested=True,
        operator_rollback_ack=False,
        rollback_value=_value(43),
    )
    assert blocked_ack["rollback_status"] == "target_write_rollback_blocked_operator_ack_required"
    assert state == {}
    blocked_value = apply_warroom_v2_ws_receiver_only_client_lightweight_state_target_write_readback_reset_rollback(
        state,
        target_write_actual_result_packet=_actual_result(),
        rollback_requested=True,
        operator_rollback_ack=True,
        rollback_value={"target_key": TARGET_KEY, "message_count": 0, "preview_only": True},
    )
    assert blocked_value["rollback_status"] == "target_write_rollback_blocked_valid_rollback_value_required"
    mismatch = dict(_value(44))
    mismatch["target_key"] = "other_key"
    blocked_mismatch = apply_warroom_v2_ws_receiver_only_client_lightweight_state_target_write_readback_reset_rollback(
        state,
        target_write_actual_result_packet=_actual_result(),
        rollback_requested=True,
        operator_rollback_ack=True,
        rollback_value=mismatch,
    )
    assert blocked_mismatch["rollback_status"] == "target_write_rollback_blocked_target_key_mismatch"
    applied = apply_warroom_v2_ws_receiver_only_client_lightweight_state_target_write_readback_reset_rollback(
        state,
        target_write_actual_result_packet=_actual_result(),
        rollback_requested=True,
        operator_rollback_ack=True,
        rollback_value=_value(45),
    )
    assert applied["rollback_status"] == "target_write_rollback_applied_no_socket"
    assert applied["rollback_applied"] is True
    assert applied["messages_committed_now"] == 1
    assert state[TARGET_KEY]["latest_sequence"] == 45
    assert applied["socket_opened"] is False
    assert applied["client_started"] is False
    assert applied["would_send_to_broker"] is False


def test_q33m_doc_and_warroom_page_preserve_no_ui_runtime_boundary() -> None:
    text = DOC.read_text(encoding="utf-8-sig")
    assert "target_write_readback_reset_rollback_kind=warroom_v2_ws_receiver_only_client_lightweight_state_target_write_readback_reset_rollback_default_off_no_socket" in text
    assert "reset_requested_default=false" in text
    assert "rollback_requested_default=false" in text
    assert "target_write_readback_target=provided_mutable_session_state_mapping_only" in text
    assert "not_opening_socket=true" in text
    page = WARROOM_PAGE.read_text(encoding="utf-8-sig")
    assert "ws_receiver_only_client_lightweight_state_target_write_readback_reset_rollback" not in page
    assert "target_write_reset_applied_no_socket" not in page
    assert "Target write readback" not in page
    assert 'st.checkbox("WS' not in page
    assert 'st.button("WS' not in page


def test_q33m_transport_modules_preserve_no_socket_order_prediction_boundary() -> None:
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
