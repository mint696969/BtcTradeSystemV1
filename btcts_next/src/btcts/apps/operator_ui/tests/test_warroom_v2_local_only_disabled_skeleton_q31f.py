# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_local_only_disabled_skeleton_q31f.py
# desc: PS-Q31F guards for WarRoom v2 local-only disabled producer/consumer skeleton.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.apps.operator_ui.prediction_warroom.v2 import (  # noqa: E402
    build_warroom_v2_local_disabled_consumer_packet,
    build_warroom_v2_local_disabled_producer_consumer_cycle,
    build_warroom_v2_local_disabled_producer_packet,
    build_warroom_v2_local_disabled_skeleton_contract,
    build_warroom_v2_local_disabled_transport_flags,
    build_warroom_v2_market_snapshot_update_event,
    build_warroom_v2_outbound_message_payload,
)

REPO_ROOT = Path(__file__).resolve().parents[6]
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q31F_WARROOM_V2_LOCAL_ONLY_DISABLED_PRODUCER_CONSUMER_SKELETON_2026-07-03.md"
TRANSPORT_DIR = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport"


def _message(sequence: int = 1, ltp: int = 1) -> dict[str, object]:
    event = build_warroom_v2_market_snapshot_update_event(snapshot_payload={"ltp": ltp}, sequence=sequence)
    message = build_warroom_v2_outbound_message_payload(event_packet=event)
    message["current_fingerprint"] = event["current_fingerprint"]
    return message


def test_q31f_flags_record_requested_but_keep_effective_disabled() -> None:
    flags = build_warroom_v2_local_disabled_transport_flags(
        transport_enabled=True,
        local_loop_enabled=True,
        producer_enabled=True,
        consumer_enabled=True,
    )
    assert flags["requested_flags"]["transport_enabled"] is True
    assert flags["requested_flags"]["producer_enabled"] is True
    assert flags["effective_flags"]["transport_enabled"] is False
    assert flags["effective_flags"]["local_loop_enabled"] is False
    assert flags["effective_flags"]["producer_enabled"] is False
    assert flags["effective_flags"]["consumer_enabled"] is False
    assert flags["effective_flags"]["message_emission_enabled"] is False
    assert flags["effective_flags"]["websocket_enabled"] is False
    assert flags["effective_flags"]["sse_enabled"] is False
    assert flags["operator_review_required_before_enable"] is True


def test_q31f_contract_is_local_only_disabled_and_display_targeted() -> None:
    packet = build_warroom_v2_local_disabled_skeleton_contract()
    assert packet["skeleton_kind"] == "local_only_disabled_producer_consumer_lifecycle_shape"
    assert packet["transport_kind"] == "local_only_disabled_in_process"
    assert packet["whole_warroom_display_update_target"] is True
    assert packet["prediction_cards_display_update_target"] is True
    assert packet["producer_shape"] == "disabled_shadow_frame_source"
    assert packet["consumer_shape"] == "disabled_shadow_consumer_state_projection"
    assert packet["topic_policy_scope"] == "whole_warroom_display"
    assert packet["transport_enabled_default"] is False
    assert packet["websocket_enabled"] is False
    assert packet["sse_enabled"] is False
    assert packet["prediction_generation_invoked"] is False
    assert packet["prediction_inference_invoked"] is False


def test_q31f_producer_packet_wraps_shadow_frame_without_emission() -> None:
    packet = build_warroom_v2_local_disabled_producer_packet(messages=[_message(4, 4)], frame_id="unit")
    assert packet["producer_enabled_effective"] is False
    assert packet["message_emission_enabled"] is False
    assert packet["emitted_message_count"] == 0
    assert packet["shadow_frame_message_count"] == 1
    assert packet["shadow_frame"]["frame_id"] == "unit"
    assert packet["shadow_frame"]["topics"] == ["warroom.market.snapshot"]
    assert packet["websocket_enabled"] is False
    assert packet["sse_enabled"] is False
    assert packet["would_send_to_broker"] is False


def test_q31f_consumer_packet_projects_state_without_runtime_connection() -> None:
    packet = build_warroom_v2_local_disabled_consumer_packet(messages=[_message(1, 1), _message(1, 1)], received_at="t1")
    assert packet["consumer_enabled_effective"] is False
    assert packet["message_emission_enabled"] is False
    assert packet["projected_message_count"] == 2
    assert packet["projected_results"][0]["applied"] is True
    assert packet["projected_results"][1]["applied"] is False
    assert packet["projected_results"][1]["reason"] == "duplicate_fingerprint"
    assert packet["projected_consumer_state"]["applied_count"] == 1
    assert packet["projected_consumer_state"]["dropped_count"] == 1
    assert packet["runtime_connected"] is False


def test_q31f_disabled_cycle_links_producer_shadow_frame_to_consumer_projection() -> None:
    packet = build_warroom_v2_local_disabled_producer_consumer_cycle(messages=[_message(2, 2)], received_at="t2")
    assert packet["cycle_kind"] == "local_only_disabled_producer_consumer_shadow_cycle"
    assert packet["local_loop_enabled"] is False
    assert packet["message_emission_enabled"] is False
    assert packet["producer"]["shadow_frame_message_count"] == 1
    assert packet["consumer"]["projected_results"][0]["applied"] is True
    assert packet["websocket_enabled"] is False
    assert packet["sse_enabled"] is False
    assert packet["prediction_generation_invoked"] is False


def test_q31f_doc_and_transport_modules_preserve_disabled_no_side_effect_boundary() -> None:
    text = DOC.read_text(encoding="utf-8-sig")
    assert "skeleton_module=" in text
    assert "local_loop_enabled_effective=false" in text
    assert "producer_enabled_effective=false" in text
    assert "consumer_enabled_effective=false" in text
    assert "message_emission_enabled=false" in text
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
