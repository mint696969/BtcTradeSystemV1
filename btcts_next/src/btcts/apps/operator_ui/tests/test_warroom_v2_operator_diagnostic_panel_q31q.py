# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_operator_diagnostic_panel_q31q.py
# desc: PS-Q31Q guards for disabled-by-default read-only diagnostic panel adapter without rendering UI.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.apps.operator_ui.prediction_warroom.v2 import (  # noqa: E402
    WARROOM_V2_LOCAL_ONLY_APPROVAL_TOKEN,
    build_warroom_v2_market_snapshot_update_event,
    build_warroom_v2_operator_review_diagnostic_gate_packet,
    build_warroom_v2_operator_review_diagnostic_panel_contract,
    build_warroom_v2_operator_review_diagnostic_panel_packet,
    build_warroom_v2_operator_review_observation_packet,
    build_warroom_v2_outbound_message_payload,
)

REPO_ROOT = Path(__file__).resolve().parents[6]
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q31Q_WARROOM_V2_OPERATOR_DIAGNOSTIC_GATE_TO_VISIBLE_READ_ONLY_PANEL_EXPLICITLY_DISABLED_BY_DEFAULT_2026-07-03.md"
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


def test_q31q_contract_is_panel_adapter_only_disabled_by_default() -> None:
    packet = build_warroom_v2_operator_review_diagnostic_panel_contract()
    assert packet["panel_kind"] == "warroom_v2_operator_review_diagnostic_panel_adapter_contract"
    assert packet["input_packet_kind"] == "warroom_v2_operator_review_diagnostic_gate_packet"
    assert packet["output_packet_kind"] == "warroom_v2_operator_review_diagnostic_panel_adapter_packet"
    assert packet["visible_panel_default_enabled"] is False
    assert packet["panel_allowed_default"] is False
    assert packet["panel_adapter_only"] is True
    assert packet["panel_mounts_into_warroom"] is False
    assert packet["panel_renders_ui"] is False
    assert packet["panel_visible_now"] is False
    assert packet["panel_read_only"] is True
    assert packet["patch_execution_allowed"] is False
    assert packet["streamlit_render_allowed"] is False
    assert packet["websocket_enabled"] is False
    assert packet["sse_enabled"] is False


def test_q31q_hidden_default_gate_maps_to_disabled_panel_packet() -> None:
    observation = build_warroom_v2_operator_review_observation_packet(fragment_summary={"fragment_widget_count": 9})
    gate = build_warroom_v2_operator_review_diagnostic_gate_packet(observation)
    panel = build_warroom_v2_operator_review_diagnostic_panel_packet(gate)
    assert panel["diagnostic_panel_status"] == "diagnostic_panel_disabled_hidden_default"
    assert panel["panel_row_count"] == 0
    assert panel["panel_adapter_only"] is True
    assert panel["panel_renders_ui"] is False
    assert panel["panel_visible_now"] is False
    assert panel["visible_ui_decoration_added"] is False


def test_q31q_blocked_gate_maps_to_blocked_panel_packet() -> None:
    observation = build_warroom_v2_operator_review_observation_packet(fragment_summary={"fragment_widget_count": 9})
    gate = build_warroom_v2_operator_review_diagnostic_gate_packet(observation, visible_diagnostic_requested=True, operator_read_only_ack=False)
    panel = build_warroom_v2_operator_review_diagnostic_panel_packet(gate)
    assert panel["diagnostic_panel_status"] == "diagnostic_panel_blocked_read_only_ack_required"
    assert panel["panel_row_count"] == 0
    assert panel["panel_mounts_into_warroom"] is False
    assert panel["panel_renders_ui"] is False
    assert panel["external_message_send_enabled"] is False


def test_q31q_ready_gate_creates_read_only_panel_rows_but_still_renders_nothing() -> None:
    observation = build_warroom_v2_operator_review_observation_packet(
        evidence=_evidence(),
        operator_approval_token=WARROOM_V2_LOCAL_ONLY_APPROVAL_TOKEN,
        messages=[_message(2, 2)],
    )
    gate = build_warroom_v2_operator_review_diagnostic_gate_packet(observation, visible_diagnostic_requested=True, operator_read_only_ack=True)
    panel = build_warroom_v2_operator_review_diagnostic_panel_packet(gate)
    assert panel["diagnostic_panel_status"] == "diagnostic_panel_ready_read_only_disabled_by_default"
    assert panel["panel_row_count"] == 1
    row = panel["panel_rows"][0]
    assert row["panel_row_action"] == "present_read_only_diagnostic_row"
    assert row["panel_row_read_only"] is True
    assert row["panel_row_renders_ui"] is False
    assert row["panel_row_executes_patch"] is False
    assert panel["panel_renders_ui"] is False
    assert panel["panel_mounts_into_warroom"] is False
    assert panel["panel_visible_now"] is False
    assert panel["patch_execution_allowed"] is False
    assert panel["streamlit_render_allowed"] is False


def test_q31q_doc_modules_and_warroom_page_preserve_no_side_effect_boundary() -> None:
    text = DOC.read_text(encoding="utf-8-sig")
    assert "panel_adapter_module=" in text
    assert "visible_panel_default_enabled=false" in text
    assert "panel_mounts_into_warroom=false" in text
    assert "panel_renders_ui=false" in text
    assert "not_mounting_panel_into_warroom=true" in text
    assert "not_invoking_prediction_inference=true" in text
    page = WARROOM_PAGE.read_text(encoding="utf-8-sig")
    assert "operator_diagnostic_panel" not in page
    assert "WARROOM_V2_OPERATOR_DIAGNOSTIC_PANEL_VERSION" not in page
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
