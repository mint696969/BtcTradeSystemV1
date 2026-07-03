# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_renderer_plan_q31k.py
# desc: PS-Q31K guards for renderer plan contract from display-update readiness without UI switch.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.apps.operator_ui.prediction_warroom.v2 import (  # noqa: E402
    WARROOM_V2_LOCAL_ONLY_APPROVAL_TOKEN,
    build_warroom_v2_display_update_readiness_packet,
    build_warroom_v2_market_snapshot_update_event,
    build_warroom_v2_outbound_message_payload,
    build_warroom_v2_renderer_plan_contract,
    build_warroom_v2_renderer_plan_from_readiness,
    build_warroom_v2_streamlit_local_loop_observation_packet,
)

REPO_ROOT = Path(__file__).resolve().parents[6]
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q31K_WARROOM_V2_DISPLAY_UPDATE_READINESS_TO_RENDERER_PLAN_NO_UI_SWITCH_2026-07-03.md"
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


def _readiness_with_message() -> dict[str, object]:
    observation = build_warroom_v2_streamlit_local_loop_observation_packet(evidence=_evidence(), operator_approval_token=WARROOM_V2_LOCAL_ONLY_APPROVAL_TOKEN, messages=[_message(2, 2)])
    return build_warroom_v2_display_update_readiness_packet(observation)


def test_q31k_contract_is_renderer_plan_only_and_external_transport_disabled() -> None:
    packet = build_warroom_v2_renderer_plan_contract()
    assert packet["plan_kind"] == "warroom_v2_display_update_renderer_plan_contract"
    assert packet["input_packet_kind"] == "warroom_v2_display_update_readiness_packet"
    assert packet["patch_unit"] == "widget_dom_region"
    assert packet["renderer_executes_patch"] is False
    assert packet["warroom_page_ui_switch"] is False
    assert packet["broad_page_reload_required"] is False
    assert packet["whole_warroom_display_update_target"] is True
    assert packet["prediction_cards_display_update_target"] is True
    assert packet["external_message_send_enabled"] is False
    assert packet["websocket_enabled"] is False
    assert packet["sse_enabled"] is False
    assert packet["prediction_generation_invoked"] is False
    assert packet["prediction_inference_invoked"] is False


def test_q31k_shadow_ready_readiness_maps_to_idle_plan() -> None:
    observation = build_warroom_v2_streamlit_local_loop_observation_packet(fragment_summary={"fragment_widget_count": 9})
    readiness = build_warroom_v2_display_update_readiness_packet(observation)
    plan = build_warroom_v2_renderer_plan_from_readiness(readiness)
    assert plan["renderer_plan_status"] == "renderer_plan_idle_shadow_ready"
    assert plan["plan_entry_count"] == 0
    assert plan["patch_execution_allowed"] is False
    assert plan["streamlit_render_allowed"] is False
    assert plan["warroom_page_ui_switch"] is False


def test_q31k_blocked_readiness_maps_to_blocked_plan() -> None:
    observation = build_warroom_v2_streamlit_local_loop_observation_packet(evidence=_evidence(), operator_approval_token="", messages=[_message(3, 3)])
    readiness = build_warroom_v2_display_update_readiness_packet(observation)
    plan = build_warroom_v2_renderer_plan_from_readiness(readiness)
    assert plan["renderer_plan_status"] == "renderer_plan_blocked"
    assert plan["plan_entry_count"] == 0
    assert plan["renderer_executes_patch"] is False
    assert plan["websocket_enabled"] is False
    assert plan["sse_enabled"] is False


def test_q31k_ready_readiness_maps_to_no_ui_switch_renderer_plan_entries() -> None:
    plan = build_warroom_v2_renderer_plan_from_readiness(_readiness_with_message())
    assert plan["renderer_plan_status"] == "renderer_plan_ready_no_ui_switch"
    assert plan["plan_entry_count"] == 1
    assert plan["observed_topics"] == ["warroom.market.snapshot"]
    assert plan["surfaces"] == ["top_information"]
    entry = plan["plan_entries"][0]
    assert entry["plan_action"] == "prepare_widget_dom_region_patch"
    assert entry["patch_unit"] == "widget_dom_region"
    assert entry["patch_execution_allowed"] is False
    assert entry["streamlit_render_allowed"] is False
    assert plan["renderer_executes_patch"] is False
    assert plan["warroom_page_ui_switch"] is False
    assert plan["external_message_send_enabled"] is False


def test_q31k_doc_and_transport_modules_preserve_no_side_effect_boundary() -> None:
    text = DOC.read_text(encoding="utf-8-sig")
    assert "renderer_plan_module=" in text
    assert "output_plan=warroom_v2_renderer_plan_packet" in text
    assert "renderer_executes_patch=false" in text
    assert "warroom_page_ui_switch=false" in text
    assert "not_executing_dom_patch=true" in text
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
