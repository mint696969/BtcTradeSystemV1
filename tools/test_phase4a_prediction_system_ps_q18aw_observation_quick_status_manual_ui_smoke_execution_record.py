# path: ./tools/test_phase4a_prediction_system_ps_q18aw_observation_quick_status_manual_ui_smoke_execution_record.py
# desc: Unit tests for PS-Q18AW manual UI smoke execution record.

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

PASS_CHECKS = (
    "section_title_visible",
    "browser_find_PS_Q18AU_OBSERVATION_QUICK_STATUS",
    "browser_find_latest_prediction_observation_status",
    "browser_find_implementation_gate_blocked_not_ready_to_enable",
    "browser_find_real_render_false",
    "browser_find_component_runtime_binding_false",
    "browser_find_autotrade_false",
    "browser_find_broker_false",
    "refresh_heartbeat_utc_advances_after_wait",
    "no_broad_page_whiteout_or_full_reload_observed",
)


def build_ps_q18aw_observation_quick_status_manual_ui_smoke_execution_record() -> dict:
    packet = {
        "ok": True,
        "ps_q18aw_execution_record_version": "prediction_warroom.latest_prediction_summary_widget.q18aw_observation_quick_status_manual_ui_smoke_execution_record.v1",
        "manual_ui_smoke_result": "pass",
        "operator_report": "ALL OK",
        "uicheck_path": "tmp/uicheck/uicheck_20260624_202405_369594_warroom.json",
        "repo_head_at_uicheck": "625de736",
        "page": "warroom",
        "pass_checks": list(PASS_CHECKS),
        "pass_check_count": len(PASS_CHECKS),
        "quick_status_refresh_heartbeat_utc": "2026-06-24T11:23:55.718920Z",
        "q18aj_refresh_heartbeat_utc_at_uicheck": "2026-06-24T11:23:55.908245Z",
        "later_refresh_heartbeat_utc_1": "2026-06-24T11:29:51.172021Z",
        "later_refresh_heartbeat_utc_2": "2026-06-24T11:30:09.481168Z",
        "ui_auto_refresh": True,
        "fragment_refresh_enabled": True,
        "page_reload_enabled": False,
        "observation_cleanup_state": "operator_quick_status_visible_display_only",
        "latest_prediction_observation_status": "ready_for_operator_review",
        "implementation_gate_review_result": "blocked_not_ready_to_enable",
        "next_safe_slice": "continue legacy preflight folding cleanup or close latest prediction observation milestone",
    }
    packet.update({key: False for key in FALSE_BOUNDARIES})
    return packet


def test_ps_q18aw_execution_record_classifies_manual_ui_smoke_as_pass() -> None:
    packet = build_ps_q18aw_observation_quick_status_manual_ui_smoke_execution_record()
    assert packet["ok"] is True
    assert packet["manual_ui_smoke_result"] == "pass"
    assert packet["operator_report"] == "ALL OK"
    assert packet["repo_head_at_uicheck"] == "625de736"
    assert packet["page"] == "warroom"
    assert packet["pass_check_count"] == 10
    assert packet["ui_auto_refresh"] is True
    assert packet["fragment_refresh_enabled"] is True
    assert packet["page_reload_enabled"] is False
    assert packet["observation_cleanup_state"] == "operator_quick_status_visible_display_only"
    assert packet["latest_prediction_observation_status"] == "ready_for_operator_review"
    assert packet["implementation_gate_review_result"] == "blocked_not_ready_to_enable"
    assert packet["quick_status_refresh_heartbeat_utc"] < packet["later_refresh_heartbeat_utc_1"] < packet["later_refresh_heartbeat_utc_2"]
    for check in PASS_CHECKS:
        assert check in packet["pass_checks"]
    for key in FALSE_BOUNDARIES:
        assert packet[key] is False, key
