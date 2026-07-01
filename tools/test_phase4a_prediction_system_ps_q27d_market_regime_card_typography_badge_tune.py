# path: ./tools/test_phase4a_prediction_system_ps_q27d_market_regime_card_typography_badge_tune.py
# desc: Focused pytest guard for PS-Q27D market regime card typography and freshness badge tune.

from __future__ import annotations

from tools.diagnose_phase4a_prediction_system_ps_q27d_market_regime_card_typography_badge_tune import run_market_regime_card_typography_badge_tune_diagnostic


def test_q27d_market_regime_card_typography_badge_tune_ready() -> None:
    result = run_market_regime_card_typography_badge_tune_diagnostic()
    assert result["ok"] is True
    assert result["ready"] is True, result["blockers"]
    assert result["blockers"] == []
    assert result["q27c_ready"] is True
    assert result["q27b_ready"] is True
    packet = result["packet"]
    assert packet["time_axis_font_size_unchanged"] is True
    assert packet["horizon_font_size_rem"] == "0.92rem"
    assert packet["regime_font_size_rem"] == "1.14rem"
    assert packet["confidence_font_size_rem"] == "1.60rem"
    assert packet["tag_font_size_rem"] == "1.04rem"
    assert packet["freshness_badge_visibility_tuned"] is True
    assert packet["freshness_badge_font_size_rem"] == "0.78rem"
    assert packet["freshness_badge_font_weight"] == 900
    assert packet["freshness_badge_min_width_px"] == 42
    assert packet["detail_overlay_background"] == "#F2F4F7"
    assert packet["detail_overlay_background_matches_unknown"] is True
    assert packet["detail_disclosure_mode"] == "card_overlay"
    assert packet["sample_data_only"] is True
    assert packet["live_data_connected"] is False
    safety = result["safety"]
    assert safety["visual_typography_tune_only"] is True
    assert safety["warroom_page_changed"] is False
    assert safety["time_axis_font_size_unchanged"] is True
    for key in ("runtime_read_allowed", "runtime_artifact_write_allowed", "status_artifact_write_allowed", "prediction_artifact_write_allowed", "view_artifact_write_allowed", "scheduler_enabled", "producer_enabled", "autotrade_trigger_allowed", "broker_private_api_allowed", "ledger_append_allowed", "mode_apply_allowed", "parameter_apply_allowed", "would_send_to_broker"):
        assert safety[key] is False
