# path: ./tools/run_phase4a_prediction_system_ps_q21w_register_disabled_scheduler_once.py
# desc: PS-Q21W gated one-time registration of a disabled Windows Scheduled Task. Default is dry-run/no registration. The registered task is disabled, has no trigger, and its action is PS-Q21V dry-run only. Producer loop remains prohibited.

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

from tools.verify_phase4a_prediction_system_ps_q21u_scheduler_producer_registration_preflight import (  # noqa: E402
    REQUIRED_NEXT_PRODUCER_CONFIRMATION,
    REQUIRED_OPERATOR_CONFIRMATION,
    run_preflight,
)

REGISTRATION_VERSION = "prediction_warroom.register_disabled_scheduler_once.ps_q21w.v1"
TASK_NAME = "BTC_TS_PredictionWarRoom_NonUI_DisabledScheduler"
TASK_PATH = "\\BtcTradeSystem\\"
PS_Q21V_TOOL = REPO_ROOT / "tools" / "run_phase4a_prediction_system_ps_q21v_disabled_scheduler_registration_smoke.py"

PowerShellRunner = Callable[[str], dict[str, Any]]


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _ps_single(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


def _git_status_short() -> str:
    proc = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True)
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


def _task_action_args() -> str:
    return f'"{PS_Q21V_TOOL}"'


def _task_query_script() -> str:
    lines = [
        "$ErrorActionPreference = 'Stop'",
        f"$TaskName = {_ps_single(TASK_NAME)}",
        f"$TaskPath = {_ps_single(TASK_PATH)}",
        "$Task = Get-ScheduledTask -TaskPath $TaskPath -TaskName $TaskName -ErrorAction SilentlyContinue",
        "if ($null -eq $Task) { [PSCustomObject]@{ task_exists = $false } | ConvertTo-Json -Depth 5; exit 0 }",
        "[PSCustomObject]@{",
        "  task_exists = $true",
        "  task_name = $Task.TaskName",
        "  task_path = $Task.TaskPath",
        "  state = \"$($Task.State)\"",
        "  action_execute = \"$($Task.Actions[0].Execute)\"",
        "  action_arguments = \"$($Task.Actions[0].Arguments)\"",
        "  trigger_count = @($Task.Triggers).Count",
        "} | ConvertTo-Json -Depth 5",
    ]
    return "\n".join(lines)


def _task_register_script() -> str:
    lines = [
        "$ErrorActionPreference = 'Stop'",
        f"$TaskName = {_ps_single(TASK_NAME)}",
        f"$TaskPath = {_ps_single(TASK_PATH)}",
        f"$Exe = {_ps_single(sys.executable)}",
        f"$Arg = {_ps_single(_task_action_args())}",
        "$Existing = Get-ScheduledTask -TaskPath $TaskPath -TaskName $TaskName -ErrorAction SilentlyContinue",
        "if ($null -ne $Existing) { throw 'ps_q21w_task_already_exists' }",
        "$Action = New-ScheduledTaskAction -Execute $Exe -Argument $Arg",
        "$Principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive -RunLevel Limited",
        "$Settings = New-ScheduledTaskSettingsSet -MultipleInstances IgnoreNew -StartWhenAvailable:$false -ExecutionTimeLimit (New-TimeSpan -Minutes 10)",
        "$Task = New-ScheduledTask -Action $Action -Principal $Principal -Settings $Settings",
        "Register-ScheduledTask -TaskPath $TaskPath -TaskName $TaskName -InputObject $Task -Force | Out-Null",
        "Disable-ScheduledTask -TaskPath $TaskPath -TaskName $TaskName | Out-Null",
        "$Registered = Get-ScheduledTask -TaskPath $TaskPath -TaskName $TaskName",
        "[PSCustomObject]@{",
        "  task_exists = $true",
        "  task_name = $Registered.TaskName",
        "  task_path = $Registered.TaskPath",
        "  state = \"$($Registered.State)\"",
        "  action_execute = \"$($Registered.Actions[0].Execute)\"",
        "  action_arguments = \"$($Registered.Actions[0].Arguments)\"",
        "  trigger_count = @($Registered.Triggers).Count",
        "} | ConvertTo-Json -Depth 5",
    ]
    return "\n".join(lines)


