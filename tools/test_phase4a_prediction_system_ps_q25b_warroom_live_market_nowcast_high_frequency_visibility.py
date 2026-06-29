# path: ./tools/test_phase4a_prediction_system_ps_q25b_warroom_live_market_nowcast_high_frequency_visibility.py
# desc: Focused pytest guard for PS-Q25B WarRoom Live Market Nowcast high-frequency visibility.

from __future__ import annotations

import json
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "btcts_next" / "src"
for candidate in (REPO_ROOT, SRC_ROOT):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

from tools.diagnose_phase4a_prediction_system_ps_q25b_warroom_live_market_nowcast_high_frequency_visibility import (  # noqa: E402
    run_warroom_live_market_nowcast_high_frequency_visibility_diagnostic,
)

DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q25B_WARROOM_LIVE_MARKET_NOWCAST_HIGH_FREQUENCY_VISIBILITY_2026-06-30.md"
PANEL = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/warroom_live_market_nowcast_panel.py"
WARROOM = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py"


def test_q25b_doc_markers() -> None:
    text = DOC.read_text(encoding="utf-8-sig")
    for marker in (
        "ps_q25b_warroom_live_market_nowcast_high_frequency_visibility=true",
        "warroom_live_market_nowcast_panel_added=true",
        "warroom_page_live_nowcast_panel_mounted=true",
        "current_state_not_prediction=true",
        "high_frequency_fragment_refresh_mode=poll_fast",
        "high_frequency_fragment_refresh_sec=3",
        "best_bid_visible=true",
        "best_ask_visible=true",
        "spread_visible=true",
        "spread_bps_visible=true",
        "market_event_age_visible=true",
        "ws_board_state_visible=true",
        "ws_executions_state_visible=true",
        "collector_health_visible=true",
        "gap_resync_visible=true",
        "attention_flags_visible=true",
        "runtime_artifact_write_allowed=false",
        "scheduler_action_changed=false",
        "autotrade_trigger_allowed=false",
        "broker_private_api_allowed=false",
    ):
        assert marker in text, marker


def test_q25b_diagnostic_ready() -> None:
    result = run_warroom_live_market_nowcast_high_frequency_visibility_diagnostic()
    assert result["ok"] is True
    assert result["ready"] is True, result["blockers"]
    assert result["blockers"] == []
    packet = result["packet"]
    assert packet["nowcast_panel_version"] == "prediction_warroom.live_market_nowcast_panel.ps_q25b.v1"
    assert packet["nowcast_role"] == "current_market_state_not_prediction"
    assert packet["refresh_mode"] == "poll_fast"
    assert packet["refresh_interval_sec"] == 3
    assert packet["current_state_summary"] == "current_market_state_live_observable"
    assert packet["nowcast_freshness_state"] in {"live", "slightly_delayed"}
    assert packet["best_bid"] == 9779378.0
    assert packet["best_ask"] == 9782310.0
    assert packet["spread"] == 2932.0
    assert packet["spread_bps"] is not None
    assert packet["market_event_age_sec"] == 8
    assert packet["ws_state"] == "LIVE"
    assert packet["ws_executions_state"] == "LIVE"
    assert packet["attention_flags"] == []
    safety = result["safety"]
    assert safety["warroom_display_only"] is True
    assert safety["current_state_not_prediction"] is True
    for key in (
        "runtime_artifact_write_allowed",
        "status_artifact_write_allowed",
        "prediction_artifact_write_allowed",
        "view_artifact_write_allowed",
        "scheduler_action_changed",
        "scheduler_enabled",
        "autotrade_trigger_allowed",
        "broker_private_api_allowed",
        "ledger_append_allowed",
        "mode_apply_allowed",
        "parameter_apply_allowed",
        "would_send_to_broker",
    ):
        assert safety[key] is False


def test_q25b_panel_mounted_in_warroom_and_safe_tokens() -> None:
    warroom_text = WARROOM.read_text(encoding="utf-8")
    panel_text = PANEL.read_text(encoding="utf-8")
    assert "render_warroom_live_market_nowcast_panel" in warroom_text
    assert "PS-Q25B Live Market Nowcast" in warroom_text
    assert "live_shell.render_fragment_slot" in panel_text
    assert "poll_fast" in panel_text
    assert "Q25B_DEFAULT_HOT_ROOT_HINT = r\"D:\\btc_ts_hot\"" in panel_text
    for forbidden in (
        "Set-ScheduledTask",
        "Enable-ScheduledTask",
        "Disable-ScheduledTask",
        "Register-ScheduledTask",
        "New-ScheduledTaskTrigger",
        "append_decision_jsonl",
        "run_shadow_decision_from_snapshot",
        "submit_mode_change_command_request",
        "validate_and_append_command",
        "send_order(",
        "place_order(",
        "create_order(",
        ".write_text(",
        ".write_bytes(",
        "os.replace",
        "shutil.copy2",
    ):
        assert forbidden not in panel_text, forbidden


if __name__ == "__main__":
    test_q25b_doc_markers()
    test_q25b_diagnostic_ready()
    test_q25b_panel_mounted_in_warroom_and_safe_tokens()
    print(json.dumps({"ok": True}, ensure_ascii=False))
