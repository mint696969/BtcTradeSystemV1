# path: ./tools/test_phase4a_prediction_system_ps_q26s_warroom_operator_focus_visual_tune.py
# desc: Focused pytest guard for PS-Q26S WarRoom operator focus visual tune.

from __future__ import annotations

from tools.diagnose_phase4a_prediction_system_ps_q26s_warroom_operator_focus_visual_tune import run_warroom_operator_focus_visual_tune_diagnostic


def test_q26s_warroom_operator_focus_visual_tune_diagnostic_ready() -> None:
    result = run_warroom_operator_focus_visual_tune_diagnostic()
    assert result["ok"] is True
    assert result["ready"] is True, result["blockers"]
    assert result["blockers"] == []
    packet = result["packet"]
    assert packet["visual_route_strip_visible"] is True
    assert packet["route_row_count"] == 4
    assert packet["improves_first_screen_scanability"] is True
    assert packet["visual_only_change"] is True
    assert packet["warroom_page_changed"] is False
    safety = result["safety"]
    assert safety["warroom_page_slimming_main_goal"] is False
    assert safety["read_only"] is True
    assert safety["display_only"] is True
    assert safety["non_executing"] is True
    for key in ("runtime_artifact_write_allowed", "status_artifact_write_allowed", "prediction_artifact_write_allowed", "view_artifact_write_allowed", "scheduler_enabled", "producer_enabled", "autotrade_trigger_allowed", "broker_private_api_allowed", "ledger_append_allowed", "mode_apply_allowed", "parameter_apply_allowed", "would_send_to_broker"):
        assert safety[key] is False