def _task_unregister_script() -> str:
    lines = [
        "$ErrorActionPreference = 'Stop'",
        f"$TaskName = {_ps_single(TASK_NAME)}",
        f"$TaskPath = {_ps_single(TASK_PATH)}",
        f"$ExpectedArg = {_ps_single(_task_action_args())}",
        "$Task = Get-ScheduledTask -TaskPath $TaskPath -TaskName $TaskName -ErrorAction SilentlyContinue",
        "if ($null -eq $Task) { [PSCustomObject]@{ rollback_state = 'nothing_to_unregister'; task_exists_after = $false } | ConvertTo-Json -Depth 5; exit 0 }",
        "$ActualArg = \"$($Task.Actions[0].Arguments)\"",
        "if ($ActualArg -ne $ExpectedArg) { throw 'ps_q21w_task_action_mismatch_refusing_unregister' }",
        "Unregister-ScheduledTask -TaskPath $TaskPath -TaskName $TaskName -Confirm:$false",
        "$After = Get-ScheduledTask -TaskPath $TaskPath -TaskName $TaskName -ErrorAction SilentlyContinue",
        "[PSCustomObject]@{",
        "  rollback_state = 'unregistered_ps_q21w_disabled_scheduler_task_only'",
        "  task_exists_after = ($null -ne $After)",
        "} | ConvertTo-Json -Depth 5",
    ]
    return "\n".join(lines)


def _recognized_disabled_task(payload: Mapping[str, Any]) -> tuple[bool, list[str]]:
    failures: list[str] = []
    if payload.get("task_exists") is not True:
        failures.append("task_missing")
    if payload.get("task_name") != TASK_NAME:
        failures.append("task_name_mismatch")
    if str(payload.get("task_path") or "") != TASK_PATH:
        failures.append("task_path_mismatch")
    if str(payload.get("state") or "").lower() != "disabled":
        failures.append("task_state_not_disabled")
    if int(payload.get("trigger_count") or 0) != 0:
        failures.append("task_has_triggers")
    if str(payload.get("action_arguments") or "") != _task_action_args():
        failures.append("task_action_not_ps_q21v_dry_run")
    return not failures, failures


def _false_boundaries() -> dict[str, Any]:
    return {
        "producer_loop_enabled": False,
        "producer_loop_allowed": False,
        "producer_runner_invoked": False,
        "bounded_manual_refresh_invoked": False,
        "actual_export_runner_invoked": False,
        "latest_prediction_artifact_written": False,
        "status_artifact_written": False,
        "runtime_artifact_write_allowed": False,
        "status_artifact_write_allowed": False,
        "prediction_artifact_write_allowed": False,
        "view_artifact_write_allowed": False,
        "warroom_ui_trigger_allowed": False,
        "warroom_ui_trigger_invoked": False,
        "approval_or_ledger_allowed": False,
        "parameter_apply_allowed": False,
        "parameter_staging_write_allowed": False,
        "autotrade_trigger_allowed": False,
        "broker_private_api_allowed": False,
        "would_send_to_broker": False,
        "would_write_collector_state": False,
        "d_hot_lock_file_created": False,
        "d_hot_lock_file_written": False,
        "lock_acquire_attempted": False,
        "lock_release_attempted": False,
    }


