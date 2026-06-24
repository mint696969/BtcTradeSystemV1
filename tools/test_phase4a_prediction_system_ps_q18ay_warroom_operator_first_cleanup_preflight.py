# path: ./tools/test_phase4a_prediction_system_ps_q18ay_warroom_operator_first_cleanup_preflight.py
# desc: Unit tests for PS-Q18AY WarRoom operator-first cleanup preflight.

from __future__ import annotations

FALSE_BOUNDARIES = (
    "real_prediction_widget_rendering_allowed",
    "real_prediction_widget_render_invoked",
    "streamlit_real_widget_render_invoked",
    "component_runtime_binding_allowed",
    "component_props_bound_to_runtime",
    "runtime_artifact_write_allowed",
    "status_artifact_write_allowed",
    "parameter_apply_allowed",
    "parameter_staging_write_allowed",
    "ledger_append_allowed",
    "autotrade_trigger_allowed",
    "broker_private_api_allowed",
    "would_send_to_broker",
)

KEEP_NORMAL_UI = (
    "latest_prediction_observation_quick_status",
    "warroom_header_compact_market_snapshot",
    "warroom_alert_summary",
    "ai_operator_action_risk_mode_short_summary",
    "bounded_refresh_heartbeat_short_status_if_needed",
)

REMOVE_FROM_NORMAL_UI_FIRST = (
    "prediction_warroom_real_payload_review",
    "prediction_warroom_disabled_widget_skeleton_review",
    "prediction_warroom_source_readiness_preflight",
    "prediction_warroom_source_read_probe_status",
    "prediction_warroom_latest_summary_props_candidate_status",
    "prediction_warroom_latest_summary_render_disabled_packet_status",
    "prediction_warroom_latest_summary_mapped_payload_details",
    "prediction_warroom_legacy_safe_display_mount_details",
    "long_warroom_reading_blocks_caption",
    "long_summary_widget_semantic_contract_caption",
    "long_ai_operator_explanation_context",
)

PRESERVE_FOR_FUTURE = (
    "latest_prediction_payload_contracts",
    "payload_to_widget_props_mapping_contract",
    "latest_prediction_summary_widget_props_schema",
    "bounded_refresh_packet_builder",
    "freshness_fallback_packet_builder",
    "real_render_implementation_gate_docs",
    "rollback_to_skeleton_contract",
    "manual_ui_smoke_contract_pattern",
)


def build_ps_q18ay_warroom_operator_first_cleanup_preflight_packet() -> dict:
    packet = {
        "ok": True,
        "ps_q18ay_preflight_version": "prediction_warroom.q18ay_operator_first_cleanup_preflight.v1",
        "warroom_cleanup_goal": "operator_first_normal_ui_with_diagnostics_out_of_path",
        "docs_guard_only": True,
        "warroom_runtime_changed": False,
        "code_deleted_this_slice": False,
        "normal_ui_keep": list(KEEP_NORMAL_UI),
        "normal_ui_keep_count": len(KEEP_NORMAL_UI),
        "remove_from_normal_ui_first": list(REMOVE_FROM_NORMAL_UI_FIRST),
        "remove_from_normal_ui_first_count": len(REMOVE_FROM_NORMAL_UI_FIRST),
        "preserve_for_future_implementation_design": list(PRESERVE_FOR_FUTURE),
        "preserve_for_future_implementation_design_count": len(PRESERVE_FOR_FUTURE),
        "delete_requires_reference_audit": True,
        "remove_warroom_page_imports_helpers_after_ui_path_cleanup": True,
        "component_file_delete_allowed_this_slice": False,
        "future_real_render_gate_design_allowed_later": True,
        "future_real_render_enablement_allowed_this_slice": False,
        "proposed_next_slices": [
            "PS-Q18AZ WarRoom operator-first render path cleanup",
            "PS-Q18BA WarRoom legacy prediction dev helper/import prune",
            "PS-Q18BB legacy component reference audit and archive/delete decision",
        ],
        "task_weight": {
            "PS-Q18AY preflight": "low",
            "PS-Q18AZ render path cleanup": "medium",
            "PS-Q18BA warroom_page code prune": "medium_high",
            "PS-Q18BB component delete/archive audit": "high",
            "future_real_render_gate_design": "medium_high",
            "future_real_render_enablement": "high",
        },
        "next_safe_slice": "PS-Q18AZ WarRoom operator-first render path cleanup",
    }
    packet.update({key: False for key in FALSE_BOUNDARIES})
    return packet


def test_ps_q18ay_preflight_separates_keep_remove_and_preserve() -> None:
    packet = build_ps_q18ay_warroom_operator_first_cleanup_preflight_packet()
    assert packet["ok"] is True
    assert packet["docs_guard_only"] is True
    assert packet["warroom_runtime_changed"] is False
    assert packet["code_deleted_this_slice"] is False
    assert packet["warroom_cleanup_goal"] == "operator_first_normal_ui_with_diagnostics_out_of_path"
    assert packet["normal_ui_keep_count"] == 5
    assert packet["remove_from_normal_ui_first_count"] == 11
    assert packet["preserve_for_future_implementation_design_count"] == 8
    assert "latest_prediction_observation_quick_status" in packet["normal_ui_keep"]
    assert "prediction_warroom_real_payload_review" in packet["remove_from_normal_ui_first"]
    assert "long_ai_operator_explanation_context" in packet["remove_from_normal_ui_first"]
    assert "payload_to_widget_props_mapping_contract" in packet["preserve_for_future_implementation_design"]
    assert packet["delete_requires_reference_audit"] is True
    assert packet["component_file_delete_allowed_this_slice"] is False
    assert packet["future_real_render_enablement_allowed_this_slice"] is False
    for key in FALSE_BOUNDARIES:
        assert packet[key] is False, key
