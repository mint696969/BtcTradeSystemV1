# path: ./tools/diagnose_phase4a_prediction_system_ps_q23g_scheduler_sidecar_action_plan_no_write.py
# desc: PS-Q23G read-only scheduler action plan for adding Q23F sidecar flags to Q22X silent scheduled launcher.

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
import subprocess
import sys
from typing import Any, Mapping

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.diagnose_phase4a_prediction_system_ps_q22m_mountain2_recurring_trigger_prep_no_enablement import FUTURE_MOUNTAIN2_TOKEN_CANDIDATE  # noqa: E402
from tools.diagnose_phase4a_prediction_system_ps_q22v_post_enablement_tick_readiness import run_post_enablement_readiness  # noqa: E402
from tools.run_phase4a_prediction_system_ps_q21w_register_disabled_scheduler_once import (  # noqa: E402
    TASK_NAME,
    TASK_PATH,
    _run_windows_powershell,
)
from tools.run_phase4a_prediction_system_ps_q23b_gated_dual_write_sidecars_once import REQUIRED_CONFIRMATION as REQUIRED_DISTRIBUTED_SIDECAR_CONFIRMATION  # noqa: E402

DIAGNOSTIC_VERSION = "prediction_warroom.scheduler_sidecar_action_plan.ps_q23g.v1"
Q22X_TOOL = REPO_ROOT / "tools/run_phase4a_prediction_system_ps_q22x_silent_q22s_launcher.py"
SIDECAR_ENABLE_FLAG = "--enable-distributed-sidecar-dual-write"
SIDECAR_CONFIRMATION_FLAG = "--distributed-sidecar-confirmation"


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _as_mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _ps_single(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


def _git_status_short() -> str:
    proc = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=False)
    return proc.stdout.strip()


def expected_silent_launcher_args() -> str:
    return f'"{Q22X_TOOL}" --operator-acknowledged --execute-tick-once --confirmation {FUTURE_MOUNTAIN2_TOKEN_CANDIDATE}'


def candidate_silent_launcher_sidecar_args() -> str:
    return f"{expected_silent_launcher_args()} {SIDECAR_ENABLE_FLAG} {SIDECAR_CONFIRMATION_FLAG} {REQUIRED_DISTRIBUTED_SIDECAR_CONFIRMATION}"


def _task_query_script() -> str:
    lines = [
        "$ErrorActionPreference = 'Stop'",
        f"$TaskName = {_ps_single(TASK_NAME)}",
        f"$TaskPath = {_ps_single(TASK_PATH)}",
        "$Task = Get-ScheduledTask -TaskPath $TaskPath -TaskName $TaskName -ErrorAction SilentlyContinue",
        "if ($null -eq $Task) { [PSCustomObject]@{ task_exists = $false } | ConvertTo-Json -Depth 6; exit 0 }",
        "$TriggerCount = if ($null -eq $Task.Triggers) { 0 } else { @($Task.Triggers).Count }",
        "[PSCustomObject]@{",
        "  task_exists = $true",
        "  task_name = $Task.TaskName",
        "  task_path = $Task.TaskPath",
        "  state = \"$($Task.State)\"",
        "  action_execute = \"$($Task.Actions[0].Execute)\"",
        "  action_arguments = \"$($Task.Actions[0].Arguments)\"",
        "  trigger_count = $TriggerCount",
        "} | ConvertTo-Json -Depth 6",
    ]
    return "\n".join(lines)


def read_scheduler_task() -> dict[str, Any]:
    return dict(_run_windows_powershell(_task_query_script()))


