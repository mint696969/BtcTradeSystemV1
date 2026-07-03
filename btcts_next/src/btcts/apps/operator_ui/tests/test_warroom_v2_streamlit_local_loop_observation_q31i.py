# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_streamlit_local_loop_observation_q31i.py
# desc: PS-Q31I guards for Streamlit hidden local-loop observation without external transport.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.apps.operator_ui.prediction_warroom.v2 import (  # noqa: E402
    WARROOM_V2_STREAMLIT_LOCAL_LOOP_OBSERVATION_STATE_KEY,
    build_warroom_v2_streamlit_local_loop_observation_contract,
    build_warroom_v2_streamlit_local_loop_observation_packet,
)

REPO_ROOT = Path(__file__).resolve().parents[6]
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q31I_WARROOM_V2_STREAMLIT_SHADOW_LOCAL_LOOP_OBSERVATION_NO_EXTERNAL_TRANSPORT_2026-07-03.md"
WARROOM_PAGE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py"
TRANSPORT_DIR = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport"


def test_q31i_contract_is_hidden_observation_and_external_transport_disabled() -> None:
    packet = build_warroom_v2_streamlit_local_loop_observation_contract()
    assert packet["state_key"] == WARROOM_V2_STREAMLIT_LOCAL_LOOP_OBSERVATION_STATE_KEY
    assert packet["observation_kind"] == "streamlit_hidden_local_loop_observation_packet"
    assert packet["whole_warroom_display_update_target"] is True
    assert packet["prediction_cards_display_update_target"] is True
    assert packet["visible_ui_decoration_added"] is False
    assert packet["fragment_refresh_replaced"] is False
    assert packet["external_message_send_enabled"] is False
    assert packet["websocket_enabled"] is False
    assert packet["sse_enabled"] is False
    assert packet["prediction_generation_invoked"] is False
    assert packet["prediction_inference_invoked"] is False


def test_q31i_packet_observes_q31h_local_loop_with_zero_default_messages() -> None:
    packet = build_warroom_v2_streamlit_local_loop_observation_packet(
        fragment_summary={
            "fragment_widget_count": 9,
            "fragment_interval_sec": 3,
            "page_reload_interval_sec": 15,
            "hybrid_refresh": True,
            "page_fragment_enabled": True,
            "prediction_fragment_enabled": True,
        }
    )
    assert packet["fragment_summary"]["fragment_widget_count"] == 9
    assert packet["local_loop_observed"] is True
    assert packet["default_streamlit_message_count"] == 0
    assert packet["emitted_message_count"] == 0
    assert packet["local_loop_result"]["transport_enabled_effective"] is True
    assert packet["local_loop_result"]["local_loop_enabled_effective"] is True
    assert packet["local_loop_result"]["external_message_send_enabled"] is False
    assert packet["local_loop_result"]["websocket_enabled"] is False
    assert packet["local_loop_result"]["sse_enabled"] is False
    assert packet["visible_ui_decoration_added"] is False
    assert packet["prediction_inference_invoked"] is False


def test_q31i_warroom_page_records_hidden_observation_state_only() -> None:
    text = WARROOM_PAGE.read_text(encoding="utf-8-sig")
    assert "WARROOM_V2_STREAMLIT_LOCAL_LOOP_OBSERVATION_STATE_KEY" in text
    assert "warroom_v2_streamlit_local_loop_observation_q31i" in text
    assert "build_warroom_v2_streamlit_local_loop_observation_packet" in text
    assert "st.session_state[WARROOM_V2_STREAMLIT_LOCAL_LOOP_OBSERVATION_STATE_KEY]" in text
    forbidden_visible_labels = (
        "WarRoom v2 local loop observation",
        "Streamlit local loop observation",
        "Run local loop observation",
    )
    for label in forbidden_visible_labels:
        assert label not in text


def test_q31i_doc_records_no_external_transport_and_no_visible_ui() -> None:
    text = DOC.read_text(encoding="utf-8-sig")
    assert "warroom_page_observation_state_key=warroom_v2_streamlit_local_loop_observation_q31i" in text
    assert "external_message_send_enabled=false" in text
    assert "visible_ui_decoration_added=false" in text
    assert "not_enabling_websocket=true" in text
    assert "not_sending_external_messages=true" in text
    assert "not_invoking_prediction_inference=true" in text


def test_q31i_transport_modules_stay_small_and_side_effect_free() -> None:
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
