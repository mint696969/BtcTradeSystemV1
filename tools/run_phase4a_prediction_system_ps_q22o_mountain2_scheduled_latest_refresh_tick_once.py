# path: ./tools/run_phase4a_prediction_system_ps_q22o_mountain2_scheduled_latest_refresh_tick_once.py
# desc: PS-Q22O no-enable future Mountain2 scheduled latest-refresh tick skeleton. It blocks any execution request and performs no lock/runtime/scheduler/broker writes.

from __future__ import annotations

import argparse
from collections.abc import Callable
from datetime import datetime, timezone
import json
from pathlib import Path
import sys
from typing import Any, Mapping

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.design_phase4a_prediction_system_ps_q22n_mountain2_scheduled_tick_contract_no_enablement import (  # noqa: E402
    CONTRACT_VERSION as Q22N_CONTRACT_VERSION,
    FUTURE_TICK_NAME,
    build_scheduled_tick_contract,
    run_contract as run_q22n_contract,
)
from tools.diagnose_phase4a_prediction_system_ps_q22m_mountain2_recurring_trigger_prep_no_enablement import (  # noqa: E402
    FUTURE_MOUNTAIN2_TOKEN_CANDIDATE,
)

RUNNER_VERSION = "prediction_warroom.mountain2_scheduled_latest_refresh_tick_skeleton_no_enablement.ps_q22o.v1"
TickContractProvider = Callable[[], Mapping[str, Any]]


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _as_mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _false_boundary() -> dict[str, Any]:
    return {
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
        "runtime_artifact_write_allowed": False,
        "status_artifact_write_allowed": False,
        "prediction_artifact_write_allowed": False,
        "lock_file_created": False,
        "lock_file_written": False,
        "lock_acquire_attempted": False,
        "lock_acquired": False,
        "lock_release_attempted": False,
        "lock_released": False,
        "warroom_ui_trigger_allowed": False,
        "approval_or_ledger_allowed": False,
        "parameter_apply_allowed": False,
        "parameter_staging_write_allowed": False,
        "autotrade_trigger_allowed": False,
        "broker_private_api_allowed": False,
        "would_send_to_broker": False,
        "would_write_collector_state": False,
    }


def build_mountain2_tick_runner_skeleton(
    *,
    q22n_packet: Mapping[str, Any],
    operator_acknowledged: bool = False,
    request_execute_tick_once: bool = False,
    future_enablement_confirmation: str = "",
) -> dict[str, Any]:
    q22n = _as_mapping(q22n_packet)
    blockers: list[str] = []
    warnings: list[str] = []
    if q22n.get("contract_version") != Q22N_CONTRACT_VERSION:
        blockers.append("q22n_contract_version_required")
    if q22n.get("future_tick_contract", {}).get("future_tick_name") != FUTURE_TICK_NAME:
        blockers.append("q22n_future_tick_contract_required")
    if q22n.get("scheduler_enabled") is not False or q22n.get("trigger_added") is not False:
        blockers.append("q22n_must_preserve_no_scheduler_no_trigger")
    if q22n.get("future_tick_contract", {}).get("must_acquire_non_overlap_lock_before_latest_read_or_write") is not True:
        blockers.append("future_lock_contract_required")
    if q22n.get("future_tick_contract", {}).get("must_run_one_bounded_latest_refresh_per_tick") is not True:
        blockers.append("future_bounded_latest_refresh_contract_required")
    if q22n.get("contract_ready_for_future_no_enable_runner_skeleton") is not True:
        warnings.append("q22n_contract_not_runtime_ready_yet_this_skeleton_still_no_enablement")
    if request_execute_tick_once:
        blockers.append("ps_q22o_blocks_execute_tick_once_by_design")
    if future_enablement_confirmation == FUTURE_MOUNTAIN2_TOKEN_CANDIDATE:
        blockers.append("future_enablement_token_detected_but_ps_q22o_must_not_use_it")
    runner_ready = not blockers
    return {
        "ok": True,
        "runner_version": RUNNER_VERSION,
        "runner_state": "mountain2_tick_runner_skeleton_ready_no_enablement" if runner_ready else "mountain2_tick_runner_execution_blocked_no_write",
        "runner_ready_for_future_danger_boundary_review": runner_ready,
        "generated_at": _utc_now(),
        "operator_acknowledged": bool(operator_acknowledged),
        "request_execute_tick_once": bool(request_execute_tick_once),
        "future_enablement_confirmation_supplied": bool(future_enablement_confirmation),
        "future_enablement_confirmation_ok_but_not_used": future_enablement_confirmation == FUTURE_MOUNTAIN2_TOKEN_CANDIDATE,
        "blocked_reasons": blockers,
        "warning_reasons": warnings,
        "q22n_contract_state": q22n.get("contract_state"),
        "q22n_contract_ready_for_future_no_enable_runner_skeleton": q22n.get("contract_ready_for_future_no_enable_runner_skeleton") is True,
        "q22n_contract_blockers": list(q22n.get("contract_blockers") or []),
        "q22n_contract_warnings": list(q22n.get("contract_warnings") or []),
        "future_tick_name": FUTURE_TICK_NAME,
        "future_enablement_token_candidate": FUTURE_MOUNTAIN2_TOKEN_CANDIDATE,
        "skeleton_sequence_no_execution": [
            "run_q22n_contract",
            "verify_future_tick_contract_present",
            "declare_future_non_overlap_lock_required",
            "declare_future_bounded_latest_refresh_required",
            "declare_future_status_visibility_required",
            "block_execute_request_in_ps_q22o",
            "return_stdout_json_only",
        ],
        "future_runtime_steps_not_executed": {
            "would_acquire_lock": True,
            "would_run_one_bounded_latest_refresh": True,
            "would_write_latest_prediction": True,
            "would_write_success_failure_or_skip_status": True,
            "would_release_lock": True,
            "would_skip_or_fail_closed_on_active_lock": True,
            "would_preserve_latest_on_failure": True,
        },
        "danger_boundary_next_stop": {
            "must_stop_before_scheduler_action_replacement": True,
            "must_stop_before_trigger_addition": True,
            "must_stop_before_scheduler_enablement": True,
            "must_stop_before_recurring_or_periodic_execution": True,
            "must_stop_before_using_future_enablement_token": True,
        },
        **_false_boundary(),
    }


def run_mountain2_tick_runner_skeleton(
    *,
    operator_acknowledged: bool = False,
    request_execute_tick_once: bool = False,
    future_enablement_confirmation: str = "",
    q22n_provider: TickContractProvider | None = None,
) -> dict[str, Any]:
    provider = q22n_provider or run_q22n_contract
    return build_mountain2_tick_runner_skeleton(
        q22n_packet=provider(),
        operator_acknowledged=operator_acknowledged,
        request_execute_tick_once=request_execute_tick_once,
        future_enablement_confirmation=future_enablement_confirmation,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="PS-Q22O no-enable Mountain2 scheduled latest-refresh tick skeleton")
    parser.add_argument("--operator-acknowledged", action="store_true")
    parser.add_argument("--request-execute-tick-once", action="store_true")
    parser.add_argument("--future-enablement-confirmation", default="")
    args = parser.parse_args(argv)
    result = run_mountain2_tick_runner_skeleton(
        operator_acknowledged=args.operator_acknowledged,
        request_execute_tick_once=args.request_execute_tick_once,
        future_enablement_confirmation=args.future_enablement_confirmation,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True, default=str))
    return 0 if result.get("ok") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
