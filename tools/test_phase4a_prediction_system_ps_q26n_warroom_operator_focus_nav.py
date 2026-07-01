# path: ./tools/test_phase4a_prediction_system_ps_q26n_warroom_operator_focus_nav.py
# desc: Focused pytest guard for PS-Q26N WarRoom operator focus navigation.

from __future__ import annotations

from tools.diagnose_phase4a_prediction_system_ps_q26n_warroom_operator_focus_nav import run_warroom_operator_focus_nav_diagnostic


def test_q26n_focus_nav_diagnostic_ready() -> None:
    result = run_warroom_operator_focus_nav_diagnostic()
    assert result["ok"] is True
    assert result["ready"] is True, result["blockers"]
    assert result["blockers"] == []
    packet = result["packet"]
    assert packet["row_count"] == 5
    assert packet["operator_first_navigation_visible"] is True
    assert packet["top_expanded_default"] is True
    assert packet["layout_only_change"] is True
    assert packet["externalized_panel_module"] is True
    safety = result["safety"]
    assert safety["production_ui_code_changed"] is True
    assert safety["warroom_page_change_boundary"] == "import_and_single_render_call_only"
    assert safety["externalized_panel_module"] is True
    assert safety["read_only"] is True
    assert safety["display_only"] is True
    assert safety["non_executing"] is True
    for key in ("runtime_artifact_write_allowed", "status_artifact_write_allowed", "prediction_artifact_write_allowed", "view_artifact_write_allowed", "scheduler_enabled", "producer_enabled", "autotrade_trigger_allowed", "broker_private_api_allowed", "ledger_append_allowed", "mode_apply_allowed", "parameter_apply_allowed", "would_send_to_broker"):
        assert safety[key] is False
