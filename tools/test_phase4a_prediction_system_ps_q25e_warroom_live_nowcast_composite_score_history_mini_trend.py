# path: ./tools/test_phase4a_prediction_system_ps_q25e_warroom_live_nowcast_composite_score_history_mini_trend.py
# desc: Focused pytest guard for PS-Q25E WarRoom Live Nowcast composite score and session mini-trend.

from __future__ import annotations

import json
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "btcts_next" / "src"
for candidate in (REPO_ROOT, SRC_ROOT):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

from tools.diagnose_phase4a_prediction_system_ps_q25e_warroom_live_nowcast_composite_score_history_mini_trend import (  # noqa: E402
    run_warroom_live_nowcast_composite_score_history_mini_trend_diagnostic,
)

DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q25E_WARROOM_LIVE_NOWCAST_COMPOSITE_SCORE_HISTORY_MINI_TREND_2026-06-30.md"
PANEL = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/warroom_live_market_nowcast_panel.py"


def test_q25e_doc_markers() -> None:
    text = DOC.read_text(encoding="utf-8-sig")
    for marker in (
        "ps_q25e_warroom_live_nowcast_composite_score_history_mini_trend=true",
        "warroom_live_nowcast_composite_score_added=true",
        "current_state_score_visible=true",
        "current_state_score_grade_visible=true",
        "current_state_score_note_visible=true",
        "penalty_reasons_visible=true",
        "mini_trend_visible=true",
        "history_sample_count_visible=true",
        "session_state_history_only=true",
        "persistent_history_artifact_written=false",
        "current_state_not_prediction=true",
        "runtime_artifact_write_allowed=false",
        "scheduler_action_changed=false",
        "autotrade_trigger_allowed=false",
        "broker_private_api_allowed=false",
    ):
        assert marker in text, marker


def test_q25e_diagnostic_ready() -> None:
    result = run_warroom_live_nowcast_composite_score_history_mini_trend_diagnostic()
    assert result["ok"] is True
    assert result["ready"] is True, result["blockers"]
    assert result["blockers"] == []
    normal = result["normal_composite"]
    warning = result["warning_composite"]
    critical = result["critical_composite"]
    mini = result["mini_trend"]
    assert normal["composite_score_version"] == "prediction_warroom.live_nowcast_composite_score_history_mini_trend.ps_q25e.v1"
    assert normal["nowcast_role"] == "current_market_state_not_prediction"
    assert isinstance(normal["current_state_score"], int)
    assert 0 <= normal["current_state_score"] <= 100
    assert warning["current_state_score"] < normal["current_state_score"]
    assert critical["current_state_score"] < warning["current_state_score"]
    assert mini["history_sample_count"] == 2
    assert mini["current_state_score_trend"] in {"improving", "stable", "deteriorating", "insufficient_history"}
    safety = result["safety"]
    assert safety["warroom_display_only"] is True
    assert safety["session_state_history_only"] is True
    assert safety["persistent_history_artifact_written"] is False
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


def test_q25e_panel_safe_and_render_markers() -> None:
    text = PANEL.read_text(encoding="utf-8")
    for marker in (
        "WARROOM_LIVE_NOWCAST_COMPOSITE_SCORE_VERSION",
        "WARROOM_LIVE_NOWCAST_HISTORY_SESSION_KEY",
        "build_warroom_live_nowcast_composite_score_packet",
        "build_warroom_live_nowcast_history_mini_trend_packet",
        "warroom_live_nowcast_composite_score_rows",
        "_render_warroom_live_nowcast_composite_score",
        "current_state_score_trend",
    ):
        assert marker in text, marker
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
        assert forbidden not in text, forbidden


if __name__ == "__main__":
    test_q25e_doc_markers()
    test_q25e_diagnostic_ready()
    test_q25e_panel_safe_and_render_markers()
    print(json.dumps({"ok": True}, ensure_ascii=False))
