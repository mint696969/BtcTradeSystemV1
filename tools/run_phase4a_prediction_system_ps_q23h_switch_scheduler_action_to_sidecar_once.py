# path: ./tools/run_phase4a_prediction_system_ps_q23h_switch_scheduler_action_to_sidecar_once.py
# desc: PS-Q23H gated one-shot scheduler action replacement to add Q23F distributed sidecar flags. Default blocked no-write.

from __future__ import annotations

import argparse
from collections.abc import Callable
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import sys
from typing import Any, Mapping

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.diagnose_phase4a_prediction_system_ps_q23g_scheduler_sidecar_action_plan_no_write import (  # noqa: E402
    candidate_silent_launcher_sidecar_args,
    expected_silent_launcher_args,
    run_scheduler_sidecar_action_plan,
)
from tools.run_phase4a_prediction_system_ps_q21w_register_disabled_scheduler_once import TASK_NAME, TASK_PATH  # noqa: E402

SWITCH_VERSION = "prediction_warroom.scheduler_sidecar_action_switch.ps_q23h.v1"
REQUIRED_CONFIRMATION = "REPLACE_SILENT_SCHEDULER_ACTION_WITH_DISTRIBUTED_SIDECAR_FLAGS_ONCE"
PowerShellRunner = Callable[[str], Mapping[str, Any]]
PlanProvider = Callable[[], Mapping[str, Any]]


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _ps_single(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


def _git_status_short() -> str:
    proc = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=False)
    return proc.stdout.strip()


def _false_boundaries() -> dict[str, Any]:
    return {
        "trigger_added": False,
        "periodic_trigger_added": False,
        "scheduler_task_created": False,
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
        "would_write_collector_state": False,
    }


def _task_readback_lines(prefix: str = "$After") -> list[str]:
    return [
        f"$TriggerCount = if ($null -eq {prefix}.Triggers) {{ 0 }} else {{ @({prefix}.Triggers).Count }}",
        "[PSCustomObject]@{",
        "  task_exists = $true",
        f"  task_name = {prefix}.TaskName",
        f"  task_path = {prefix}.TaskPath",
        f"  state = \"$({prefix}.State)\"",
        f"  action_execute = \"$({prefix}.Actions[0].Execute)\"",
        f"  action_arguments = \"$({prefix}.Actions[0].Arguments)\"",
        "  trigger_count = $TriggerCount",
        "} | ConvertTo-Json -Depth 6",
    ]


def _run_windows_powershell(script: str) -> dict[str, Any]:
    proc = subprocess.run(["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", script], cwd=REPO_ROOT, text=True, capture_output=True, check=False)
    if proc.returncode != 0:
        return {"ok": False, "returncode": proc.returncode, "stdout": proc.stdout.strip(), "stderr": proc.stderr.strip()}
    text = proc.stdout.strip()
    try:
        data = json.loads(text) if text else {}
    except json.JSONDecodeError:
        data = {"raw_stdout": text}
    return {"ok": True, **data} if isinstance(data, dict) else {"ok": True, "raw_stdout": text}


def _switch_script(*, action_execute: str) -> str:
    current_args = expected_silent_launcher_args()
    candidate_args = candidate_silent_launcher_sidecar_args()
    lines = [
        "$ErrorActionPreference = 'Stop'",
        f"$TaskName = {_ps_single(TASK_NAME)}",
        f"$TaskPath = {_ps_single(TASK_PATH)}",
        f"$ExpectedCurrentArg = {_ps_single(current_args)}",
        f"$CandidateArg = {_ps_single(candidate_args)}",
        f"$ActionExecute = {_ps_single(action_execute)}",
        "$Before = Get-ScheduledTask -TaskPath $TaskPath -TaskName $TaskName -ErrorAction Stop",
        "$BeforeState = \"$($Before.State)\"",
        "$BeforeTriggerCount = if ($null -eq $Before.Triggers) { 0 } else { @($Before.Triggers).Count }",
        "$BeforeArg = \"$($Before.Actions[0].Arguments)\"",
        "$BeforeExe = \"$($Before.Actions[0].Execute)\"",
        "if ($BeforeTriggerCount -ne 1) { throw 'trigger_count_must_remain_one_before_sidecar_switch' }",
        "if ($BeforeArg -ne $ExpectedCurrentArg) { throw 'current_scheduler_action_must_be_q22x_silent_without_sidecar_flags' }",
        "if ($BeforeExe -ne $ActionExecute) { throw 'current_scheduler_action_execute_mismatch' }",
        "$WasEnabled = ($BeforeState -ne 'Disabled')",
        "Disable-ScheduledTask -TaskPath $TaskPath -TaskName $TaskName | Out-Null",
        "$Action = New-ScheduledTaskAction -Execute $ActionExecute -Argument $CandidateArg",
        "Set-ScheduledTask -TaskPath $TaskPath -TaskName $TaskName -Action $Action | Out-Null",
        "if ($WasEnabled) { Enable-ScheduledTask -TaskPath $TaskPath -TaskName $TaskName | Out-Null }",
        "$After = Get-ScheduledTask -TaskPath $TaskPath -TaskName $TaskName -ErrorAction Stop",
        *_task_readback_lines("$After"),
    ]
    return "\n".join(lines)


