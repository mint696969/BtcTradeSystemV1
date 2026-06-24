# path: ./tools/test_phase4a_prediction_system_ps_q18ax_latest_prediction_observation_milestone_close.py
# desc: Unit tests for PS-Q18AX latest prediction observation milestone close.

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

EVIDENCE_CHAIN = (
    "PS-Q18AQ manual UI re-smoke pass",
    "PS-Q18AT implementation-gate review blocked_not_ready_to_enable",
    "PS-Q18AU quick status visible/display-only",
    "PS-Q18AV manual UI smoke packet defined",
    "PS-Q18AW manual UI smoke execution pass",
)


def build_ps_q18ax_latest_prediction_observation_milestone_close_packet() -> dict:
    packet = {
        "ok": True,
        "ps_q18ax_close_packet_version": "prediction_warroom.latest_prediction_summary_widget.q18ax_observation_milestone_close.v1",
        "latest_prediction_observation_milestone_closed": True,
        "milestone_close_result": "closed_with_manual_ui_smoke_pass",
        "latest_prediction_observation_status": "ready_for_operator_review",
        "manual_ui_smoke_result": "pass",
        "pass_check_count": 10,
        "quick_status_visible": True,
        "quick_status_searchable": True,
        "refresh_heartbeat_advances": True,
        "fragment_refresh_enabled": True,
        "page_reload_enabled": False,
        "implementation_gate_review_result": "blocked_not_ready_to_enable",
        "implementation_gate_opened": False,
        "real_rendering_enabled": False,
        "trading_execution_behavior_changed": False,
        "uicheck_path": "tmp/uicheck/uicheck_20260624_202405_369594_warroom.json",
        "repo_head_at_uicheck": "625de736",
        "evidence_chain": list(EVIDENCE_CHAIN),
        "evidence_chain_count": len(EVIDENCE_CHAIN),
        "next_safe_slice": "archive/cleanup legacy folded preflight details or future implementation gate design; keep real rendering disabled",
    }
    packet.update({key: False for key in FALSE_BOUNDARIES})
    return packet


def test_ps_q18ax_observation_milestone_is_closed_without_runtime_enablement() -> None:
    packet = build_ps_q18ax_latest_prediction_observation_milestone_close_packet()
    assert packet["ok"] is True
    assert packet["latest_prediction_observation_milestone_closed"] is True
    assert packet["milestone_close_result"] == "closed_with_manual_ui_smoke_pass"
    assert packet["latest_prediction_observation_status"] == "ready_for_operator_review"
    assert packet["manual_ui_smoke_result"] == "pass"
    assert packet["pass_check_count"] == 10
    assert packet["quick_status_visible"] is True
    assert packet["quick_status_searchable"] is True
    assert packet["refresh_heartbeat_advances"] is True
    assert packet["fragment_refresh_enabled"] is True
    assert packet["page_reload_enabled"] is False
    assert packet["implementation_gate_review_result"] == "blocked_not_ready_to_enable"
    assert packet["implementation_gate_opened"] is False
    assert packet["real_rendering_enabled"] is False
    assert packet["trading_execution_behavior_changed"] is False
    assert packet["evidence_chain_count"] == 5
    for item in EVIDENCE_CHAIN:
        assert item in packet["evidence_chain"]
    for key in FALSE_BOUNDARIES:
        assert packet[key] is False, key
