# path: ./tools/test_phase4a_prediction_system_ps_q26y_market_regime_card_renderer_shell.py
# desc: Focused pytest guard for PS-Q26Y market regime card renderer shell.

from __future__ import annotations

from tools.diagnose_phase4a_prediction_system_ps_q26y_market_regime_card_renderer_shell import run_market_regime_card_renderer_shell_diagnostic


def test_q26y_market_regime_card_renderer_shell_diagnostic_ready() -> None:
    result = run_market_regime_card_renderer_shell_diagnostic()
    assert result["ok"] is True
    assert result["ready"] is True, result["blockers"]
    assert result["blockers"] == []
    packet = result["packet"]
    assert packet["card_count"] == 8
    assert packet["horizons"][-1] == "24時間後"
    assert packet["sample_data_only"] is True
    assert packet["live_data_connected"] is False
    assert packet["warroom_page_changed"] is False
    assert packet["warroom_page_mounted"] is False
    assert packet["freshness_encoded_by_badge_only"] is True
    assert packet["border_meaning"] == "evidence_quality"
    safety = result["safety"]
    assert safety["read_only"] is True
    assert safety["display_only"] is True
    assert safety["non_executing"] is True
    for key in ("runtime_read_allowed", "runtime_artifact_write_allowed", "status_artifact_write_allowed", "prediction_artifact_write_allowed", "view_artifact_write_allowed", "scheduler_enabled", "producer_enabled", "autotrade_trigger_allowed", "broker_private_api_allowed", "ledger_append_allowed", "mode_apply_allowed", "parameter_apply_allowed", "would_send_to_broker"):
        assert safety[key] is False