def _recognized_switched(readback: Mapping[str, Any], *, expected_execute: str) -> tuple[bool, list[str]]:
    failures: list[str] = []
    if readback.get("ok") is not True:
        failures.append("powershell_result_not_ok")
    if readback.get("task_name") != TASK_NAME:
        failures.append("task_name_mismatch")
    if str(readback.get("task_path") or "") != TASK_PATH:
        failures.append("task_path_mismatch")
    if int(readback.get("trigger_count") or 0) != 1:
        failures.append("trigger_count_not_one_after_sidecar_switch")
    if str(readback.get("action_execute") or "").lower() != expected_execute.lower():
        failures.append("task_action_execute_mismatch_after_sidecar_switch")
    if str(readback.get("action_arguments") or "") != candidate_silent_launcher_sidecar_args():
        failures.append("task_action_arguments_not_sidecar_candidate")
    if str(readback.get("state") or "").lower() == "disabled":
        failures.append("task_disabled_after_sidecar_switch")
    return not failures, failures


def run_switch_scheduler_action_to_sidecar_once(
    *,
    operator_acknowledged: bool = False,
    execute_switch_once: bool = False,
    confirmation: str = "",
    ps_runner: PowerShellRunner | None = None,
    plan_provider: PlanProvider | None = None,
    repo_status_short: str | None = None,
) -> dict[str, Any]:
    confirmation_ok = confirmation == REQUIRED_CONFIRMATION
    base = {
        "ok": True,
        "switch_version": SWITCH_VERSION,
        "generated_at": _utc_now(),
        "required_confirmation": REQUIRED_CONFIRMATION,
        "confirmation_ok": confirmation_ok,
        "default_execution_is_dry_run_no_write": True,
        "scheduler_action_replacement_executed": False,
        "scheduled_sidecar_write_enabled": False,
        "scheduler_enabled_by_this_tool": False,
        "powershell_invoked": False,
        **_false_boundaries(),
    }
    blockers: list[str] = []
    if not operator_acknowledged:
        blockers.append("operator_acknowledgement_required")
    if not execute_switch_once:
        blockers.append("execute_switch_once_flag_required")
    if not confirmation_ok:
        blockers.append("exact_scheduler_sidecar_action_switch_confirmation_required")
    repo_status = _git_status_short() if repo_status_short is None else str(repo_status_short)
    if repo_status:
        blockers.append("repo_clean_required_before_scheduler_sidecar_action_switch")
    plan_provider = plan_provider or run_scheduler_sidecar_action_plan
    plan = dict(plan_provider())
    if plan.get("plan_ready_for_future_scheduler_action_replacement") is not True:
        blockers.append("q23g_scheduler_sidecar_action_plan_ready_required")
    action_execute = str(plan.get("candidate_action_execute") or "")
    if not action_execute.lower().endswith("pythonw.exe"):
        blockers.append("candidate_action_execute_must_be_pythonw")
    if blockers:
        return {
            **base,
            "success": False,
            "execution_state": "scheduler_sidecar_action_switch_blocked_no_write",
            "blocked_reasons": blockers,
            "repo_status_short": repo_status,
            "q23g_plan": plan,
            "candidate_action_execute": action_execute,
            "candidate_action_arguments": str(plan.get("candidate_action_arguments") or candidate_silent_launcher_sidecar_args()),
        }
    ps_runner = ps_runner or _run_windows_powershell
    ps_result = dict(ps_runner(_switch_script(action_execute=action_execute)))
    recognized, failures = _recognized_switched(ps_result, expected_execute=action_execute)
    return {
        **base,
        "success": recognized,
        "execution_state": "scheduler_sidecar_action_switch_completed" if recognized else "scheduler_sidecar_action_switch_failed_or_incomplete",
        "blocked_reasons": [] if recognized else failures,
        "repo_status_short": repo_status,
        "q23g_plan": plan,
        "powershell_invoked": True,
        "powershell_result": ps_result,
        "candidate_action_execute": action_execute,
        "candidate_action_arguments": candidate_silent_launcher_sidecar_args(),
        "scheduler_action_replacement_executed": recognized,
        "scheduled_sidecar_write_enabled": recognized,
        "scheduler_enabled_by_this_tool": recognized,
        "trigger_added": False,
        "periodic_trigger_added": False,
        "scheduler_task_created": False,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="PS-Q23H switch Q22X scheduler action to Q23F sidecar-enabled action once")
    parser.add_argument("--operator-acknowledged", action="store_true")
    parser.add_argument("--execute-switch-once", action="store_true")
    parser.add_argument("--confirmation", default="")
    args = parser.parse_args(argv)
    result = run_switch_scheduler_action_to_sidecar_once(
        operator_acknowledged=bool(args.operator_acknowledged),
        execute_switch_once=bool(args.execute_switch_once),
        confirmation=str(args.confirmation),
    )
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True, default=str))
    return 0 if result.get("ok") is True and (result.get("success") is True or not args.execute_switch_once) else 1


if __name__ == "__main__":
    raise SystemExit(main())
