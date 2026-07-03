# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_ws_receiver_only_client_lightweight_state_target_write_preview_q33i.py
# desc: PS-Q33I guards for receiver-only client lightweight-state target write preview. Default-off/no-socket/no-target-write.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.apps.operator_ui.prediction_warroom.v2 import (  # noqa: E402
    build_warroom_v2_ws_receiver_only_client_lightweight_state_target_write_preview_contract,
    build_warroom_v2_ws_receiver_only_client_lightweight_state_target_write_preview_packet,
)

REPO_ROOT = Path(__file__).resolve().parents[6]
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q33I_WARROOM_V2_WEBSOCKET_RECEIVER_ONLY_CLIENT_LIGHTWEIGHT_STATE_TARGET_WRITE_PREVIEW_DEFAULT_OFF_NO_SOCKET_2026-07-03.md"
TRANSPORT_DIR = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport"
WARROOM_PAGE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py"


def _target_apply_gate_ready() -> dict[str, object]:
    target_write_preview = {
        "write_preview_kind": "future_streamlit_session_state_write_preview",
        "target_key": "warroom_v2_ws_receiver_only_client_lightweight_state_q33f_preview",
        "value_kind": "receiver_only_lightweight_state_update_preview",
        "message_count": 1,
        "latest_topic": "warroom.market.snapshot",
        "latest_widget_id": "market_snapshot_strip",
        "latest_sequence": 19,
        "topics": ["warroom.market.snapshot"],
        "messages": [{"topic": "warroom.market.snapshot", "widget_id": "market_snapshot_strip", "sequence": 19}],
        "preview_only": True,
        "write_applied_now": False,
    }
    return {
        "target_apply_gate_allowed_for_next_slice": True,
        "target_apply_gate_status": "lightweight_state_target_apply_gate_ready_for_next_slice_no_socket",
        "target_session_state_write_preview": target_write_preview,
        "target_apply_allowed_effective": False,
        "target_session_state_write_allowed_effective": False,
        "target_session_state_write_applied": False,
        "target_session_state_mutated": False,
        "state_mutated": False,
        "socket_opened": False,
        "client_started": False,
        "client_sends_messages": False,
    }


def test_q33i_contract_defines_default_off_target_write_preview_boundary() -> None:
    packet = build_warroom_v2_ws_receiver_only_client_lightweight_state_target_write_preview_contract()
    assert packet["target_write_preview_kind"] == "warroom_v2_ws_receiver_only_client_lightweight_state_target_write_preview_default_off_no_socket"
    assert packet["lightweight_state_target_write_preview_requested_default"] is False
    assert packet["operator_lightweight_state_target_write_preview_ack_default"] is False
    assert packet["target_write_preview_status_default"] == "lightweight_state_target_write_preview_hidden_default"
    assert packet["target_write_preview_status_ready"] == "lightweight_state_target_write_preview_ready_for_next_slice_no_socket"
    assert packet["target_write_preview_checks_gate_ready"] is True
    assert packet["target_write_preview_checks_message_count"] is True
    assert packet["target_write_allowed_effective"] is False
    assert packet["target_session_state_write_allowed_effective"] is False
    assert packet["target_session_state_write_applied"] is False
    assert packet["socket_opened"] is False


def test_q33i_default_packet_stays_hidden_and_does_not_target_write() -> None:
    packet = build_warroom_v2_ws_receiver_only_client_lightweight_state_target_write_preview_packet()
    assert packet["packet_kind"] == "warroom_v2_ws_receiver_only_client_lightweight_state_target_write_preview_packet"
    assert packet["target_write_preview_status"] == "lightweight_state_target_write_preview_hidden_default"
    assert packet["lightweight_state_target_write_preview_requested"] is False
    assert packet["operator_lightweight_state_target_write_preview_ack"] is False
    assert packet["target_apply_gate_ready_for_next_slice"] is False
    assert packet["target_lightweight_state_value_preview"] == {}
    assert packet["target_write_preview_allowed_for_next_slice"] is False
    assert packet["target_write_allowed_effective"] is False
    assert packet["target_session_state_write_applied"] is False
    assert packet["target_session_state_mutated"] is False
    assert packet["websocket_enabled"] is False


