# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_compact_ws_status_line_streamlit_visible_mount_gate_q32o.py
# desc: PS-Q32O guards for compact WS status line Streamlit visible mount gate. Default-off; no WarRoom page mount and no socket open.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.apps.operator_ui.prediction_warroom.v2 import (  # noqa: E402
    build_warroom_v2_compact_ws_status_line_streamlit_visible_mount_gate_contract,
    build_warroom_v2_compact_ws_status_line_streamlit_visible_mount_gate_packet,
)

REPO_ROOT = Path(__file__).resolve().parents[6]
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q32O_WARROOM_V2_COMPACT_WS_STATUS_LINE_STREAMLIT_VISIBLE_MOUNT_GATE_DEFAULT_OFF_2026-07-03.md"
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


def test_q32o_contract_is_default_off_visible_mount_gate() -> None:
    packet = build_warroom_v2_compact_ws_status_line_streamlit_visible_mount_gate_contract()
    assert packet["gate_kind"] == "warroom_v2_compact_ws_status_line_streamlit_visible_mount_gate_default_off"
    assert packet["current_small_goal"] == "warroom_tab_ws_push_realtime_update_and_japanese_readability"
    assert packet["visible_streamlit_mount_requested_default"] is False
    assert packet["operator_visible_streamlit_mount_ack_default"] is False
    assert packet["default_gate_status"] == "compact_ws_status_line_streamlit_visible_mount_hidden_default"
    assert packet["ready_gate_status"] == "compact_ws_status_line_streamlit_visible_mount_ready_not_mounted"
    assert packet["mount_allowed_for_future_warroom_page_default"] is False
    assert packet["warroom_page_modified"] is False
    assert packet["display_item_labels_ja"] == ["WS状態", "データ鮮度", "最終更新", "受信数", "破棄数", "案内"]
    assert packet["streamlit_imported"] is False
    assert packet["socket_opened"] is False
    assert packet["order_intent_submitted"] is False


def test_q32o_default_packet_keeps_mount_gate_hidden() -> None:
    packet = build_warroom_v2_compact_ws_status_line_streamlit_visible_mount_gate_packet(fragment_summary={"fragment_widget_count": 9})
    assert packet["packet_kind"] == "warroom_v2_compact_ws_status_line_streamlit_visible_mount_gate_packet"
    assert packet["gate_status"] == "compact_ws_status_line_streamlit_visible_mount_hidden_default"
    assert packet["visible_streamlit_mount_requested"] is False
    assert packet["operator_visible_streamlit_mount_ack"] is False
    assert packet["upstream_renderer_model_ready"] is False
    assert packet["mount_allowed_for_future_warroom_page"] is False
    assert packet["renderer_model"]["layout_role"] == "top_minimal_operator_status_line"
    assert packet["display_items"][0] == {"field": "transport_state_ja", "label_ja": "WS状態", "value": "WS未接続（準備中）"}
    assert "WS状態: WS未接続（準備中）" in packet["compact_line_ja"]
    assert packet["status_line_visible_now"] is False
    assert packet["status_line_mounted_now"] is False
    assert packet["streamlit_imported"] is False
    assert packet["streamlit_render_invoked"] is False


def test_q32o_ready_requires_visible_mount_ack_and_upstream_renderer_ready_but_still_not_mounted() -> None:
    blocked = build_warroom_v2_compact_ws_status_line_streamlit_visible_mount_gate_packet(
        visible_streamlit_mount_requested=True,
        operator_visible_streamlit_mount_ack=True,
        renderer_requested=False,
        operator_renderer_ack=False,
    )
    assert blocked["gate_status"] == "compact_ws_status_line_streamlit_visible_mount_blocked_renderer_not_ready"
    ready = build_warroom_v2_compact_ws_status_line_streamlit_visible_mount_gate_packet(
        visible_streamlit_mount_requested=True,
        operator_visible_streamlit_mount_ack=True,
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
    assert ready["gate_status"] == "compact_ws_status_line_streamlit_visible_mount_ready_not_mounted"
    assert ready["upstream_renderer_model_ready"] is True
    assert ready["mount_allowed_for_future_warroom_page"] is True
    assert ready["display_items"][3]["value"] == "1"
    assert ready["status_line_visible_now"] is False
    assert ready["status_line_mounted_now"] is False
    assert ready["streamlit_render_allowed"] is False
    assert ready["streamlit_render_invoked"] is False
    assert ready["would_send_to_broker"] is False


def test_q32o_warroom_page_is_not_modified_for_visible_mount_gate() -> None:
    page = WARROOM_PAGE.read_text(encoding="utf-8-sig")
    assert "build_warroom_v2_compact_ws_status_line_streamlit_visible_mount_gate_packet" not in page
    assert "WARROOM_V2_COMPACT_WS_STATUS_LINE_STREAMLIT_VISIBLE_MOUNT_GATE_VERSION" not in page
    assert "compact_ws_status_line_streamlit_visible_mount_gate" not in page
    assert "mount_allowed_for_future_warroom_page" not in page
    for label in ("compact WS status line visible mount", "WS状態: WS未接続（準備中）", "WarRoom WebSocket 状態"):
        assert label not in page


def test_q32o_doc_modules_preserve_no_side_effect_boundary() -> None:
    text = DOC.read_text(encoding="utf-8-sig")
    assert "gate_kind=warroom_v2_compact_ws_status_line_streamlit_visible_mount_gate_default_off" in text
    assert "visible_streamlit_mount_requested_default=false" in text
    assert "not_mounting_status_line_into_warroom=true" in text
    assert "not_importing_streamlit=true" in text
    forbidden = (
        "import streamlit", "from streamlit", "websocket.", "sse.", "polling_loop(", "browser_timer_reload(",
        "send_to_broker(", "submit_order(", "append_ledger(", "write_runtime_artifact(", "write_prediction_artifact(",
        "run_prediction(", "invoke_classifier(", "st.write(", "st.metric(", "st.caption(", "D:" + chr(92), "E:" + chr(92),
    )
    for path in TRANSPORT_DIR.glob("*.py"):
        body = path.read_text(encoding="utf-8-sig")
        assert len(body.splitlines()) <= 220, f"transport file too large: {path}"
        for token in forbidden:
            assert token not in body, f"forbidden token {token!r} found in {path}"
