# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_compact_ws_status_line_gate_observation_q32f.py
# desc: PS-Q32F guards for hidden session_state compact WS status line gate observation. No UI mount and no socket open.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.apps.operator_ui.prediction_warroom.v2 import (  # noqa: E402
    WARROOM_V2_COMPACT_WS_STATUS_LINE_GATE_OBSERVATION_STATE_KEY,
    build_warroom_v2_compact_ws_status_line_gate_observation_contract,
    build_warroom_v2_compact_ws_status_line_gate_observation_packet,
)

REPO_ROOT = Path(__file__).resolve().parents[6]
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q32F_WARROOM_V2_COMPACT_WS_STATUS_LINE_GATE_OBSERVATION_TO_HIDDEN_SESSION_STATE_NO_UI_MOUNT_2026-07-03.md"
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


def test_q32f_contract_is_hidden_state_for_default_off_status_line_gate() -> None:
    packet = build_warroom_v2_compact_ws_status_line_gate_observation_contract()
    assert packet["state_key"] == WARROOM_V2_COMPACT_WS_STATUS_LINE_GATE_OBSERVATION_STATE_KEY
    assert packet["observation_kind"] == "warroom_v2_hidden_compact_ws_status_line_gate_observation_packet"
    assert packet["current_small_goal"] == "warroom_tab_ws_push_realtime_update_and_japanese_readability"
    assert packet["render_requested_default"] is False
    assert packet["operator_read_only_ack_default"] is False
    assert packet["default_gate_status"] == "compact_ws_status_line_hidden_default"
    assert packet["warroom_page_hidden_state_only"] is True
    assert packet["compact_status_only"] is True
    assert packet["socket_opened"] is False
    assert packet["order_intent_submitted"] is False


def test_q32f_default_hidden_observation_keeps_status_line_unmounted() -> None:
    packet = build_warroom_v2_compact_ws_status_line_gate_observation_packet(fragment_summary={"fragment_widget_count": 9})
    assert packet["packet_kind"] == "warroom_v2_compact_ws_status_line_gate_observation_packet"
    assert packet["gate_status"] == "compact_ws_status_line_hidden_default"
    assert packet["render_requested"] is False
    assert packet["operator_read_only_ack"] is False
    assert packet["status_line_available"] is True
    assert packet["status_line_ready_for_future_mount"] is False
    assert packet["status_line_visible_now"] is False
    assert packet["status_line_mounted_now"] is False
    assert packet["status_line_row"]["transport_state_ja"] == "WS未接続（準備中）"
    assert packet["visible_ui_decoration_added"] is False
    assert packet["socket_opened"] is False


def test_q32f_hidden_observation_can_record_ready_gate_but_still_not_mount() -> None:
    packet = build_warroom_v2_compact_ws_status_line_gate_observation_packet(
        render_requested=True,
        operator_read_only_ack=True,
        messages=[_message()],
    )
    assert packet["gate_status"] == "compact_ws_status_line_ready_read_only_not_mounted"
    assert packet["status_line_ready_for_future_mount"] is True
    assert packet["status_line_visible_now"] is False
    assert packet["status_line_mounted_now"] is False
    assert packet["status_line_row"]["received_message_count"] == 1
    assert packet["streamlit_render_allowed"] is False
    assert packet["warroom_page_ui_switch"] is False
    assert packet["would_send_to_broker"] is False


def test_q32f_warroom_page_records_hidden_status_line_gate_observation_only() -> None:
    text = WARROOM_PAGE.read_text(encoding="utf-8-sig")
    assert "WARROOM_V2_COMPACT_WS_STATUS_LINE_GATE_OBSERVATION_STATE_KEY" in text
    assert "warroom_v2_compact_ws_status_line_gate_observation_q32f" in text
    assert "build_warroom_v2_compact_ws_status_line_gate_observation_packet" in text
    assert "st.session_state[WARROOM_V2_COMPACT_WS_STATUS_LINE_GATE_OBSERVATION_STATE_KEY]" in text
    assert "build_warroom_v2_compact_ws_status_line_gate_packet" not in text
    assert "WARROOM_V2_COMPACT_WS_STATUS_LINE_GATE_VERSION" not in text
    forbidden_visible_labels = (
        "compact WS status line",
        "WS未接続（準備中）",
        "Enable compact WS status line",
    )
    for label in forbidden_visible_labels:
        assert label not in text


def test_q32f_doc_modules_preserve_no_side_effect_boundary() -> None:
    text = DOC.read_text(encoding="utf-8-sig")
    assert "state_key=warroom_v2_compact_ws_status_line_gate_observation_q32f" in text
    assert "default_gate_status=compact_ws_status_line_hidden_default" in text
    assert "status_line_mounted_now=false" in text
    assert "not_mounting_status_line_into_warroom=true" in text
    assert "not_opening_socket=true" in text
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
