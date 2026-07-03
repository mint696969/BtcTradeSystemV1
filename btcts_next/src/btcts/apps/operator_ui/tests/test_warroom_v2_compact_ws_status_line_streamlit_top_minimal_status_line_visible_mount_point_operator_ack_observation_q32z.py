# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_compact_ws_status_line_streamlit_top_minimal_status_line_visible_mount_point_operator_ack_observation_q32z.py
# desc: PS-Q32Z guards for top minimal visible mount point operator ack observation/manual smoke guide. No socket and no visible controls.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.apps.operator_ui.prediction_warroom.v2 import (  # noqa: E402
    build_warroom_v2_compact_ws_status_line_streamlit_top_minimal_status_line_visible_mount_point_operator_ack_observation_contract,
    build_warroom_v2_compact_ws_status_line_streamlit_top_minimal_status_line_visible_mount_point_operator_ack_observation_packet,
    build_warroom_v2_compact_ws_status_line_streamlit_top_minimal_status_line_visible_render_mount_gate_observation_packet,
)

REPO_ROOT = Path(__file__).resolve().parents[6]
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q32Z_WARROOM_V2_COMPACT_WS_STATUS_LINE_STREAMLIT_TOP_MINIMAL_STATUS_LINE_VISIBLE_MOUNT_POINT_OPERATOR_ACK_OBSERVATION_AND_MANUAL_SMOKE_GUIDE_2026-07-03.md"
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


def test_q32z_contract_is_manual_smoke_observation_without_visible_controls() -> None:
    packet = build_warroom_v2_compact_ws_status_line_streamlit_top_minimal_status_line_visible_mount_point_operator_ack_observation_contract()
    assert packet["observation_kind"] == "warroom_v2_compact_ws_status_line_streamlit_top_minimal_status_line_visible_mount_point_operator_ack_observation_packet"
    assert packet["manual_smoke_guide_added"] is True
    assert packet["manual_smoke_default_enabled"] is False
    assert packet["manual_smoke_requires_operator_ack"] is True
    assert packet["manual_smoke_status_default"] == "manual_smoke_not_requested"
    assert packet["manual_smoke_status_ready"] == "manual_smoke_ready_for_operator_visual_check_no_socket"
    assert packet["visible_controls_added"] is False
    assert packet["warroom_page_modified"] is False
    assert packet["streamlit_markdown_allowed_default"] is False
    assert packet["socket_opened"] is False
    assert packet["order_intent_submitted"] is False


def test_q32z_default_packet_keeps_manual_smoke_and_mount_point_off() -> None:
    packet = build_warroom_v2_compact_ws_status_line_streamlit_top_minimal_status_line_visible_mount_point_operator_ack_observation_packet()
    assert packet["manual_smoke_status"] == "manual_smoke_not_requested"
    assert packet["manual_smoke_ready_for_operator_visual_check"] is False
    assert packet["visible_mount_point_requested"] is False
    assert packet["operator_visible_mount_point_ack"] is False
    assert packet["operator_ack_observed"] is False
    assert packet["q32y_mount_point_status"] == "compact_ws_status_line_streamlit_top_minimal_status_line_visible_mount_point_hidden_default"
    assert packet["q32y_markdown_allowed"] is False
    assert packet["streamlit_markdown_invoked"] is False
    assert packet["status_line_visible_now"] is False
    assert packet["status_line_mounted_now"] is False
    assert packet["socket_opened"] is False


def test_q32z_manual_smoke_requires_operator_manual_ack_and_q32y_markdown_allowed() -> None:
    blocked_ack = build_warroom_v2_compact_ws_status_line_streamlit_top_minimal_status_line_visible_mount_point_operator_ack_observation_packet(
        visible_render_mount_gate_observation_packet=_ready_observation(),
        visible_mount_point_requested=True,
        operator_visible_mount_point_ack=True,
        manual_smoke_requested=True,
        operator_manual_smoke_ack=False,
    )
    assert blocked_ack["manual_smoke_status"] == "manual_smoke_blocked_operator_ack_required"
    blocked_gate = build_warroom_v2_compact_ws_status_line_streamlit_top_minimal_status_line_visible_mount_point_operator_ack_observation_packet(
        visible_mount_point_requested=True,
        operator_visible_mount_point_ack=True,
        manual_smoke_requested=True,
        operator_manual_smoke_ack=True,
    )
    assert blocked_gate["manual_smoke_status"] == "manual_smoke_blocked_mount_point_not_markdown_allowed"
    ready = build_warroom_v2_compact_ws_status_line_streamlit_top_minimal_status_line_visible_mount_point_operator_ack_observation_packet(
        visible_render_mount_gate_observation_packet=_ready_observation(),
        visible_mount_point_requested=True,
        operator_visible_mount_point_ack=True,
        manual_smoke_requested=True,
        operator_manual_smoke_ack=True,
    )
    assert ready["manual_smoke_status"] == "manual_smoke_ready_for_operator_visual_check_no_socket"
    assert ready["manual_smoke_ready_for_operator_visual_check"] is True
    assert ready["q32y_markdown_allowed"] is True
    assert ready["streamlit_markdown_invoked"] is False
    assert ready["status_line_visible_now"] is True
    assert "WS状態: WS未接続（準備中）" in ready["compact_line_ja"]
    assert ready["would_send_to_broker"] is False


def test_q32z_doc_and_warroom_page_preserve_manual_only_boundary() -> None:
    text = DOC.read_text(encoding="utf-8-sig")
    assert "manual_smoke_guide_added=true" in text
    assert "manual_smoke_default_enabled=false" in text
    assert "step_7=reset_request_key_false_and_operator_ack_key_false" in text
    assert "not_modifying_warroom_page=true" in text
    assert "not_opening_socket=true" in text
    page = WARROOM_PAGE.read_text(encoding="utf-8-sig")
    assert "operator_ack_observation_q32z" not in page
    assert "manual_smoke_ready_for_operator_visual_check_no_socket" not in page
    assert page.count('st.markdown(str(mount_point_packet.get("compact_line_ja") or ""))') == 1
    assert 'st.checkbox("WS' not in page
    assert 'st.button("WS' not in page


def test_q32z_transport_modules_preserve_no_socket_order_prediction_boundary() -> None:
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
