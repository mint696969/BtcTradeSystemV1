# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_operator_visible_panel_plan_q31t.py
# desc: PS-Q31T guards for default-off operator-visible panel plan with WebSocket-first premise. No UI mount and no socket.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.apps.operator_ui.prediction_warroom.v2 import (  # noqa: E402
    WARROOM_V2_LOCAL_ONLY_APPROVAL_TOKEN,
    build_warroom_v2_bidirectional_order_boundary_contract,
    build_warroom_v2_market_snapshot_update_event,
    build_warroom_v2_operator_diagnostic_observation_packet,
    build_warroom_v2_operator_visible_panel_plan_contract,
    build_warroom_v2_operator_visible_panel_plan_packet,
    build_warroom_v2_outbound_message_payload,
)

REPO_ROOT = Path(__file__).resolve().parents[6]
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q31T_WARROOM_V2_HIDDEN_DIAGNOSTIC_OBSERVATION_TO_OPERATOR_VISIBLE_PANEL_PLAN_DEFAULT_OFF_2026-07-03.md"
TRANSPORT_DIR = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport"
WARROOM_PAGE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py"


def _evidence() -> dict[str, str]:
    return {
        "q31f_focused_guard": "6_passed",
        "q31f_close_guard": "68_passed",
        "q31f_py_compile": "passed",
        "q31e_focused_guard": "5_passed",
        "q31d_focused_guard": "7_passed",
        "q31c_focused_guard": "7_passed",
        "q31b_focused_guard": "7_passed",
        "q31a_focused_guard": "8_passed",
    }


def _message(sequence: int = 1, ltp: int = 1) -> dict[str, object]:
    event = build_warroom_v2_market_snapshot_update_event(snapshot_payload={"ltp": ltp}, sequence=sequence)
    message = build_warroom_v2_outbound_message_payload(event_packet=event)
    message["current_fingerprint"] = event["current_fingerprint"]
    return message


def test_q31t_contract_preserves_websocket_first_default_off_plan() -> None:
    packet = build_warroom_v2_operator_visible_panel_plan_contract()
    assert packet["plan_kind"] == "warroom_v2_operator_visible_panel_plan_contract"
    assert packet["websocket_first_future_transport"] is True
    assert packet["bidirectional_websocket_premise"] is True
    assert packet["no_polling_fallback_introduced"] is True
    assert packet["no_browser_timer_reload_introduced"] is True
    assert packet["operator_visible_panel_default_enabled"] is False
    assert packet["operator_visible_panel_allowed_default"] is False
    assert packet["plan_packet_only"] is True
    assert packet["plan_mounts_into_warroom"] is False
    assert packet["plan_renders_ui"] is False
    assert packet["websocket_enabled"] is False
    assert packet["order_intent_submitted"] is False


def test_q31t_default_request_false_maps_to_hidden_default_without_alternative_refresh() -> None:
    observation = build_warroom_v2_operator_diagnostic_observation_packet(fragment_summary={"fragment_widget_count": 9})
    plan = build_warroom_v2_operator_visible_panel_plan_packet(observation)
    assert plan["operator_visible_panel_plan_status"] == "operator_visible_panel_plan_hidden_default"
    assert plan["operator_visible_panel_requested"] is False
    assert plan["operator_visible_panel_allowed"] is False
    assert plan["plan_row_count"] == 0
    assert plan["websocket_first_future_transport"] is True
    assert plan["no_polling_fallback_introduced"] is True
    assert plan["no_browser_timer_reload_introduced"] is True
    assert plan["plan_renders_ui"] is False
    assert plan["plan_visible_now"] is False


def test_q31t_request_without_ack_blocks_panel_plan() -> None:
    observation = build_warroom_v2_operator_diagnostic_observation_packet(fragment_summary={"fragment_widget_count": 9})
    plan = build_warroom_v2_operator_visible_panel_plan_packet(observation, operator_visible_panel_requested=True, operator_read_only_ack=False)
    assert plan["operator_visible_panel_plan_status"] == "operator_visible_panel_plan_blocked_read_only_ack_required"
    assert plan["operator_visible_panel_requested"] is True
    assert plan["operator_read_only_ack"] is False
    assert plan["operator_visible_panel_allowed"] is False
    assert plan["plan_row_count"] == 0
    assert plan["order_intent_submitted"] is False
    assert plan["would_send_to_broker"] is False


def test_q31t_ack_with_non_ready_diagnostic_blocks_panel_plan() -> None:
    observation = build_warroom_v2_operator_diagnostic_observation_packet(fragment_summary={"fragment_widget_count": 9})
    plan = build_warroom_v2_operator_visible_panel_plan_packet(observation, operator_visible_panel_requested=True, operator_read_only_ack=True)
    assert plan["operator_visible_panel_plan_status"] == "operator_visible_panel_plan_blocked_diagnostic_not_ready"
    assert plan["diagnostic_ready"] is False
    assert plan["operator_visible_panel_allowed"] is False
    assert plan["plan_mounts_into_warroom"] is False
    assert plan["websocket_enabled"] is False


def test_q31t_ready_diagnostic_creates_plan_rows_but_mounts_and_renders_nothing() -> None:
    observation = build_warroom_v2_operator_diagnostic_observation_packet(
        evidence=_evidence(),
        operator_approval_token=WARROOM_V2_LOCAL_ONLY_APPROVAL_TOKEN,
        visible_diagnostic_requested=True,
        operator_read_only_ack=True,
        messages=[_message(2, 2)],
    )
    boundary = build_warroom_v2_bidirectional_order_boundary_contract()
    plan = build_warroom_v2_operator_visible_panel_plan_packet(
        observation,
        boundary,
        operator_visible_panel_requested=True,
        operator_read_only_ack=True,
    )
    assert plan["operator_visible_panel_plan_status"] == "operator_visible_panel_plan_ready_default_off_no_mount"
    assert plan["operator_visible_panel_allowed"] is True
    assert plan["diagnostic_ready"] is True
    assert plan["plan_row_count"] == 1
    row = plan["plan_rows"][0]
    assert row["plan_row_action"] == "prepare_read_only_panel_mount_plan"
    assert row["websocket_first_future_transport"] is True
    assert row["plan_row_mounts_ui"] is False
    assert row["plan_row_renders_ui"] is False
    assert row["plan_row_executes_patch"] is False
    assert row["order_intent_submitted"] is False
    assert plan["plan_mounts_into_warroom"] is False
    assert plan["plan_renders_ui"] is False
    assert plan["websocket_enabled"] is False


def test_q31t_doc_modules_and_warroom_page_preserve_no_side_effect_boundary() -> None:
    text = DOC.read_text(encoding="utf-8-sig")
    assert "websocket_first_future_transport=true" in text
    assert "bidirectional_websocket_premise=true" in text
    assert "no_polling_fallback_introduced=true" in text
    assert "no_browser_timer_reload_introduced=true" in text
    assert "not_using_polling_fallback=true" in text
    assert "not_using_browser_timer_reload=true" in text
    page = WARROOM_PAGE.read_text(encoding="utf-8-sig")
    assert "operator_visible_panel_plan" not in page
    assert "WARROOM_V2_OPERATOR_VISIBLE_PANEL_PLAN_VERSION" not in page
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
