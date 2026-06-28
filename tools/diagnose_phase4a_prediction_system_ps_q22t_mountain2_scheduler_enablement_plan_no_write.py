# path: ./tools/diagnose_phase4a_prediction_system_ps_q22t_mountain2_scheduler_enablement_plan_no_write.py
# desc: PS-Q22T no-write final plan for Mountain2 scheduler enablement. Lists action/trigger/enable/rollback commands without executing them.

from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import sys
from typing import Any, Mapping

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.diagnose_phase4a_prediction_system_ps_q22m_mountain2_recurring_trigger_prep_no_enablement import FUTURE_MOUNTAIN2_TOKEN_CANDIDATE  # noqa: E402
from tools.diagnose_phase4a_prediction_system_ps_q22q_mountain2_final_readiness_no_enablement import run_final_readiness  # noqa: E402
from tools.run_phase4a_prediction_system_ps_q21w_register_disabled_scheduler_once import (  # noqa: E402
    PS_Q21V_TOOL,
    TASK_NAME,
    TASK_PATH,
    query_disabled_scheduler_registration,
)
from tools.run_phase4a_prediction_system_ps_q22s_mountain2_actual_scheduled_latest_refresh_tick_once import RUNNER_VERSION as Q22S_RUNNER_VERSION  # noqa: E402

PLAN_VERSION = "prediction_warroom.mountain2_scheduler_enablement_plan_no_write.ps_q22t.v1"
Q22S_TOOL = REPO_ROOT / "tools/run_phase4a_prediction_system_ps_q22s_mountain2_actual_scheduled_latest_refresh_tick_once.py"
RECOMMENDED_CADENCE_MINUTES = 5


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _git_status_short() -> str:
    proc = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=False)
    return proc.stdout.strip()


def _as_mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _task_packet() -> dict[str, Any]:
    query = query_disabled_scheduler_registration()
    readback = _as_mapping(query.get("task_readback"))
    return {
        "query_state": query.get("query_state"),
        "task_recognized_as_ps_q21w": query.get("task_recognized_as_ps_q21w") is True,
        "task_exists": readback.get("task_exists") is True,
        "task_name": readback.get("task_name"),
        "task_path": readback.get("task_path"),
        "task_state": readback.get("state"),
        "task_trigger_count": int(readback.get("trigger_count") or 0),
        "task_action_execute": readback.get("action_execute"),
        "task_action_arguments": readback.get("action_arguments"),
        "task_readback_failures": list(query.get("task_readback_failures") or []),
    }


def build_plan(*, repo_status_short: str, q22q_packet: Mapping[str, Any], task: Mapping[str, Any]) -> dict[str, Any]:
    q22q = _as_mapping(q22q_packet)
    blockers: list[str] = []
    warnings: list[str] = []
    if repo_status_short.strip():
        blockers.append("repo_clean_required_before_scheduler_enablement_plan")
    if q22q.get("readiness_state") != "mountain2_final_pre_danger_boundary_ready_no_enablement":
        blockers.append("q22q_final_readiness_green_required")
    if q22q.get("readiness_blockers") not in ([], None):
        blockers.append("q22q_readiness_blockers_must_be_empty")
    if q22q.get("runtime_readiness_blockers") not in ([], None):
        blockers.append("q22q_runtime_blockers_must_be_empty")
    if task.get("task_recognized_as_ps_q21w") is not True:
        blockers.append("disabled_scheduler_task_must_be_q21w_recognized")
    if task.get("task_state") != "Disabled":
        blockers.append("scheduler_task_must_be_disabled_before_enablement_plan")
    if int(task.get("task_trigger_count") or 0) != 0:
        blockers.append("scheduler_task_must_have_zero_triggers_before_enablement_plan")
    action_args = str(task.get("task_action_arguments") or "")
    if str(PS_Q21V_TOOL) not in action_args and "run_phase4a_prediction_system_ps_q21v_disabled_scheduler_registration_smoke.py" not in action_args:
        blockers.append("scheduler_task_action_must_still_be_q21v_dry_run_before_replacement")
    future_action_args = f'"{Q22S_TOOL}" --operator-acknowledged --execute-tick-once --confirmation {FUTURE_MOUNTAIN2_TOKEN_CANDIDATE}'
    if not Q22S_TOOL.exists():
        blockers.append("q22s_actual_tick_tool_required")
    ready = not blockers
    return {
        "ok": True,
        "plan_version": PLAN_VERSION,
        "plan_state": "mountain2_scheduler_enablement_plan_ready_no_write" if ready else "mountain2_scheduler_enablement_plan_blocked_no_write",
        "plan_ready_for_explicit_operator_gate": ready,
        "plan_blockers": blockers,
        "plan_warnings": warnings,
        "generated_at": _utc_now(),
        "repo_status_short": repo_status_short,
        "q22q_state": q22q.get("readiness_state"),
        "q22q_readiness_blockers": list(q22q.get("readiness_blockers") or []),
        "q22q_runtime_readiness_blockers": list(q22q.get("runtime_readiness_blockers") or []),
        "task_before": dict(task),
        "future_task_action": {
            "execute": sys.executable,
            "arguments": future_action_args,
            "q22s_tool": str(Q22S_TOOL),
            "q22s_runner_version": Q22S_RUNNER_VERSION,
            "confirmation_embedded_in_scheduled_action": FUTURE_MOUNTAIN2_TOKEN_CANDIDATE,
        },
        "future_trigger_plan": {
            "trigger_type": "Once with RepetitionInterval",
            "repetition_interval_minutes": RECOMMENDED_CADENCE_MINUTES,
            "multiple_instances_policy_required": "IgnoreNew",
        },
        "future_enablement_sequence_not_executed": [
            "Disable-ScheduledTask existing task",
            "Set-ScheduledTask action to Q22S actual tick once",
            "Add periodic trigger every 5 minutes",
            "Enable-ScheduledTask",
            "Observe first scheduled tick",
            "Verify D-hot lock absent and Q22Q readiness green",
        ],
        "future_rollback_sequence_not_executed": [
            "Disable-ScheduledTask",
            "Remove PS-Q22T periodic triggers",
            "Restore Q21V dry-run action",
            "Keep task registered and disabled",
            "Verify trigger_count=0",
        ],
        "required_operator_confirmation_before_execution": FUTURE_MOUNTAIN2_TOKEN_CANDIDATE,
        "read_only_plan_only": True,
        "scheduler_action_replacement_executed": False,
        "scheduler_enabled": False,
        "trigger_added": False,
        "trigger_addition_allowed_now": False,
        "recurring_enablement_allowed_now": False,
        "periodic_execution_enabled": False,
        "rollback_executed": False,
        "latest_prediction_artifact_written": False,
        "status_artifact_written": False,
        "lock_acquire_attempted": False,
        "producer_loop_enabled": False,
        "producer_runner_invoked": False,
        "bounded_manual_refresh_invoked": False,
        "actual_export_runner_invoked": False,
        "warroom_ui_trigger_allowed": False,
        "approval_or_ledger_allowed": False,
        "parameter_apply_allowed": False,
        "parameter_staging_write_allowed": False,
        "autotrade_trigger_allowed": False,
        "broker_private_api_allowed": False,
        "would_send_to_broker": False,
        "would_write_collector_state": False,
    }


def run_plan() -> dict[str, Any]:
    return build_plan(repo_status_short=_git_status_short(), q22q_packet=run_final_readiness(), task=_task_packet())


def main() -> int:
    result = run_plan()
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True, default=str))
    return 0 if result.get("ok") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
