# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_compact_ws_status_line_streamlit_minimal_renderer_q32m.py
# desc: PS-Q32M guards for compact WS status line minimal renderer spec. Default-off; no WarRoom page mount and no socket open.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.apps.operator_ui.prediction_warroom.v2 import (  # noqa: E402
    build_warroom_v2_compact_ws_status_line_streamlit_minimal_renderer_contract,
    build_warroom_v2_compact_ws_status_line_streamlit_minimal_renderer_packet,
)

REPO_ROOT = Path(__file__).resolve().parents[6]
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q32M_WARROOM_V2_COMPACT_WS_STATUS_LINE_STREAMLIT_MINIMAL_RENDERER_DEFAULT_OFF_2026-07-03.md"
TRANSPORT_DIR = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport"
WARROOM_PAGE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py"


def _message(topic: str = "warroom.market.snapshot", widget_id: str = "market_snapshot_strip", sequence: int = 1) -> dict[str, object]:
    return {
        "message_type": "warroom_v2_widget_update",
        "payload_kind": "widget_update_event_envelope",
        "topic": topic,
        "widget_id": widget_id,
        "sequence": sequence,
        "generated_at": "2026-07-03T00:00:00Z",
        "ui_patch_unit": "widget_dom_region",
        "broad_page_reload_required": False,
        "envelope": {"topic": topic, "widget_id": widget_id, "sequence": sequence},
        "json_payload": "{}",
    }


def test_q32m_contract_is_default_off_minimal_renderer_spec() -> None:
    packet = build_warroom_v2_compact_ws_status_line_streamlit_minimal_renderer_contract()
    assert packet["renderer_kind"] == "warroom_v2_compact_ws_status_line_streamlit_minimal_renderer_default_off"
    assert packet["current_small_goal"] == "warroom_tab_ws_push_realtime_update_and_japanese_readability"
    assert packet["renderer_requested_default"] is False
    assert packet["operator_renderer_ack_default"] is False
    assert packet["default_renderer_status"] == "compact_ws_status_line_streamlit_minimal_renderer_hidden_default"
    assert packet["ready_renderer_status"] == "compact_ws_status_line_streamlit_minimal_renderer_model_ready_not_rendered"
    assert packet["warroom_mount_surface"] == "top_minimal_operator_status_line"
    assert packet["warroom_page_modified"] is False
    assert packet["display_item_labels_ja"] == ["WS状態", "データ鮮度", "最終更新", "受信数", "破棄数", "案内"]
    assert packet["streamlit_imported"] is False
    assert packet["socket_opened"] is False
    assert packet["order_intent_submitted"] is False


def test_q32m_default_packet_builds_model_but_keeps_renderer_hidden() -> None:
    packet = build_warroom_v2_compact_ws_status_line_streamlit_minimal_renderer_packet(fragment_summary={"fragment_widget_count": 9})
    assert packet["packet_kind"] == "warroom_v2_compact_ws_status_line_streamlit_minimal_renderer_packet"
    assert packet["renderer_status"] == "compact_ws_status_line_streamlit_minimal_renderer_hidden_default"
    assert packet["renderer_requested"] is False
    assert packet["operator_renderer_ack"] is False
    assert packet["upstream_render_mount_ready"] is False
    assert packet["renderer_model_ready_for_future_streamlit_mount"] is False
    assert packet["renderer_model"]["layout_role"] == "top_minimal_operator_status_line"
    assert packet["renderer_model"]["ready_for_future_streamlit_call"] is False
    assert packet["display_items"][0] == {"field": "transport_state_ja", "label_ja": "WS状態", "value": "WS未接続（準備中）"}
    assert "WS状態: WS未接続（準備中）" in packet["compact_line_ja"]
    assert packet["status_line_visible_now"] is False
    assert packet["status_line_mounted_now"] is False
    assert packet["streamlit_render_invoked"] is False


