# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_local_loop_readiness_q31j.py
# desc: PS-Q31J guards for display-update readiness read-model from local-loop observation.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.apps.operator_ui.prediction_warroom.v2 import (  # noqa: E402
    WARROOM_V2_LOCAL_ONLY_APPROVAL_TOKEN,
    build_warroom_v2_display_update_readiness_contract,
    build_warroom_v2_display_update_readiness_packet,
    build_warroom_v2_market_snapshot_update_event,
    build_warroom_v2_outbound_message_payload,
    build_warroom_v2_streamlit_local_loop_observation_packet,
)

REPO_ROOT = Path(__file__).resolve().parents[6]
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q31J_WARROOM_V2_LOCAL_LOOP_OBSERVATION_PACKET_TO_DISPLAY_UPDATE_READINESS_2026-07-03.md"
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


def test_q31j_contract_is_readiness_only_and_external_transport_disabled() -> None:
    packet = build_warroom_v2_display_update_readiness_contract()
    assert packet["readiness_kind"] == "warroom_v2_display_update_readiness_read_model"
    assert packet["input_packet_kind"] == "warroom_v2_streamlit_local_loop_observation_packet"
    assert packet["patch_unit"] == "widget_dom_region"
    assert packet["broad_page_reload_required"] is False
    assert packet["whole_warroom_display_update_target"] is True
    assert packet["prediction_cards_display_update_target"] is True
    assert packet["visible_ui_decoration_added"] is False
    assert packet["external_message_send_enabled"] is False
    assert packet["websocket_enabled"] is False
    assert packet["sse_enabled"] is False
    assert packet["prediction_generation_invoked"] is False
    assert packet["prediction_inference_invoked"] is False


def test_q31j_empty_streamlit_observation_maps_to_shadow_ready_no_display_events() -> None:
    observation = build_warroom_v2_streamlit_local_loop_observation_packet(fragment_summary={"fragment_widget_count": 9})
    readiness = build_warroom_v2_display_update_readiness_packet(observation)
    assert readiness["readiness_status"] == "shadow_ready_no_display_events"
    assert readiness["display_update_events_ready"] is False
    assert readiness["local_loop_ready"] is True
    assert readiness["observed_message_count"] == 0
    assert readiness["emitted_message_count"] == 0
    assert readiness["surface_summary"]["top_information"]["observed_message_count"] == 0
    assert readiness["external_message_send_enabled"] is False


def test_q31j_non_empty_local_loop_outbox_maps_to_widget_dom_region_ready() -> None:
    observation = build_warroom_v2_streamlit_local_loop_observation_packet(evidence=_evidence(), operator_approval_token=WARROOM_V2_LOCAL_ONLY_APPROVAL_TOKEN, messages=[_message(2, 2)])
    readiness = build_warroom_v2_display_update_readiness_packet(observation)
    assert readiness["readiness_status"] == "display_events_ready_for_widget_dom_region"
    assert readiness["display_update_events_ready"] is True
    assert readiness["observed_message_count"] == 1
    assert readiness["emitted_message_count"] == 1
    assert readiness["observed_topics"] == ["warroom.market.snapshot"]
    assert readiness["surface_summary"]["top_information"]["observed_message_count"] == 1
    assert readiness["patch_unit"] == "widget_dom_region"
    assert readiness["websocket_enabled"] is False
    assert readiness["sse_enabled"] is False


def test_q31j_blocked_observation_maps_to_blocked_readiness() -> None:
    observation = build_warroom_v2_streamlit_local_loop_observation_packet(evidence=_evidence(), operator_approval_token="", messages=[_message(3, 3)])
    readiness = build_warroom_v2_display_update_readiness_packet(observation)
    assert readiness["readiness_status"] == "blocked_local_loop_not_ready"
    assert readiness["display_update_events_ready"] is False
    assert readiness["local_loop_ready"] is False
    assert readiness["observed_message_count"] == 0
    assert readiness["emitted_message_count"] == 0
    assert readiness["runtime_connected"] is False
    assert readiness["would_send_to_broker"] is False


def test_q31j_doc_and_transport_modules_preserve_no_side_effect_boundary() -> None:
    text = DOC.read_text(encoding="utf-8-sig")
    assert "readiness_module=" in text
    assert "output_read_model=warroom_v2_display_update_readiness_packet" in text
    assert "external_message_send_enabled=false" in text
    assert "not_enabling_websocket=true" in text
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
