# path: ./tools/diagnose_phase4a_prediction_system_ps_q23i_post_switch_closeout_readiness.py
# desc: PS-Q23I read-only closeout/readiness after scheduled distributed sidecar dual-write enablement.

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

from tools.diagnose_phase4a_prediction_system_ps_q23e_manifest_first_live_read_model import run_manifest_first_live_read_model_diagnostic  # noqa: E402
from tools.diagnose_phase4a_prediction_system_ps_q23g_scheduler_sidecar_action_plan_no_write import (  # noqa: E402
    SIDECAR_CONFIRMATION_FLAG,
    SIDECAR_ENABLE_FLAG,
    expected_silent_launcher_args,
)
from tools.run_phase4a_prediction_system_ps_q21w_register_disabled_scheduler_once import (  # noqa: E402
    TASK_NAME,
    TASK_PATH,
    _run_windows_powershell,
)
from tools.run_phase4a_prediction_system_ps_q23b_gated_dual_write_sidecars_once import REQUIRED_CONFIRMATION as REQUIRED_DISTRIBUTED_SIDECAR_CONFIRMATION  # noqa: E402
from tools.run_phase4a_prediction_system_ps_q21i_one_shot_bounded_manual_latest_prediction_write import DEFAULT_HOT_ROOT  # noqa: E402

DIAGNOSTIC_VERSION = "prediction_warroom.post_switch_closeout_readiness.ps_q23i.v1"
LATEST_MANIFEST_RELATIVE_PATH = Path("prediction/latest_manifest.json")
ROLLBACK_CONFIRMATION_CANDIDATE = "ROLLBACK_SILENT_SCHEDULER_ACTION_REMOVE_DISTRIBUTED_SIDECAR_FLAGS_ONCE"


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _as_mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _ps_single(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


def _git_status_short() -> str:
    proc = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=False)
    return proc.stdout.strip()


def _load_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8-sig")) if path.exists() else {}
        return data if isinstance(data, dict) else {}
    except Exception as exc:
        return {"_load_error": f"{exc.__class__.__name__}: {exc}"}


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


def _sidecar_flags_present(args: str) -> bool:
    return SIDECAR_ENABLE_FLAG in args and SIDECAR_CONFIRMATION_FLAG in args and REQUIRED_DISTRIBUTED_SIDECAR_CONFIRMATION in args


