# path: ./tools/test_phase4a_prediction_system_ps_q25q_warroom_prediction_display_closeout_handoff.py
# desc: Focused pytest guard for PS-Q25Q WarRoom prediction display closeout handoff.

from __future__ import annotations

import json
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.diagnose_phase4a_prediction_system_ps_q25q_warroom_prediction_display_closeout_handoff import run_warroom_prediction_display_closeout_handoff_diagnostic  # noqa: E402

DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q25Q_WARROOM_PREDICTION_DISPLAY_CLOSEOUT_HANDOFF_2026-06-30.md"


def test_q25q_doc_markers() -> None:
    text = DOC.read_text(encoding="utf-8-sig")
    for marker in ("ps_q25q_warroom_prediction_display_closeout_handoff=true", "display_closeout_handoff_added=true", "display_lane_closed_out=true", "visual_review_recorded=true", "visual_review_result=pass_for_operator_review_not_trade_decision", "visual_final_for_operator_review=true", "trade_decision_approved=false", "execution_approval=false", "production_code_changed=false", "producer_cadence_changed=false", "scheduler_action_changed=false", "broker_private_api_allowed=false"):
        assert marker in text, marker


def test_q25q_diagnostic_ready() -> None:
    result = run_warroom_prediction_display_closeout_handoff_diagnostic()
    assert result["ok"] is True
    assert result["ready"] is True, result["blockers"]
    assert result["blockers"] == []
    packet = result["packet"]
    assert packet["display_closeout_handoff_version"] == "prediction_warroom.display_closeout_handoff.ps_q25q.v1"
    assert packet["display_lane_closed_out"] is True
    assert packet["visual_review_recorded"] is True
    assert packet["visual_review_result"] == "pass_for_operator_review_not_trade_decision"
    assert packet["visual_final_for_operator_review"] is True
    assert packet["trade_decision_approved"] is False
    assert packet["execution_approval"] is False
    assert packet["safe_stop_here"] is True
    assert packet["cadence_lane_stopped_at_human_gate"] is True
    assert packet["safe_default_option_id"] == "keep_current_300s_context_only_until_gate"
    safety = result["safety"]
    assert safety["production_code_changed"] is False
    assert safety["read_only_closeout_handoff"] is True
    assert safety["planning_only"] is True
    assert safety["trade_decision_approved"] is False
    assert safety["execution_approval"] is False
    for key in ("producer_cadence_changed", "scheduler_action_changed", "scheduler_enabled", "producer_enabled", "runtime_artifact_write_allowed", "status_artifact_write_allowed", "prediction_artifact_write_allowed", "view_artifact_write_allowed", "latest_manifest_written", "run_sidecars_written", "autotrade_trigger_allowed", "broker_private_api_allowed", "ledger_append_allowed", "mode_apply_allowed", "parameter_apply_allowed", "would_send_to_broker"):
        assert safety[key] is False


if __name__ == "__main__":
    test_q25q_doc_markers()
    test_q25q_diagnostic_ready()
    print(json.dumps({"ok": True}, ensure_ascii=False))
