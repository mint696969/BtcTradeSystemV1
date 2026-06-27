# path: ./tools/verify_phase4a_prediction_system_ps_q21y_freshness_recovery_preflight_no_write.py
# desc: PS-Q21Y read-only freshness recovery preflight that prepares the gated PS-Q21I bounded manual refresh command. No D-hot writes, no producer-loop execution, no scheduler enablement.

from __future__ import annotations

import json
from pathlib import Path
import sys
from typing import Any, Mapping

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.run_phase4a_prediction_system_ps_q21i_one_shot_bounded_manual_latest_prediction_write import (  # noqa: E402
    REQUIRED_CONFIRMATION as Q21I_REQUIRED_CONFIRMATION,
)
from tools.verify_phase4a_prediction_system_ps_q21x_producer_loop_shadow_preflight_no_enablement import (  # noqa: E402
    run_shadow_preflight,
)
from tools.verify_phase4a_prediction_system_ps_q21u_scheduler_producer_registration_preflight import (  # noqa: E402
    REQUIRED_NEXT_PRODUCER_CONFIRMATION,
)

FRESHNESS_PREFLIGHT_VERSION = "prediction_warroom.freshness_recovery_preflight.ps_q21y.v1"
Q21I_TOOL = "tools/run_phase4a_prediction_system_ps_q21i_one_shot_bounded_manual_latest_prediction_write.py"
EXPECTED_Q21X_STALE_BLOCKER = "latest_prediction_non_stale_required_before_shadow_once"


def _as_mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _false_boundary_fields() -> dict[str, Any]:
    return {
        "manual_refresh_runner_invoked": False,
        "latest_prediction_artifact_written": False,
        "status_artifact_written": False,
        "runtime_artifact_write_allowed": False,
        "status_artifact_write_allowed": False,
        "prediction_artifact_write_allowed": False,
        "producer_loop_enabled": False,
        "producer_runner_invoked": False,
        "scheduler_enabled": False,
        "scheduler_enablement_allowed_now": False,
        "trigger_added": False,
        "trigger_addition_allowed_now": False,
        "recurring_enablement_allowed_now": False,
        "warroom_ui_trigger_allowed": False,
        "approval_or_ledger_allowed": False,
        "parameter_apply_allowed": False,
        "parameter_staging_write_allowed": False,
        "autotrade_trigger_allowed": False,
        "broker_private_api_allowed": False,
        "would_send_to_broker": False,
        "would_write_collector_state": False,
    }


def _prepared_command() -> list[str]:
    tool_path = ".\\" + Q21I_TOOL.replace("/", "\\")
    return [
        "python",
        tool_path,
        "--operator-acknowledged",
        "--execute-one-shot-write",
        "--confirmation",
        Q21I_REQUIRED_CONFIRMATION,
    ]


