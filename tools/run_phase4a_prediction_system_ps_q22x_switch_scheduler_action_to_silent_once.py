# path: ./tools/run_phase4a_prediction_system_ps_q22x_switch_scheduler_action_to_silent_once.py
# desc: PS-Q22X exact-token scheduler action replacement from visible python.exe Q22S to hidden pythonw.exe silent launcher. Preserves trigger/cadence.

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
from tools.diagnose_phase4a_prediction_system_ps_q22v_post_enablement_tick_readiness import run_post_enablement_readiness  # noqa: E402
from tools.run_phase4a_prediction_system_ps_q21w_register_disabled_scheduler_once import TASK_NAME, TASK_PATH  # noqa: E402
from tools.diagnose_phase4a_prediction_system_ps_q22t_mountain2_scheduler_enablement_plan_no_write import Q22S_TOOL  # noqa: E402

SWITCH_VERSION = "prediction_warroom.silent_scheduler_action_switch.ps_q22x.v1"
Q22X_TOOL = REPO_ROOT / "tools/run_phase4a_prediction_system_ps_q22x_silent_q22s_launcher.py"
PowerShellRunner = Callable[[str], Mapping[str, Any]]
ReadinessProvider = Callable[[], Mapping[str, Any]]


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _ps_single(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


def _git_status_short() -> str:
    proc = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=False)
    return proc.stdout.strip()


def _direct_q22s_action_args() -> str:
    return f'"{Q22S_TOOL}" --operator-acknowledged --execute-tick-once --confirmation {FUTURE_MOUNTAIN2_TOKEN_CANDIDATE}'


def _silent_q22x_action_args() -> str:
    return f'"{Q22X_TOOL}" --operator-acknowledged --execute-tick-once --confirmation {FUTURE_MOUNTAIN2_TOKEN_CANDIDATE}'


def _pythonw_candidates() -> list[Path]:
    candidates: list[Path] = []
    venv = REPO_ROOT / ".venv/Scripts/pythonw.exe"
    candidates.append(venv)
    exe = Path(sys.executable)
    if exe.name.lower() == "python.exe":
        candidates.append(exe.with_name("pythonw.exe"))
    return candidates


def _default_pythonw() -> Path | None:
    for candidate in _pythonw_candidates():
        if candidate.exists():
            return candidate
    return None


