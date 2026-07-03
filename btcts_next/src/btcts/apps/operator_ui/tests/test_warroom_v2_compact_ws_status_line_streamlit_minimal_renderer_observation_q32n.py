# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_compact_ws_status_line_streamlit_minimal_renderer_observation_q32n.py
# desc: PS-Q32N guards for hidden session_state compact WS status line minimal renderer observation. No UI mount and no socket open.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.apps.operator_ui.prediction_warroom.v2 import (  # noqa: E402
    WARROOM_V2_COMPACT_WS_STATUS_LINE_STREAMLIT_MINIMAL_RENDERER_OBSERVATION_STATE_KEY,
    build_warroom_v2_compact_ws_status_line_streamlit_minimal_renderer_observation_contract,
    build_warroom_v2_compact_ws_status_line_streamlit_minimal_renderer_observation_packet,
)

REPO_ROOT = Path(__file__).resolve().parents[6]
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q32N_WARROOM_V2_COMPACT_WS_STATUS_LINE_STREAMLIT_MINIMAL_RENDERER_OBSERVATION_TO_HIDDEN_SESSION_STATE_NO_UI_MOUNT_2026-07-03.md"
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


def test_q32n_contract_is_hidden_state_for_minimal_renderer() -> None:
    packet = build_warroom_v2_compact_ws_status_line_streamlit_minimal_renderer_observation_contract()
    assert packet["state_key"] == WARROOM_V2_COMPACT_WS_STATUS_LINE_STREAMLIT_MINIMAL_RENDERER_OBSERVATION_STATE_KEY
    assert packet["observation_kind"] == "warroom_v2_hidden_compact_ws_status_line_streamlit_minimal_renderer_observation_packet"
    assert packet["current_small_goal"] == "warroom_tab_ws_push_realtime_update_and_japanese_readability"
    assert packet["renderer_requested_default"] is False
    assert packet["operator_renderer_ack_default"] is False
    assert packet["default_renderer_status"] == "compact_ws_status_line_streamlit_minimal_renderer_hidden_default"
    assert packet["warroom_page_hidden_state_only"] is True
    assert packet["display_item_labels_ja"] == ["WS状態", "データ鮮度", "最終更新", "受信数", "破棄数", "案内"]
    assert packet["streamlit_imported"] is False
    assert packet["socket_opened"] is False
    assert packet["order_intent_submitted"] is False


def test_q32n_default_hidden_observation_keeps_renderer_unmounted() -> None:
    packet = build_warroom_v2_compact_ws_status_line_streamlit_minimal_renderer_observation_packet(fragment_summary={"fragment_widget_count": 9})
    assert packet["packet_kind"] == "warroom_v2_compact_ws_status_line_streamlit_minimal_renderer_observation_packet"
    assert packet["renderer_status"] == "compact_ws_status_line_streamlit_minimal_renderer_hidden_default"
    assert packet["renderer_requested"] is False
    assert packet["operator_renderer_ack"] is False
    assert packet["upstream_render_mount_ready"] is False
    assert packet["renderer_model_ready_for_future_streamlit_mount"] is False
    assert packet["renderer_model"]["layout_role"] == "top_minimal_operator_status_line"
    assert packet["display_items"][0] == {"field": "transport_state_ja", "label_ja": "WS状態", "value": "WS未接続（準備中）"}
    assert "WS状態: WS未接続（準備中）" in packet["compact_line_ja"]
    assert packet["status_line_visible_now"] is False
    assert packet["status_line_mounted_now"] is False
    assert packet["streamlit_imported"] is False
    assert packet["streamlit_render_invoked"] is False


def test_q32n_hidden_observation_can_record_ready_renderer_but_still_not_mount() -> None:
    packet = build_warroom_v2_compact_ws_status_line_streamlit_minimal_renderer_observation_packet(
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
    assert packet["renderer_status"] == "compact_ws_status_line_streamlit_minimal_renderer_model_ready_not_rendered"
    assert packet["upstream_render_mount_ready"] is True
    assert packet["renderer_model_ready_for_future_streamlit_mount"] is True
    assert packet["renderer_model"]["ready_for_future_streamlit_call"] is True
    assert packet["display_items"][3]["value"] == "1"
    assert packet["status_line_visible_now"] is False
    assert packet["status_line_mounted_now"] is False
    assert packet["streamlit_render_allowed"] is False
    assert packet["warroom_page_ui_switch"] is False
    assert packet["would_send_to_broker"] is False


def test_q32n_warroom_page_records_hidden_minimal_renderer_observation_only() -> None:
    text = WARROOM_PAGE.read_text(encoding="utf-8-sig")
    assert "WARROOM_V2_COMPACT_WS_STATUS_LINE_STREAMLIT_MINIMAL_RENDERER_OBSERVATION_STATE_KEY" in text
    assert "warroom_v2_compact_ws_status_line_streamlit_minimal_renderer_observation_q32n" in text
    assert "build_warroom_v2_compact_ws_status_line_streamlit_minimal_renderer_observation_packet" in text
    assert "st.session_state[WARROOM_V2_COMPACT_WS_STATUS_LINE_STREAMLIT_MINIMAL_RENDERER_OBSERVATION_STATE_KEY]" in text
    assert "build_warroom_v2_compact_ws_status_line_streamlit_minimal_renderer_packet" not in text
    assert "WARROOM_V2_COMPACT_WS_STATUS_LINE_STREAMLIT_MINIMAL_RENDERER_VERSION" not in text
    for label in ("compact WS status line streamlit minimal renderer", "WS状態: WS未接続（準備中）", "WarRoom WebSocket 状態"):
        assert label not in text


def test_q32n_doc_modules_preserve_no_side_effect_boundary() -> None:
    text = DOC.read_text(encoding="utf-8-sig")
    assert "state_key=warroom_v2_compact_ws_status_line_streamlit_minimal_renderer_observation_q32n" in text
    assert "default_renderer_status=compact_ws_status_line_streamlit_minimal_renderer_hidden_default" in text
    assert "streamlit_render_invoked=false" in text
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
