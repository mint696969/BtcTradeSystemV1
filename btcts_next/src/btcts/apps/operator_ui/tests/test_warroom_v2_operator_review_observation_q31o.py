# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_operator_review_observation_q31o.py
# desc: PS-Q31O guards for hidden session_state operator-review observation without visible UI.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.apps.operator_ui.prediction_warroom.v2 import (  # noqa: E402
    WARROOM_V2_LOCAL_ONLY_APPROVAL_TOKEN,
    WARROOM_V2_OPERATOR_REVIEW_OBSERVATION_STATE_KEY,
    build_warroom_v2_market_snapshot_update_event,
    build_warroom_v2_operator_review_observation_contract,
    build_warroom_v2_operator_review_observation_packet,
    build_warroom_v2_outbound_message_payload,
)

REPO_ROOT = Path(__file__).resolve().parents[6]
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q31O_WARROOM_V2_OPERATOR_REVIEW_PACKET_TO_HIDDEN_SESSION_STATE_NO_VISIBLE_UI_2026-07-03.md"
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


def test_q31o_contract_is_hidden_operator_review_observation_and_external_disabled() -> None:
    packet = build_warroom_v2_operator_review_observation_contract()
    assert packet["state_key"] == WARROOM_V2_OPERATOR_REVIEW_OBSERVATION_STATE_KEY
    assert packet["observation_kind"] == "warroom_v2_hidden_operator_review_observation_packet"
    assert packet["input_pipeline"] == ["q31m_shadow_renderer_observation", "q31n_operator_review_packet"]
    assert packet["review_packet_only"] is True
    assert packet["review_renders_ui"] is False
    assert packet["renderer_executes_patch"] is False
    assert packet["patch_execution_allowed"] is False
    assert packet["streamlit_render_allowed"] is False
    assert packet["warroom_page_ui_switch"] is False
    assert packet["whole_warroom_display_update_target"] is True
    assert packet["prediction_cards_display_update_target"] is True
    assert packet["external_message_send_enabled"] is False
    assert packet["websocket_enabled"] is False
    assert packet["sse_enabled"] is False
    assert packet["prediction_inference_invoked"] is False


def test_q31o_default_streamlit_path_records_idle_operator_review_with_zero_rows() -> None:
    packet = build_warroom_v2_operator_review_observation_packet(fragment_summary={"fragment_widget_count": 9})
    assert packet["state_key"] == WARROOM_V2_OPERATOR_REVIEW_OBSERVATION_STATE_KEY
    assert packet["default_streamlit_message_count"] == 0
    assert packet["operator_review_status"] == "operator_review_idle_shadow_no_candidates"
    assert packet["review_row_count"] == 0
    assert packet["operator_review_packet"]["review_row_count"] == 0
    assert packet["review_packet_only"] is True
    assert packet["review_renders_ui"] is False
    assert packet["patch_execution_allowed"] is False
    assert packet["streamlit_render_allowed"] is False
    assert packet["warroom_page_ui_switch"] is False


def test_q31o_non_empty_messages_still_review_only_and_do_not_execute_patch() -> None:
    packet = build_warroom_v2_operator_review_observation_packet(
        evidence=_evidence(),
        operator_approval_token=WARROOM_V2_LOCAL_ONLY_APPROVAL_TOKEN,
        messages=[_message(2, 2)],
    )
    assert packet["operator_review_status"] == "operator_review_ready_shadow_candidates"
    assert packet["review_row_count"] == 1
    review = packet["operator_review_packet"]
    assert review["observed_topics"] == ["warroom.market.snapshot"]
    assert review["review_rows"][0]["review_row_executes_patch"] is False
    assert review["review_rows"][0]["review_row_renders_ui"] is False
    assert packet["renderer_executes_patch"] is False
    assert packet["patch_execution_allowed"] is False
    assert packet["streamlit_render_allowed"] is False
    assert packet["external_message_send_enabled"] is False
    assert packet["websocket_enabled"] is False
    assert packet["sse_enabled"] is False


def test_q31o_warroom_page_records_hidden_operator_review_observation_state_only() -> None:
    text = WARROOM_PAGE.read_text(encoding="utf-8-sig")
    assert "WARROOM_V2_OPERATOR_REVIEW_OBSERVATION_STATE_KEY" in text
    assert "warroom_v2_operator_review_observation_q31o" in text
    assert "build_warroom_v2_operator_review_observation_packet" in text
    assert "st.session_state[WARROOM_V2_OPERATOR_REVIEW_OBSERVATION_STATE_KEY]" in text
    forbidden_visible_labels = (
        "WarRoom v2 operator review observation",
        "Operator review observation",
        "Run operator review observation",
    )
    for label in forbidden_visible_labels:
        assert label not in text


def test_q31o_doc_and_transport_modules_preserve_no_side_effect_boundary() -> None:
    text = DOC.read_text(encoding="utf-8-sig")
    assert "warroom_page_observation_state_key=warroom_v2_operator_review_observation_q31o" in text
    assert "streamlit_path_messages=[]" in text
    assert "streamlit_path_review_row_count=0" in text
    assert "review_renders_ui=false" in text
    assert "not_rendering_streamlit=true" in text
    assert "not_invoking_prediction_inference=true" in text
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
