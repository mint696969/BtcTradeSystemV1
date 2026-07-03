# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_ws_display_adapter_q31y.py
# desc: PS-Q31Y guards for WarRoom v2 WS display push adapter contract. No socket and no UI mount.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.apps.operator_ui.prediction_warroom.v2 import (  # noqa: E402
    build_warroom_v2_ws_display_push_adapter_contract,
    build_warroom_v2_ws_display_push_outbox,
)

REPO_ROOT = Path(__file__).resolve().parents[6]
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q31Y_WARROOM_V2_WS_DISPLAY_PUSH_TRANSPORT_ADAPTER_CONTRACT_NO_SOCKET_2026-07-03.md"
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


def test_q31y_contract_is_ws_display_main_path_but_no_socket() -> None:
    packet = build_warroom_v2_ws_display_push_adapter_contract()
    assert packet["adapter_kind"] == "ws_display_push_transport_adapter_contract_no_socket"
    assert packet["current_small_goal"] == "warroom_tab_ws_push_realtime_update_and_japanese_readability"
    assert packet["websocket_display_push_required"] is True
    assert packet["websocket_display_push_main_path"] is True
    assert packet["bidirectional_websocket_premise"] is True
    assert packet["read_model_push_plane"] == "server_to_warroom_ui"
    assert packet["browser_timer_polling_is_legacy_compat_only"] is True
    assert packet["browser_timer_refresh_replacement_target"] is True
    assert packet["socket_opened"] is False
    assert packet["adapter_sends_messages"] is False
    assert packet["websocket_enabled"] is False
    assert packet["order_intent_submitted"] is False


def test_q31y_diagnostic_policy_keeps_warroom_readable_and_routes_details_elsewhere() -> None:
    packet = build_warroom_v2_ws_display_push_adapter_contract()
    assert packet["warroom_diagnostic_policy"] == "minimal_status_only"
    assert packet["diagnostic_minimal_summary_allowed_in_warroom"] is True
    assert packet["detailed_diagnostics_default_surface"] == "audit_or_diagnostics_tab"
    assert packet["warroom_visible_diagnostic_panel_default"] is False
    assert packet["visible_panel_render_plan_deprioritized"] is True
    assert packet["allowed_warroom_diagnostic_summary_fields"] == ["safety_state", "data_freshness", "transport_state", "last_update_age"]


def test_q31y_outbox_normalizes_display_target_messages_without_sending() -> None:
    outbox = build_warroom_v2_ws_display_push_outbox(messages=[_message(), _message("not.warroom.topic", "other", 2)])
    assert outbox["packet_kind"] == "warroom_v2_ws_display_push_outbox_contract_packet"
    assert outbox["message_count"] == 1
    assert outbox["dropped_count"] == 1
    assert outbox["messages"][0]["topic"] == "warroom.market.snapshot"
    assert outbox["messages"][0]["would_send_over_ws_later"] is True
    assert outbox["messages"][0]["adapter_sends_messages"] is False
    assert outbox["messages"][0]["socket_opened"] is False
    assert outbox["all_messages_are_display_targets"] is True
    assert outbox["all_messages_are_read_only"] is True
    assert outbox["all_messages_are_display_only"] is True
    assert outbox["all_messages_no_broad_page_reload"] is True
    assert outbox["would_send_to_broker"] is False


def test_q31y_no_polling_reload_ui_or_order_path_is_introduced() -> None:
    packet = build_warroom_v2_ws_display_push_outbox(messages=[_message()])
    assert packet["no_new_polling_fallback"] is True
    assert packet["no_browser_timer_reload_introduced"] is True
    assert packet["streamlit_render_allowed"] is False
    assert packet["warroom_page_ui_switch"] is False
    assert packet["external_message_send_enabled"] is False
    assert packet["broker_send_enabled"] is False
    assert packet["ledger_append_allowed"] is False
    assert packet["mode_apply_allowed"] is False
    assert packet["parameter_apply_allowed"] is False
    assert packet["prediction_generation_invoked"] is False
    assert packet["prediction_inference_invoked"] is False
    assert packet["classifier_invoked"] is False


def test_q31y_doc_modules_and_warroom_page_preserve_no_side_effect_boundary() -> None:
    text = DOC.read_text(encoding="utf-8-sig")
    assert "websocket_display_push_main_path=true" in text
    assert "browser_timer_polling_is_legacy_compat_only=true" in text
    assert "warroom_diagnostic_policy=minimal_status_only" in text
    assert "detailed_diagnostics_default_surface=audit_or_diagnostics_tab" in text
    assert "not_opening_socket=true" in text
    assert "not_submitting_order_intent=true" in text
    page = WARROOM_PAGE.read_text(encoding="utf-8-sig")
    assert "build_warroom_v2_ws_display_push_outbox" not in page
    assert "WARROOM_V2_WS_DISPLAY_ADAPTER_VERSION" not in page
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
