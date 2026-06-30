# path: ./tools/test_phase4a_prediction_system_ps_q25o_warroom_prediction_screenshot_review_intake_readiness.py
# desc: Focused pytest guard for PS-Q25O WarRoom prediction screenshot review intake readiness.

from __future__ import annotations

import json
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.diagnose_phase4a_prediction_system_ps_q25o_warroom_prediction_screenshot_review_intake_readiness import run_warroom_prediction_screenshot_review_intake_readiness_diagnostic  # noqa: E402

DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q25O_WARROOM_PREDICTION_SCREENSHOT_REVIEW_INTAKE_READINESS_2026-06-30.md"


def test_q25o_doc_markers() -> None:
    text = DOC.read_text(encoding="utf-8-sig")
    for marker in ("ps_q25o_warroom_prediction_screenshot_review_intake_readiness=true", "screenshot_review_intake_packet_added=true", "actual_screenshot_supplied=false", "actual_screenshot_review_performed=false", "actual_screenshot_review_required_before_visual_final=true", "q25j_density_tuning_review_target=true", "producer_cadence_changed=false", "scheduler_action_changed=false", "broker_private_api_allowed=false"):
        assert marker in text, marker


def test_q25o_diagnostic_ready() -> None:
    result = run_warroom_prediction_screenshot_review_intake_readiness_diagnostic()
    assert result["ok"] is True
    assert result["ready"] is True, result["blockers"]
    assert result["blockers"] == []
    packet = result["packet"]
    assert packet["actual_screenshot_supplied"] is False
    assert packet["actual_screenshot_review_performed"] is False
    assert packet["actual_screenshot_review_required_before_visual_final"] is True
    assert packet["required_screenshot_area_count"] == 8
    assert packet["acceptance_check_count"] == 9
    assert packet["q25j_density_tuning_review_target"] is True
    assert packet["safe_default_option_id"] == "keep_current_300s_context_only_until_gate"
    safety = result["safety"]
    assert safety["production_code_changed"] is False
    assert safety["read_only_review_intake"] is True
    assert safety["planning_only"] is True
    for key in ("producer_cadence_changed", "scheduler_action_changed", "scheduler_enabled", "producer_enabled", "runtime_artifact_write_allowed", "status_artifact_write_allowed", "prediction_artifact_write_allowed", "view_artifact_write_allowed", "latest_manifest_written", "run_sidecars_written", "autotrade_trigger_allowed", "broker_private_api_allowed", "ledger_append_allowed", "mode_apply_allowed", "parameter_apply_allowed", "would_send_to_broker"):
        assert safety[key] is False


if __name__ == "__main__":
    test_q25o_doc_markers()
    test_q25o_diagnostic_ready()
    print(json.dumps({"ok": True}, ensure_ascii=False))
