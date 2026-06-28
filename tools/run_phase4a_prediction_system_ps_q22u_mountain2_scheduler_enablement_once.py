# path: ./tools/run_phase4a_prediction_system_ps_q22u_mountain2_scheduler_enablement_once.py
# desc: PS-Q22U exact-token Mountain2 scheduler enablement/rollback executor. Default no-write.

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

from tools.diagnose_phase4a_prediction_system_ps_q22m_mountain2_recurring_trigger_prep_no_enablement import FUTURE_MOUNTAIN2_TOKEN_CANDIDATE  # noqa: E402
from tools.diagnose_phase4a_prediction_system_ps_q22t_mountain2_scheduler_enablement_plan_no_write import (  # noqa: E402
    Q22S_TOOL,
    RECOMMENDED_CADENCE_MINUTES,
    run_plan,
)
from tools.run_phase4a_prediction_system_ps_q21w_register_disabled_scheduler_once import (  # noqa: E402
    PS_Q21V_TOOL,
    TASK_NAME,
    TASK_PATH,
)

ENABLE_VERSION = "prediction_warroom.mountain2_scheduler_enablement_once.ps_q22u.v1"
PowerShellRunner = Callable[[str], Mapping[str, Any]]
PlanProvider = Callable[[], Mapping[str, Any]]


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _ps_single(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


def _git_status_short() -> str:
    proc = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=False)
    return proc.stdout.strip()


