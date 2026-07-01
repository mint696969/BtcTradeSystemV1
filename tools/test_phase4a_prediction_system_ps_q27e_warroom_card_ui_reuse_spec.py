# path: ./tools/test_phase4a_prediction_system_ps_q27e_warroom_card_ui_reuse_spec.py
# desc: Focused pytest guard for PS-Q27E WarRoom card UI reuse spec.

from __future__ import annotations

from tools.diagnose_phase4a_prediction_system_ps_q27e_warroom_card_ui_reuse_spec import run_warroom_card_ui_reuse_spec_diagnostic


def test_q27e_warroom_card_ui_reuse_spec_ready() -> None:
    result = run_warroom_card_ui_reuse_spec_diagnostic()
    assert result["ok"] is True
    assert result["ready"] is True, result["blockers"]
    assert result["blockers"] == []
    assert result["q27d_ready"] is True
    contract = result["contract"]
    assert contract["spec_only_change"] is True
    assert contract["market_regime_card_ui_is_canonical_reference"] is True
    assert contract["future_prediction_card_reuse_expected"] is True
    assert contract["next_thread_ready_for_market_regime_live_data_binding_design"] is True
    for key in ("production_ui_code_changed", "runtime_code_changed", "warroom_page_changed", "live_data_connected", "runtime_read_allowed", "runtime_artifact_write_allowed", "status_artifact_write_allowed", "prediction_artifact_write_allowed", "view_artifact_write_allowed", "scheduler_enabled", "producer_enabled", "autotrade_trigger_allowed", "broker_private_api_allowed", "ledger_append_allowed", "mode_apply_allowed", "parameter_apply_allowed", "would_send_to_broker"):
        assert contract[key] is False
    q27d = result["q27d_head_contract"]
    assert q27d["card_width_px"] == 208
    assert q27d["horizon_font_size_rem"] == "0.92rem"
    assert q27d["regime_font_size_rem"] == "1.14rem"
    assert q27d["confidence_font_size_rem"] == "1.60rem"
    assert q27d["tag_font_size_rem"] == "1.04rem"
    assert q27d["freshness_badge_font_size_rem"] == "0.78rem"
    assert q27d["freshness_badge_font_weight"] == 900
    assert q27d["freshness_badge_min_width_px"] == 42
    assert q27d["detail_disclosure_mode"] == "card_overlay"
    assert q27d["detail_overlay_background"] == "#F2F4F7"
    assert q27d["detail_overlay_background_matches_unknown"] is True
