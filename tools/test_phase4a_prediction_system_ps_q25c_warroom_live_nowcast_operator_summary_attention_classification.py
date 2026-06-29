# path: ./tools/test_phase4a_prediction_system_ps_q25c_warroom_live_nowcast_operator_summary_attention_classification.py
# desc: Focused pytest guard for PS-Q25C WarRoom Live Nowcast operator summary and attention classification.

from __future__ import annotations

import json
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "btcts_next" / "src"
for candidate in (REPO_ROOT, SRC_ROOT):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

from tools.diagnose_phase4a_prediction_system_ps_q25c_warroom_live_nowcast_operator_summary_attention_classification import (  # noqa: E402
    run_warroom_live_nowcast_operator_summary_attention_classification_diagnostic,
)

DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q25C_WARROOM_LIVE_NOWCAST_OPERATOR_SUMMARY_ATTENTION_CLASSIFICATION_2026-06-30.md"
PANEL = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/warroom_live_market_nowcast_panel.py"


def test_q25c_doc_markers() -> None:
    text = DOC.read_text(encoding="utf-8-sig")
    for marker in (
        "ps_q25c_warroom_live_nowcast_operator_summary_attention_classification=true",
        "warroom_live_nowcast_operator_summary_added=true",
        "operator_state_grade_visible=true",
        "operator_attention_severity_visible=true",
        "operator_summary_text_visible=true",
        "operator_instruction_text_visible=true",
        "attention_rows_visible=true",
        "current_state_not_prediction=true",
        "live_observable_grade_supported=true",
        "usable_with_caution_grade_supported=true",
        "not_usable_for_current_decision_grade_supported=true",
        "review_required_grade_supported=true",
        "runtime_artifact_write_allowed=false",
        "scheduler_action_changed=false",
        "autotrade_trigger_allowed=false",
        "broker_private_api_allowed=false",
    ):
        assert marker in text, marker


def test_q25c_diagnostic_ready() -> None:
    result = run_warroom_live_nowcast_operator_summary_attention_classification_diagnostic()
    assert result["ok"] is True
    assert result["ready"] is True, result["blockers"]
    assert result["blockers"] == []
    normal = result["normal_summary"]
    warning = result["warning_summary"]
    critical = result["critical_summary"]
    assert normal["operator_summary_version"] == "prediction_warroom.live_nowcast_operator_summary.ps_q25c.v1"
    assert normal["operator_state_grade"] == "live_observable"
    assert normal["operator_attention_severity"] == "ok"
    assert normal["attention_flag_count"] == 0
    assert "予測ではなく" in normal["operator_instruction_text"]
    assert warning["operator_state_grade"] == "usable_with_caution"
    assert warning["operator_attention_severity"] == "warning"
    assert warning["attention_flag_count"] >= 1
    assert critical["operator_state_grade"] == "not_usable_for_current_decision"
    assert critical["operator_attention_severity"] == "critical"
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


def test_q25c_panel_safe_and_render_markers() -> None:
    text = PANEL.read_text(encoding="utf-8")
    for marker in (
        "WARROOM_LIVE_NOWCAST_OPERATOR_SUMMARY_VERSION",
        "classify_warroom_live_nowcast_attention",
        "build_warroom_live_nowcast_operator_summary_packet",
        "_render_warroom_live_nowcast_operator_summary",
        "operator_state_grade",
        "operator_attention_severity",
        "current_market_state_not_prediction",
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
    test_q25c_doc_markers()
    test_q25c_diagnostic_ready()
    test_q25c_panel_safe_and_render_markers()
    print(json.dumps({"ok": True}, ensure_ascii=False))
