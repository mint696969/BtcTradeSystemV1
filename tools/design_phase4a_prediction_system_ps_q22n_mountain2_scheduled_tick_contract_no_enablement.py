# path: ./tools/design_phase4a_prediction_system_ps_q22n_mountain2_scheduled_tick_contract_no_enablement.py
# desc: PS-Q22N read-only Mountain2 scheduled latest-refresh tick contract. No scheduler enablement, no trigger addition, no recurring execution, no runtime writes, no broker/AutoTrade.

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

from tools.diagnose_phase4a_prediction_system_ps_q22m_mountain2_recurring_trigger_prep_no_enablement import (  # noqa: E402
    FUTURE_MOUNTAIN2_TOKEN_CANDIDATE,
    run_prep as run_q22m_prep,
)
from tools.design_phase4a_prediction_system_ps_q21o_single_run_lock_contract import run_contract as run_q21o_lock_contract  # noqa: E402

CONTRACT_VERSION = "prediction_warroom.mountain2_scheduled_tick_contract_no_enablement.ps_q22n.v1"
FUTURE_TICK_NAME = "mountain2_scheduled_latest_refresh_tick_once"
FUTURE_TICK_SCRIPT_CANDIDATE = "tools/run_phase4a_prediction_system_ps_q22o_mountain2_scheduled_latest_refresh_tick_once.py"


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _as_mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _git_status_short() -> str:
    proc = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=False)
    return proc.stdout.strip()


def build_scheduled_tick_contract(*, repo_status_short: str, q22m_packet: Mapping[str, Any], q21o_packet: Mapping[str, Any]) -> dict[str, Any]:
    q22m = _as_mapping(q22m_packet)
    q21o = _as_mapping(q21o_packet)
    blockers: list[str] = []
    warnings: list[str] = []
    if repo_status_short.strip():
        blockers.append("repo_clean_required_before_scheduled_tick_contract")
    if q22m.get("prep_ready_for_future_enablement_design") is not True:
        warnings.append("q22m_prep_not_ready_runtime_conditions_may_need_fresh_latest_before_enablement")
    if q22m.get("scheduler_task", {}).get("task_state") != "Disabled":
        blockers.append("existing_scheduler_task_must_be_disabled_before_tick_contract")
    if q22m.get("scheduler_task", {}).get("task_trigger_count") not in (0, None):
        blockers.append("existing_scheduler_task_must_have_zero_triggers_before_tick_contract")
    if q22m.get("scheduler_enabled") is not False or q22m.get("trigger_added") is not False:
        blockers.append("q22m_must_not_have_enabled_scheduler_or_trigger")
    if q21o.get("lock_file_creation_allowed") is not False or q21o.get("lock_acquire_allowed_now") is not False:
        blockers.append("q21o_lock_contract_must_be_no_file_creation_no_acquire")
    if q21o.get("run_lock_contract", {}).get("single_non_overlapping_runner_lock_required") is not True:
        blockers.append("single_non_overlapping_lock_contract_required")
    ready = not blockers
    return {
        "ok": True,
        "contract_version": CONTRACT_VERSION,
        "contract_state": "mountain2_scheduled_tick_contract_ready_no_enablement" if ready else "mountain2_scheduled_tick_contract_blocked_no_enablement",
        "contract_ready_for_future_no_enable_runner_skeleton": ready,
        "contract_blockers": blockers,
        "contract_warnings": warnings,
        "generated_at": _utc_now(),
        "repo_status_short": repo_status_short,
        "q22m_prep_state": q22m.get("prep_state"),
        "q22m_prep_ready_for_future_enablement_design": q22m.get("prep_ready_for_future_enablement_design") is True,
        "q22m_prep_blockers": list(q22m.get("prep_blockers") or []),
        "q21o_lock_contract_state": q21o.get("lock_contract_state"),
        "q21o_lock_contract_ready": q21o.get("lock_contract_ready") is True,
        "q21o_lock_contract_blockers": list(q21o.get("lock_contract_blockers") or []),
        "future_tick_contract": {
            "future_tick_name": FUTURE_TICK_NAME,
            "future_tick_script_candidate": FUTURE_TICK_SCRIPT_CANDIDATE,
            "future_tick_requires_separate_operator_enablement": True,
            "future_enablement_token_candidate": FUTURE_MOUNTAIN2_TOKEN_CANDIDATE,
            "must_stop_for_operator_before_enablement": True,
            "must_acquire_non_overlap_lock_before_latest_read_or_write": True,
            "must_skip_or_fail_closed_when_lock_active": True,
            "must_use_stale_lock_recovery_policy": True,
            "must_run_one_bounded_latest_refresh_per_tick": True,
            "must_write_status_on_success_failure_or_skip": True,
            "must_release_lock_on_success_failure_or_skip": True,
            "must_preserve_last_success_on_failure": True,
            "must_not_delete_latest_on_failure": True,
            "must_not_trigger_warroom_ui": True,
            "must_not_call_broker_or_autotrade": True,
            "must_not_apply_or_stage_parameters": True,
            "must_not_append_ledger": True,
        },
        "future_scheduler_contract_not_executed": {
            "would_replace_disabled_task_action": True,
            "would_add_periodic_trigger": True,
            "would_enable_scheduler": True,
            "would_enable_recurring_execution": True,
            "would_write_latest_prediction_per_tick": True,
            "would_write_status_per_tick": True,
            "rollback_must_disable_scheduler": True,
            "rollback_must_remove_added_trigger": True,
            "rollback_must_restore_disabled_dry_run_action_if_changed": True,
        },
        "next_recommended_action": "Implement PS-Q22O no-enable future tick runner skeleton/guard. Stop before scheduler action replacement, trigger addition, scheduler enablement, or actual recurring execution." if ready else "Resolve no-enable contract blockers or refresh latest, then re-run PS-Q22N.",
        "read_only_contract_only": True,
        "scheduler_enabled": False,
        "trigger_added": False,
        "trigger_addition_allowed_now": False,
        "recurring_enablement_allowed_now": False,
        "periodic_execution_enabled": False,
        "producer_loop_enabled": False,
        "producer_runner_invoked": False,
        "latest_prediction_artifact_written": False,
        "status_artifact_written": False,
        "lock_file_created": False,
        "lock_file_written": False,
        "lock_acquire_attempted": False,
        "lock_release_attempted": False,
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
    return build_scheduled_tick_contract(
        repo_status_short=_git_status_short(),
        q22m_packet=run_q22m_prep(),
        q21o_packet=run_q21o_lock_contract(),
    )


def main() -> int:
    result = run_contract()
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True, default=str))
    return 0 if result.get("ok") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
