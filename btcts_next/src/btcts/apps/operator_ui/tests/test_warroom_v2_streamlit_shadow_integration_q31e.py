# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_streamlit_shadow_integration_q31e.py
# desc: PS-Q31E guards for hidden WarRoom v2 Streamlit shadow integration without UI decoration.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.apps.operator_ui.prediction_warroom.v2 import (  # noqa: E402
    WARROOM_V2_STREAMLIT_SHADOW_STATE_KEY,
    build_warroom_v2_market_snapshot_update_event,
    build_warroom_v2_outbound_message_payload,
    build_warroom_v2_streamlit_shadow_integration_contract,
    build_warroom_v2_streamlit_shadow_integration_packet,
)

REPO_ROOT = Path(__file__).resolve().parents[6]
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q31E_WARROOM_V2_STREAMLIT_SHADOW_INTEGRATION_NO_UI_DECORATION_2026-07-03.md"
WARROOM_PAGE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py"
TRANSPORT_DIR = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport"


def _message(sequence: int = 1) -> dict[str, object]:
    event = build_warroom_v2_market_snapshot_update_event(snapshot_payload={"ltp": sequence}, sequence=sequence)
    return build_warroom_v2_outbound_message_payload(event_packet=event)


def test_q31e_contract_is_hidden_disabled_and_display_only() -> None:
    packet = build_warroom_v2_streamlit_shadow_integration_contract()
    assert packet["state_key"] == WARROOM_V2_STREAMLIT_SHADOW_STATE_KEY
    assert packet["integration_kind"] == "streamlit_hidden_session_state_shadow_packet"
    assert packet["whole_warroom_display_update_target"] is True
    assert packet["prediction_cards_display_update_target"] is True
    assert packet["prediction_generation_invoked"] is False
    assert packet["prediction_inference_invoked"] is False
    assert packet["visible_ui_decoration_added"] is False
    assert packet["fragment_refresh_replaced"] is False
    assert packet["transport_enabled"] is False
    assert packet["websocket_enabled"] is False
    assert packet["sse_enabled"] is False
    assert packet["would_send_to_broker"] is False


def test_q31e_shadow_packet_compares_fragment_summary_with_disabled_frame_and_policy() -> None:
    packet = build_warroom_v2_streamlit_shadow_integration_packet(
        fragment_summary={
            "fragment_widget_count": 9,
            "fragment_interval_sec": 3,
            "page_reload_interval_sec": 15,
            "hybrid_refresh": True,
            "page_fragment_enabled": True,
            "prediction_fragment_enabled": True,
        },
        messages=[_message(4)],
        subscribed_topics=["warroom.market.snapshot", "warroom.prediction.market_regime"],
    )
    assert packet["fragment_summary"]["fragment_widget_count"] == 9
    assert packet["fragment_summary"]["prediction_fragment_enabled"] is True
    assert packet["disabled_shadow_frame"]["frame_kind"] == "disabled_in_process_transport_shadow_frame"
    assert packet["disabled_shadow_frame"]["topics"] == ["warroom.market.snapshot"]
    assert packet["topic_policy_contract"]["policy_scope"] == "whole_warroom_display"
    assert "warroom.prediction.market_regime" in packet["topic_policy_contract"]["prediction_display_topics"]
    assert packet["reconnect_request"]["topics"] == ["warroom.market.snapshot", "warroom.prediction.market_regime"]
    assert packet["visible_ui_decoration_added"] is False
    assert packet["fragment_refresh_replaced"] is False
    assert packet["websocket_enabled"] is False
    assert packet["sse_enabled"] is False


def test_q31e_warroom_page_records_hidden_session_state_only() -> None:
    text = WARROOM_PAGE.read_text(encoding="utf-8-sig")
    assert "_record_warroom_v2_transport_shadow_integration_state" in text
    assert "warroom_v2_transport_shadow_integration_q31e" in text
    assert "build_warroom_v2_streamlit_shadow_integration_packet" in text
    assert "st.session_state[WARROOM_V2_STREAMLIT_SHADOW_STATE_KEY]" in text
    forbidden_visible_labels = (
        "WarRoom v2 transport shadow",
        "Streamlit shadow integration",
        "Run WarRoom v2 transport shadow",
    )
    for label in forbidden_visible_labels:
        assert label not in text


def test_q31e_doc_records_no_ui_decoration_and_no_live_transport() -> None:
    text = DOC.read_text(encoding="utf-8-sig")
    assert "visible_ui_decoration_added=false" in text
    assert "fragment_refresh_replaced=false" in text
    assert "warroom_page_shadow_state_key=warroom_v2_transport_shadow_integration_q31e" in text
    assert "not_adding_visible_ui_decoration=true" in text
    assert "not_enabling_websocket=true" in text
    assert "not_invoking_prediction_inference=true" in text


def test_q31e_transport_modules_stay_small_and_side_effect_free() -> None:
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
        text = path.read_text(encoding="utf-8-sig")
        assert len(text.splitlines()) <= 220, f"transport file too large: {path}"
        for token in forbidden:
            assert token not in text, f"forbidden token {token!r} found in {path}"
