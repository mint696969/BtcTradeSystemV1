# path: ./tools/test_phase4a_prediction_system_ps_q26p_warroom_secondary_detail_folding.py
# desc: Focused pytest guard for PS-Q26P WarRoom secondary detail folding.

from __future__ import annotations

from tools.diagnose_phase4a_prediction_system_ps_q26p_warroom_secondary_detail_folding import run_warroom_secondary_detail_folding_diagnostic


def test_q26p_secondary_detail_folding_diagnostic_ready() -> None:
    result = run_warroom_secondary_detail_folding_diagnostic()
    assert result["ok"] is True
    assert result["ready"] is True, result["blockers"]
    assert result["blockers"] == []
    packet = result["packet"]
    assert packet["secondary_detail_sections_folded_default"] is True
    assert packet["market_evidence_detail_folded_default"] is True
    assert packet["operator_support_detail_folded_default"] is True
    assert packet["header_alert_operator_expanded_default"] is True
    safety = result["safety"]
    assert safety["warroom_page_change_boundary"] == "import_and_policy_lookup_only"
    assert safety["read_only"] is True
    assert safety["display_only"] is True
    assert safety["non_executing"] is True
    for key in ("runtime_artifact_write_allowed", "status_artifact_write_allowed", "prediction_artifact_write_allowed", "view_artifact_write_allowed", "scheduler_enabled", "producer_enabled", "autotrade_trigger_allowed", "broker_private_api_allowed", "ledger_append_allowed", "mode_apply_allowed", "parameter_apply_allowed", "would_send_to_broker"):
        assert safety[key] is False
