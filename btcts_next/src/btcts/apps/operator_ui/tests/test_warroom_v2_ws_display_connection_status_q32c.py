# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_ws_display_connection_status_q32c.py
# desc: PS-Q32C guards for WarRoom v2 compact WS display connection status contract. No socket open and no UI mount.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.apps.operator_ui.prediction_warroom.v2 import (  # noqa: E402
    build_warroom_v2_ws_display_connection_status_contract,
    build_warroom_v2_ws_display_connection_status_packet,
)

REPO_ROOT = Path(__file__).resolve().parents[6]
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q32C_WARROOM_V2_WS_DISPLAY_CONNECTION_STATUS_CONTRACT_NO_SOCKET_OPEN_2026-07-03.md"
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


def test_q32c_contract_defines_compact_warroom_safe_status_line_without_socket() -> None:
    packet = build_warroom_v2_ws_display_connection_status_contract()
    assert packet["status_kind"] == "warroom_v2_ws_display_connection_status_contract_no_socket_open"
    assert packet["current_small_goal"] == "warroom_tab_ws_push_realtime_update_and_japanese_readability"
    assert packet["warroom_status_line_allowed_later"] is True
    assert packet["warroom_status_line_mounted_now"] is False
    assert packet["compact_status_only"] is True
    assert packet["detailed_diagnostics_default_surface"] == "audit_or_diagnostics_tab"
    assert packet["socket_opened"] is False
    assert packet["client_started"] is False
    assert packet["order_intent_submitted"] is False
    assert packet["allowed_warroom_status_fields"] == [
        "transport_state_ja",
        "data_freshness_ja",
        "last_update_age_ja",
        "received_message_count",
        "dropped_count",
        "operator_guidance_ja",
    ]


def test_q32c_default_status_is_japanese_not_started_no_socket_open() -> None:
    packet = build_warroom_v2_ws_display_connection_status_packet()
    assert packet["packet_kind"] == "warroom_v2_ws_display_connection_status_packet"
    assert packet["status_code"] == "ws_not_started_no_socket_open"
    assert packet["status_line"]["transport_state_ja"] == "WS未接続（準備中）"
    assert packet["status_line"]["data_freshness_ja"] == "未接続のため未取得"
    assert packet["status_line"]["last_update_age_ja"] == "未接続"
    assert packet["status_line"]["received_message_count"] == 0
    assert packet["status_line"]["dropped_count"] == 0
    assert "表示契約のみ確認中" in packet["status_line"]["operator_guidance_ja"]
    assert packet["status_line_visible_now"] is False
    assert packet["socket_opened"] is False
    assert packet["client_started"] is False


def test_q32c_status_can_reflect_buffer_counts_without_starting_client() -> None:
    packet = build_warroom_v2_ws_display_connection_status_packet(messages=[_message(), _message("x.y", "bad", 2)])
    assert packet["status_code"] == "ws_not_started_no_socket_open"
    assert packet["received_message_count"] == 1
    assert packet["dropped_count"] == 1
    assert packet["status_line"]["received_message_count"] == 1
    assert packet["status_line"]["dropped_count"] == 1
    assert packet["client_observation_packet"]["packet_kind"] == "warroom_v2_ws_display_client_observation_packet"
    assert packet["socket_opened"] is False
    assert packet["client_started"] is False
    assert packet["client_sends_messages"] is False


def test_q32c_status_contract_adds_no_visible_warroom_mount() -> None:
    packet = build_warroom_v2_ws_display_connection_status_packet()
    assert packet["streamlit_render_allowed"] is False
    assert packet["warroom_page_ui_switch"] is False
    assert packet["visible_ui_decoration_added"] is False
    assert packet["streamlit_component_added"] is False
    assert packet["button_added"] is False
    assert packet["checkbox_added"] is False
    assert packet["metric_added"] is False
    assert packet["caption_added"] is False
    page = WARROOM_PAGE.read_text(encoding="utf-8-sig")
    assert "build_warroom_v2_ws_display_connection_status_packet" not in page
    assert "WARROOM_V2_WS_DISPLAY_CONNECTION_STATUS_VERSION" not in page


def test_q32c_doc_modules_preserve_no_side_effect_boundary() -> None:
    text = DOC.read_text(encoding="utf-8-sig")
    assert "status_kind=warroom_v2_ws_display_connection_status_contract_no_socket_open" in text
    assert "warroom_status_line_allowed_later=true" in text
    assert "warroom_status_line_mounted_now=false" in text
    assert "not_opening_socket=true" in text
    assert "not_using_polling_fallback=true" in text
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
