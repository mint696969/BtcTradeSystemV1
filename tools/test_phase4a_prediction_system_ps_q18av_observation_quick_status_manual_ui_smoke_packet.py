# path: ./tools/test_phase4a_prediction_system_ps_q18av_observation_quick_status_manual_ui_smoke_packet.py
# desc: Unit tests for PS-Q18AV manual UI smoke packet for WarRoom observation quick status.

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

MANUAL_CHECKS = (
    "section_title_visible",
    "browser_find_PS_Q18AU_OBSERVATION_QUICK_STATUS",
    "browser_find_latest_prediction_observation_status",
    "browser_find_implementation_gate_blocked_not_ready_to_enable",
    "browser_find_real_render_false",
    "browser_find_component_runtime_binding_false",
    "browser_find_autotrade_false",
    "browser_find_broker_false",
    "refresh_heartbeat_utc_advances_after_10_to_15_seconds",
    "no_broad_page_whiteout_or_full_reload_observed",
)


def build_ps_q18av_observation_quick_status_manual_ui_smoke_packet() -> dict:
    packet = {
        "ok": True,
        "ps_q18av_manual_ui_smoke_packet_version": "prediction_warroom.latest_prediction_summary_widget.q18av_observation_quick_status_manual_ui_smoke_packet.v1",
        "manual_ui_smoke_expected_result": "pass_if_all_checks_true",
        "launch_command_script": "tools/run_operator_ui_sr_fx_dhot.ps1",
        "launch_command_port": 501,
        "target_page": "warroom",
        "target_section_title": "Prediction WarRoom latest summary observation quick status",
        "plain_text_token": "PS_Q18AU_OBSERVATION_QUICK_STATUS",
        "required_browser_find_tokens": [
            "PS_Q18AU_OBSERVATION_QUICK_STATUS",
            "latest_prediction_observation_status",
            "implementation_gate=blocked_not_ready_to_enable",
            "real_render=false",
            "component_runtime_binding=false",
            "autotrade=false",
            "broker=false",
        ],
        "manual_checks": list(MANUAL_CHECKS),
        "manual_check_count": len(MANUAL_CHECKS),
        "required_wait_seconds_min": 10,
        "required_wait_seconds_max": 15,
        "evidence_required": ["screenshots", "repo_head", "repo_status"],
        "optional_evidence": ["tmp/uicheck/*_warroom.json"],
        "next_safe_slice": "PS-Q18AW manual UI smoke execution record after operator evidence is supplied",
    }
    packet.update({key: False for key in FALSE_BOUNDARIES})
    return packet


def test_ps_q18av_manual_ui_smoke_packet_defines_required_checks() -> None:
    packet = build_ps_q18av_observation_quick_status_manual_ui_smoke_packet()
    assert packet["ok"] is True
    assert packet["manual_ui_smoke_expected_result"] == "pass_if_all_checks_true"
    assert packet["launch_command_script"] == "tools/run_operator_ui_sr_fx_dhot.ps1"
    assert packet["launch_command_port"] == 501
    assert packet["target_page"] == "warroom"
    assert packet["plain_text_token"] == "PS_Q18AU_OBSERVATION_QUICK_STATUS"
    assert packet["manual_check_count"] == 10
    assert packet["required_wait_seconds_min"] == 10
    assert packet["required_wait_seconds_max"] == 15
    for token in (
        "PS_Q18AU_OBSERVATION_QUICK_STATUS",
        "latest_prediction_observation_status",
        "implementation_gate=blocked_not_ready_to_enable",
        "real_render=false",
        "component_runtime_binding=false",
        "autotrade=false",
        "broker=false",
    ):
        assert token in packet["required_browser_find_tokens"]
    for key in FALSE_BOUNDARIES:
        assert packet[key] is False, key
