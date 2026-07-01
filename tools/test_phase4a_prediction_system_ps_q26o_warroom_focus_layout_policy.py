# path: ./tools/test_phase4a_prediction_system_ps_q26o_warroom_focus_layout_policy.py
# desc: Focused pytest guard for PS-Q26O WarRoom focus layout policy.

from __future__ import annotations

from tools.diagnose_phase4a_prediction_system_ps_q26o_warroom_focus_layout_policy import run_warroom_focus_layout_policy_diagnostic


def test_q26o_focus_layout_policy_diagnostic_ready() -> None:
    result = run_warroom_focus_layout_policy_diagnostic()
    assert result["ok"] is True
    assert result["ready"] is True, result["blockers"]
    assert result["blockers"] == []
    packet = result["packet"]
    assert packet["quick_status_detail_folded_default"] is True
    assert packet["operator_focus_nav_expanded_default"] is True
    assert packet["live_nowcast_expanded_default"] is True
    assert packet["latest_prediction_read_model_expanded_default"] is True
    assert packet["externalized_layout_policy_module"] is True
    safety = result["safety"]
    assert safety["warroom_page_change_boundary"] == "import_and_policy_lookup_only"
    assert safety["read_only"] is True
    assert safety["display_only"] is True
    assert safety["non_executing"] is True
    for key in ("runtime_artifact_write_allowed", "status_artifact_write_allowed", "prediction_artifact_write_allowed", "view_artifact_write_allowed", "scheduler_enabled", "producer_enabled", "autotrade_trigger_allowed", "broker_private_api_allowed", "ledger_append_allowed", "mode_apply_allowed", "parameter_apply_allowed", "would_send_to_broker"):
        assert safety[key] is False
