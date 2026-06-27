# path: ./tools/verify_phase4a_prediction_system_ps_q21x_producer_loop_shadow_preflight_no_enablement.py
# desc: PS-Q21X read-only producer-loop shadow preflight after PS-Q21W. No producer runner invocation, no scheduler enablement, no trigger addition, no D-hot writes, no AutoTrade/broker.

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
from typing import Any, Mapping

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.run_phase4a_prediction_system_ps_q21w_register_disabled_scheduler_once import (  # noqa: E402
    PS_Q21V_TOOL,
    TASK_NAME,
    TASK_PATH,
    query_disabled_scheduler_registration,
)
from tools.verify_phase4a_prediction_system_ps_q21q_read_only_lock_scheduler_status_visibility import (  # noqa: E402
    DEFAULT_HOT_ROOT,
    run_visibility,
)
from tools.verify_phase4a_prediction_system_ps_q21u_scheduler_producer_registration_preflight import (  # noqa: E402
    REQUIRED_NEXT_PRODUCER_CONFIRMATION,
)

SHADOW_PREFLIGHT_VERSION = "prediction_warroom.producer_loop_shadow_preflight.ps_q21x.v1"


def _as_mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _git_status_short() -> str:
    proc = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True)
    return proc.stdout.strip()


def _false_boundary_fields() -> dict[str, Any]:
    return {
        "producer_loop_enabled": False,
        "producer_runner_invoked": False,
        "scheduled_loop_enabled": False,
        "scheduler_enabled": False,
        "trigger_added": False,
        "producer_runner_invocation_allowed_now": False,
        "producer_loop_enablement_allowed_now": False,
        "scheduler_enablement_allowed_now": False,
        "trigger_addition_allowed_now": False,
        "recurring_enablement_allowed_now": False,
        "runtime_artifact_write_allowed": False,
        "status_artifact_write_allowed": False,
        "prediction_artifact_write_allowed": False,
        "view_artifact_write_allowed": False,
        "warroom_ui_trigger_allowed": False,
        "approval_or_ledger_allowed": False,
        "parameter_apply_allowed": False,
        "parameter_staging_write_allowed": False,
        "autotrade_trigger_allowed": False,
        "broker_private_api_allowed": False,
        "would_send_to_broker": False,
        "would_write_collector_state": False,
        "bounded_manual_refresh_invoked": False,
        "actual_export_runner_invoked": False,
        "latest_prediction_artifact_written": False,
        "status_artifact_written": False,
        "d_hot_lock_file_created": False,
        "lock_acquire_attempted": False,
        "lock_release_attempted": False,
        "warroom_ui_trigger_invoked": False,
    }


def _task_readback(task: Mapping[str, Any]) -> Mapping[str, Any]:
    readback = task.get("task_readback")
    return readback if isinstance(readback, Mapping) else task


def _task_state(task: Mapping[str, Any], readback: Mapping[str, Any]) -> str:
    return str(task.get("task_state") or readback.get("state") or "")


def _task_action_target(task: Mapping[str, Any], readback: Mapping[str, Any]) -> str:
    return str(task.get("action_target") or readback.get("action_arguments") or "")


def _task_trigger_count(readback: Mapping[str, Any]) -> int:
    try:
        return int(readback.get("trigger_count") or 0)
    except Exception:
        return -1


def _task_recognized_for_shadow_preflight(task: Mapping[str, Any]) -> tuple[bool, list[str]]:
    failures: list[str] = []
    readback = _task_readback(task)
    if task.get("ok") is not True:
        failures.append("task_query_ok_required")
    if readback.get("task_exists") is not True:
        failures.append("ps_q21w_disabled_scheduler_task_exists_required")
    if task.get("task_recognized_as_ps_q21w") is not True:
        failures.append("ps_q21w_task_recognized_required")
    if str(readback.get("task_name") or "") != TASK_NAME:
        failures.append("task_name_mismatch")
    if str(readback.get("task_path") or "") != TASK_PATH:
        failures.append("task_path_mismatch")
    if _task_state(task, readback) != "Disabled":
        failures.append("task_state_disabled_required")
    if _task_trigger_count(readback) != 0:
        failures.append("task_trigger_count_zero_required")
    action_target = _task_action_target(task, readback)
    if str(PS_Q21V_TOOL) not in action_target and "run_phase4a_prediction_system_ps_q21v_disabled_scheduler_registration_smoke.py" not in action_target:
        failures.append("task_action_must_remain_ps_q21v_dry_run_tool")
    if task.get("producer_loop_enabled") is True:
        failures.append("task_result_producer_loop_must_remain_disabled")
    return not failures, failures


