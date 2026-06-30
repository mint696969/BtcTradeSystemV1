# path: ./tools/test_phase4a_prediction_system_ps_q25v_disabled_single_producer_60s_skeleton_validation.py
# desc: Focused pytest guard for PS-Q25V disabled single-producer 60s skeleton validation.

from __future__ import annotations

import json
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
SRC_ROOT = REPO_ROOT / "btcts_next" / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from tools.diagnose_phase4a_prediction_system_ps_q25v_disabled_single_producer_60s_skeleton_validation import run_disabled_single_producer_60s_skeleton_validation_diagnostic  # noqa: E402

DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q25V_DISABLED_SINGLE_PRODUCER_60S_SKELETON_VALIDATION_2026-06-30.md"


def test_q25v_doc_markers() -> None:
    text = DOC.read_text(encoding="utf-8-sig")
    for marker in ("ps_q25v_disabled_single_producer_60s_skeleton_validation=true", "selected_option_id=single_producer_60s_candidate", "selected_target_cadence_sec=60", "disabled_validation_packet_added=true", "validation_only=true", "read_only=true", "non_executing=true", "ready_for_disabled_dry_run_planning=true", "manual_one_shot_run_allowed=false", "scheduler_enablement_allowed=false", "producer_enablement_allowed=false", "broker_private_api_allowed=false"):
        assert marker in text, marker


def test_q25v_diagnostic_ready_and_safe() -> None:
    result = run_disabled_single_producer_60s_skeleton_validation_diagnostic()
    assert result["ok"] is True
    assert result["ready"] is True, result["blockers"]
    assert result["blockers"] == []
    packet = result["packet"]
    assert packet["selected_option_id"] == "single_producer_60s_candidate"
    assert packet["selected_target_cadence_sec"] == 60
    assert packet["ready_for_disabled_dry_run_planning"] is True
    safety = result["safety"]
    assert safety["validation_only"] is True
    assert safety["read_only"] is True
    assert safety["non_executing"] is True
    assert safety["ready_for_disabled_dry_run_planning"] is True
    for key in ("manual_one_shot_run_invoked_by_this_validation", "q16b_runner_invoked_for_actual_refresh", "q16b_status_artifact_written", "q16b_latest_prediction_artifact_written", "scheduler_enabled", "producer_enabled", "runtime_artifact_write_enabled", "status_artifact_write_enabled", "prediction_artifact_write_enabled", "latest_manifest_written", "run_sidecars_written", "warroom_ui_trigger_enabled", "autotrade_trigger_allowed", "broker_private_api_allowed", "ledger_append_allowed", "mode_apply_allowed", "parameter_apply_allowed", "would_send_to_broker"):
        assert safety[key] is False


if __name__ == "__main__":
    test_q25v_doc_markers()
    test_q25v_diagnostic_ready_and_safe()
    print(json.dumps({"ok": True}, ensure_ascii=False))
