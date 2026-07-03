# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_compact_ws_status_line_gate_q32e.py
# desc: PS-Q32E guards for compact WS status line render gate. Default-off; no UI mount and no socket open.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.apps.operator_ui.prediction_warroom.v2 import (  # noqa: E402
    build_warroom_v2_compact_ws_status_line_gate_contract,
    build_warroom_v2_compact_ws_status_line_gate_packet,
)

REPO_ROOT = Path(__file__).resolve().parents[6]
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q32E_WARROOM_V2_COMPACT_WS_STATUS_LINE_RENDER_GATE_DEFAULT_OFF_2026-07-03.md"
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


def test_q32e_contract_is_default_off_render_gate() -> None:
    packet = build_warroom_v2_compact_ws_status_line_gate_contract()
    assert packet["gate_kind"] == "warroom_v2_compact_ws_status_line_render_gate_default_off"
    assert packet["current_small_goal"] == "warroom_tab_ws_push_realtime_update_and_japanese_readability"
    assert packet["render_requested_default"] is False
    assert packet["operator_read_only_ack_default"] is False
    assert packet["status_line_visible_now_default"] is False
    assert packet["status_line_mounted_now_default"] is False
    assert packet["default_gate_status"] == "compact_ws_status_line_hidden_default"
    assert packet["warroom_visible_surface"] == "top_minimal_operator_status_line_later"
    assert packet["compact_status_only"] is True
    assert packet["socket_opened"] is False
    assert packet["order_intent_submitted"] is False


def test_q32e_default_packet_keeps_status_line_hidden() -> None:
    packet = build_warroom_v2_compact_ws_status_line_gate_packet(fragment_summary={"fragment_widget_count": 9})
    assert packet["packet_kind"] == "warroom_v2_compact_ws_status_line_gate_packet"
    assert packet["gate_status"] == "compact_ws_status_line_hidden_default"
    assert packet["render_requested"] is False
    assert packet["operator_read_only_ack"] is False
    assert packet["status_line_available"] is True
    assert packet["status_line_ready_for_future_mount"] is False
    assert packet["status_line_visible_now"] is False
    assert packet["status_line_mounted_now"] is False
    assert packet["status_line_row"]["transport_state_ja"] == "WS未接続（準備中）"
    assert packet["status_line_row"]["data_freshness_ja"] == "未接続のため未取得"
    assert packet["status_line_row"]["last_update_age_ja"] == "未接続"
    assert packet["socket_opened"] is False


def test_q32e_ready_state_requires_request_and_read_only_ack_but_still_not_mounted() -> None:
    blocked = build_warroom_v2_compact_ws_status_line_gate_packet(render_requested=True, operator_read_only_ack=False)
    assert blocked["gate_status"] == "compact_ws_status_line_blocked_read_only_ack_required"
    assert blocked["status_line_ready_for_future_mount"] is False
    ready = build_warroom_v2_compact_ws_status_line_gate_packet(render_requested=True, operator_read_only_ack=True, messages=[_message()])
    assert ready["gate_status"] == "compact_ws_status_line_ready_read_only_not_mounted"
    assert ready["status_line_ready_for_future_mount"] is True
    assert ready["status_line_visible_now"] is False
    assert ready["status_line_mounted_now"] is False
    assert ready["status_line_row"]["received_message_count"] == 1
    assert ready["streamlit_render_allowed"] is False
    assert ready["visible_ui_decoration_added"] is False


def test_q32e_gate_exposes_exact_compact_status_fields_only() -> None:
    packet = build_warroom_v2_compact_ws_status_line_gate_packet(render_requested=True, operator_read_only_ack=True)
    assert list(packet["status_line_row"].keys()) == [
        "transport_state_ja",
        "data_freshness_ja",
        "last_update_age_ja",
        "received_message_count",
        "dropped_count",
        "operator_guidance_ja",
    ]
    assert packet["status_line_field_count"] == 6
    assert packet["detailed_diagnostics_default_surface"] == "audit_or_diagnostics_tab"
    assert packet["read_only"] is True
    assert packet["display_only"] is True


def test_q32e_doc_modules_and_warroom_page_preserve_no_side_effect_boundary() -> None:
    text = DOC.read_text(encoding="utf-8-sig")
    assert "gate_kind=warroom_v2_compact_ws_status_line_render_gate_default_off" in text
    assert "render_requested_default=false" in text
    assert "not_mounting_status_line_into_warroom=true" in text
    assert "not_opening_socket=true" in text
    page = WARROOM_PAGE.read_text(encoding="utf-8-sig")
    assert "build_warroom_v2_compact_ws_status_line_gate_packet" not in page
    assert "WARROOM_V2_COMPACT_WS_STATUS_LINE_GATE_VERSION" not in page
    assert "compact_ws_status_line" not in page
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
