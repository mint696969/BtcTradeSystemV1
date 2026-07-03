# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_ws_receiver_only_client_lightweight_state_apply_gate_q33e.py
# desc: PS-Q33E guards for receiver-only client lightweight state apply gate. Default-off/no-socket/no-mutation.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.apps.operator_ui.prediction_warroom.v2 import (  # noqa: E402
    build_warroom_v2_ws_receiver_only_client_lightweight_state_apply_gate_contract,
    build_warroom_v2_ws_receiver_only_client_lightweight_state_apply_gate_packet,
)

REPO_ROOT = Path(__file__).resolve().parents[6]
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q33E_WARROOM_V2_WEBSOCKET_RECEIVER_ONLY_CLIENT_LIGHTWEIGHT_STATE_APPLY_GATE_DEFAULT_OFF_NO_SOCKET_2026-07-03.md"
TRANSPORT_DIR = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport"
WARROOM_PAGE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py"


def _preview_ready() -> dict[str, object]:
    candidate = {
        "candidate_kind": "future_lightweight_receiver_state_update_preview",
        "message_count": 1,
        "topics": ["warroom.market.snapshot"],
        "latest_topic": "warroom.market.snapshot",
        "latest_widget_id": "market_snapshot_strip",
        "latest_sequence": 7,
        "messages": [{"topic": "warroom.market.snapshot", "widget_id": "market_snapshot_strip", "sequence": 7}],
        "preview_only": True,
        "applied_now": False,
    }
    return {
        "lightweight_state_drain_allowed_for_next_slice": True,
        "lightweight_state_drain_preview_status": "lightweight_state_drain_preview_ready_for_next_slice_no_socket",
        "candidate_state_update_preview": candidate,
        "lightweight_state_update_allowed_effective": False,
        "candidate_state_update_applied": False,
        "messages_committed_now": 0,
        "state_mutated": False,
        "session_state_write_allowed": False,
        "socket_opened": False,
        "client_started": False,
        "client_sends_messages": False,
    }


def test_q33e_contract_defines_default_off_apply_gate_boundary() -> None:
    packet = build_warroom_v2_ws_receiver_only_client_lightweight_state_apply_gate_contract()
    assert packet["apply_gate_kind"] == "warroom_v2_ws_receiver_only_client_lightweight_state_apply_gate_default_off_no_socket"
    assert packet["lightweight_state_apply_requested_default"] is False
    assert packet["operator_lightweight_state_apply_ack_default"] is False
    assert packet["lightweight_state_apply_gate_status_default"] == "lightweight_state_apply_gate_hidden_default"
    assert packet["lightweight_state_apply_gate_status_ready"] == "lightweight_state_apply_gate_ready_for_next_slice_no_socket"
    assert packet["apply_gate_checks_candidate_message_count"] is True
    assert packet["lightweight_state_apply_allowed_effective"] is False
    assert packet["candidate_state_update_applied"] is False
    assert packet["messages_committed_now"] == 0
    assert packet["state_mutated"] is False
    assert packet["socket_opened"] is False


def test_q33e_default_packet_stays_hidden_and_does_not_apply() -> None:
    packet = build_warroom_v2_ws_receiver_only_client_lightweight_state_apply_gate_packet()
    assert packet["packet_kind"] == "warroom_v2_ws_receiver_only_client_lightweight_state_apply_gate_packet"
    assert packet["lightweight_state_apply_gate_status"] == "lightweight_state_apply_gate_hidden_default"
    assert packet["lightweight_state_apply_requested"] is False
    assert packet["operator_lightweight_state_apply_ack"] is False
    assert packet["lightweight_state_drain_preview_ready_for_next_slice"] is False
    assert packet["candidate_state_update_validated"] is False
    assert packet["lightweight_state_apply_allowed_for_next_slice"] is False
    assert packet["lightweight_state_apply_allowed_effective"] is False
    assert packet["candidate_state_update_applied"] is False
    assert packet["state_mutated"] is False
    assert packet["websocket_enabled"] is False


def test_q33e_ready_requires_request_ack_preview_and_candidate_but_still_no_apply() -> None:
    blocked_ack = build_warroom_v2_ws_receiver_only_client_lightweight_state_apply_gate_packet(
        lightweight_state_drain_preview_packet=_preview_ready(),
        lightweight_state_apply_requested=True,
        operator_lightweight_state_apply_ack=False,
    )
    assert blocked_ack["lightweight_state_apply_gate_status"] == "lightweight_state_apply_gate_blocked_operator_ack_required"
    blocked_preview = build_warroom_v2_ws_receiver_only_client_lightweight_state_apply_gate_packet(
        lightweight_state_apply_requested=True,
        operator_lightweight_state_apply_ack=True,
    )
    assert blocked_preview["lightweight_state_apply_gate_status"] == "lightweight_state_apply_gate_blocked_preview_required"
    bad_candidate = dict(_preview_ready())
    bad_candidate["candidate_state_update_preview"] = {"message_count": 0, "preview_only": True}
    blocked_candidate = build_warroom_v2_ws_receiver_only_client_lightweight_state_apply_gate_packet(
        lightweight_state_drain_preview_packet=bad_candidate,
        lightweight_state_apply_requested=True,
        operator_lightweight_state_apply_ack=True,
    )
    assert blocked_candidate["lightweight_state_apply_gate_status"] == "lightweight_state_apply_gate_blocked_candidate_required"
    ready = build_warroom_v2_ws_receiver_only_client_lightweight_state_apply_gate_packet(
        lightweight_state_drain_preview_packet=_preview_ready(),
        lightweight_state_apply_requested=True,
        operator_lightweight_state_apply_ack=True,
    )
    assert ready["lightweight_state_apply_gate_status"] == "lightweight_state_apply_gate_ready_for_next_slice_no_socket"
    assert ready["candidate_state_update_validated"] is True
    assert ready["candidate_message_count"] == 1
    assert ready["candidate_latest_topic"] == "warroom.market.snapshot"
    assert ready["candidate_latest_sequence"] == 7
    assert ready["lightweight_state_apply_allowed_for_next_slice"] is True
    assert ready["lightweight_state_apply_allowed_effective"] is False
    assert ready["candidate_state_update_applied"] is False
    assert ready["messages_committed_now"] == 0
    assert ready["state_mutated"] is False
    assert ready["session_state_write_allowed"] is False
    assert ready["socket_opened"] is False
    assert ready["client_started"] is False
    assert ready["client_sends_messages"] is False
    assert ready["would_send_to_broker"] is False


def test_q33e_doc_and_warroom_page_preserve_no_ui_boundary() -> None:
    text = DOC.read_text(encoding="utf-8-sig")
    assert "apply_gate_kind=warroom_v2_ws_receiver_only_client_lightweight_state_apply_gate_default_off_no_socket" in text
    assert "lightweight_state_apply_requested_default=false" in text
    assert "operator_lightweight_state_apply_ack_default=false" in text
    assert "not_mutating_session_state=true" in text
    assert "not_opening_socket=true" in text
    page = WARROOM_PAGE.read_text(encoding="utf-8-sig")
    assert "ws_receiver_only_client_lightweight_state_apply_gate" not in page
    assert "lightweight_state_apply_gate_ready_for_next_slice_no_socket" not in page
    assert "Lightweight state apply" not in page
    assert 'st.checkbox("WS' not in page
    assert 'st.button("WS' not in page


def test_q33e_transport_modules_preserve_no_socket_order_prediction_boundary() -> None:
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
