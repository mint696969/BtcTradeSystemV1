# path: ./tools/test_phase4a_prediction_system_ps_q25n_warroom_prediction_display_cadence_gate_closeout_readiness.py
# desc: Focused pytest guard for PS-Q25N WarRoom prediction display/cadence-gate closeout readiness.

from __future__ import annotations

import json
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.diagnose_phase4a_prediction_system_ps_q25n_warroom_prediction_display_cadence_gate_closeout_readiness import run_warroom_prediction_display_cadence_gate_closeout_readiness_diagnostic  # noqa: E402

DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q25N_WARROOM_PREDICTION_DISPLAY_CADENCE_GATE_CLOSEOUT_READINESS_2026-06-30.md"


def test_q25n_doc_markers() -> None:
    text = DOC.read_text(encoding="utf-8-sig")
    for marker in ("ps_q25n_warroom_prediction_display_cadence_gate_closeout_readiness=true", "closeout_readiness_packet_added=true", "production_code_changed=false", "read_only_closeout=true", "display_lane_closeout_ready=true", "cadence_lane_stopped_at_human_gate=true", "producer_cadence_changed=false", "scheduler_action_changed=false", "broker_private_api_allowed=false"):
        assert marker in text, marker


def test_q25n_diagnostic_ready() -> None:
    result = run_warroom_prediction_display_cadence_gate_closeout_readiness_diagnostic()
    assert result["ok"] is True
    assert result["ready"] is True, result["blockers"]
    assert result["blockers"] == []
    packet = result["packet"]
    assert packet["display_lane_closeout_ready"] is True
    assert packet["cadence_lane_stopped_at_human_gate"] is True
    assert packet["safe_default_option_id"] == "keep_current_300s_context_only_until_gate"
    assert packet["actual_screenshot_review_performed"] is False
    assert packet["actual_screenshot_review_required_before_visual_final"] is True
    assert packet["q25b_to_q25m_required_doc_count"] == packet["q25b_to_q25m_existing_doc_count"]
    assert packet["missing_docs"] == []
    safety = result["safety"]
    assert safety["production_code_changed"] is False
    assert safety["read_only_closeout"] is True
    assert safety["planning_only"] is True
    for key in ("producer_cadence_changed", "scheduler_action_changed", "scheduler_enabled", "producer_enabled", "runtime_artifact_write_allowed", "status_artifact_write_allowed", "prediction_artifact_write_allowed", "view_artifact_write_allowed", "latest_manifest_written", "run_sidecars_written", "autotrade_trigger_allowed", "broker_private_api_allowed", "ledger_append_allowed", "mode_apply_allowed", "parameter_apply_allowed", "would_send_to_broker"):
        assert safety[key] is False


if __name__ == "__main__":
    test_q25n_doc_markers()
    test_q25n_diagnostic_ready()
    print(json.dumps({"ok": True}, ensure_ascii=False))
