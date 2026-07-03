# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_operator_diagnostic_gate_q31p.py
# desc: PS-Q31P guards for visible read-only diagnostic gate from operator-review observation without rendering UI.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.apps.operator_ui.prediction_warroom.v2 import (  # noqa: E402
    WARROOM_V2_LOCAL_ONLY_APPROVAL_TOKEN,
    build_warroom_v2_market_snapshot_update_event,
    build_warroom_v2_operator_review_diagnostic_gate_contract,
    build_warroom_v2_operator_review_diagnostic_gate_packet,
    build_warroom_v2_operator_review_observation_packet,
    build_warroom_v2_outbound_message_payload,
)

REPO_ROOT = Path(__file__).resolve().parents[6]
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q31P_WARROOM_V2_OPERATOR_REVIEW_OBSERVATION_TO_VISIBLE_READ_ONLY_DIAGNOSTIC_GATE_2026-07-03.md"
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


def test_q31p_contract_is_gate_only_default_off_and_external_disabled() -> None:
    packet = build_warroom_v2_operator_review_diagnostic_gate_contract()
    assert packet["gate_kind"] == "warroom_v2_operator_review_diagnostic_gate_contract"
    assert packet["input_packet_kind"] == "warroom_v2_operator_review_observation_packet"
    assert packet["output_packet_kind"] == "warroom_v2_operator_review_diagnostic_gate_packet"
    assert packet["visible_diagnostic_default_enabled"] is False
    assert packet["visible_diagnostic_allowed_default"] is False
    assert packet["future_visible_diagnostic_read_only"] is True
    assert packet["gate_packet_only"] is True
    assert packet["gate_renders_ui"] is False
    assert packet["renderer_executes_patch"] is False
    assert packet["patch_execution_allowed"] is False
    assert packet["streamlit_render_allowed"] is False
    assert packet["warroom_page_ui_switch"] is False
    assert packet["websocket_enabled"] is False
    assert packet["sse_enabled"] is False
    assert packet["prediction_inference_invoked"] is False


def test_q31p_default_request_false_maps_to_hidden_default() -> None:
    observation = build_warroom_v2_operator_review_observation_packet(fragment_summary={"fragment_widget_count": 9})
    gate = build_warroom_v2_operator_review_diagnostic_gate_packet(observation)
    assert gate["diagnostic_gate_status"] == "diagnostic_gate_hidden_default"
    assert gate["visible_diagnostic_requested"] is False
    assert gate["visible_diagnostic_allowed"] is False
    assert gate["gate_row_count"] == 0
    assert gate["gate_renders_ui"] is False
    assert gate["visible_ui_decoration_added"] is False


def test_q31p_request_without_ack_blocks_visible_read_only_diagnostic() -> None:
    observation = build_warroom_v2_operator_review_observation_packet(fragment_summary={"fragment_widget_count": 9})
    gate = build_warroom_v2_operator_review_diagnostic_gate_packet(observation, visible_diagnostic_requested=True, operator_read_only_ack=False)
    assert gate["diagnostic_gate_status"] == "diagnostic_gate_blocked_read_only_ack_required"
    assert gate["visible_diagnostic_requested"] is True
    assert gate["operator_read_only_ack"] is False
    assert gate["visible_diagnostic_allowed"] is False
    assert gate["gate_row_count"] == 0
    assert gate["external_message_send_enabled"] is False


def test_q31p_request_with_ack_allows_future_read_only_diagnostic_but_renders_nothing_here() -> None:
    observation = build_warroom_v2_operator_review_observation_packet(
        evidence=_evidence(),
        operator_approval_token=WARROOM_V2_LOCAL_ONLY_APPROVAL_TOKEN,
        messages=[_message(2, 2)],
    )
    gate = build_warroom_v2_operator_review_diagnostic_gate_packet(observation, visible_diagnostic_requested=True, operator_read_only_ack=True)
    assert gate["diagnostic_gate_status"] == "diagnostic_gate_ready_visible_read_only_no_render_here"
    assert gate["visible_diagnostic_allowed"] is True
    assert gate["operator_review_status"] == "operator_review_ready_shadow_candidates"
    assert gate["review_row_count"] == 1
    assert gate["gate_row_count"] == 1
    row = gate["gate_rows"][0]
    assert row["gate_row_action"] == "diagnostic_inspect_read_only"
    assert row["read_only"] is True
    assert row["row_executes_patch"] is False
    assert row["row_renders_ui"] is False
    assert gate["gate_renders_ui"] is False
    assert gate["patch_execution_allowed"] is False
    assert gate["streamlit_render_allowed"] is False


def test_q31p_doc_modules_and_warroom_page_preserve_no_side_effect_boundary() -> None:
    text = DOC.read_text(encoding="utf-8-sig")
    assert "diagnostic_gate_module=" in text
    assert "visible_diagnostic_default_enabled=false" in text
    assert "gate_renders_ui=false" in text
    assert "not_rendering_visible_diagnostic=true" in text
    assert "not_invoking_prediction_inference=true" in text
    page = WARROOM_PAGE.read_text(encoding="utf-8-sig")
    assert "operator_diagnostic_gate" not in page
    assert "WARROOM_V2_OPERATOR_DIAGNOSTIC_GATE_VERSION" not in page
    forbidden = (
        "import streamlit",
        "from streamlit",
        "websocket.",
        "sse.",
        "send_to_broker(",
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
