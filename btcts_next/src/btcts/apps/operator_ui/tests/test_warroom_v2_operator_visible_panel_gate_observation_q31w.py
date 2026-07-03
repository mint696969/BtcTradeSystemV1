# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_operator_visible_panel_gate_observation_q31w.py
# desc: PS-Q31W guards for hidden session_state visible panel gate observation. No UI mount and no socket.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.apps.operator_ui.prediction_warroom.v2 import (  # noqa: E402
    WARROOM_V2_LOCAL_ONLY_APPROVAL_TOKEN,
    WARROOM_V2_OPERATOR_VISIBLE_PANEL_GATE_OBSERVATION_STATE_KEY,
    build_warroom_v2_market_snapshot_update_event,
    build_warroom_v2_operator_visible_panel_gate_observation_contract,
    build_warroom_v2_operator_visible_panel_gate_observation_packet,
    build_warroom_v2_outbound_message_payload,
)

REPO_ROOT = Path(__file__).resolve().parents[6]
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q31W_WARROOM_V2_VISIBLE_PANEL_GATE_TO_HIDDEN_SESSION_STATE_NO_UI_MOUNT_2026-07-03.md"
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


def test_q31w_contract_is_hidden_state_and_ws_first_without_alternative_refresh() -> None:
    packet = build_warroom_v2_operator_visible_panel_gate_observation_contract()
    assert packet["state_key"] == WARROOM_V2_OPERATOR_VISIBLE_PANEL_GATE_OBSERVATION_STATE_KEY
    assert packet["observation_kind"] == "warroom_v2_hidden_operator_visible_panel_gate_observation_packet"
    assert packet["input_pipeline"] == ["q31u_operator_visible_panel_observation", "q31v_operator_visible_panel_gate"]
    assert packet["websocket_first_future_transport"] is True
    assert packet["no_polling_fallback_introduced"] is True
    assert packet["no_browser_timer_reload_introduced"] is True
    assert packet["visible_panel_gate_allowed_default"] is False
    assert packet["gate_mounts_into_warroom"] is False
    assert packet["gate_renders_ui"] is False
    assert packet["websocket_enabled"] is False
    assert packet["order_intent_submitted"] is False


def test_q31w_default_streamlit_path_records_hidden_gate_only() -> None:
    packet = build_warroom_v2_operator_visible_panel_gate_observation_packet(fragment_summary={"fragment_widget_count": 9})
    assert packet["state_key"] == WARROOM_V2_OPERATOR_VISIBLE_PANEL_GATE_OBSERVATION_STATE_KEY
    assert packet["default_streamlit_message_count"] == 0
    assert packet["visible_panel_gate_requested"] is False
    assert packet["visible_panel_gate_read_only_ack"] is False
    assert packet["visible_panel_gate_allowed"] is False
    assert packet["visible_panel_gate_status"] == "visible_panel_gate_hidden_default"
    assert packet["gate_row_count"] == 0
    assert packet["gate_mounts_into_warroom"] is False
    assert packet["gate_renders_ui"] is False
    assert packet["gate_visible_now"] is False
    assert packet["websocket_enabled"] is False


def test_q31w_ready_request_still_hidden_observation_and_mounts_nothing() -> None:
    packet = build_warroom_v2_operator_visible_panel_gate_observation_packet(
        evidence=_evidence(),
        operator_approval_token=WARROOM_V2_LOCAL_ONLY_APPROVAL_TOKEN,
        visible_diagnostic_requested=True,
        diagnostic_read_only_ack=True,
        operator_visible_panel_requested=True,
        operator_visible_panel_read_only_ack=True,
        visible_panel_gate_requested=True,
        visible_panel_gate_read_only_ack=True,
        messages=[_message(2, 2)],
    )
    assert packet["visible_panel_gate_status"] == "visible_panel_gate_ready_read_only_no_mount"
    assert packet["visible_panel_gate_allowed"] is True
    assert packet["gate_row_count"] == 1
    row = packet["operator_visible_panel_gate_packet"]["gate_rows"][0]
    assert row["gate_row_mounts_ui"] is False
    assert row["gate_row_renders_ui"] is False
    assert row["gate_row_executes_patch"] is False
    assert packet["gate_mounts_into_warroom"] is False
    assert packet["gate_renders_ui"] is False
    assert packet["external_message_send_enabled"] is False
    assert packet["order_intent_submitted"] is False
    assert packet["would_send_to_broker"] is False


def test_q31w_warroom_page_records_hidden_visible_panel_gate_observation_state_only() -> None:
    text = WARROOM_PAGE.read_text(encoding="utf-8-sig")
    assert "WARROOM_V2_OPERATOR_VISIBLE_PANEL_GATE_OBSERVATION_STATE_KEY" in text
    assert "warroom_v2_operator_visible_panel_gate_observation_q31w" in text
    assert "build_warroom_v2_operator_visible_panel_gate_observation_packet" in text
    assert "st.session_state[WARROOM_V2_OPERATOR_VISIBLE_PANEL_GATE_OBSERVATION_STATE_KEY]" in text
    forbidden_visible_labels = (
        "WarRoom v2 operator visible panel gate",
        "Operator visible panel gate",
        "Run operator visible panel gate",
        "Enable operator visible panel gate",
    )
    for label in forbidden_visible_labels:
        assert label not in text


def test_q31w_doc_and_transport_modules_preserve_no_side_effect_boundary() -> None:
    text = DOC.read_text(encoding="utf-8-sig")
    assert "state_key=warroom_v2_operator_visible_panel_gate_observation_q31w" in text
    assert "websocket_first_future_transport=true" in text
    assert "no_polling_fallback_introduced=true" in text
    assert "not_mounting_panel_into_warroom=true" in text
    assert "not_submitting_order_intent=true" in text
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
