# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_local_only_transport_experiment_q31h.py
# desc: PS-Q31H guards for WarRoom v2 local-only true transport experiment.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.apps.operator_ui.prediction_warroom.v2 import (  # noqa: E402
    WARROOM_V2_LOCAL_ONLY_APPROVAL_TOKEN,
    apply_warroom_v2_local_only_transport_outbox,
    build_warroom_v2_local_only_transport_experiment_contract,
    build_warroom_v2_local_only_transport_outbox,
    build_warroom_v2_local_only_transport_session,
    build_warroom_v2_market_snapshot_update_event,
    build_warroom_v2_outbound_message_payload,
    run_warroom_v2_local_only_transport_experiment,
)

REPO_ROOT = Path(__file__).resolve().parents[6]
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q31H_WARROOM_V2_LOCAL_ONLY_TRUE_TRANSPORT_EXPERIMENT_2026-07-03.md"
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


def test_q31h_contract_is_local_only_and_external_transports_disabled() -> None:
    packet = build_warroom_v2_local_only_transport_experiment_contract()
    assert packet["experiment_kind"] == "local_only_in_process_true_transport_experiment"
    assert packet["transport_kind"] == "local_only_in_process"
    assert packet["whole_warroom_display_update_target"] is True
    assert packet["prediction_cards_display_update_target"] is True
    assert packet["external_message_send_enabled"] is False
    assert packet["websocket_enabled"] is False
    assert packet["sse_enabled"] is False
    assert packet["would_send_to_broker"] is False
    assert packet["prediction_generation_invoked"] is False
    assert packet["prediction_inference_invoked"] is False


def test_q31h_session_without_approval_stays_disabled() -> None:
    session = build_warroom_v2_local_only_transport_session(evidence=_evidence(), operator_approval_token="")
    assert session["gate"]["gate_status"] == "blocked_waiting_for_operator_approval"
    assert session["transport_enabled_effective"] is False
    assert session["local_loop_enabled_effective"] is False
    assert session["message_emission_enabled"] is False


def test_q31h_session_with_approval_enables_only_local_in_process_flags() -> None:
    session = build_warroom_v2_local_only_transport_session(evidence=_evidence(), operator_approval_token=WARROOM_V2_LOCAL_ONLY_APPROVAL_TOKEN)
    assert session["transport_enabled_effective"] is True
    assert session["local_loop_enabled_effective"] is True
    assert session["producer_enabled_effective"] is True
    assert session["consumer_enabled_effective"] is True
    assert session["message_emission_enabled"] is True
    assert session["external_message_send_enabled"] is False
    assert session["websocket_enabled"] is False
    assert session["sse_enabled"] is False
    assert session["runtime_connected"] is False


def test_q31h_outbox_emits_no_messages_when_session_disabled() -> None:
    session = build_warroom_v2_local_only_transport_session(evidence=_evidence(), operator_approval_token="")
    outbox = build_warroom_v2_local_only_transport_outbox(messages=[_message(1)], session=session)
    assert outbox["emitted_message_count"] == 0
    assert outbox["blocked_reason"] == "local_only_transport_session_not_enabled"
    assert outbox["message_emission_enabled"] is False


def test_q31h_outbox_with_approval_contains_normalized_display_messages_only() -> None:
    session = build_warroom_v2_local_only_transport_session(evidence=_evidence(), operator_approval_token=WARROOM_V2_LOCAL_ONLY_APPROVAL_TOKEN)
    invalid = {"topic": "not.warroom", "widget_id": "x", "sequence": 1}
    outbox = build_warroom_v2_local_only_transport_outbox(messages=[_message(2), invalid], session=session)
    assert outbox["emitted_message_count"] == 1
    assert outbox["outbox"][0]["topic"] == "warroom.market.snapshot"
    assert outbox["outbox"][0]["transport_enabled"] is False
    assert outbox["external_message_send_enabled"] is False
    assert outbox["websocket_enabled"] is False
    assert outbox["sse_enabled"] is False


def test_q31h_consumer_applies_local_outbox_to_q31d_state_projection() -> None:
    session = build_warroom_v2_local_only_transport_session(evidence=_evidence(), operator_approval_token=WARROOM_V2_LOCAL_ONLY_APPROVAL_TOKEN)
    outbox = build_warroom_v2_local_only_transport_outbox(messages=[_message(3, 3), _message(3, 3)], session=session)
    applied = apply_warroom_v2_local_only_transport_outbox(outbox=outbox, received_at="t3")
    assert applied["projected_result_count"] == 2
    assert applied["applied_message_count"] == 1
    assert applied["projected_results"][1]["reason"] == "duplicate_fingerprint"
    assert applied["projected_consumer_state"]["applied_count"] == 1
    assert applied["projected_consumer_state"]["dropped_count"] == 1
    assert applied["runtime_connected"] is False


def test_q31h_full_experiment_is_local_only_and_does_not_touch_external_systems() -> None:
    packet = run_warroom_v2_local_only_transport_experiment(evidence=_evidence(), operator_approval_token=WARROOM_V2_LOCAL_ONLY_APPROVAL_TOKEN, messages=[_message(4)], received_at="t4")
    assert packet["experiment_kind"] == "local_only_true_transport_experiment_result"
    assert packet["transport_enabled_effective"] is True
    assert packet["local_loop_enabled_effective"] is True
    assert packet["message_emission_enabled"] is True
    assert packet["outbox"]["emitted_message_count"] == 1
    assert packet["consumer"]["applied_message_count"] == 1
    assert packet["external_message_send_enabled"] is False
    assert packet["websocket_enabled"] is False
    assert packet["sse_enabled"] is False
    assert packet["would_send_to_broker"] is False
    assert packet["prediction_inference_invoked"] is False


def test_q31h_doc_and_transport_modules_preserve_no_side_effect_boundary() -> None:
    text = DOC.read_text(encoding="utf-8-sig")
    assert "local_loop_module=" in text
    assert "approval_token_required=APPROVE_Q31G_LOCAL_ONLY_SHADOW_EXPERIMENT" in text
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
