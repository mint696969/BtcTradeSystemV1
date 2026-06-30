# path: ./tools/test_phase4a_prediction_system_ps_q25y_disabled_single_producer_60s_dry_run_human_gate_packet.py
# desc: Focused pytest guard for PS-Q25Y disabled single-producer 60s dry-run human gate packet.

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

from tools.diagnose_phase4a_prediction_system_ps_q25y_disabled_single_producer_60s_dry_run_human_gate_packet import run_disabled_single_producer_60s_dry_run_human_gate_packet_diagnostic  # noqa: E402

DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q25Y_DISABLED_SINGLE_PRODUCER_60S_DRY_RUN_HUMAN_GATE_PACKET_2026-06-30.md"


def test_q25y_doc_markers() -> None:
    text = DOC.read_text(encoding="utf-8-sig")
    for marker in ("ps_q25y_disabled_single_producer_60s_dry_run_human_gate_packet=true", "selected_option_id=single_producer_60s_candidate", "selected_target_cadence_sec=60", "dry_run_human_gate_packet_added=true", "gate_marker_only=true", "decision_packet_only=true", "human_gate_required_before_any_dry_run=true", "human_gate_granted_by_this_packet=false", "separate_execution_slice_required=true", "manual_one_shot_run_allowed=false", "execute_dry_run_allowed=false", "broker_private_api_allowed=false"):
        assert marker in text, marker


def test_q25y_diagnostic_ready_and_safe() -> None:
    result = run_disabled_single_producer_60s_dry_run_human_gate_packet_diagnostic()
    assert result["ok"] is True
    assert result["ready"] is True, result["blockers"]
    assert result["blockers"] == []
    packet = result["default_packet"]
    assert packet["selected_option_id"] == "single_producer_60s_candidate"
    assert packet["selected_target_cadence_sec"] == 60
    assert packet["ready_for_future_disabled_manual_dry_run_gate_decision"] is True
    token_packet = result["token_intent_packet"]
    assert token_packet["gate_token_detected"] is True
    assert token_packet["human_gate_granted_by_this_packet"] is False
    safety = result["safety"]
    assert safety["gate_marker_only"] is True
    assert safety["decision_packet_only"] is True
    assert safety["read_only"] is True
    assert safety["non_executing"] is True
    assert safety["human_gate_required_before_any_dry_run"] is True
    assert safety["separate_execution_slice_required"] is True
    for key in ("human_gate_granted_by_this_packet", "execute_dry_run_allowed_by_this_packet", "execute_dry_run_enabled", "manual_one_shot_run_invoked_by_this_gate", "status_artifact_write_performed_by_this_gate", "runtime_artifact_write_performed_by_this_gate", "prediction_artifact_write_performed_by_this_gate", "latest_manifest_written", "run_sidecars_written", "lock_file_created_by_this_gate", "lock_file_deleted_by_this_gate", "scheduler_enabled", "producer_enabled", "warroom_ui_trigger_enabled", "autotrade_trigger_allowed", "broker_private_api_allowed", "ledger_append_allowed", "mode_apply_allowed", "parameter_apply_allowed", "would_send_to_broker"):
        assert safety[key] is False


if __name__ == "__main__":
    test_q25y_doc_markers()
    test_q25y_diagnostic_ready_and_safe()
    print(json.dumps({"ok": True}, ensure_ascii=False))
