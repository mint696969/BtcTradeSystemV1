# path: ./tools/test_phase4a_prediction_system_ps_q26w_market_regime_card_spec.py
# desc: Focused pytest guard for PS-Q26W market regime card specification foundation.

from __future__ import annotations

from tools.diagnose_phase4a_prediction_system_ps_q26w_market_regime_card_spec import run_market_regime_card_spec_diagnostic


def test_q26w_market_regime_card_spec_ready() -> None:
    result = run_market_regime_card_spec_diagnostic()
    assert result["ok"] is True
    assert result["ready"] is True, result["blockers"]
    assert result["blockers"] == []
    contract = result["contract"]
    assert contract["spec_only_change"] is True
    assert contract["production_ui_code_changed"] is False
    assert contract["runtime_code_changed"] is False
    assert contract["warroom_page_changed"] is False
    assert contract["warroom_page_slimming_main_goal"] is False
    assert contract["market_regime_first"] is True
    assert contract["future_prediction_card_reuse_expected"] is True
    assert contract["regime_count_v1"] == 9
    assert contract["has_unknown_regime"] is True
    assert contract["background_tone_is_readability_first"] is True
    assert contract["freshness_badge_required"] is True
    assert contract["freshness_not_encoded_by_border"] is True
    assert contract["border_meaning"] == "evidence_quality"
    assert contract["diagnostic_record_required"] is True
    assert contract["unknown_improvement_record_required"] is True
    assert contract["low_confidence_improvement_record_required"] is True
    assert contract["confidence_is_not_directional_win_rate"] is True
    assert contract["read_only"] is True
    assert contract["display_only"] is True
    assert contract["non_executing"] is True
    for key in ("runtime_artifact_write_allowed", "status_artifact_write_allowed", "prediction_artifact_write_allowed", "view_artifact_write_allowed", "scheduler_enabled", "producer_enabled", "autotrade_trigger_allowed", "broker_private_api_allowed", "ledger_append", "mode_apply", "parameter_apply", "would_send_to_broker"):
        assert contract[key] is False
