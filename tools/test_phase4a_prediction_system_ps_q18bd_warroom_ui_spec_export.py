# path: ./tools/test_phase4a_prediction_system_ps_q18bd_warroom_ui_spec_export.py
# desc: Unit tests for PS-Q18BD WarRoom UI spec export.

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SPEC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q18BD_WARROOM_UI_SPEC_EXPORT_2026-06-24.md"

REQUIRED_MARKERS = (
    "warroom_ui_spec_exported=true",
    "warroom_cleanup_optimization_complete=true",
    "normal_ui_operator_first=true",
    "development_preflight_sections_removed_from_normal_ui=true",
    "latest_prediction_observation_status=ready_for_operator_review",
    "implementation_gate_review_result=blocked_not_ready_to_enable",
    "current_freshness_state=stale",
    "latest_prediction_payload_contracts",
    "payload_to_widget_props_mapping_contract",
    "freshness_fallback_packet_builder",
    "rollback_to_skeleton_contract",
    "manual_ui_smoke_contract_pattern",
    "components/prediction_widgets/latest_prediction_summary_widget.py",
    "prediction_warroom_realtime_review_preflight_panel",
    "prediction_warroom_latest_prediction_summary_widget_real_source_handoff_preflight_panel",
    "prediction_widgets real component code must not be deleted by legacy cleanup",
    "PS-Q19A: Prediction real-render and AutoTrade trigger roadmap gate design",
    "bitFlyer FX-only execution boundary",
    "real_prediction_widget_rendering_allowed=false",
    "autotrade_trigger_allowed=false",
    "broker_private_api_allowed=false",
)

FALSE_BOUNDARIES = (
    "real_prediction_widget_rendering_allowed=false",
    "real_prediction_widget_render_invoked=false",
    "streamlit_real_widget_render_invoked=false",
    "component_runtime_binding_allowed=false",
    "component_props_bound_to_runtime=false",
    "runtime_artifact_write_allowed=false",
    "status_artifact_write_allowed=false",
    "parameter_apply_allowed=false",
    "parameter_staging_write_allowed=false",
    "ledger_append_allowed=false",
    "autotrade_trigger_allowed=false",
    "broker_private_api_allowed=false",
    "would_send_to_broker=false",
)


def test_ps_q18bd_warroom_ui_spec_exports_current_state_and_future_contracts() -> None:
    text = SPEC.read_text(encoding="utf-8-sig")
    for marker in REQUIRED_MARKERS:
        assert marker in text, marker
    for marker in FALSE_BOUNDARIES:
        assert marker in text, marker
    assert text.count("components/prediction_widgets/") >= 12
    assert "WarRoom UI sorting and normal UI optimization=complete" in text
    assert "AutoTrade trigger integration=not enabled" in text
