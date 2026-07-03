# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_ws_display_client_q32a.py
# desc: PS-Q32A guards for WarRoom v2 UI-side WS display client contract. No socket open and no UI mount.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.apps.operator_ui.prediction_warroom.v2 import (  # noqa: E402
    build_warroom_v2_ws_display_client_contract,
    build_warroom_v2_ws_display_client_packet,
    build_warroom_v2_ws_display_client_receive_buffer,
    build_warroom_v2_ws_display_client_subscription_packet,
)

REPO_ROOT = Path(__file__).resolve().parents[6]
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q32A_WARROOM_V2_WS_DISPLAY_CLIENT_CONTRACT_NO_SOCKET_OPEN_2026-07-03.md"
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


def test_q32a_contract_defines_ui_receiver_without_socket_open() -> None:
    packet = build_warroom_v2_ws_display_client_contract()
    assert packet["client_kind"] == "ws_display_client_contract_no_socket_open"
    assert packet["current_small_goal"] == "warroom_tab_ws_push_realtime_update_and_japanese_readability"
    assert packet["ui_receiver_side"] is True
    assert packet["server_to_warroom_ui"] is True
    assert packet["websocket_display_push_main_path"] is True
    assert packet["subscriptions_source"] == "q31x_realtime_japanese_read_surface_targets"
    assert packet["inbound_source"] == "q31z_ws_display_adapter_observation_outbox"
    assert packet["socket_open_requested_default"] is False
    assert packet["socket_opened"] is False
    assert packet["client_started"] is False
    assert packet["client_sends_messages"] is False
    assert packet["order_intent_submitted"] is False


def test_q32a_subscription_packet_uses_japanese_read_surface_targets_but_subscribes_later() -> None:
    packet = build_warroom_v2_ws_display_client_subscription_packet()
    assert packet["packet_kind"] == "warroom_v2_ws_display_client_subscription_packet"
    assert packet["subscription_count"] >= 10
    topics = {row["topic"] for row in packet["subscriptions"]}
    assert "warroom.market.snapshot" in topics
    assert "warroom.prediction.scenario_ja" in topics
    assert all(row["subscribe_later"] is True for row in packet["subscriptions"])
    assert all(row["subscribed_now"] is False for row in packet["subscriptions"])
    assert all(row["socket_opened"] is False for row in packet["subscriptions"])
    assert all(row["client_sends_messages"] is False for row in packet["subscriptions"])


def test_q32a_receive_buffer_accepts_only_display_targets_without_opening_socket() -> None:
    packet = build_warroom_v2_ws_display_client_receive_buffer(messages=[_message(), _message("not.display", "bad", 2)])
    assert packet["packet_kind"] == "warroom_v2_ws_display_client_receive_buffer_packet"
    assert packet["received_message_count"] == 1
    assert packet["dropped_count"] == 1
    assert packet["messages"][0]["topic"] == "warroom.market.snapshot"
    assert packet["messages"][0]["accepted_by_client_contract"] is True
    assert packet["messages"][0]["received_over_ws_now"] is False
    assert packet["all_messages_are_display_targets"] is True
    assert packet["all_messages_are_read_only"] is True
    assert packet["all_messages_are_display_only"] is True
    assert packet["all_messages_no_broad_page_reload"] is True
    assert packet["socket_opened"] is False
    assert packet["client_sends_messages"] is False


def test_q32a_composed_packet_uses_q31z_adapter_observation_and_stays_no_side_effect() -> None:
    packet = build_warroom_v2_ws_display_client_packet(messages=[_message(), _message("x.y", "bad", 2)])
    assert packet["packet_kind"] == "warroom_v2_ws_display_client_packet"
    assert packet["adapter_observation_packet"]["packet_kind"] == "warroom_v2_ws_display_adapter_observation_packet"
    assert packet["input_message_count"] == 2
    assert packet["received_message_count"] == 1
    assert packet["dropped_count"] == 1
    assert packet["socket_open_requested"] is False
    assert packet["socket_opened"] is False
    assert packet["client_started"] is False
    assert packet["client_sends_messages"] is False
    assert packet["external_message_send_enabled"] is False
    assert packet["would_send_to_broker"] is False
    assert packet["visible_ui_decoration_added"] is False


def test_q32a_doc_modules_and_warroom_page_preserve_no_side_effect_boundary() -> None:
    text = DOC.read_text(encoding="utf-8-sig")
    assert "client_kind=ws_display_client_contract_no_socket_open" in text
    assert "ui_receiver_side=true" in text
    assert "socket_open_requested_default=false" in text
    assert "not_opening_socket=true" in text
    assert "not_using_polling_fallback=true" in text
    page = WARROOM_PAGE.read_text(encoding="utf-8-sig")
    assert "build_warroom_v2_ws_display_client_packet" not in page
    assert "WARROOM_V2_WS_DISPLAY_CLIENT_VERSION" not in page
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
