# path: ./tools/test_phase4a_prediction_system_ps_q26z_market_regime_card_warroom_mount_sample_only.py
# desc: Focused pytest guard for PS-Q26Z sample-only market regime card WarRoom mount.

from __future__ import annotations

from tools.diagnose_phase4a_prediction_system_ps_q26z_market_regime_card_warroom_mount_sample_only import run_market_regime_card_warroom_mount_sample_only_diagnostic


def test_q26z_market_regime_card_warroom_mount_sample_only_ready() -> None:
    result = run_market_regime_card_warroom_mount_sample_only_diagnostic()
    assert result["ok"] is True
    assert result["ready"] is True, result["blockers"]
    assert result["blockers"] == []
    assert result["policy_section_count"] == 8
    assert result["section_renderer_count"] == 8
    renderer = result["renderer_packet"]
    assert renderer["sample_data_only"] is True
    assert renderer["live_data_connected"] is False
    assert renderer["runtime_read_allowed"] is False
    assert renderer["card_count"] == 8
    safety = result["safety"]
    assert safety["warroom_page_changed"] is True
    assert safety["warroom_page_mounted"] is True
    assert safety["streamlit_render_invoked_by_page"] is True
    assert safety["read_only"] is True
    assert safety["display_only"] is True
    assert safety["non_executing"] is True
    for key in ("runtime_read_allowed", "runtime_artifact_write_allowed", "status_artifact_write_allowed", "prediction_artifact_write_allowed", "view_artifact_write_allowed", "scheduler_enabled", "producer_enabled", "autotrade_trigger_allowed", "broker_private_api_allowed", "ledger_append_allowed", "mode_apply_allowed", "parameter_apply_allowed", "would_send_to_broker"):
        assert safety[key] is False
