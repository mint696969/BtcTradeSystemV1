# path: ./tools/test_phase4a_prediction_system_ps_q26r_warroom_quick_status_panel_extraction.py
# desc: Focused pytest guard for PS-Q26R WarRoom quick-status panel extraction.

from __future__ import annotations

from tools.diagnose_phase4a_prediction_system_ps_q26r_warroom_quick_status_panel_extraction import run_warroom_quick_status_panel_extraction_diagnostic


def test_q26r_quick_status_panel_extraction_diagnostic_ready() -> None:
    result = run_warroom_quick_status_panel_extraction_diagnostic()
    assert result["ok"] is True
    assert result["ready"] is True, result["blockers"]
    assert result["blockers"] == []
    packet = result["packet"]
    assert packet["quick_status_implementation_externalized"] is True
    assert packet["legacy_private_api_wrappers_preserved"] is True
    assert packet["legacy_searchable_markers_preserved"] is True
    assert packet["warroom_page_change_boundary"] == "thin_compatibility_wrappers_only"
    assert packet["page_packet_matches_panel_packet"] is True
    safety = result["safety"]
    assert safety["read_only"] is True
    assert safety["display_only"] is True
    assert safety["non_executing"] is True
    for key in ("runtime_artifact_write_allowed", "status_artifact_write_allowed", "prediction_artifact_write_allowed", "view_artifact_write_allowed", "scheduler_enabled", "producer_enabled", "autotrade_trigger_allowed", "broker_private_api_allowed", "ledger_append_allowed", "mode_apply_allowed", "parameter_apply_allowed", "would_send_to_broker"):
        assert safety[key] is False