def _run_windows_powershell(script: str) -> dict[str, Any]:
    proc = subprocess.run(
        ["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", script],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if proc.returncode != 0:
        return {"ok": False, "returncode": proc.returncode, "stdout": proc.stdout.strip(), "stderr": proc.stderr.strip()}
    text = proc.stdout.strip()
    try:
        data = json.loads(text) if text else {}
    except json.JSONDecodeError:
        data = {"raw_stdout": text}
    return {"ok": True, **data} if isinstance(data, dict) else {"ok": True, "raw_stdout": text}


def _q22s_action_args() -> str:
    return f'"{Q22S_TOOL}" --operator-acknowledged --execute-tick-once --confirmation {FUTURE_MOUNTAIN2_TOKEN_CANDIDATE}'


def _q21v_action_args() -> str:
    return f'"{PS_Q21V_TOOL}"'


def _false_runtime_boundaries() -> dict[str, Any]:
    return {
        "latest_prediction_artifact_written": False,
        "status_artifact_written": False,
        "lock_acquire_attempted": False,
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
        "} | ConvertTo-Json -Depth 5",
    ]


def _enable_script() -> str:
    exe = sys.executable
    lines = [
        "$ErrorActionPreference = 'Stop'",
        f"$TaskName = {_ps_single(TASK_NAME)}",
        f"$TaskPath = {_ps_single(TASK_PATH)}",
        f"$ExpectedOldArg = {_ps_single(_q21v_action_args())}",
        f"$Exe = {_ps_single(exe)}",
        f"$Arg = {_ps_single(_q22s_action_args())}",
        f"$Minutes = {int(RECOMMENDED_CADENCE_MINUTES)}",
        "$Task = Get-ScheduledTask -TaskPath $TaskPath -TaskName $TaskName -ErrorAction Stop",
        "$BeforeTriggerCount = if ($null -eq $Task.Triggers) { 0 } else { @($Task.Triggers).Count }",
        "$BeforeArg = \"$($Task.Actions[0].Arguments)\"",
        "if (\"$($Task.State)\" -ne 'Disabled') { throw 'ps_q22u_task_must_start_disabled' }",
        "if ($BeforeTriggerCount -ne 0) { throw 'ps_q22u_task_must_start_with_zero_triggers' }",
        "if ($BeforeArg -ne $ExpectedOldArg) { throw 'ps_q22u_task_action_must_start_as_q21v_dry_run' }",
        "Disable-ScheduledTask -TaskPath $TaskPath -TaskName $TaskName | Out-Null",
        "$Action = New-ScheduledTaskAction -Execute $Exe -Argument $Arg",
        "$Start = (Get-Date).AddMinutes(1)",
        "$Trigger = New-ScheduledTaskTrigger -Once -At $Start -RepetitionInterval (New-TimeSpan -Minutes $Minutes) -RepetitionDuration (New-TimeSpan -Days 3650)",
        "$Settings = New-ScheduledTaskSettingsSet -MultipleInstances IgnoreNew -StartWhenAvailable:$false -ExecutionTimeLimit (New-TimeSpan -Minutes 10)",
        "Set-ScheduledTask -TaskPath $TaskPath -TaskName $TaskName -Action $Action -Trigger $Trigger -Settings $Settings | Out-Null",
        "Enable-ScheduledTask -TaskPath $TaskPath -TaskName $TaskName | Out-Null",
        "$After = Get-ScheduledTask -TaskPath $TaskPath -TaskName $TaskName -ErrorAction Stop",
        * _task_readback_lines("$After"),
    ]
    return "\n".join(lines)


def _rollback_script() -> str:
    exe = sys.executable
    lines = [
        "$ErrorActionPreference = 'Stop'",
        f"$TaskName = {_ps_single(TASK_NAME)}",
        f"$TaskPath = {_ps_single(TASK_PATH)}",
        f"$Exe = {_ps_single(exe)}",
        f"$Q21VArg = {_ps_single(_q21v_action_args())}",
        f"$Q22SArg = {_ps_single(_q22s_action_args())}",
        "$Task = Get-ScheduledTask -TaskPath $TaskPath -TaskName $TaskName -ErrorAction SilentlyContinue",
        "if ($null -eq $Task) { throw 'ps_q22u_task_missing_before_rollback' }",
        "$CurrentArg = \"$($Task.Actions[0].Arguments)\"",
        "$CurrentTriggerCount = if ($null -eq $Task.Triggers) { 0 } else { @($Task.Triggers).Count }",
        "if (($CurrentArg -ne $Q22SArg) -and ($CurrentArg -ne $Q21VArg)) { throw 'ps_q22u_refuse_rollback_unknown_action' }",
        "Disable-ScheduledTask -TaskPath $TaskPath -TaskName $TaskName | Out-Null",
        "Unregister-ScheduledTask -TaskPath $TaskPath -TaskName $TaskName -Confirm:$false",
        "$Action = New-ScheduledTaskAction -Execute $Exe -Argument $Q21VArg",
        "$Principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive -RunLevel Limited",
        "$Settings = New-ScheduledTaskSettingsSet -MultipleInstances IgnoreNew -StartWhenAvailable:$false -ExecutionTimeLimit (New-TimeSpan -Minutes 10)",
        "$NewTask = New-ScheduledTask -Action $Action -Principal $Principal -Settings $Settings",
        "Register-ScheduledTask -TaskPath $TaskPath -TaskName $TaskName -InputObject $NewTask -Force | Out-Null",
        "Disable-ScheduledTask -TaskPath $TaskPath -TaskName $TaskName | Out-Null",
        "$After = Get-ScheduledTask -TaskPath $TaskPath -TaskName $TaskName -ErrorAction Stop",
        * _task_readback_lines("$After"),
    ]
    return "\n".join(lines)


def _recognized_enabled(readback: Mapping[str, Any]) -> tuple[bool, list[str]]:
    failures: list[str] = []
    if readback.get("ok") is not True:
        failures.append("powershell_result_not_ok")
    if readback.get("task_name") != TASK_NAME:
        failures.append("task_name_mismatch")
    if str(readback.get("task_path") or "") != TASK_PATH:
        failures.append("task_path_mismatch")
    if str(readback.get("state") or "").lower() == "disabled":
        failures.append("task_state_still_disabled")
    if int(readback.get("trigger_count") or 0) != 1:
        failures.append("trigger_count_not_one")
    if str(readback.get("action_arguments") or "") != _q22s_action_args():
        failures.append("task_action_not_q22s")
    return not failures, failures


def _recognized_rolled_back(readback: Mapping[str, Any]) -> tuple[bool, list[str]]:
    failures: list[str] = []
    if readback.get("ok") is not True:
        failures.append("powershell_result_not_ok")
    if str(readback.get("state") or "").lower() != "disabled":
        failures.append("task_not_disabled_after_rollback")
    if int(readback.get("trigger_count") or 0) != 0:
        failures.append("trigger_count_not_zero_after_rollback")
    if str(readback.get("action_arguments") or "") != _q21v_action_args():
        failures.append("task_action_not_q21v_after_rollback")
    return not failures, failures


def _base(*, mode: str, confirmation_ok: bool) -> dict[str, Any]:
    return {
        "ok": True,
        "enable_version": ENABLE_VERSION,
        "generated_at": _utc_now(),
        "mode": mode,
        "task_name": TASK_NAME,
        "task_path": TASK_PATH,
        "required_confirmation": FUTURE_MOUNTAIN2_TOKEN_CANDIDATE,
        "confirmation_ok": bool(confirmation_ok),
        "default_execution_is_dry_run_no_write": True,
        "scheduler_action_replacement_executed": False,
        "scheduler_enabled": False,
        "trigger_added": False,
        "periodic_execution_enabled": False,
        "recurring_enablement_allowed_now": False,
        "rollback_executed": False,
        **_false_runtime_boundaries(),
    }


def run_scheduler_enablement_once(
    *,
    operator_acknowledged: bool = False,
    execute_enable_once: bool = False,
    rollback: bool = False,
    confirmation: str = "",
    ps_runner: PowerShellRunner | None = None,
    plan_provider: PlanProvider | None = None,
    repo_status_short: str | None = None,
) -> dict[str, Any]:
    confirmation_ok = confirmation == FUTURE_MOUNTAIN2_TOKEN_CANDIDATE
    mode = "rollback" if rollback else "enable"
    base = _base(mode=mode, confirmation_ok=confirmation_ok)
    blockers: list[str] = []
    if not operator_acknowledged:
        blockers.append("operator_acknowledgement_required")
    if not execute_enable_once and not rollback:
        blockers.append("execute_enable_once_flag_required")
    if not confirmation_ok:
        blockers.append("exact_scheduler_enablement_confirmation_required")
    repo_status = _git_status_short() if repo_status_short is None else str(repo_status_short)
    if repo_status:
        blockers.append("repo_clean_required_before_scheduler_enablement")
    plan_provider = plan_provider or run_plan
    plan = dict(plan_provider())
    if not rollback:
        if plan.get("plan_ready_for_explicit_operator_gate") is not True:
            blockers.append("ps_q22t_plan_ready_required")
        if plan.get("plan_blockers") not in ([], None):
            blockers.append("ps_q22t_plan_blockers_must_be_empty")
    if blockers:
        return {**base, "success": False, "execution_state": f"mountain2_scheduler_{mode}_blocked_no_write", "blocked_reasons": blockers, "repo_status_short": repo_status, "q22t_plan": plan, "powershell_invoked": False}

    ps_runner = ps_runner or _run_windows_powershell
    script = _rollback_script() if rollback else _enable_script()
    result = dict(ps_runner(script))
    if rollback:
        recognized, failures = _recognized_rolled_back(result)
        return {
            **base,
            "success": recognized,
            "execution_state": "mountain2_scheduler_rollback_completed" if recognized else "mountain2_scheduler_rollback_failed_or_incomplete",
            "blocked_reasons": [] if recognized else failures,
            "repo_status_short": repo_status,
            "q22t_plan": plan,
            "powershell_invoked": True,
            "powershell_result": result,
            "rollback_executed": recognized,
            "scheduler_enabled": False,
            "trigger_added": False,
            "periodic_execution_enabled": False,
        }
    recognized, failures = _recognized_enabled(result)
    return {
        **base,
        "success": recognized,
        "execution_state": "mountain2_scheduler_enabled" if recognized else "mountain2_scheduler_enablement_failed_or_incomplete",
        "blocked_reasons": [] if recognized else failures,
        "repo_status_short": repo_status,
        "q22t_plan": plan,
        "powershell_invoked": True,
        "powershell_result": result,
        "scheduler_action_replacement_executed": recognized,
        "scheduler_enabled": recognized,
        "trigger_added": recognized,
        "periodic_execution_enabled": recognized,
        "recurring_enablement_allowed_now": recognized,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="PS-Q22U Mountain2 scheduler enablement/rollback executor")
    parser.add_argument("--operator-acknowledged", action="store_true")
    parser.add_argument("--execute-enable-once", action="store_true")
    parser.add_argument("--rollback", action="store_true")
    parser.add_argument("--confirmation", default="")
    args = parser.parse_args(argv)
    result = run_scheduler_enablement_once(
        operator_acknowledged=bool(args.operator_acknowledged),
        execute_enable_once=bool(args.execute_enable_once),
        rollback=bool(args.rollback),
        confirmation=str(args.confirmation),
    )
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True, default=str))
    return 0 if result.get("ok") is True and (result.get("success") is True or (not args.execute_enable_once and not args.rollback)) else 1


if __name__ == "__main__":
    raise SystemExit(main())
