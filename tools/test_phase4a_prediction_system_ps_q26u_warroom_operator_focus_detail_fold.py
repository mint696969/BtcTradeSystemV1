# path: ./tools/test_phase4a_prediction_system_ps_q26u_warroom_operator_focus_detail_fold.py
# desc: Focused pytest guard for PS-Q26U WarRoom operator focus detail fold.

from __future__ import annotations

from tools.diagnose_phase4a_prediction_system_ps_q26u_warroom_operator_focus_detail_fold import run_warroom_operator_focus_detail_fold_diagnostic


def test_q26u_warroom_operator_focus_detail_fold_diagnostic_ready() -> None:
    result = run_warroom_operator_focus_detail_fold_diagnostic()
    assert result["ok"] is True
    assert result["ready"] is True, result["blockers"]
    assert result["blockers"] == []
    packet = result["packet"]
    assert packet["detail_table_available"] is True
    assert packet["detail_table_folded_default"] is True
    assert packet["reduces_first_screen_density"] is True
    assert packet["command_cards_visible"] is True
    assert packet["visual_route_strip_visible"] is True
    assert packet["visual_only_change"] is True
    assert packet["warroom_page_changed"] is False
    assert packet["warroom_page_slimming_main_goal"] is False
    safety = result["safety"]
    assert safety["read_only"] is True
    assert safety["display_only"] is True
    assert safety["non_executing"] is True
    for key in ("runtime_artifact_write_allowed", "status_artifact_write_allowed", "prediction_artifact_write_allowed", "view_artifact_write_allowed", "scheduler_enabled", "producer_enabled", "autotrade_trigger_allowed", "broker_private_api_allowed", "ledger_append_allowed", "mode_apply_allowed", "parameter_apply_allowed", "would_send_to_broker"):
        assert safety[key] is False
