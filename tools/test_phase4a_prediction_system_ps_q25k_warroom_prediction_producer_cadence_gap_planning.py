# path: ./tools/test_phase4a_prediction_system_ps_q25k_warroom_prediction_producer_cadence_gap_planning.py
# desc: Focused pytest guard for PS-Q25K WarRoom prediction producer cadence/freshness gap planning.

from __future__ import annotations

import json
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "btcts_next" / "src"
for candidate in (REPO_ROOT, SRC_ROOT):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

from tools.diagnose_phase4a_prediction_system_ps_q25k_warroom_prediction_producer_cadence_gap_planning import run_warroom_prediction_producer_cadence_gap_planning_diagnostic  # noqa: E402

DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q25K_WARROOM_PREDICTION_PRODUCER_CADENCE_GAP_PLANNING_2026-06-30.md"
CONTRACT = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_non_ui_scheduled_producer_contract.py"


def test_q25k_doc_markers() -> None:
    text = DOC.read_text(encoding="utf-8-sig")
    for marker in ("ps_q25k_warroom_prediction_producer_cadence_gap_planning=true", "cadence_gap_plan_added=true", "planning_only=true", "contract_only=true", "human_gate_required_before_any_change=true", "producer_cadence_changed=false", "scheduler_action_changed=false", "autotrade_trigger_allowed=false", "broker_private_api_allowed=false"):
        assert marker in text, marker


def test_q25k_diagnostic_ready() -> None:
    result = run_warroom_prediction_producer_cadence_gap_planning_diagnostic()
    assert result["ok"] is True
    assert result["ready"] is True, result["blockers"]
    assert result["blockers"] == []
    plan = result["plan"]
    assert plan["cadence_gap_plan_version"] == "prediction_warroom.producer_cadence_gap_planning.ps_q25k.v1"
    assert plan["horizon_cadence_gap_row_count"] == 6
    assert plan["short_horizon_freshness_gap_present"] is True
    assert plan["producer_cadence_changed"] is False
    blocked = result["blocked_request_plan"]
    assert blocked["planning_state"] == "blocked_dangerous_request_without_explicit_gate"
    assert blocked["blocker_count"] >= 1
    safety = result["safety"]
    assert safety["planning_only"] is True
    assert safety["contract_only"] is True
    for key in ("producer_cadence_changed", "scheduler_action_changed", "scheduler_enabled", "producer_enabled", "runtime_artifact_write_allowed", "status_artifact_write_allowed", "prediction_artifact_write_allowed", "view_artifact_write_allowed", "latest_manifest_written", "run_sidecars_written", "autotrade_trigger_allowed", "broker_private_api_allowed", "ledger_append_allowed", "mode_apply_allowed", "parameter_apply_allowed", "would_send_to_broker"):
        assert safety[key] is False


def test_q25k_contract_safe_and_markers() -> None:
    text = CONTRACT.read_text(encoding="utf-8-sig")
    for marker in ("PREDICTION_WARROOM_PRODUCER_CADENCE_GAP_PLAN_VERSION", "HORIZON_CADENCE_PLANNING_TARGETS", "build_prediction_warroom_producer_cadence_gap_plan", "producer_cadence_changed"):
        assert marker in text, marker
    for forbidden in ("Set-ScheduledTask", "Enable-ScheduledTask", "Disable-ScheduledTask", "Register-ScheduledTask", "New-ScheduledTaskTrigger", "append_decision_jsonl", "run_shadow_decision_from_snapshot", "submit_mode_change_command_request", "validate_and_append_command", "send_order(", "place_order(", "create_order(", ".write_text(", ".write_bytes(", "os.replace", "shutil.copy2"):
        assert forbidden not in text, forbidden


if __name__ == "__main__":
    test_q25k_doc_markers()
    test_q25k_diagnostic_ready()
    test_q25k_contract_safe_and_markers()
    print(json.dumps({"ok": True}, ensure_ascii=False))
