# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_operator_review_packet_q31n.py
# desc: PS-Q31N guards for operator-review packet from hidden shadow renderer observation without UI switch.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.apps.operator_ui.prediction_warroom.v2 import (  # noqa: E402
    WARROOM_V2_LOCAL_ONLY_APPROVAL_TOKEN,
    build_warroom_v2_market_snapshot_update_event,
    build_warroom_v2_operator_shadow_renderer_review_contract,
    build_warroom_v2_operator_shadow_renderer_review_packet,
    build_warroom_v2_outbound_message_payload,
    build_warroom_v2_shadow_renderer_observation_packet,
)

REPO_ROOT = Path(__file__).resolve().parents[6]
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q31N_WARROOM_V2_SHADOW_RENDERER_OBSERVATION_TO_OPERATOR_REVIEW_PACKET_NO_UI_SWITCH_2026-07-03.md"
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


def test_q31n_contract_is_review_packet_only_and_external_transport_disabled() -> None:
    packet = build_warroom_v2_operator_shadow_renderer_review_contract()
    assert packet["review_kind"] == "warroom_v2_operator_shadow_renderer_review_contract"
    assert packet["input_packet_kind"] == "warroom_v2_shadow_renderer_observation_packet"
    assert packet["output_packet_kind"] == "warroom_v2_operator_shadow_renderer_review_packet"
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


def test_q31n_idle_observation_maps_to_idle_operator_review() -> None:
    observation = build_warroom_v2_shadow_renderer_observation_packet(fragment_summary={"fragment_widget_count": 9})
    review = build_warroom_v2_operator_shadow_renderer_review_packet(observation)
    assert review["operator_review_status"] == "operator_review_idle_shadow_no_candidates"
    assert review["review_row_count"] == 0
    assert review["review_packet_only"] is True
    assert review["review_renders_ui"] is False
    assert review["patch_execution_allowed"] is False
    assert review["warroom_page_ui_switch"] is False


def test_q31n_ready_observation_maps_to_review_rows_without_patch_execution() -> None:
    observation = build_warroom_v2_shadow_renderer_observation_packet(evidence=_evidence(), operator_approval_token=WARROOM_V2_LOCAL_ONLY_APPROVAL_TOKEN, messages=[_message(2, 2)])
    review = build_warroom_v2_operator_shadow_renderer_review_packet(observation)
    assert review["operator_review_status"] == "operator_review_ready_shadow_candidates"
    assert review["review_row_count"] == 1
    assert review["observed_topics"] == ["warroom.market.snapshot"]
    assert review["surfaces"] == ["top_information"]
    row = review["review_rows"][0]
    assert row["review_row_action"] == "inspect_shadow_candidate"
    assert row["source_candidate_action"] == "shadow_prepare_widget_dom_region_patch"
    assert row["patch_unit"] == "widget_dom_region"
    assert row["review_row_executes_patch"] is False
    assert row["review_row_renders_ui"] is False
    assert review["renderer_executes_patch"] is False
    assert review["streamlit_render_allowed"] is False
    assert review["external_message_send_enabled"] is False


def test_q31n_blocked_adapter_maps_to_blocked_operator_review() -> None:
    observation = build_warroom_v2_shadow_renderer_observation_packet(evidence=_evidence(), operator_approval_token="", messages=[_message(3, 3)])
    review = build_warroom_v2_operator_shadow_renderer_review_packet(observation)
    assert review["operator_review_status"] == "operator_review_blocked_shadow_renderer"
    assert review["review_row_count"] == 0
    assert review["websocket_enabled"] is False
    assert review["sse_enabled"] is False
    assert review["would_send_to_broker"] is False


def test_q31n_doc_and_transport_modules_preserve_no_side_effect_boundary() -> None:
    text = DOC.read_text(encoding="utf-8-sig")
    assert "operator_review_module=" in text
    assert "output_review_packet=warroom_v2_operator_shadow_renderer_review_packet" in text
    assert "review_packet_only=true" in text
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