def test_q33i_ready_requires_request_ack_q33h_gate_and_valid_preview_but_still_no_write() -> None:
    blocked_ack = build_warroom_v2_ws_receiver_only_client_lightweight_state_target_write_preview_packet(
        lightweight_state_target_apply_gate_packet=_target_apply_gate_ready(),
        lightweight_state_target_write_preview_requested=True,
        operator_lightweight_state_target_write_preview_ack=False,
    )
    assert blocked_ack["target_write_preview_status"] == "lightweight_state_target_write_preview_blocked_operator_ack_required"
    blocked_gate = build_warroom_v2_ws_receiver_only_client_lightweight_state_target_write_preview_packet(
        lightweight_state_target_write_preview_requested=True,
        operator_lightweight_state_target_write_preview_ack=True,
    )
    assert blocked_gate["target_write_preview_status"] == "lightweight_state_target_write_preview_blocked_target_apply_gate_required"
    bad_preview = dict(_target_apply_gate_ready())
    bad_preview["target_session_state_write_preview"] = {"target_key": "", "message_count": 0, "preview_only": True}
    blocked_preview = build_warroom_v2_ws_receiver_only_client_lightweight_state_target_write_preview_packet(
        lightweight_state_target_apply_gate_packet=bad_preview,
        lightweight_state_target_write_preview_requested=True,
        operator_lightweight_state_target_write_preview_ack=True,
    )
    assert blocked_preview["target_write_preview_status"] == "lightweight_state_target_write_preview_blocked_target_preview_required"
    ready = build_warroom_v2_ws_receiver_only_client_lightweight_state_target_write_preview_packet(
        lightweight_state_target_apply_gate_packet=_target_apply_gate_ready(),
        lightweight_state_target_write_preview_requested=True,
        operator_lightweight_state_target_write_preview_ack=True,
    )
    assert ready["target_write_preview_status"] == "lightweight_state_target_write_preview_ready_for_next_slice_no_socket"
    assert ready["source_target_write_preview_validated"] is True
    assert ready["target_write_preview_allowed_for_next_slice"] is True
    value = ready["target_lightweight_state_value_preview"]
    assert value["value_kind"] == "receiver_only_lightweight_state_value_preview"
    assert value["target_key"] == "warroom_v2_ws_receiver_only_client_lightweight_state_q33f_preview"
    assert value["message_count"] == 1
    assert value["latest_topic"] == "warroom.market.snapshot"
    assert value["latest_widget_id"] == "market_snapshot_strip"
    assert value["latest_sequence"] == 19
    assert value["preview_only"] is True
    assert value["target_write_applied_now"] is False
    assert ready["target_write_allowed_effective"] is False
    assert ready["target_session_state_write_allowed_effective"] is False
    assert ready["target_session_state_write_applied"] is False
    assert ready["target_session_state_mutated"] is False
    assert ready["state_mutated"] is False
    assert ready["messages_committed_now"] == 0
    assert ready["socket_opened"] is False
    assert ready["client_started"] is False
    assert ready["client_sends_messages"] is False
    assert ready["would_send_to_broker"] is False


def test_q33i_doc_and_warroom_page_preserve_no_ui_boundary() -> None:
    text = DOC.read_text(encoding="utf-8-sig")
    assert "target_write_preview_kind=warroom_v2_ws_receiver_only_client_lightweight_state_target_write_preview_default_off_no_socket" in text
    assert "lightweight_state_target_write_preview_requested_default=false" in text
    assert "operator_lightweight_state_target_write_preview_ack_default=false" in text
    assert "not_writing_target_lightweight_state=true" in text
    assert "not_opening_socket=true" in text
    page = WARROOM_PAGE.read_text(encoding="utf-8-sig")
    assert "ws_receiver_only_client_lightweight_state_target_write_preview" not in page
    assert "lightweight_state_target_write_preview_ready_for_next_slice_no_socket" not in page
    assert "Target write preview" not in page
    assert 'st.checkbox("WS' not in page
    assert 'st.button("WS' not in page


def test_q33i_transport_modules_preserve_no_socket_order_prediction_boundary() -> None:
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
