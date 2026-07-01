# path: ./tools/test_phase4a_prediction_system_ps_q27c_market_regime_card_selected_detail_panel.py
# desc: Focused pytest guard for PS-Q27C market regime card detail overlay.

from __future__ import annotations

from tools.diagnose_phase4a_prediction_system_ps_q27c_market_regime_card_selected_detail_panel import run_market_regime_card_selected_detail_panel_diagnostic


def test_q27c_market_regime_card_detail_overlay_ready() -> None:
    result = run_market_regime_card_selected_detail_panel_diagnostic()
    assert result["ok"] is True
    assert result["ready"] is True, result["blockers"]
    assert result["blockers"] == []
    assert result["q27b_ready"] is True
    assert result["q27a_ready"] is True
    assert result["q26z_ready"] is True
    packet = result["packet"]
    assert packet["detail_disclosure_mode"] == "card_overlay"
    assert packet["card_detail_overlay_enabled"] is True
    assert packet["overlay_covers_card_row"] is True
    assert packet["overlay_close_button_enabled"] is True
    assert packet["selected_detail_panel_enabled"] is False
    assert packet["detail_popover_enabled"] is False
    assert packet["inline_detail_expansion_enabled"] is False
    assert packet["no_vertical_layout_shift_on_detail_open"] is True
    assert packet["card_width_px"] == 208
    assert packet["horizon_font_size_rem"] == "0.92rem"
    assert packet["sample_data_only"] is True
    assert packet["live_data_connected"] is False
    safety = result["safety"]
    assert safety["visual_interaction_tune_only"] is True
    assert safety["warroom_page_changed"] is False
    assert safety["warroom_page_mounted_unchanged"] is True
    assert safety["detail_disclosure_mode"] == "card_overlay"
    for key in ("runtime_read_allowed", "runtime_artifact_write_allowed", "status_artifact_write_allowed", "prediction_artifact_write_allowed", "view_artifact_write_allowed", "scheduler_enabled", "producer_enabled", "autotrade_trigger_allowed", "broker_private_api_allowed", "ledger_append_allowed", "mode_apply_allowed", "parameter_apply_allowed", "would_send_to_broker"):
        assert safety[key] is False