def build_producer_loop_shadow_preflight(
    *,
    visibility_packet: Mapping[str, Any],
    scheduler_query_packet: Mapping[str, Any],
    git_status_short: str,
) -> dict[str, Any]:
    visibility = _as_mapping(visibility_packet)
    task = _as_mapping(scheduler_query_packet)
    task_readback = _task_readback(task)
    task_ok, task_failures = _task_recognized_for_shadow_preflight(task)
    blockers: list[str] = []
    if git_status_short.strip():
        blockers.append("working_tree_must_be_clean_before_shadow_once_preflight")
    if visibility.get("ok") is not True:
        blockers.append("visibility_packet_ok_required")
    if visibility.get("latest_prediction_non_stale") is not True:
        blockers.append("latest_prediction_non_stale_required_before_shadow_once")
    if visibility.get("latest_status_success_observed") is not True:
        blockers.append("latest_status_success_required_before_shadow_once")
    if visibility.get("disabled_boundary_preserved") is not True:
        blockers.append("disabled_boundary_preserved_required")
    if visibility.get("d_hot_lock_artifact_exists") is not False:
        blockers.append("d_hot_lock_absent_required_before_shadow_once")
    if visibility.get("scheduler_enabled") is not False:
        blockers.append("d_hot_status_scheduler_disabled_required")
    if visibility.get("producer_enabled") is not False:
        blockers.append("d_hot_status_producer_disabled_required")
    if not task_ok:
        blockers.extend(task_failures)
    shadow_ready = not blockers
    status_disable_rollback_state = str(visibility.get("disable_rollback_state") or "")
    d_hot_scheduler_not_registered_caveat = "scheduler_not_registered" in status_disable_rollback_state
    return {
        "ok": True,
        "preflight_version": SHADOW_PREFLIGHT_VERSION,
        "preflight_state": "producer_loop_shadow_preflight_ready_for_one_shot_no_enablement" if shadow_ready else "producer_loop_shadow_preflight_blocked_no_enablement",
        "shadow_preflight_ready_for_one_shot": shadow_ready,
        "shadow_preflight_blockers": blockers,
        "read_only_shadow_preflight_only": True,
        "repo_clean": not bool(git_status_short.strip()),
        "git_status_short": git_status_short,
        "required_next_producer_confirmation": REQUIRED_NEXT_PRODUCER_CONFIRMATION,
        "producer_loop_shadow_once_requires_confirmation": REQUIRED_NEXT_PRODUCER_CONFIRMATION,
        "hot_root": str(DEFAULT_HOT_ROOT),
        "visibility_state": str(visibility.get("visibility_state") or ""),
        "visibility_attention_reasons": list(visibility.get("visibility_attention_reasons") or []),
        "generated_at": str(visibility.get("generated_at") or ""),
        "age_sec": visibility.get("age_sec"),
        "latest_prediction_non_stale": visibility.get("latest_prediction_non_stale") is True,
        "latest_status_success_observed": visibility.get("latest_status_success_observed") is True,
        "disabled_boundary_preserved": visibility.get("disabled_boundary_preserved") is True,
        "d_hot_lock_artifact_exists": visibility.get("d_hot_lock_artifact_exists") is True,
        "producer_state": str(visibility.get("producer_state") or ""),
        "producer_enabled": visibility.get("producer_enabled") is True,
        "scheduler_enabled_by_d_hot_status": visibility.get("scheduler_enabled") is True,
        "status_warnings": list(visibility.get("status_warnings") or []),
        "status_blockers": list(visibility.get("status_blockers") or []),
        "status_disable_rollback_state": status_disable_rollback_state,
        "producer_status_scheduler_not_registered_may_be_stale_manual_status_caveat": d_hot_scheduler_not_registered_caveat,
        "scheduler_not_registered_in_d_hot_status_does_not_invalidate_ps_q21w_os_task_query": True,
        "os_scheduler_registration_source": "ps_q21w_task_query",
        "producer_status_artifact_source": "D-hot prediction/status/non_ui_scheduled_producer_status.json",
        "task_query_state": str(task.get("query_state") or ""),
        "task_recognized_as_ps_q21w": task.get("task_recognized_as_ps_q21w") is True,
        "task_exists": task_readback.get("task_exists") is True,
        "task_name": str(task_readback.get("task_name") or ""),
        "task_path": str(task_readback.get("task_path") or ""),
        "task_state": _task_state(task, task_readback),
        "task_trigger_count": _task_trigger_count(task_readback),
        "task_action_target": _task_action_target(task, task_readback),
        "task_readback_failures": list(task.get("task_readback_failures") or []),
        "shadow_once_contract": {
            "single_run_only": True,
            "non_recurring": True,
            "requires_non_overlap_lock": True,
            "requires_status_visibility_update": True,
            "requires_rollback_conditions": True,
            "must_keep_broker_autotrade_false": True,
            "must_not_enable_scheduler": True,
            "must_not_add_trigger": True,
        },
        "next_allowed_slice_after_explicit_approval": "producer_loop_shadow_once_single_run_with_rollback_plan",
        **_false_boundary_fields(),
    }


def run_shadow_preflight() -> dict[str, Any]:
    visibility = run_visibility(hot_root=DEFAULT_HOT_ROOT)
    scheduler_query = query_disabled_scheduler_registration()
    return build_producer_loop_shadow_preflight(
        visibility_packet=visibility,
        scheduler_query_packet=scheduler_query,
        git_status_short=_git_status_short(),
    )


def main() -> int:
    result = run_shadow_preflight()
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True, default=str))
    return 0 if result.get("ok") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
