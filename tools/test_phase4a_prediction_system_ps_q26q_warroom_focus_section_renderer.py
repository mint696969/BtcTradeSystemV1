# path: ./tools/test_phase4a_prediction_system_ps_q26q_warroom_focus_section_renderer.py
# desc: Focused pytest guard for PS-Q26Q WarRoom focus section renderer.

from __future__ import annotations

from tools.diagnose_phase4a_prediction_system_ps_q26q_warroom_focus_section_renderer import run_warroom_focus_section_renderer_diagnostic


def test_q26q_focus_section_renderer_diagnostic_ready() -> None:
    result = run_warroom_focus_section_renderer_diagnostic()
    assert result["ok"] is True
    assert result["ready"] is True, result["blockers"]
    assert result["blockers"] == []
    packet = result["packet"]
    assert packet["section_renderer_externalized"] is True
    assert packet["uses_externalized_layout_policy_module"] is True
    assert packet["warroom_page_change_boundary"] == "import_and_focus_section_renderer_calls_only"
    assert packet["section_count"] == 7
    safety = result["safety"]
    assert safety["read_only"] is True
    assert safety["display_only"] is True
    assert safety["non_executing"] is True
    for key in ("runtime_artifact_write_allowed", "status_artifact_write_allowed", "prediction_artifact_write_allowed", "view_artifact_write_allowed", "scheduler_enabled", "producer_enabled", "autotrade_trigger_allowed", "broker_private_api_allowed", "ledger_append_allowed", "mode_apply_allowed", "parameter_apply_allowed", "would_send_to_broker"):
        assert safety[key] is False
