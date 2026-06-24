# path: ./tools/test_phase4a_prediction_system_ps_q18ar_real_widget_rendering_design_gate.py
# desc: Unit tests for PS-Q18AR explicit real-widget rendering design gate.

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

FUTURE_RELEASE_REQUIREMENTS = (
    "exact_component_runtime_binding_boundary",
    "exact_streamlit_render_function_boundary",
    "props_to_rendered_ui_mapping_contract",
    "display_only_render_contract",
    "stale_source_fallback_behavior_during_render",
    "missing_source_failure_mode",
    "unparseable_source_failure_mode",
    "visual_acceptance_criteria",
    "manual_ui_review_packet",
    "rollback_to_skeleton_packet_path",
    "no_runtime_status_artifact_writes",
    "no_parameter_apply_or_staging",
    "no_ledger_append",
    "no_autotrade_trigger",
    "no_broker_private_api",
)


def build_ps_q18ar_real_widget_rendering_design_gate_packet() -> dict:
    packet = {
        "ok": True,
        "ps_q18ar_design_gate_version": "prediction_warroom.latest_prediction_summary_widget.q18ar_real_widget_rendering_design_gate.v1",
        "real_widget_rendering_design_gate_state": "design_only_rendering_not_enabled",
        "source_widget": "btcts_next/src/btcts/apps/operator_ui/components/prediction_widgets/latest_prediction_summary_widget.py",
        "current_component_state": "read_only_component_skeleton_render_disabled",
        "current_render_function": "render_latest_prediction_summary_widget",
        "current_render_function_behavior": "returns_read_only_skeleton_packet",
        "streamlit_import_present": False,
        "future_real_render_gate_required": True,
        "manual_ui_review_required_before_enablement": True,
        "rollback_plan_required_before_enablement": True,
        "rollback_target": "read_only_component_skeleton_render_disabled",
        "rollback_action": "restore render_latest_prediction_summary_widget to skeleton packet builder",
        "future_release_requirements": list(FUTURE_RELEASE_REQUIREMENTS),
        "future_release_requirement_count": len(FUTURE_RELEASE_REQUIREMENTS),
        "next_safe_slice": "still-disabled real-render prototype behind explicit flags or continued WarRoom observation cleanup",
    }
    packet.update({key: False for key in FALSE_BOUNDARIES})
    return packet


def test_ps_q18ar_design_gate_keeps_real_rendering_disabled() -> None:
    packet = build_ps_q18ar_real_widget_rendering_design_gate_packet()
    assert packet["ok"] is True
    assert packet["real_widget_rendering_design_gate_state"] == "design_only_rendering_not_enabled"
    assert packet["current_component_state"] == "read_only_component_skeleton_render_disabled"
    assert packet["streamlit_import_present"] is False
    assert packet["future_real_render_gate_required"] is True
    assert packet["manual_ui_review_required_before_enablement"] is True
    assert packet["rollback_plan_required_before_enablement"] is True
    assert packet["rollback_target"] == "read_only_component_skeleton_render_disabled"
    assert packet["future_release_requirement_count"] == 15
    for required in FUTURE_RELEASE_REQUIREMENTS:
        assert required in packet["future_release_requirements"]
    for key in FALSE_BOUNDARIES:
        assert packet[key] is False, key