def _false_boundaries() -> dict[str, Any]:
    return {
        "trigger_added": False,
        "trigger_addition_allowed_now": False,
        "periodic_execution_enabled_by_this_tool": False,
        "latest_prediction_artifact_written": False,
        "status_artifact_written": False,
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


def _switch_script(*, pythonw: Path) -> str:
    lines = [
        "$ErrorActionPreference = 'Stop'",
        f"$TaskName = {_ps_single(TASK_NAME)}",
        f"$TaskPath = {_ps_single(TASK_PATH)}",
        f"$DirectArg = {_ps_single(_direct_q22s_action_args())}",
        f"$SilentArg = {_ps_single(_silent_q22x_action_args())}",
        f"$Pythonw = {_ps_single(str(pythonw))}",
        "if (!(Test-Path $Pythonw)) { throw 'pythonw_exe_missing' }",
        "$Before = Get-ScheduledTask -TaskPath $TaskPath -TaskName $TaskName -ErrorAction Stop",
        "$BeforeState = \"$($Before.State)\"",
        "$BeforeTriggerCount = if ($null -eq $Before.Triggers) { 0 } else { @($Before.Triggers).Count }",
        "$BeforeArg = \"$($Before.Actions[0].Arguments)\"",
        "$BeforeExe = \"$($Before.Actions[0].Execute)\"",
        "if ($BeforeTriggerCount -ne 1) { throw 'trigger_count_must_remain_one_before_silent_switch' }",
        "if (($BeforeArg -ne $DirectArg) -and ($BeforeArg -ne $SilentArg)) { throw 'unknown_scheduler_action_before_silent_switch' }",
        "$WasEnabled = ($BeforeState -ne 'Disabled')",
        "Disable-ScheduledTask -TaskPath $TaskPath -TaskName $TaskName | Out-Null",
        "$Action = New-ScheduledTaskAction -Execute $Pythonw -Argument $SilentArg",
        "Set-ScheduledTask -TaskPath $TaskPath -TaskName $TaskName -Action $Action | Out-Null",
        "if ($WasEnabled) { Enable-ScheduledTask -TaskPath $TaskPath -TaskName $TaskName | Out-Null }",
        "$After = Get-ScheduledTask -TaskPath $TaskPath -TaskName $TaskName -ErrorAction Stop",
        * _task_readback_lines("$After"),
    ]
    return "\n".join(lines)


def _recognized_silent(readback: Mapping[str, Any], *, pythonw: Path) -> tuple[bool, list[str]]:
    failures: list[str] = []
    if readback.get("ok") is not True:
        failures.append("powershell_result_not_ok")
    if readback.get("task_name") != TASK_NAME:
        failures.append("task_name_mismatch")
    if str(readback.get("task_path") or "") != TASK_PATH:
        failures.append("task_path_mismatch")
    if int(readback.get("trigger_count") or 0) != 1:
        failures.append("trigger_count_not_one_after_silent_switch")
    if str(readback.get("action_execute") or "").lower() != str(pythonw).lower():
        failures.append("task_action_execute_not_pythonw")
    if str(readback.get("action_arguments") or "") != _silent_q22x_action_args():
        failures.append("task_action_arguments_not_silent_launcher")
    if str(readback.get("state") or "").lower() == "disabled":
        failures.append("task_disabled_after_silent_switch")
    return not failures, failures


def run_switch_to_silent_scheduler_action_once(
    *,
    operator_acknowledged: bool = False,
    execute_switch_once: bool = False,
    confirmation: str = "",
    pythonw_path: Path | None = None,
    ps_runner: PowerShellRunner | None = None,
    readiness_provider: ReadinessProvider | None = None,
    repo_status_short: str | None = None,
) -> dict[str, Any]:
    confirmation_ok = confirmation == FUTURE_MOUNTAIN2_TOKEN_CANDIDATE
    base = {
        "ok": True,
        "switch_version": SWITCH_VERSION,
        "generated_at": _utc_now(),
        "required_confirmation": FUTURE_MOUNTAIN2_TOKEN_CANDIDATE,
        "confirmation_ok": confirmation_ok,
        "default_execution_is_dry_run_no_write": True,
        "scheduler_action_replacement_executed": False,
        "scheduler_enabled_by_this_tool": False,
        "rollback_executed": False,
        **_false_boundaries(),
    }
    blockers: list[str] = []
    if not operator_acknowledged:
        blockers.append("operator_acknowledgement_required")
    if not execute_switch_once:
        blockers.append("execute_switch_once_flag_required")
    if not confirmation_ok:
        blockers.append("exact_silent_scheduler_switch_confirmation_required")
    repo_status = _git_status_short() if repo_status_short is None else str(repo_status_short)
    if repo_status:
        blockers.append("repo_clean_required_before_silent_scheduler_switch")
    pythonw = pythonw_path or _default_pythonw()
    if pythonw is None:
        blockers.append("pythonw_exe_required_for_silent_scheduler_switch")
    readiness_provider = readiness_provider or run_post_enablement_readiness
    readiness = dict(readiness_provider())
    if readiness.get("post_enablement_tick_ready") is not True:
        blockers.append("q22v_post_enablement_ready_required_before_silent_switch")
    if blockers:
        return {**base, "success": False, "execution_state": "silent_scheduler_action_switch_blocked_no_write", "blocked_reasons": blockers, "repo_status_short": repo_status, "q22v_readiness": readiness, "powershell_invoked": False, "pythonw_path": str(pythonw) if pythonw else ""}
    ps_runner = ps_runner or _run_windows_powershell
    result = dict(ps_runner(_switch_script(pythonw=pythonw)))
    recognized, failures = _recognized_silent(result, pythonw=pythonw)
    return {
        **base,
        "success": recognized,
        "execution_state": "silent_scheduler_action_switch_completed" if recognized else "silent_scheduler_action_switch_failed_or_incomplete",
        "blocked_reasons": [] if recognized else failures,
        "repo_status_short": repo_status,
        "q22v_readiness": readiness,
        "powershell_invoked": True,
        "powershell_result": result,
        "pythonw_path": str(pythonw),
        "silent_launcher_args": _silent_q22x_action_args(),
        "scheduler_action_replacement_executed": recognized,
        "scheduler_enabled_by_this_tool": recognized,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="PS-Q22X switch visible Q22S scheduler action to pythonw silent launcher")
    parser.add_argument("--operator-acknowledged", action="store_true")
    parser.add_argument("--execute-switch-once", action="store_true")
    parser.add_argument("--confirmation", default="")
    args = parser.parse_args(argv)
    result = run_switch_to_silent_scheduler_action_once(
        operator_acknowledged=bool(args.operator_acknowledged),
        execute_switch_once=bool(args.execute_switch_once),
        confirmation=str(args.confirmation),
    )
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True, default=str))
    return 0 if result.get("ok") is True and (result.get("success") is True or not args.execute_switch_once) else 1


if __name__ == "__main__":
    raise SystemExit(main())
