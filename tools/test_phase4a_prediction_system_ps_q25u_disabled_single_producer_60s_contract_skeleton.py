# path: ./tools/test_phase4a_prediction_system_ps_q25u_disabled_single_producer_60s_contract_skeleton.py
# desc: Focused pytest guard for PS-Q25U disabled single-producer 60s contract/skeleton.

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

from tools.diagnose_phase4a_prediction_system_ps_q25u_disabled_single_producer_60s_contract_skeleton import run_disabled_single_producer_60s_contract_skeleton_diagnostic  # noqa: E402

DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q25U_DISABLED_SINGLE_PRODUCER_60S_CONTRACT_SKELETON_2026-06-30.md"


def test_q25u_doc_markers() -> None:
    text = DOC.read_text(encoding="utf-8-sig")
    for marker in ("ps_q25u_disabled_single_producer_60s_contract_skeleton=true", "selected_option_id=single_producer_60s_candidate", "selected_target_cadence_sec=60", "disabled_contract_skeleton_added=true", "production_code_skeleton_added=true", "contract_skeleton_only=true", "implementation_allowed_by_this_packet=false", "manual_one_shot_run_allowed=false", "scheduler_enablement_allowed=false", "producer_enablement_allowed=false", "broker_private_api_allowed=false"):
        assert marker in text, marker


def test_q25u_diagnostic_ready_and_safe() -> None:
    result = run_disabled_single_producer_60s_contract_skeleton_diagnostic()
    assert result["ok"] is True
    assert result["ready"] is True, result["blockers"]
    assert result["blockers"] == []
    packet = result["packet"]
    assert packet["selected_option_id"] == "single_producer_60s_candidate"
    assert packet["selected_target_cadence_sec"] == 60
    assert packet["ready_for_future_disabled_single_producer_60s_skeleton_validation"] is True
    assert packet["contract_skeleton_only"] is True
    assert packet["read_only"] is True
    assert packet["non_executing"] is True
    assert len(packet["candidate_components"]) == 6
    safety = result["safety"]
    assert safety["contract_skeleton_only"] is True
    assert safety["read_only"] is True
    assert safety["non_executing"] is True
    for key in ("default_enabled", "ready_for_manual_one_shot_run", "ready_for_scheduler_enablement", "ready_for_producer_enablement", "scheduler_enabled", "producer_enabled", "scheduled_loop_enabled", "manual_one_shot_run_invoked_by_this_skeleton", "prediction_build_requested", "actual_export_runner_invoked", "bounded_manual_refresh_invoked", "would_write_runtime_artifact", "would_write_status_artifact", "would_write_prediction_artifact", "would_write_view_artifact", "latest_manifest_written", "run_sidecars_written", "warroom_ui_trigger_enabled", "autotrade_trigger_allowed", "broker_private_api_allowed", "ledger_append_allowed", "parameter_apply_allowed", "mode_apply_allowed", "would_send_to_broker"):
        assert safety[key] is False


if __name__ == "__main__":
    test_q25u_doc_markers()
    test_q25u_diagnostic_ready_and_safe()
    print(json.dumps({"ok": True}, ensure_ascii=False))