def run_disabled_scheduler_registration_once(
    *,
    execute_register: bool = False,
    rollback: bool = False,
    confirmation: str = "",
    ps_runner: PowerShellRunner | None = None,
    preflight_packet: Mapping[str, Any] | None = None,
    git_status_short: str | None = None,
) -> dict[str, Any]:
    ps_runner = ps_runner or _run_windows_powershell
    confirmation_ok = confirmation == REQUIRED_OPERATOR_CONFIRMATION
    base = {
        "ok": True,
        "registration_version": REGISTRATION_VERSION,
        "task_name": TASK_NAME,
        "task_path": TASK_PATH,
        "task_action_execute": sys.executable,
        "task_action_arguments": _task_action_args(),
        "task_default_state_required": "Disabled",
        "task_trigger_count_required": 0,
        "created_at_utc": _utc_now(),
        "execute_register_requested": execute_register,
        "rollback_requested": rollback,
        "confirmation_ok": confirmation_ok,
        "required_operator_confirmation": REQUIRED_OPERATOR_CONFIRMATION,
        "required_next_producer_confirmation": REQUIRED_NEXT_PRODUCER_CONFIRMATION,
        "producer_loop_separate_operator_approval_required": True,
        "blocked_reasons": [],
        "os_scheduler_registration_attempted": False,
        "os_scheduler_registered": False,
        "scheduler_registered": False,
        "scheduler_registered_enabled": False,
        "scheduler_started": False,
        "scheduled_loop_enabled": False,
        "post_registration_readback_ok": False,
        "rollback_unregister_attempted": False,
        "rollback_unregister_ok": False,
        **_false_boundaries(),
    }
    if rollback:
        if not confirmation_ok:
            return {**base, "ok": False, "registration_state": "rollback_blocked_missing_exact_confirmation", "blocked_reasons": ["exact_operator_confirmation_required_for_rollback"]}
        rollback_result = ps_runner(_task_unregister_script())
        ok = rollback_result.get("ok") is True and rollback_result.get("task_exists_after") is False
        return {**base, "ok": ok, "registration_state": "rollback_unregistered_disabled_scheduler_task" if ok else "rollback_failed_or_incomplete", "rollback_unregister_attempted": True, "rollback_unregister_ok": ok, "rollback_result": rollback_result}
    if not execute_register:
        return {**base, "registration_state": "disabled_scheduler_registration_dry_run_no_registration", "next_required_action": "rerun_with_execute_register_and_exact_confirmation_only_when_operator_approves"}
    blockers: list[str] = []
    if not confirmation_ok:
        blockers.append("exact_operator_confirmation_required")
    status = _git_status_short() if git_status_short is None else git_status_short
    if status.strip():
        blockers.append("working_tree_must_be_clean_before_disabled_scheduler_registration")
    preflight = dict(preflight_packet) if preflight_packet is not None else run_preflight()
    if preflight.get("preflight_ready_for_separate_approval") is not True:
        blockers.append("ps_q21u_preflight_ready_required")
    if preflight.get("d_hot_lock_artifact_exists") is not False:
        blockers.append("d_hot_lock_absent_required")
    if blockers:
        return {**base, "ok": False, "registration_state": "disabled_scheduler_registration_blocked_no_registration", "blocked_reasons": blockers, "git_status_short": status, "preflight_state": preflight.get("preflight_state"), "preflight_blockers": list(preflight.get("preflight_blockers") or [])}
    register_result = ps_runner(_task_register_script())
    recognized, failures = _recognized_disabled_task(register_result)
    ok = register_result.get("ok") is True and recognized
    return {
        **base,
        "ok": ok,
        "registration_state": "disabled_scheduler_registered_and_verified" if ok else "disabled_scheduler_registration_readback_failed",
        "os_scheduler_registration_attempted": True,
        "os_scheduler_registered": ok,
        "scheduler_registered": ok,
        "scheduler_registered_enabled": False,
        "post_registration_readback_ok": ok,
        "registration_readback_failures": failures,
        "registration_result": register_result,
        "git_status_short": status,
        "preflight_state": preflight.get("preflight_state"),
        "preflight_blockers": list(preflight.get("preflight_blockers") or []),
        "latest_prediction_non_stale": preflight.get("latest_prediction_non_stale") is True,
        "latest_status_success_observed": preflight.get("latest_status_success_observed") is True,
        "d_hot_lock_artifact_exists": preflight.get("d_hot_lock_artifact_exists") is True,
    }


def query_disabled_scheduler_registration(*, ps_runner: PowerShellRunner | None = None) -> dict[str, Any]:
    ps_runner = ps_runner or _run_windows_powershell
    payload = ps_runner(_task_query_script())
    recognized, failures = _recognized_disabled_task(payload) if payload.get("task_exists") is True else (False, ["task_missing"])
    return {"ok": payload.get("ok") is True, "registration_version": REGISTRATION_VERSION, "query_state": "disabled_scheduler_task_visible" if recognized else "disabled_scheduler_task_not_visible_or_not_recognized", "task_recognized_as_ps_q21w": recognized, "task_readback_failures": failures, "task_readback": payload, **_false_boundaries()}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--execute-register", action="store_true")
    parser.add_argument("--rollback", action="store_true")
    parser.add_argument("--query", action="store_true")
    parser.add_argument("--confirmation", default="")
    args = parser.parse_args()
    if args.query:
        result = query_disabled_scheduler_registration()
    else:
        result = run_disabled_scheduler_registration_once(execute_register=args.execute_register, rollback=args.rollback, confirmation=args.confirmation)
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True, default=str))
    return 0 if result.get("ok") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
