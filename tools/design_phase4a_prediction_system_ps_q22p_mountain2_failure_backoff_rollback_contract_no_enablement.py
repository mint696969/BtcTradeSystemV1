# path: ./tools/design_phase4a_prediction_system_ps_q22p_mountain2_failure_backoff_rollback_contract_no_enablement.py
# desc: PS-Q22P read-only Mountain2 failure/backoff/status visibility/rollback contract. No scheduler enablement, no trigger addition, no recurring execution, no runtime writes.

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

from tools.run_phase4a_prediction_system_ps_q22o_mountain2_scheduled_latest_refresh_tick_once import (  # noqa: E402
    RUNNER_VERSION as Q22O_RUNNER_VERSION,
    run_mountain2_tick_runner_skeleton,
)

CONTRACT_VERSION = "prediction_warroom.mountain2_failure_backoff_rollback_contract_no_enablement.ps_q22p.v1"
SOFT_BACKOFF_FAILURES = 2
HARD_DISABLE_FAILURES = 3


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _as_mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _git_status_short() -> str:
    proc = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=False)
    return proc.stdout.strip()


def build_failure_backoff_rollback_contract(*, repo_status_short: str, q22o_packet: Mapping[str, Any]) -> dict[str, Any]:
    q22o = _as_mapping(q22o_packet)
    blockers: list[str] = []
    warnings: list[str] = []
    if repo_status_short.strip():
        blockers.append("repo_clean_required_before_failure_backoff_contract")
    if q22o.get("runner_version") != Q22O_RUNNER_VERSION:
        blockers.append("q22o_runner_skeleton_required")
    if q22o.get("scheduler_enabled") is not False or q22o.get("trigger_added") is not False:
        blockers.append("q22o_must_preserve_no_scheduler_no_trigger")
    if q22o.get("latest_prediction_artifact_written") is not False or q22o.get("status_artifact_written") is not False:
        blockers.append("q22o_must_preserve_no_runtime_writes")
    if q22o.get("lock_acquire_attempted") is not False:
        blockers.append("q22o_must_not_acquire_lock")
    if q22o.get("danger_boundary_next_stop", {}).get("must_stop_before_scheduler_enablement") is not True:
        blockers.append("q22o_danger_boundary_stop_required")
    if q22o.get("runner_ready_for_future_danger_boundary_review") is not True:
        warnings.append("q22o_not_fully_runtime_ready_may_need_fresh_latest_before_enablement")
    ready = not blockers
    return {
        "ok": True,
        "contract_version": CONTRACT_VERSION,
        "contract_state": "mountain2_failure_backoff_rollback_contract_ready_no_enablement" if ready else "mountain2_failure_backoff_rollback_contract_blocked_no_enablement",
        "contract_ready_for_future_enablement_review": ready,
        "contract_blockers": blockers,
        "contract_warnings": warnings,
        "generated_at": _utc_now(),
        "repo_status_short": repo_status_short,
        "q22o_runner_state": q22o.get("runner_state"),
        "q22o_runner_ready_for_future_danger_boundary_review": q22o.get("runner_ready_for_future_danger_boundary_review") is True,
        "q22o_blocked_reasons": list(q22o.get("blocked_reasons") or []),
        "q22o_warning_reasons": list(q22o.get("warning_reasons") or []),
        "failure_backoff_contract": {
            "write_status_on_success_required": True,
            "write_status_on_failure_required": True,
            "write_status_on_skip_required": True,
            "preserve_last_success_on_failure": True,
            "do_not_delete_latest_prediction_on_failure": True,
            "increment_consecutive_failure_count": True,
            "soft_backoff_after_consecutive_failures": SOFT_BACKOFF_FAILURES,
            "hard_disable_after_consecutive_failures": HARD_DISABLE_FAILURES,
            "fail_closed_on_blockers": True,
            "no_retry_inside_same_tick": True,
            "release_lock_on_success_failure_or_skip": True,
            "operator_required_after_hard_disable": True,
        },
        "status_visibility_contract": {
            "must_show_last_run_started_at": True,
            "must_show_last_run_finished_at": True,
            "must_show_last_success_generated_at": True,
            "must_show_last_failure_at": True,
            "must_show_consecutive_failure_count": True,
            "must_show_last_blocker_count": True,
            "must_show_warnings_and_blockers": True,
            "must_show_scheduler_and_trigger_state": True,
            "must_show_safe_flags": True,
        },
        "rollback_contract": {
            "disable_scheduler_first": True,
            "remove_added_periodic_trigger": True,
            "restore_disabled_dry_run_action_if_action_replaced": True,
            "do_not_delete_latest_prediction": True,
            "do_not_mutate_parameters": True,
            "do_not_append_ledger": True,
            "preserve_status_visibility": True,
            "operator_confirmation_required": True,
        },
        "future_danger_boundary_not_crossed": {
            "scheduler_action_replacement_executed": False,
            "periodic_trigger_added": False,
            "scheduler_enabled": False,
            "recurring_execution_enabled": False,
            "latest_write_enabled_per_tick": False,
            "lock_acquire_enabled": False,
            "rollback_executed": False,
        },
        "next_recommended_action": "Stop for operator before any Mountain2 enablement, or implement a final no-enable readiness packet that names the exact dangerous commands without running them." if ready else "Resolve contract blockers, then re-run PS-Q22P.",
        "read_only_contract_only": True,
        "scheduler_enabled": False,
        "trigger_added": False,
        "trigger_addition_allowed_now": False,
        "recurring_enablement_allowed_now": False,
        "periodic_execution_enabled": False,
        "producer_loop_enabled": False,
        "producer_runner_invoked": False,
        "bounded_manual_refresh_invoked": False,
        "actual_export_runner_invoked": False,
        "latest_prediction_artifact_written": False,
        "status_artifact_written": False,
        "lock_file_created": False,
        "lock_file_written": False,
        "lock_acquire_attempted": False,
        "lock_release_attempted": False,
        "rollback_executed": False,
        "warroom_ui_trigger_allowed": False,
        "approval_or_ledger_allowed": False,
        "parameter_apply_allowed": False,
        "parameter_staging_write_allowed": False,
        "autotrade_trigger_allowed": False,
        "broker_private_api_allowed": False,
        "would_send_to_broker": False,
        "would_write_collector_state": False,
    }


def run_contract() -> dict[str, Any]:
    return build_failure_backoff_rollback_contract(
        repo_status_short=_git_status_short(),
        q22o_packet=run_mountain2_tick_runner_skeleton(),
    )


def main() -> int:
    result = run_contract()
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True, default=str))
    return 0 if result.get("ok") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
