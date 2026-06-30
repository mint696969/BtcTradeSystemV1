# path: ./tools/test_phase4a_prediction_system_ps_q25p_warroom_prediction_actual_screenshot_review_record.py
# desc: Focused pytest guard for PS-Q25P WarRoom prediction actual screenshot review record.

from __future__ import annotations

import json
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.diagnose_phase4a_prediction_system_ps_q25p_warroom_prediction_actual_screenshot_review_record import run_warroom_prediction_actual_screenshot_review_record_diagnostic  # noqa: E402

DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q25P_WARROOM_PREDICTION_ACTUAL_SCREENSHOT_REVIEW_RECORD_2026-06-30.md"


def test_q25p_doc_markers() -> None:
    text = DOC.read_text(encoding="utf-8-sig")
    for marker in ("ps_q25p_warroom_prediction_actual_screenshot_review_record=true", "actual_screenshot_review_record_added=true", "actual_screenshot_supplied=true", "actual_screenshot_review_performed=true", "visual_review_result=pass_for_operator_review_not_trade_decision", "q25j_density_tuning_reviewed=true", "production_code_changed=false", "producer_cadence_changed=false", "scheduler_action_changed=false", "broker_private_api_allowed=false"):
        assert marker in text, marker


def test_q25p_diagnostic_ready() -> None:
    result = run_warroom_prediction_actual_screenshot_review_record_diagnostic()
    assert result["ok"] is True
    assert result["ready"] is True, result["blockers"]
    assert result["blockers"] == []
    packet = result["packet"]
    assert packet["actual_screenshot_supplied"] is True
    assert packet["actual_screenshot_review_performed"] is True
    assert packet["actual_screenshot_count"] == 6
    assert packet["visual_review_result"] == "pass_for_operator_review_not_trade_decision"
    assert packet["visual_final_candidate"] is True
    assert packet["visual_final_blocker_count"] == 0
    assert packet["q25j_density_tuning_reviewed"] is True
    for key in ("compact_header_first", "detail_checks_folded_by_default", "detail_checks_expandable", "reading_guide_folded_by_default", "prediction_metrics_visible", "prediction_rows_visible", "operator_action_guidance_visible_or_accessible", "horizon_expiry_visible_or_accessible", "no_nested_expander_runtime_error_observed", "no_autotrade_or_broker_control_added"):
        assert packet[key] is True
    safety = result["safety"]
    assert safety["production_code_changed"] is False
    assert safety["read_only_review_record"] is True
    assert safety["planning_only"] is True
    for key in ("producer_cadence_changed", "scheduler_action_changed", "scheduler_enabled", "producer_enabled", "runtime_artifact_write_allowed", "status_artifact_write_allowed", "prediction_artifact_write_allowed", "view_artifact_write_allowed", "latest_manifest_written", "run_sidecars_written", "autotrade_trigger_allowed", "broker_private_api_allowed", "ledger_append_allowed", "mode_apply_allowed", "parameter_apply_allowed", "would_send_to_broker"):
        assert safety[key] is False


if __name__ == "__main__":
    test_q25p_doc_markers()
    test_q25p_diagnostic_ready()
    print(json.dumps({"ok": True}, ensure_ascii=False))
