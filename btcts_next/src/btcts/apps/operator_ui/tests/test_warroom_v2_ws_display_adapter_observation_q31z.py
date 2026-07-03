# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_ws_display_adapter_observation_q31z.py
# desc: PS-Q31Z guards for hidden session_state WS display adapter observation. No socket and no UI mount.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.apps.operator_ui.prediction_warroom.v2 import (  # noqa: E402
    WARROOM_V2_WS_DISPLAY_ADAPTER_OBSERVATION_STATE_KEY,
    build_warroom_v2_ws_display_adapter_observation_contract,
    build_warroom_v2_ws_display_adapter_observation_packet,
)

REPO_ROOT = Path(__file__).resolve().parents[6]
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q31Z_WARROOM_V2_WS_DISPLAY_ADAPTER_OBSERVATION_TO_HIDDEN_SESSION_STATE_NO_SOCKET_2026-07-03.md"
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


def test_q31z_contract_is_hidden_state_for_ws_display_adapter() -> None:
    packet = build_warroom_v2_ws_display_adapter_observation_contract()
    assert packet["state_key"] == WARROOM_V2_WS_DISPLAY_ADAPTER_OBSERVATION_STATE_KEY
    assert packet["observation_kind"] == "warroom_v2_hidden_ws_display_adapter_observation_packet"
    assert packet["current_small_goal"] == "warroom_tab_ws_push_realtime_update_and_japanese_readability"
    assert packet["websocket_display_push_required"] is True
    assert packet["websocket_display_push_main_path"] is True
    assert packet["browser_timer_polling_is_legacy_compat_only"] is True
    assert packet["socket_opened"] is False
    assert packet["adapter_sends_messages"] is False
    assert packet["websocket_enabled"] is False
    assert packet["order_intent_submitted"] is False


def test_q31z_default_streamlit_path_records_empty_no_send_outbox() -> None:
    packet = build_warroom_v2_ws_display_adapter_observation_packet(fragment_summary={"fragment_widget_count": 9})
    assert packet["packet_kind"] == "warroom_v2_ws_display_adapter_observation_packet"
    assert packet["default_streamlit_message_count"] == 0
    assert packet["outbox_message_count"] == 0
    assert packet["outbox_dropped_count"] == 0
    assert packet["outbox_normalizes_display_targets_only"] is True
    assert packet["socket_opened"] is False
    assert packet["adapter_sends_messages"] is False
    assert packet["external_message_send_enabled"] is False
    assert packet["streamlit_render_allowed"] is False
    assert packet["would_send_to_broker"] is False


def test_q31z_observation_can_hold_display_outbox_without_sending() -> None:
    packet = build_warroom_v2_ws_display_adapter_observation_packet(messages=[_message(), _message("x.y", "bad", 2)])
    assert packet["default_streamlit_message_count"] == 2
    assert packet["outbox_message_count"] == 1
    assert packet["outbox_dropped_count"] == 1
    outbox = packet["ws_display_adapter_outbox_packet"]
    assert outbox["messages"][0]["topic"] == "warroom.market.snapshot"
    assert outbox["messages"][0]["would_send_over_ws_later"] is True
    assert outbox["messages"][0]["adapter_sends_messages"] is False
    assert outbox["messages"][0]["socket_opened"] is False
    assert packet["all_messages_are_display_targets"] is True
    assert packet["all_messages_no_broad_page_reload"] is True


def test_q31z_diagnostics_policy_keeps_main_warroom_compact() -> None:
    packet = build_warroom_v2_ws_display_adapter_observation_packet()
    assert packet["warroom_diagnostic_policy"] == "minimal_status_only"
    assert packet["detailed_diagnostics_default_surface"] == "audit_or_diagnostics_tab"
    assert packet["diagnostic_minimal_summary_allowed_in_warroom"] is True
    assert packet["warroom_visible_diagnostic_panel_default"] is False
    assert packet["visible_panel_render_plan_deprioritized"] is True
    assert packet["visible_ui_decoration_added"] is False
    assert packet["metric_added"] is False
    assert packet["caption_added"] is False


def test_q31z_warroom_page_records_hidden_ws_observation_state_only() -> None:
    text = WARROOM_PAGE.read_text(encoding="utf-8-sig")
    assert "WARROOM_V2_WS_DISPLAY_ADAPTER_OBSERVATION_STATE_KEY" in text
    assert "warroom_v2_ws_display_adapter_observation_q31z" in text
    assert "build_warroom_v2_ws_display_adapter_observation_packet" in text
    assert "st.session_state[WARROOM_V2_WS_DISPLAY_ADAPTER_OBSERVATION_STATE_KEY]" in text
    assert "build_warroom_v2_ws_display_push_outbox" not in text
    assert "WARROOM_V2_WS_DISPLAY_ADAPTER_VERSION" not in text
    forbidden_visible_labels = (
        "WS display adapter observation",
        "WebSocket display adapter observation",
        "Run WS display adapter",
        "Enable WS display adapter",
    )
    for label in forbidden_visible_labels:
        assert label not in text


def test_q31z_doc_modules_preserve_no_side_effect_boundary() -> None:
    text = DOC.read_text(encoding="utf-8-sig")
    assert "state_key=warroom_v2_ws_display_adapter_observation_q31z" in text
    assert "websocket_display_push_main_path=true" in text
    assert "not_opening_socket=true" in text
    assert "not_using_polling_fallback=true" in text
    assert "detailed_diagnostics_default_surface=audit_or_diagnostics_tab" in text
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
