# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_compact_ws_status_line_streamlit_top_minimal_status_line_visible_mount_point_q32y.py
# desc: PS-Q32Y guards for compact WS status line top minimal visible mount point. Default-off/operator-ack/no-socket.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.apps.operator_ui.prediction_warroom.v2 import (  # noqa: E402
    WARROOM_V2_COMPACT_WS_STATUS_LINE_STREAMLIT_TOP_MINIMAL_STATUS_LINE_VISIBLE_MOUNT_POINT_OPERATOR_ACK_STATE_KEY,
    WARROOM_V2_COMPACT_WS_STATUS_LINE_STREAMLIT_TOP_MINIMAL_STATUS_LINE_VISIBLE_MOUNT_POINT_REQUEST_STATE_KEY,
    WARROOM_V2_COMPACT_WS_STATUS_LINE_STREAMLIT_TOP_MINIMAL_STATUS_LINE_VISIBLE_MOUNT_POINT_STATE_KEY,
    build_warroom_v2_compact_ws_status_line_streamlit_top_minimal_status_line_visible_mount_point_contract,
    build_warroom_v2_compact_ws_status_line_streamlit_top_minimal_status_line_visible_mount_point_packet,
    build_warroom_v2_compact_ws_status_line_streamlit_top_minimal_status_line_visible_render_mount_gate_observation_packet,
)

REPO_ROOT = Path(__file__).resolve().parents[6]
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q32Y_WARROOM_V2_COMPACT_WS_STATUS_LINE_STREAMLIT_TOP_MINIMAL_STATUS_LINE_VISIBLE_MOUNT_POINT_DEFAULT_OFF_OPERATOR_ACK_NO_SOCKET_2026-07-03.md"
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