def build_scheduler_sidecar_action_plan(*, repo_status_short: str, scheduler_task: Mapping[str, Any], q22v_readiness: Mapping[str, Any]) -> dict[str, Any]:
    task = _as_mapping(scheduler_task)
    current_args = str(task.get("action_arguments") or "")
    current_execute = str(task.get("action_execute") or "")
    expected_args = expected_silent_launcher_args()
    candidate_args = candidate_silent_launcher_sidecar_args()
    blockers: list[str] = []
    warnings: list[str] = []
    if repo_status_short.strip():
        blockers.append("repo_clean_required_before_scheduler_sidecar_action_plan")
    if task.get("ok") is not True or task.get("task_exists") is not True:
        blockers.append("scheduler_task_exists_required")
    if task.get("task_name") != TASK_NAME or str(task.get("task_path") or "") != TASK_PATH:
        blockers.append("scheduler_task_identity_mismatch")
    if int(task.get("trigger_count") or 0) != 1:
        blockers.append("scheduler_task_trigger_count_must_be_one")
    if not current_execute.lower().endswith("pythonw.exe"):
        blockers.append("scheduler_action_execute_must_be_pythonw")
    if current_args != expected_args:
        if SIDECAR_ENABLE_FLAG in current_args and SIDECAR_CONFIRMATION_FLAG in current_args:
            warnings.append("scheduler_action_already_contains_sidecar_flags")
        else:
            blockers.append("scheduler_action_arguments_must_be_current_q22x_silent_launcher_without_sidecar_flags")
    if SIDECAR_ENABLE_FLAG not in candidate_args or SIDECAR_CONFIRMATION_FLAG not in candidate_args:
        blockers.append("candidate_action_missing_sidecar_flags")
    if REQUIRED_DISTRIBUTED_SIDECAR_CONFIRMATION not in candidate_args:
        blockers.append("candidate_action_missing_exact_sidecar_confirmation")
    if q22v_readiness.get("post_enablement_tick_ready") is not True:
        blockers.append("q22v_post_enablement_readiness_required")
    ready = not blockers
    return {
        "ok": True,
        "diagnostic_version": DIAGNOSTIC_VERSION,
        "generated_at": _utc_now(),
        "plan_state": "scheduler_sidecar_action_plan_ready_no_write" if ready else "scheduler_sidecar_action_plan_blocked_no_write",
        "plan_ready_for_future_scheduler_action_replacement": ready,
        "blockers": blockers,
        "warnings": warnings,
        "repo_status_short": repo_status_short,
        "scheduler_task": dict(task),
        "current_action_execute": current_execute,
        "current_action_arguments": current_args,
        "expected_current_action_arguments": expected_args,
        "candidate_action_execute": current_execute,
        "candidate_action_arguments": candidate_args,
        "candidate_action_adds_sidecar_flags": True,
        "required_scheduler_confirmation_for_future_step": "REPLACE_SILENT_SCHEDULER_ACTION_WITH_DISTRIBUTED_SIDECAR_FLAGS_ONCE",
        "q22v_readiness_state": q22v_readiness.get("readiness_state"),
        "q22v_post_enablement_tick_ready": q22v_readiness.get("post_enablement_tick_ready") is True,
        "read_only_diagnostic": True,
        "scheduler_action_replacement_executed": False,
        "scheduler_enabled_by_this_tool": False,
        "trigger_added": False,
        "scheduled_sidecar_write_enabled": False,
        "latest_prediction_artifact_written": False,
        "status_artifact_written": False,
        "latest_manifest_written": False,
        "run_sidecars_written": False,
        "runtime_artifact_write_enabled": False,
        "broker_private_api_allowed": False,
        "autotrade_trigger_allowed": False,
        "approval_or_ledger_allowed": False,
        "parameter_apply_allowed": False,
        "parameter_staging_write_allowed": False,
        "would_send_to_broker": False,
    }


def run_scheduler_sidecar_action_plan() -> dict[str, Any]:
    return build_scheduler_sidecar_action_plan(
        repo_status_short=_git_status_short(),
        scheduler_task=read_scheduler_task(),
        q22v_readiness=run_post_enablement_readiness(),
    )


def main() -> int:
    result = run_scheduler_sidecar_action_plan()
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True, default=str))
    return 0 if result.get("ok") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
