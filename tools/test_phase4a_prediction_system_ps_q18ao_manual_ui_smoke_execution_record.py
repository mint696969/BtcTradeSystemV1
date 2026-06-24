# path: ./tools/test_phase4a_prediction_system_ps_q18ao_manual_ui_smoke_execution_record.py
# desc: Unit tests for PS-Q18AO manual UI smoke execution record.

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
)

UX_GAPS = (
    "browser_find_freshness_state_false",
    "browser_find_safe_fallback_reason_codes_false",
    "auto_refresh_visibly_obvious_false",
)


def build_ps_q18ao_manual_ui_smoke_execution_record_packet() -> dict:
    packet = {
        "ok": True,
        "ps_q18ao_manual_ui_smoke_record_version": "prediction_warroom.latest_prediction_summary_widget.q18ao_manual_ui_smoke_execution_record.v1",
        "manual_ui_smoke_result": "observed_with_ux_gaps_not_full_pass",
        "uicheck_path": "tmp/uicheck/uicheck_20260624_135754_220198_warroom.json",
        "repo_head_at_uicheck": "5c180c18",
        "page": "warroom",
        "latest_prediction_auto_refresh_panel_visible": True,
        "latest_prediction_freshness_fallback_panel_visible": True,
        "q18aj_auto_refresh_enabled": True,
        "q18aj_fragment_refresh_enabled": True,
        "q18aj_page_reload_enabled": False,
        "q18ak_freshness_state": "stale",
        "q18ak_safe_fallback_reason_codes": ["source_generated_at_stale"],
        "source_age_sec_changes_across_screenshots": True,
        "observed_now_utc_changes_across_screenshots": True,
        "operator_reported_ux_gaps": list(UX_GAPS),
        "operator_searchability_gap_present": True,
        "operator_refresh_visibility_gap_present": True,
        "next_safe_slice": "PS-Q18AP UI visibility polish for searchable tokens and refresh heartbeat",
    }
    packet.update({key: False for key in FALSE_BOUNDARIES})
    return packet


def test_ps_q18ao_records_manual_ui_smoke_as_observed_with_ux_gaps() -> None:
    packet = build_ps_q18ao_manual_ui_smoke_execution_record_packet()
    assert packet["ok"] is True
    assert packet["manual_ui_smoke_result"] == "observed_with_ux_gaps_not_full_pass"
    assert packet["latest_prediction_auto_refresh_panel_visible"] is True
    assert packet["latest_prediction_freshness_fallback_panel_visible"] is True
    assert packet["q18aj_auto_refresh_enabled"] is True
    assert packet["q18aj_fragment_refresh_enabled"] is True
    assert packet["q18aj_page_reload_enabled"] is False
    assert packet["q18ak_freshness_state"] == "stale"
    assert packet["q18ak_safe_fallback_reason_codes"] == ["source_generated_at_stale"]
    assert packet["source_age_sec_changes_across_screenshots"] is True
    assert packet["observed_now_utc_changes_across_screenshots"] is True
    assert packet["operator_searchability_gap_present"] is True
    assert packet["operator_refresh_visibility_gap_present"] is True
    for key in FALSE_BOUNDARIES:
        assert packet[key] is False, key
