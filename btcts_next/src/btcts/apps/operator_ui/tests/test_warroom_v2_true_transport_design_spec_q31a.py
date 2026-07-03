# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_true_transport_design_spec_q31a.py
# desc: PS-Q31A guards for WarRoom v2 true transport design/spec boundary.

from __future__ import annotations
from pathlib import Path
REPO_ROOT = Path(__file__).resolve().parents[6]
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q31A_WARROOM_V2_TRUE_TRANSPORT_DESIGN_SPEC_2026-07-03.md"
Q30G_ADAPTER = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/disabled_transport_adapter.py"

def _doc_text() -> str:
    return DOC.read_text(encoding="utf-8-sig")

def test_q31a_doc_exists_and_records_manual_daytrade_low_latency_goal() -> None:
    text = _doc_text()
    assert "Slice: PS-Q31A_WARROOM_V2_TRUE_TRANSPORT_DESIGN_SPEC" in text
    assert "manual_daytrade_support=true" in text
    assert "low_latency_information_board=true" in text
    assert "independent_widget_updates=true" in text
    assert "operator_decision_human_only=true" in text
    assert "Each information area should be able to update independently" in text

def test_q31a_preserves_disabled_transport_and_no_execution_boundary() -> None:
    text = _doc_text()
    for token in (
        "true_transport_design_spec_only=true",
        "transport_enabled_default=false",
        "websocket_enabled=false",
        "sse_enabled=false",
        "push_connected=false",
        "runtime_connected=false",
        "would_send_to_broker=false",
        "not_touching_autotrade_broker_ledger_mode_parameter=true",
    ):
        assert token in text
    for token in (
        "not_enabling_websocket=true",
        "not_enabling_sse=true",
        "not_opening_socket=true",
        "not_sending_messages=true",
        "not_invoking_classifier=true",
        "not_connecting_broker=true",
        "not_creating_order=true",
        "not_appending_ledger=true",
        "not_applying_mode=true",
        "not_applying_parameter=true",
    ):
        assert token in text

def test_q31a_message_schema_is_q30g_payload_compatible() -> None:
    text = _doc_text()
    for token in (
        "q30g_payload_contract=disabled_outbound_transport_payload_adapter",
        "message_type=warroom_v2_widget_update",
        "payload_kind=widget_update_event_envelope",
        "adapter_version=prediction_warroom.v2.disabled_transport_adapter.ps_q30g.v1 compatible",
        "topic=<widget topic>",
        "widget_id=<widget dom region id>",
        "sequence=<monotonic per topic sequence>",
        "previous_fingerprint=<previous stable payload fingerprint>",
        "current_fingerprint=<current stable payload fingerprint>",
        "ui_patch_unit=widget_dom_region",
        "broad_page_reload_required=false",
        "fingerprint_algorithm=sha256_json_sort_keys_24",
    ):
        assert token in text

def test_q31a_independent_topic_cadence_and_stale_policy_are_defined() -> None:
    text = _doc_text()
    for token in (
        "market_snapshot_strip:",
        "preferred_update_class: fastest_safe",
        "chart_review_panel:",
        "preferred_update_class: opt_in_or_medium_frequency",
        "prediction_cards:",
        "preferred_update_class: evidence_change_or_moderate_frequency",
        "safety/current_state/alerts:",
        "preferred_update_class: high_priority_when_changed",
        "Each topic may have its own cadence, dedup state, replay cursor, and freshness policy.",
    ):
        assert token in text

def test_q31a_dedup_reconnect_replay_and_fragment_fallback_are_defined() -> None:
    text = _doc_text()
    for token in (
        "sequence_scope=per_topic",
        "fingerprint_scope=widget_id",
        "dedup_rule=drop_if_current_fingerprint_matches_latest_widget_fingerprint",
        "replay_cursor=last_applied_sequence_per_topic",
        "initial_connect_behavior=send_latest_snapshot_per_subscribed_topic",
        "reconnect_behavior=request_events_after_last_sequence_then_latest_snapshot_if_gap",
        "large_gap_behavior=send_latest_snapshot_and_gap_marker",
        "streamlit_fragment_refresh_remains_active=true",
        "fragment_refresh_retirement_gate=operator_accepts_true_transport_stability",
    ):
        assert token in text

def test_q31a_transport_promotion_gate_is_explicit() -> None:
    text = _doc_text()
    for token in (
        "transport_enabled_promotion_gate_required=true",
        "operator_review_required=true",
        "disabled_simulator_guard_passed_required=true",
        "producer_consumer_skeleton_guard_passed_required=true",
        "message_schema_guard_passed_required=true",
        "dedup_reconnect_replay_guard_passed_required=true",
        "no_broker_runtime_classifier_guard_passed_required=true",
        "fragment_fallback_preserved_required=true",
        "PS-Q31B: disabled in-process transport simulator contract, transport_enabled=false.",
    ):
        assert token in text

def test_q31a_records_responsibility_separated_layout_and_anti_bloat_policy() -> None:
    text = _doc_text()
    for token in (
        "## Responsibility-separated future folder layout",
        "future_transport_folder=btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport",
        "one_module_one_responsibility=true",
        "schema_module_no_socket=true",
        "topic_policy_module_no_ui=true",
        "consumer_state_module_no_streamlit=true",
        "replay_module_no_broker_runtime_classifier=true",
        "simulator_module_disabled_by_default=true",
        "gates_module_required_before_transport_enabled=true",
        "ui_renderer_must_not_own_transport_lifecycle=true",
        "## Anti-bloat policy for future implementation",
        "no_monolithic_transport_file=true",
        "no_one_file_bloat=true",
        "max_future_transport_module_lines=220",
        "max_renderer_module_lines=120",
        "split_required_when_responsibilities_mix=true",
    ):
        assert token in text

def test_q31a_does_not_modify_q30g_adapter_into_live_transport() -> None:
    text = Q30G_ADAPTER.read_text(encoding="utf-8-sig")
    for token in (
        '"transport_implemented_now": False',
        '"adapter_sends_messages": False',
        '"adapter_opens_socket": False',
        '"websocket_enabled": False',
        '"sse_enabled": False',
        '"runtime_connected": False',
        '"push_connected": False',
        '"would_send_to_broker": False',
    ):
        assert token in text