def test_q32m_ready_requires_renderer_ack_and_upstream_mount_ready_but_still_not_rendered() -> None:
    blocked = build_warroom_v2_compact_ws_status_line_streamlit_minimal_renderer_packet(
        renderer_requested=True,
        operator_renderer_ack=True,
        visible_render_mount_requested=False,
        operator_visible_render_mount_ack=False,
    )
    assert blocked["renderer_status"] == "compact_ws_status_line_streamlit_minimal_renderer_blocked_mount_gate_not_ready"
    ready = build_warroom_v2_compact_ws_status_line_streamlit_minimal_renderer_packet(
        renderer_requested=True,
        operator_renderer_ack=True,
        visible_render_mount_requested=True,
        operator_visible_render_mount_ack=True,
        visible_render_adapter_requested=True,
        operator_visible_render_ack=True,
        visible_mount_requested=True,
        operator_visible_mount_ack=True,
        status_gate_render_requested=True,
        status_gate_read_only_ack=True,
        messages=[_message()],
    )
    assert ready["renderer_status"] == "compact_ws_status_line_streamlit_minimal_renderer_model_ready_not_rendered"
    assert ready["upstream_render_mount_ready"] is True
    assert ready["renderer_model_ready_for_future_streamlit_mount"] is True
    assert ready["renderer_model"]["ready_for_future_streamlit_call"] is True
    assert ready["display_items"][3]["value"] == "1"
    assert ready["streamlit_render_allowed"] is False
    assert ready["streamlit_render_invoked"] is False
    assert ready["would_send_to_broker"] is False


def test_q32m_renderer_model_preserves_exact_japanese_minimal_status_items() -> None:
    packet = build_warroom_v2_compact_ws_status_line_streamlit_minimal_renderer_packet()
    model = packet["renderer_model"]
    assert model["display_item_labels_ja"] == ["WS状態", "データ鮮度", "最終更新", "受信数", "破棄数", "案内"]
    assert model["display_item_count"] == 6
    assert model["aria_label_ja"] == "WarRoom WebSocket 状態"
    assert model["render_instruction_kind"] == "future_single_line_status_text"
    assert packet["compact_status_only"] is True
    assert packet["detailed_diagnostics_default_surface"] == "audit_or_diagnostics_tab"


def test_q32m_doc_modules_and_warroom_page_preserve_no_side_effect_boundary() -> None:
    text = DOC.read_text(encoding="utf-8-sig")
    assert "renderer_kind=warroom_v2_compact_ws_status_line_streamlit_minimal_renderer_default_off" in text
    assert "renderer_requested_default=false" in text
    assert "not_mounting_status_line_into_warroom=true" in text
    assert "not_modifying_warroom_page=true" in text
    assert "not_importing_streamlit=true" in text
    page = WARROOM_PAGE.read_text(encoding="utf-8-sig")
    assert "build_warroom_v2_compact_ws_status_line_streamlit_minimal_renderer_packet" not in page
    assert "WARROOM_V2_COMPACT_WS_STATUS_LINE_STREAMLIT_MINIMAL_RENDERER_VERSION" not in page
    # Later slices may record hidden observation state in WarRoom page, but must not mount
    # the Q32M direct renderer packet/version or any visible status-line label.
    visible_status_labels = (
        "compact WS status line streamlit minimal renderer",
        "WS状態: WS未接続（準備中）",
        "WarRoom WebSocket 状態",
    )
    for label in visible_status_labels:
        assert label not in page
    forbidden = (
        "import streamlit",
        "from streamlit",
        "websocket.",
        "sse.",
        "polling_loop(",
        "browser_timer_reload(",
        "send_to_broker(",
        "submit_order(",
        "append_ledger(",
        "write_runtime_artifact(",
        "write_prediction_artifact(",
        "run_prediction(",
        "invoke_classifier(",
        "st.write(",
        "st.metric(",
        "st.caption(",
        "D:" + chr(92),
        "E:" + chr(92),
    )
    for path in TRANSPORT_DIR.glob("*.py"):
        body = path.read_text(encoding="utf-8-sig")
        assert len(body.splitlines()) <= 220, f"transport file too large: {path}"
        for token in forbidden:
            assert token not in body, f"forbidden token {token!r} found in {path}"