def _false_safety_flags() -> dict[str, Any]:
    return {
        "scheduler_action_changed_by_this_tool": False,
        "rollback_executed": False,
        "ui_default_call_path_changed": False,
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


def build_post_switch_closeout(*, repo_status_short: str, scheduler_task: Mapping[str, Any], latest_manifest: Mapping[str, Any], q23e: Mapping[str, Any]) -> dict[str, Any]:
    task = _as_mapping(scheduler_task)
    manifest = _as_mapping(latest_manifest)
    q23e_map = _as_mapping(q23e)
    args = str(task.get("action_arguments") or "")
    execute = str(task.get("action_execute") or "")
    rollback_action_args = expected_silent_launcher_args()
    blockers: list[str] = []
    warnings: list[str] = []
    if repo_status_short.strip():
        blockers.append("repo_clean_required_before_post_switch_closeout")
    if task.get("ok") is not True or task.get("task_exists") is not True:
        blockers.append("scheduler_task_exists_required")
    if task.get("task_name") != TASK_NAME or str(task.get("task_path") or "") != TASK_PATH:
        blockers.append("scheduler_task_identity_mismatch")
    if int(task.get("trigger_count") or 0) != 1:
        blockers.append("scheduler_task_trigger_count_must_be_one")
    if not execute.lower().endswith("pythonw.exe"):
        blockers.append("scheduler_action_execute_must_be_pythonw")
    if not _sidecar_flags_present(args):
        blockers.append("scheduler_action_must_include_sidecar_flags")
    if not str(manifest.get("run_dir") or "").startswith("prediction/runs/"):
        blockers.append("latest_manifest_run_dir_required")
    if manifest.get("record_count") in (None, "", 0):
        blockers.append("latest_manifest_record_count_required")
    if q23e_map.get("ok") is not True:
        blockers.append("q23e_manifest_first_diagnostic_ok_required")
    if q23e_map.get("distributed_reader_ready") is not True:
        blockers.append("q23e_distributed_reader_ready_required")
    if q23e_map.get("legacy_fallback_ready") is not True:
        blockers.append("q23e_legacy_fallback_ready_required")
    if q23e_map.get("distributed_stale_vs_legacy") is True:
        blockers.append("q23e_distributed_must_not_be_stale_vs_legacy")
    if q23e_map.get("source_artifact_mode") != "distributed":
        blockers.append("q23e_source_artifact_mode_must_be_distributed")
    if q23e_map.get("selected_record_count") != manifest.get("record_count"):
        warnings.append("q23e_selected_record_count_differs_from_latest_manifest")
    ready = not blockers
    return {
        "ok": True,
        "diagnostic_version": DIAGNOSTIC_VERSION,
        "generated_at": _utc_now(),
        "closeout_state": "post_switch_closeout_ready" if ready else "post_switch_closeout_blocked",
        "post_switch_closeout_ready": ready,
        "reader_default_change_preflight_ready": ready,
        "rollback_plan_ready": bool(_sidecar_flags_present(args) and execute.lower().endswith("pythonw.exe") and int(task.get("trigger_count") or 0) == 1),
        "blockers": blockers,
        "warnings": warnings,
        "repo_status_short": repo_status_short,
        "scheduler_task": dict(task),
        "scheduled_sidecar_dual_write_enabled_observed": _sidecar_flags_present(args),
        "trigger_count": int(task.get("trigger_count") or 0),
        "current_action_execute": execute,
        "current_action_arguments": args,
        "rollback_candidate_action_execute": execute,
        "rollback_candidate_action_arguments": rollback_action_args,
        "rollback_confirmation_candidate": ROLLBACK_CONFIRMATION_CANDIDATE,
        "latest_manifest": {
            "generated_at": manifest.get("generated_at"),
            "latest_manifest_written_at": manifest.get("latest_manifest_written_at"),
            "record_count": manifest.get("record_count"),
            "run_dir": manifest.get("run_dir"),
            "legacy_latest_retained": manifest.get("legacy_latest_retained"),
            "legacy_latest_modified": manifest.get("legacy_latest_modified"),
            "status_artifact_written": manifest.get("status_artifact_written"),
        },
        "q23e": {
            "ok": q23e_map.get("ok"),
            "source_artifact_mode": q23e_map.get("source_artifact_mode"),
            "selected_generated_at": q23e_map.get("selected_generated_at"),
            "selected_record_count": q23e_map.get("selected_record_count"),
            "distributed_reader_ready": q23e_map.get("distributed_reader_ready"),
            "distributed_stale_vs_legacy": q23e_map.get("distributed_stale_vs_legacy"),
            "legacy_fallback_ready": q23e_map.get("legacy_fallback_ready"),
            "read_model_freshness_state": _as_mapping(q23e_map.get("read_model")).get("freshness_state"),
            "read_model_record_count": _as_mapping(q23e_map.get("read_model")).get("record_count"),
        },
        "read_only_diagnostic": True,
        **_false_safety_flags(),
    }


def run_post_switch_closeout_readiness(*, hot_root: Path = DEFAULT_HOT_ROOT) -> dict[str, Any]:
    return build_post_switch_closeout(
        repo_status_short=_git_status_short(),
        scheduler_task=read_scheduler_task(),
        latest_manifest=_load_json(hot_root / LATEST_MANIFEST_RELATIVE_PATH),
        q23e=run_manifest_first_live_read_model_diagnostic(hot_root=hot_root),
    )


def main() -> int:
    result = run_post_switch_closeout_readiness()
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True, default=str))
    return 0 if result.get("ok") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
