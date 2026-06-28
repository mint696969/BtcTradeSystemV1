# path: ./tools/diagnose_phase4a_prediction_system_ps_q22v_post_enablement_tick_readiness.py
# desc: PS-Q22V read-only post-enablement scheduled tick readiness accepted by Q22S after Q22U scheduler enablement.

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

from tools.run_phase4a_prediction_system_ps_q21w_register_disabled_scheduler_once import (  # noqa: E402
    TASK_NAME,
    TASK_PATH,
    _run_windows_powershell,
)

HOT_ROOT = Path(r"D:\btc_ts_hot")
LATEST = HOT_ROOT / "prediction/latest_prediction_system_result.json"
STATUS = HOT_ROOT / "prediction/status/non_ui_scheduled_producer_status.json"
Q22V_VERSION = "prediction_warroom.post_enablement_tick_readiness.ps_q22v.v1"
Q22E_STATUS_VERSION = "prediction_warroom.success_preserving_status_write_once.ps_q22e.v1"
Q22S_TOOL_NAME = "run_phase4a_prediction_system_ps_q22s_mountain2_actual_scheduled_latest_refresh_tick_once.py"
Q22S_RUNNER_VERSION = "prediction_warroom.mountain2_actual_scheduled_latest_refresh_tick_once.ps_q22s.v1"


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _as_mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _load_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8-sig")) if path.exists() else {}
        return data if isinstance(data, dict) else {}
    except Exception as exc:
        return {"_load_error": f"{exc.__class__.__name__}: {exc}"}


def _file_meta(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"exists": False, "size_bytes": None, "mtime_utc": ""}
    stat = path.stat()
    return {
        "exists": True,
        "size_bytes": int(stat.st_size),
        "mtime_utc": datetime.fromtimestamp(stat.st_mtime, timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
    }


def _git_status_short() -> str:
    proc = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=False)
    return proc.stdout.strip()


def _generated_at(latest: Mapping[str, Any]) -> str:
    batch = _as_mapping(latest.get("forecast_batch"))
    return str(batch.get("generated_at") or latest.get("generated_at") or "")


def _ps_single(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


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


def _task_packet() -> dict[str, Any]:
    return dict(_run_windows_powershell(_task_query_script()))


def build_post_enablement_readiness(*, repo_status_short: str, latest_payload: Mapping[str, Any], latest_meta: Mapping[str, Any], status_payload: Mapping[str, Any], status_meta: Mapping[str, Any], scheduler_task: Mapping[str, Any]) -> dict[str, Any]:
    latest = _as_mapping(latest_payload)
    status = _as_mapping(status_payload)
    task = _as_mapping(scheduler_task)
    generated_at = _generated_at(latest)
    safe = _as_mapping(status.get("safe_flags"))
    blockers: list[str] = []
    if repo_status_short.strip():
        blockers.append("repo_clean_required_before_post_enablement_tick")
    if latest_meta.get("exists") is not True or status_meta.get("exists") is not True:
        blockers.append("latest_and_status_artifacts_required")
    if task.get("ok") is not True or task.get("task_exists") is not True:
        blockers.append("scheduler_task_exists_required")
    if task.get("task_name") != TASK_NAME or str(task.get("task_path") or "") != TASK_PATH:
        blockers.append("scheduler_task_identity_mismatch")
    if str(task.get("state") or "") not in {"Ready", "Running", "Queued"}:
        blockers.append("scheduler_task_must_be_ready_running_or_queued_after_enablement")
    if int(task.get("trigger_count") or 0) < 1:
        blockers.append("scheduler_task_trigger_required_after_enablement")
    action_args = str(task.get("action_arguments") or "")
    if Q22S_TOOL_NAME not in action_args:
        blockers.append("scheduler_task_action_must_be_q22s_after_enablement")
    q22e_success_marker = bool(
        status.get("producer_version") == Q22E_STATUS_VERSION
        and status.get("producer_state") == "manual_refresh_exported_status_written"
    )
    retryable_q22s_failure = bool(
        status.get("producer_version") == Q22S_RUNNER_VERSION
        and status.get("producer_state") in {"mountain2_tick_failed", "mountain2_actual_tick_failed", "mountain2_actual_tick_skipped_active_lock"}
        and status.get("failure_preserved_previous_success") is True
        and status.get("last_tick_run_id")
        and int(status.get("consecutive_failure_count") or 0) < 3
    )
    status_acceptance_mode = "q22e_success_marker" if q22e_success_marker else "retryable_q22s_failure_preserved_success" if retryable_q22s_failure else "blocked"
    if not (q22e_success_marker or retryable_q22s_failure):
        blockers.append("q22e_success_or_retryable_q22s_failure_status_required_before_tick")
    if status.get("last_success_generated_at") != generated_at:
        blockers.append("status_last_success_generated_at_must_match_latest")
    if status.get("producer_enabled") is not False:
        blockers.append("d_hot_status_producer_enabled_must_remain_false")
    for key in (
        "autotrade_trigger_allowed_false",
        "broker_private_api_allowed_false",
        "would_send_to_broker_false",
        "parameter_apply_allowed_false",
        "parameter_staging_write_allowed_false",
    ):
        if safe.get(key) is not True:
            blockers.append(f"safe_flag_required:{key}")
    ready = not blockers
    return {
        "ok": True,
        "readiness_version": Q22V_VERSION,
        "readiness_state": "post_enablement_tick_readiness_ready" if ready else "post_enablement_tick_readiness_blocked",
        "post_enablement_tick_ready": ready,
        "readiness_blockers": blockers,
        "generated_at": _utc_now(),
        "repo_status_short": repo_status_short,
        "latest_generated_at": generated_at,
        "latest_meta": dict(latest_meta),
        "status_meta": dict(status_meta),
        "status_producer_version": status.get("producer_version"),
        "status_producer_state": status.get("producer_state"),
        "status_last_success_generated_at": status.get("last_success_generated_at"),
        "status_acceptance_mode": status_acceptance_mode,
        "status_consecutive_failure_count": status.get("consecutive_failure_count"),
        "scheduler_task": dict(task),
        "q22s_runner_version": Q22S_RUNNER_VERSION,
        "read_only_diagnostic": True,
        "scheduler_action_replacement_executed": False,
        "scheduler_enabled_by_this_tool": False,
        "trigger_added_by_this_tool": False,
        "periodic_execution_enabled_by_this_tool": False,
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


def run_post_enablement_readiness() -> dict[str, Any]:
    return build_post_enablement_readiness(
        repo_status_short=_git_status_short(),
        latest_payload=_load_json(LATEST),
        latest_meta=_file_meta(LATEST),
        status_payload=_load_json(STATUS),
        status_meta=_file_meta(STATUS),
        scheduler_task=_task_packet(),
    )


def main() -> int:
    result = run_post_enablement_readiness()
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True, default=str))
    return 0 if result.get("ok") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