def build_freshness_recovery_preflight(*, q21x_packet: Mapping[str, Any]) -> dict[str, Any]:
    q21x = _as_mapping(q21x_packet)
    blockers: list[str] = []
    q21x_blockers = [str(item) for item in q21x.get("shadow_preflight_blockers", []) if item] if isinstance(q21x.get("shadow_preflight_blockers"), list) else []
    q21x_blocker_set = set(q21x_blockers)
    allowed_q21x_blockers = {EXPECTED_Q21X_STALE_BLOCKER}
    if q21x.get("ok") is not True:
        blockers.append("q21x_packet_ok_required")
    if q21x.get("repo_clean") is not True:
        blockers.append("repo_clean_required_before_manual_freshness_recovery")
    if q21x.get("latest_prediction_non_stale") is True:
        blockers.append("latest_prediction_already_non_stale_manual_recovery_not_needed")
    if EXPECTED_Q21X_STALE_BLOCKER not in q21x_blocker_set:
        blockers.append("q21x_stale_prediction_blocker_required_for_recovery_preflight")
    unexpected_q21x_blockers = sorted(q21x_blocker_set - allowed_q21x_blockers)
    if unexpected_q21x_blockers:
        blockers.append("q21x_must_be_blocked_only_by_latest_prediction_stale")
    if q21x.get("latest_status_success_observed") is not True:
        blockers.append("latest_status_success_observed_required")
    if q21x.get("d_hot_lock_artifact_exists") is not False:
        blockers.append("d_hot_lock_absent_required_before_manual_freshness_recovery")
    if q21x.get("task_exists") is not True:
        blockers.append("ps_q21w_disabled_scheduler_task_exists_required")
    if q21x.get("task_recognized_as_ps_q21w") is not True:
        blockers.append("ps_q21w_task_recognized_required")
    if str(q21x.get("task_state") or "") != "Disabled":
        blockers.append("ps_q21w_task_state_disabled_required")
    try:
        trigger_count = int(q21x.get("task_trigger_count") or 0)
    except Exception:
        trigger_count = -1
    if trigger_count != 0:
        blockers.append("ps_q21w_task_trigger_count_zero_required")
    if q21x.get("producer_runner_invoked") is not False:
        blockers.append("producer_runner_must_not_be_invoked")
    if q21x.get("producer_loop_enabled") is not False:
        blockers.append("producer_loop_must_remain_disabled")
    if q21x.get("scheduler_enablement_allowed_now") is not False:
        blockers.append("scheduler_enablement_must_not_be_allowed")
    if q21x.get("trigger_addition_allowed_now") is not False:
        blockers.append("trigger_addition_must_not_be_allowed")
    ready = not blockers
    return {
        "ok": True,
        "preflight_version": FRESHNESS_PREFLIGHT_VERSION,
        "preflight_state": "freshness_recovery_preflight_ready_for_operator_token_no_write" if ready else "freshness_recovery_preflight_blocked_no_write",
        "freshness_recovery_ready_for_operator_token": ready,
        "freshness_recovery_blockers": blockers,
        "unexpected_q21x_blockers": unexpected_q21x_blockers,
        "read_only_freshness_recovery_preflight_only": True,
        "manual_refresh_command_prepared_only": True,
        "manual_refresh_execute_allowed_now": False,
        "manual_refresh_confirmation_required": Q21I_REQUIRED_CONFIRMATION,
        "required_existing_q21i_confirmation_token": Q21I_REQUIRED_CONFIRMATION,
        "producer_loop_shadow_once_still_separate": True,
        "producer_loop_shadow_once_requires_confirmation": REQUIRED_NEXT_PRODUCER_CONFIRMATION,
        "prepared_command_target": Q21I_TOOL,
        "prepared_command": _prepared_command(),
        "prepared_command_is_not_executed_by_q21y": True,
        "q21x_preflight_state": str(q21x.get("preflight_state") or ""),
        "q21x_shadow_preflight_ready_for_one_shot": q21x.get("shadow_preflight_ready_for_one_shot") is True,
        "q21x_shadow_preflight_blockers": q21x_blockers,
        "repo_clean": q21x.get("repo_clean") is True,
        "generated_at": str(q21x.get("generated_at") or ""),
        "age_sec": q21x.get("age_sec"),
        "latest_prediction_non_stale": q21x.get("latest_prediction_non_stale") is True,
        "latest_status_success_observed": q21x.get("latest_status_success_observed") is True,
        "d_hot_lock_artifact_exists": q21x.get("d_hot_lock_artifact_exists") is True,
        "task_exists": q21x.get("task_exists") is True,
        "task_name": str(q21x.get("task_name") or ""),
        "task_path": str(q21x.get("task_path") or ""),
        "task_state": str(q21x.get("task_state") or ""),
        "task_trigger_count": trigger_count,
        "task_recognized_as_ps_q21w": q21x.get("task_recognized_as_ps_q21w") is True,
        "status_warnings": list(q21x.get("status_warnings") or []),
        "status_blockers": list(q21x.get("status_blockers") or []),
        **_false_boundary_fields(),
    }


def run_freshness_recovery_preflight() -> dict[str, Any]:
    return build_freshness_recovery_preflight(q21x_packet=run_shadow_preflight())


def main() -> int:
    result = run_freshness_recovery_preflight()
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True, default=str))
    return 0 if result.get("ok") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
