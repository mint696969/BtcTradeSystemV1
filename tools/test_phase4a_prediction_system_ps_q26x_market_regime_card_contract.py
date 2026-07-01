# path: ./tools/test_phase4a_prediction_system_ps_q26x_market_regime_card_contract.py
# desc: Focused pytest guard for PS-Q26X market regime card pure-data contract helpers.

from __future__ import annotations

from tools.diagnose_phase4a_prediction_system_ps_q26x_market_regime_card_contract import run_market_regime_card_contract_diagnostic


def test_q26x_market_regime_card_contract_diagnostic_ready() -> None:
    result = run_market_regime_card_contract_diagnostic()
    assert result["ok"] is True
    assert result["ready"] is True, result["blockers"]
    assert result["blockers"] == []
    report = result["contract_report"]
    assert len(report["regime_codes"]) == 9
    assert "UNKNOWN" in report["regime_codes"]
    assert report["freshness_encoded_by_badge_only"] is True
    assert report["border_meaning"] == "evidence_quality"
    assert report["diagnostic_record_required_for_unknown_and_low_confidence"] is True
    assert report["production_ui_code_changed"] is False
    assert report["warroom_page_changed"] is False
    safety = result["safety"]
    assert safety["contract_helper_only"] is True
    assert safety["read_only"] is True
    assert safety["display_only"] is True
    assert safety["non_executing"] is True
    for key in ("runtime_artifact_write_allowed", "status_artifact_write_allowed", "prediction_artifact_write_allowed", "view_artifact_write_allowed", "scheduler_enabled", "producer_enabled", "autotrade_trigger_allowed", "broker_private_api_allowed", "ledger_append_allowed", "mode_apply_allowed", "parameter_apply_allowed", "would_send_to_broker"):
        assert safety[key] is False