def _ready_observation() -> dict[str, object]:
    return build_warroom_v2_compact_ws_status_line_streamlit_top_minimal_status_line_visible_render_mount_gate_observation_packet(
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


def test_q32y_contract_is_default_off_operator_ack_mount_point() -> None:
    packet = build_warroom_v2_compact_ws_status_line_streamlit_top_minimal_status_line_visible_mount_point_contract()
    assert packet["state_key"] == WARROOM_V2_COMPACT_WS_STATUS_LINE_STREAMLIT_TOP_MINIMAL_STATUS_LINE_VISIBLE_MOUNT_POINT_STATE_KEY
    assert packet["request_state_key"] == WARROOM_V2_COMPACT_WS_STATUS_LINE_STREAMLIT_TOP_MINIMAL_STATUS_LINE_VISIBLE_MOUNT_POINT_REQUEST_STATE_KEY
    assert packet["operator_ack_state_key"] == WARROOM_V2_COMPACT_WS_STATUS_LINE_STREAMLIT_TOP_MINIMAL_STATUS_LINE_VISIBLE_MOUNT_POINT_OPERATOR_ACK_STATE_KEY
    assert packet["mount_point_kind"] == "warroom_v2_compact_ws_status_line_streamlit_top_minimal_status_line_visible_mount_point_default_off_operator_ack"
    assert packet["visible_mount_point_requested_default"] is False
    assert packet["operator_visible_mount_point_ack_default"] is False
    assert packet["q32x_ready_required"] is True
    assert packet["mount_point_status_default"] == "compact_ws_status_line_streamlit_top_minimal_status_line_visible_mount_point_hidden_default"
    assert packet["mount_point_status_ready"] == "compact_ws_status_line_streamlit_top_minimal_status_line_visible_mount_point_markdown_allowed"
    assert packet["streamlit_markdown_allowed_default"] is False
    assert packet["socket_opened"] is False
    assert packet["order_intent_submitted"] is False


def test_q32y_default_packet_does_not_allow_markdown_or_mount() -> None:
    packet = build_warroom_v2_compact_ws_status_line_streamlit_top_minimal_status_line_visible_mount_point_packet()
    assert packet["packet_kind"] == "warroom_v2_compact_ws_status_line_streamlit_top_minimal_status_line_visible_mount_point_packet"
    assert packet["mount_point_status"] == "compact_ws_status_line_streamlit_top_minimal_status_line_visible_mount_point_hidden_default"
    assert packet["visible_mount_point_requested"] is False
    assert packet["operator_visible_mount_point_ack"] is False
    assert packet["q32x_ready_observation"] is False
    assert packet["streamlit_markdown_allowed"] is False
    assert packet["streamlit_markdown_invoked"] is False
    assert packet["status_line_visible_now"] is False
    assert packet["status_line_mounted_now"] is False
    assert packet["visible_ui_decoration_added"] is False
    assert packet["socket_opened"] is False


def test_q32y_ready_requires_request_ack_and_q32x_ready_observation() -> None:
    blocked_ack = build_warroom_v2_compact_ws_status_line_streamlit_top_minimal_status_line_visible_mount_point_packet(
        visible_render_mount_gate_observation_packet=_ready_observation(),
        visible_mount_point_requested=True,
        operator_visible_mount_point_ack=False,
    )
    assert blocked_ack["mount_point_status"] == "compact_ws_status_line_streamlit_top_minimal_status_line_visible_mount_point_blocked_operator_ack_required"
    blocked_ready = build_warroom_v2_compact_ws_status_line_streamlit_top_minimal_status_line_visible_mount_point_packet(
        visible_mount_point_requested=True,
        operator_visible_mount_point_ack=True,
    )
    assert blocked_ready["mount_point_status"] == "compact_ws_status_line_streamlit_top_minimal_status_line_visible_mount_point_blocked_ready_observation_required"
    ready = build_warroom_v2_compact_ws_status_line_streamlit_top_minimal_status_line_visible_mount_point_packet(
        visible_render_mount_gate_observation_packet=_ready_observation(),
        visible_mount_point_requested=True,
        operator_visible_mount_point_ack=True,
    )
    assert ready["mount_point_status"] == "compact_ws_status_line_streamlit_top_minimal_status_line_visible_mount_point_markdown_allowed"
    assert ready["streamlit_markdown_allowed"] is True
    assert ready["streamlit_markdown_invoked"] is False
    assert ready["status_line_visible_now"] is True
    assert ready["status_line_mounted_now"] is True
    assert ready["streamlit_call_name"] == "markdown"
    assert ready["display_items"][3]["value"] == "1"
    assert "WS状態: WS未接続（準備中）" in ready["compact_line_ja"]
    assert ready["would_send_to_broker"] is False


def test_q32y_warroom_page_has_default_off_mount_point_after_header() -> None:
    text = WARROOM_PAGE.read_text(encoding="utf-8-sig")
    assert "WARROOM_V2_COMPACT_WS_STATUS_LINE_STREAMLIT_TOP_MINIMAL_STATUS_LINE_VISIBLE_MOUNT_POINT_STATE_KEY" in text
    assert "WARROOM_V2_COMPACT_WS_STATUS_LINE_STREAMLIT_TOP_MINIMAL_STATUS_LINE_VISIBLE_MOUNT_POINT_REQUEST_STATE_KEY" in text
    assert "WARROOM_V2_COMPACT_WS_STATUS_LINE_STREAMLIT_TOP_MINIMAL_STATUS_LINE_VISIBLE_MOUNT_POINT_OPERATOR_ACK_STATE_KEY" in text
    assert "build_warroom_v2_compact_ws_status_line_streamlit_top_minimal_status_line_visible_mount_point_packet" in text
    assert "_render_warroom_v2_top_minimal_status_line_mount_q32y()" in text
    assert "st.session_state[WARROOM_V2_COMPACT_WS_STATUS_LINE_STREAMLIT_TOP_MINIMAL_STATUS_LINE_VISIBLE_MOUNT_POINT_STATE_KEY]" in text
    assert 'st.markdown(str(mount_point_packet.get("compact_line_ja") or ""))' in text
    header_pos = text.index("    live_shell.render_compact_page_header(get_text(lang, \"warroom_title\"))")
    mount_call_pos = text.index("    _render_warroom_v2_top_minimal_status_line_mount_q32y()", header_pos)
    focus_nav_pos = text.index("        render_warroom_operator_focus_nav()", mount_call_pos)
    assert header_pos < mount_call_pos < focus_nav_pos
    assert "build_warroom_v2_compact_ws_status_line_streamlit_top_minimal_status_line_visible_render_mount_gate_packet" not in text
    assert "WARROOM_V2_COMPACT_WS_STATUS_LINE_STREAMLIT_TOP_MINIMAL_STATUS_LINE_VISIBLE_RENDER_MOUNT_GATE_VERSION" not in text
    assert "render_mount_ready_for_future_streamlit_mount" not in text
    for label in ("WS状態: WS未接続（準備中）", "WarRoom WebSocket 状態"):
        assert label not in text


def test_q32y_doc_modules_preserve_no_socket_order_prediction_boundary() -> None:
    text = DOC.read_text(encoding="utf-8-sig")
    assert "visible_mount_point_requested_default=false" in text
    assert "operator_visible_mount_point_ack_default=false" in text
    assert "streamlit_markdown_allowed_default=false" in text
    assert "not_opening_socket=true" in text
    forbidden = (
        "websocket.", "sse.", "polling_loop(", "browser_timer_reload(", "send_to_broker(", "submit_order(",
        "append_ledger(", "write_runtime_artifact(", "write_prediction_artifact(", "run_prediction(", "invoke_classifier(",
        "D:" + chr(92), "E:" + chr(92),
    )
    for path in TRANSPORT_DIR.glob("*.py"):
        body = path.read_text(encoding="utf-8-sig")
        assert len(body.splitlines()) <= 220, f"transport file too large: {path}"
        for token in forbidden:
            assert token not in body, f"forbidden token {token!r} found in {path}"
