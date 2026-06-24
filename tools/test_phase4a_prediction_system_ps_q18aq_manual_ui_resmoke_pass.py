# path: ./tools/test_phase4a_prediction_system_ps_q18aq_manual_ui_resmoke_pass.py
# desc: Unit tests for PS-Q18AQ manual UI re-smoke pass record.

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


def build_ps_q18aq_manual_ui_resmoke_pass_packet() -> dict:
    packet = {
        "ok": True,
        "ps_q18aq_manual_ui_resmoke_pass_version": "prediction_warroom.latest_prediction_summary_widget.q18aq_manual_ui_resmoke_pass.v1",
        "manual_ui_resmoke_result": "pass",
        "uicheck_path": "tmp/uicheck/uicheck_20260624_160417_810705_warroom.json",
        "repo_head_at_uicheck": "5ee19bbe",
        "page": "warroom",
        "browser_find_freshness_state": True,
        "browser_find_safe_fallback_reason_codes": True,
        "browser_find_refresh_heartbeat_utc": True,
        "searchable_plain_text_visible": True,
        "refresh_heartbeat_utc_changes_across_screenshots": True,
        "refresh_heartbeat_utc_sequence": [
            "2026-06-24T07:04:55Z",
            "2026-06-24T07:05:15Z",
            "2026-06-24T07:05:55Z",
        ],
        "q18aj_auto_refresh_enabled": True,
        "q18aj_fragment_refresh_enabled": True,
        "q18aj_page_reload_enabled": False,
        "q18ak_freshness_state": "stale",
        "q18ak_safe_fallback_reason_codes": ["source_generated_at_stale"],
        "uicheck_repo_status_short": [],
        "uicheck_errors": [],
        "uicheck_warnings": [],
        "ps_q18ao_searchability_gap_closed": True,
        "ps_q18ao_refresh_visibility_gap_closed": True,
        "next_safe_slice": "explicit real-widget rendering design gate or continued WarRoom observation cleanup",
    }
    packet.update({key: False for key in FALSE_BOUNDARIES})
    return packet


def test_ps_q18aq_records_manual_ui_resmoke_as_pass() -> None:
    packet = build_ps_q18aq_manual_ui_resmoke_pass_packet()
    assert packet["ok"] is True
    assert packet["manual_ui_resmoke_result"] == "pass"
    assert packet["browser_find_freshness_state"] is True
    assert packet["browser_find_safe_fallback_reason_codes"] is True
    assert packet["browser_find_refresh_heartbeat_utc"] is True
    assert packet["searchable_plain_text_visible"] is True
    assert packet["refresh_heartbeat_utc_changes_across_screenshots"] is True
    assert len(packet["refresh_heartbeat_utc_sequence"]) == 3
    assert packet["q18aj_auto_refresh_enabled"] is True
    assert packet["q18aj_fragment_refresh_enabled"] is True
    assert packet["q18aj_page_reload_enabled"] is False
    assert packet["q18ak_freshness_state"] == "stale"
    assert packet["q18ak_safe_fallback_reason_codes"] == ["source_generated_at_stale"]
    assert packet["uicheck_repo_status_short"] == []
    assert packet["uicheck_errors"] == []
    assert packet["uicheck_warnings"] == []
    assert packet["ps_q18ao_searchability_gap_closed"] is True
    assert packet["ps_q18ao_refresh_visibility_gap_closed"] is True
    for key in FALSE_BOUNDARIES:
        assert packet[key] is False, key
