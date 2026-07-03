# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_ws_receiver_only_client_enable_gate_q33a.py
# desc: PS-Q33A guards for receiver-only client enable gate. Default-off/no-send/no-socket.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.apps.operator_ui.prediction_warroom.v2 import (  # noqa: E402
    build_warroom_v2_compact_ws_status_line_streamlit_top_minimal_status_line_visible_mount_point_operator_ack_observation_packet,
    build_warroom_v2_compact_ws_status_line_streamlit_top_minimal_status_line_visible_render_mount_gate_observation_packet,
    build_warroom_v2_ws_receiver_only_client_enable_gate_contract,
    build_warroom_v2_ws_receiver_only_client_enable_gate_packet,
)

REPO_ROOT = Path(__file__).resolve().parents[6]
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q33A_WARROOM_V2_WEBSOCKET_RECEIVER_ONLY_CLIENT_ENABLE_GATE_DEFAULT_OFF_NO_SEND_2026-07-03.md"
TRANSPORT_DIR = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport"
WARROOM_PAGE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py"


def _message() -> dict[str, object]:
    return {
        "message_type": "warroom_v2_widget_update",
        "payload_kind": "widget_update_event_envelope",
        "topic": "warroom.market.snapshot",
        "widget_id": "market_snapshot_strip",
        "sequence": 1,
        "generated_at": "2026-07-03T00:00:00Z",
        "ui_patch_unit": "widget_dom_region",
        "broad_page_reload_required": False,
        "envelope": {"topic": "warroom.market.snapshot", "widget_id": "market_snapshot_strip", "sequence": 1},
        "json_payload": "{}",
    }


def _ready_q32z() -> dict[str, object]:
    q32x = build_warroom_v2_compact_ws_status_line_streamlit_top_minimal_status_line_visible_render_mount_gate_observation_packet(
        visible_render_mount_requested=True,
        operator_visible_render_mount_ack=True,
        visible_render_adapter_requested=True,
        operator_visible_render_ack=True,
        actual_mount_requested=True,
        operator_actual_mount_ack=True,
        top_minimal_status_line_render_requested=True,
        operator_top_minimal_status_line_render_ack=True,
        visible_streamlit_mount_requested=True,
        operator_visible_streamlit_mount_ack=True,
        renderer_requested=True,
        operator_renderer_ack=True,
        visible_mount_requested=True,
        operator_visible_mount_ack=True,
        status_gate_render_requested=True,
        status_gate_read_only_ack=True,
        messages=[_message()],
    )
    return build_warroom_v2_compact_ws_status_line_streamlit_top_minimal_status_line_visible_mount_point_operator_ack_observation_packet(
        visible_render_mount_gate_observation_packet=q32x,
        visible_mount_point_requested=True,
        operator_visible_mount_point_ack=True,
        manual_smoke_requested=True,
        operator_manual_smoke_ack=True,
    )


def test_q33a_contract_is_receiver_only_default_off_no_send_gate() -> None:
    packet = build_warroom_v2_ws_receiver_only_client_enable_gate_contract()
    assert packet["gate_kind"] == "warroom_v2_ws_receiver_only_client_enable_gate_default_off_no_send"
    assert packet["receiver_enable_requested_default"] is False
    assert packet["operator_receiver_enable_ack_default"] is False
    assert packet["receiver_enable_gate_status_default"] == "receiver_enable_gate_hidden_default"
    assert packet["receiver_enable_gate_status_ready"] == "receiver_enable_gate_ready_for_next_slice_no_socket"
    assert packet["receiver_only"] is True
    assert packet["send_disabled"] is True
    assert packet["receive_only_boundary"] is True
    assert packet["receiver_client_enable_allowed_effective"] is False
    assert packet["socket_opened"] is False
    assert packet["client_started"] is False
    assert packet["client_sends_messages"] is False
    assert packet["order_intent_submitted"] is False


def test_q33a_default_packet_stays_hidden_and_does_not_start_receiver() -> None:
    packet = build_warroom_v2_ws_receiver_only_client_enable_gate_packet()
    assert packet["packet_kind"] == "warroom_v2_ws_receiver_only_client_enable_gate_packet"
    assert packet["receiver_enable_gate_status"] == "receiver_enable_gate_hidden_default"
    assert packet["receiver_enable_requested"] is False
    assert packet["operator_receiver_enable_ack"] is False
    assert packet["q32_display_mount_preparation_ready"] is False
    assert packet["receiver_client_enable_allowed_for_next_slice"] is False
    assert packet["receiver_client_enable_allowed_effective"] is False
    assert packet["receiver_enabled_effective"] is False
    assert packet["socket_open_requested"] is False
    assert packet["socket_opened"] is False
    assert packet["client_started"] is False
    assert packet["client_sends_messages"] is False


def test_q33a_ready_requires_request_operator_ack_and_q32z_ready_but_still_no_socket() -> None:
    blocked_ack = build_warroom_v2_ws_receiver_only_client_enable_gate_packet(
        q32z_operator_ack_observation_packet=_ready_q32z(),
        receiver_enable_requested=True,
        operator_receiver_enable_ack=False,
    )
    assert blocked_ack["receiver_enable_gate_status"] == "receiver_enable_gate_blocked_operator_ack_required"
    blocked_q32 = build_warroom_v2_ws_receiver_only_client_enable_gate_packet(
        receiver_enable_requested=True,
        operator_receiver_enable_ack=True,
    )
    assert blocked_q32["receiver_enable_gate_status"] == "receiver_enable_gate_blocked_q32_display_mount_preparation_required"
    ready = build_warroom_v2_ws_receiver_only_client_enable_gate_packet(
        q32z_operator_ack_observation_packet=_ready_q32z(),
        receiver_enable_requested=True,
        operator_receiver_enable_ack=True,
    )
    assert ready["receiver_enable_gate_status"] == "receiver_enable_gate_ready_for_next_slice_no_socket"
    assert ready["receiver_client_enable_allowed_for_next_slice"] is True
    assert ready["receiver_client_enable_allowed_effective"] is False
    assert ready["receiver_enabled_effective"] is False
    assert ready["socket_opened"] is False
    assert ready["client_started"] is False
    assert ready["client_sends_messages"] is False
    assert ready["would_send_to_broker"] is False


def test_q33a_doc_and_warroom_page_preserve_default_off_no_ui_boundary() -> None:
    text = DOC.read_text(encoding="utf-8-sig")
    assert "gate_kind=warroom_v2_ws_receiver_only_client_enable_gate_default_off_no_send" in text
    assert "receiver_enable_requested_default=false" in text
    assert "operator_receiver_enable_ack_default=false" in text
    assert "receiver_enable_gate_status_ready=receiver_enable_gate_ready_for_next_slice_no_socket" in text
    assert "not_opening_socket=true" in text
    assert "not_sending_external_messages=true" in text
    page = WARROOM_PAGE.read_text(encoding="utf-8-sig")
    assert "ws_receiver_only_client_enable_gate" not in page
    assert "receiver_enable_gate_ready_for_next_slice_no_socket" not in page
    assert "Enable WS receiver" not in page
    assert 'st.checkbox("WS' not in page
    assert 'st.button("WS' not in page


def test_q33a_transport_modules_preserve_no_socket_order_prediction_boundary() -> None:
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
