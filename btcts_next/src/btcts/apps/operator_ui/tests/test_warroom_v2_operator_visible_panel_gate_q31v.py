# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_operator_visible_panel_gate_q31v.py
# desc: PS-Q31V guards for default-off read-only visible panel gate. No UI mount and no socket.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.apps.operator_ui.prediction_warroom.v2 import (  # noqa: E402
    WARROOM_V2_LOCAL_ONLY_APPROVAL_TOKEN,
    build_warroom_v2_market_snapshot_update_event,
    build_warroom_v2_operator_visible_panel_gate_contract,
    build_warroom_v2_operator_visible_panel_gate_packet,
    build_warroom_v2_operator_visible_panel_observation_packet,
    build_warroom_v2_outbound_message_payload,
)

REPO_ROOT = Path(__file__).resolve().parents[6]
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q31V_WARROOM_V2_OPERATOR_VISIBLE_PANEL_OBSERVATION_TO_READ_ONLY_VISIBLE_PANEL_GATE_DEFAULT_OFF_2026-07-03.md"
WARROOM_PAGE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py"
TRANSPORT_DIR = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport"


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


def test_q31v_contract_is_default_off_read_only_gate_and_external_disabled() -> None:
    packet = build_warroom_v2_operator_visible_panel_gate_contract()
    assert packet["gate_kind"] == "warroom_v2_operator_visible_panel_gate_contract"
    assert packet["websocket_first_future_transport"] is True
    assert packet["no_polling_fallback_introduced"] is True
    assert packet["visible_panel_gate_default_enabled"] is False
    assert packet["visible_panel_gate_allowed_default"] is False
    assert packet["gate_packet_only"] is True
    assert packet["gate_mounts_into_warroom"] is False
    assert packet["gate_renders_ui"] is False
    assert packet["websocket_enabled"] is False
    assert packet["order_intent_submitted"] is False
    assert packet["would_send_to_broker"] is False


def test_q31v_default_request_false_maps_to_hidden_default() -> None:
    observation = build_warroom_v2_operator_visible_panel_observation_packet(fragment_summary={"fragment_widget_count": 9})
    gate = build_warroom_v2_operator_visible_panel_gate_packet(observation)
    assert gate["visible_panel_gate_status"] == "visible_panel_gate_hidden_default"
    assert gate["visible_panel_gate_requested"] is False
    assert gate["visible_panel_gate_allowed"] is False
    assert gate["gate_row_count"] == 0
    assert gate["gate_mounts_into_warroom"] is False
    assert gate["gate_renders_ui"] is False
    assert gate["websocket_enabled"] is False


def test_q31v_request_without_ack_blocks_gate() -> None:
    observation = build_warroom_v2_operator_visible_panel_observation_packet(fragment_summary={"fragment_widget_count": 9})
    gate = build_warroom_v2_operator_visible_panel_gate_packet(
        observation,
        visible_panel_gate_requested=True,
        operator_read_only_ack=False,
    )
    assert gate["visible_panel_gate_status"] == "visible_panel_gate_blocked_read_only_ack_required"
    assert gate["visible_panel_gate_requested"] is True
    assert gate["operator_read_only_ack"] is False
    assert gate["visible_panel_gate_allowed"] is False
    assert gate["order_intent_submitted"] is False
    assert gate["would_send_to_broker"] is False


def test_q31v_ack_with_non_allowed_plan_blocks_gate() -> None:
    observation = build_warroom_v2_operator_visible_panel_observation_packet(fragment_summary={"fragment_widget_count": 9})
    gate = build_warroom_v2_operator_visible_panel_gate_packet(
        observation,
        visible_panel_gate_requested=True,
        operator_read_only_ack=True,
    )
    assert gate["visible_panel_gate_status"] == "visible_panel_gate_blocked_plan_not_allowed"
    assert gate["source_operator_visible_panel_allowed"] is False
    assert gate["visible_panel_gate_allowed"] is False
    assert gate["gate_row_count"] == 0
    assert gate["gate_mounts_into_warroom"] is False


def test_q31v_allowed_plan_creates_read_only_gate_rows_but_mounts_nothing() -> None:
    observation = build_warroom_v2_operator_visible_panel_observation_packet(
        evidence=_evidence(),
        operator_approval_token=WARROOM_V2_LOCAL_ONLY_APPROVAL_TOKEN,
        visible_diagnostic_requested=True,
        diagnostic_read_only_ack=True,
        operator_visible_panel_requested=True,
        operator_read_only_ack=True,
        messages=[_message(2, 2)],
    )
    gate = build_warroom_v2_operator_visible_panel_gate_packet(
        observation,
        visible_panel_gate_requested=True,
        operator_read_only_ack=True,
    )
    assert gate["visible_panel_gate_status"] == "visible_panel_gate_ready_read_only_no_mount"
    assert gate["visible_panel_gate_allowed"] is True
    assert gate["gate_row_count"] == 1
    row = gate["gate_rows"][0]
    assert row["gate_row_action"] == "allow_read_only_panel_gate_no_mount"
    assert row["gate_row_read_only"] is True
    assert row["gate_row_mounts_ui"] is False
    assert row["gate_row_renders_ui"] is False
    assert row["gate_row_executes_patch"] is False
    assert gate["gate_mounts_into_warroom"] is False
    assert gate["gate_renders_ui"] is False
    assert gate["external_message_send_enabled"] is False
    assert gate["order_intent_submitted"] is False


def test_q31v_doc_modules_and_warroom_page_preserve_no_side_effect_boundary() -> None:
    text = DOC.read_text(encoding="utf-8-sig")
    assert "visible_panel_gate_default_enabled=false" in text
    assert "websocket_first_future_transport=true" in text
    assert "not_using_polling_fallback=true" in text
    assert "not_mounting_panel_into_warroom=true" in text
    page = WARROOM_PAGE.read_text(encoding="utf-8-sig")
    assert "operator_visible_panel_gate" not in page
    assert "WARROOM_V2_OPERATOR_VISIBLE_PANEL_GATE_VERSION" not in page
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
