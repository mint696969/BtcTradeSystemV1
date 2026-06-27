# path: ./tools/run_phase4a_prediction_system_ps_q21z_bounded_manual_freshness_recovery_execute_existing_q21i_once.py
# desc: PS-Q21Z gated one-shot wrapper for existing PS-Q21I bounded manual freshness recovery. Default is dry-run/no write; exact token required; no producer-loop/scheduler/broker.

from __future__ import annotations

import argparse
from collections.abc import Callable
import json
from pathlib import Path
import sys
from typing import Any, Mapping

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.run_phase4a_prediction_system_ps_q21i_one_shot_bounded_manual_latest_prediction_write import (  # noqa: E402
    DEFAULT_HOT_ROOT,
    REQUIRED_CONFIRMATION as Q21I_REQUIRED_CONFIRMATION,
    run_one_shot_write,
)
from tools.verify_phase4a_prediction_system_ps_q21u_scheduler_producer_registration_preflight import (  # noqa: E402
    REQUIRED_NEXT_PRODUCER_CONFIRMATION,
)
from tools.verify_phase4a_prediction_system_ps_q21y_freshness_recovery_preflight_no_write import (  # noqa: E402
    run_freshness_recovery_preflight,
)

RECOVERY_VERSION = "prediction_warroom.bounded_manual_freshness_recovery_execute_existing_q21i_once.ps_q21z.v1"
Q21I_TOOL = "tools/run_phase4a_prediction_system_ps_q21i_one_shot_bounded_manual_latest_prediction_write.py"
Q21IRunner = Callable[..., dict[str, Any]]


def _as_mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _false_boundary_fields() -> dict[str, Any]:
    return {
        "producer_loop_enabled": False,
        "producer_runner_invoked": False,
        "scheduled_loop_enabled": False,
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


def build_blocked_recovery_packet(*, reasons: list[str], q21y_packet: Mapping[str, Any], requested_execute: bool, confirmation_ok: bool) -> dict[str, Any]:
    q21y = _as_mapping(q21y_packet)
    return {
        "ok": True,
        "recovery_version": RECOVERY_VERSION,
        "recovery_state": "bounded_manual_freshness_recovery_blocked_no_write",
        "success": False,
        "requested_execute_existing_q21i_once": bool(requested_execute),
        "confirmation_ok": bool(confirmation_ok),
        "blocked_reasons": reasons,
        "q21y_preflight_state": str(q21y.get("preflight_state") or ""),
        "q21y_ready_for_operator_token": q21y.get("freshness_recovery_ready_for_operator_token") is True,
        "q21y_blockers": list(q21y.get("freshness_recovery_blockers") or []),
        "manual_refresh_confirmation_required": Q21I_REQUIRED_CONFIRMATION,
        "required_next_producer_confirmation": REQUIRED_NEXT_PRODUCER_CONFIRMATION,
        "q21i_runner_invoked": False,
        "latest_prediction_artifact_written": False,
        "status_artifact_written": False,
        "one_shot_manual_refresh_only": True,
        "producer_loop_shadow_once_still_separate": True,
        **_false_boundary_fields(),
    }


def summarize_recovery_result(*, q21y_packet: Mapping[str, Any], q21i_result: Mapping[str, Any], requested_execute: bool, confirmation_ok: bool) -> dict[str, Any]:
    q21y = _as_mapping(q21y_packet)
    q21i = _as_mapping(q21i_result)
    latest_written = q21i.get("latest_prediction_artifact_written") is True
    status_written = q21i.get("status_artifact_written") is True
    success = q21i.get("success") is True and latest_written and status_written
    return {
        "ok": True,
        "recovery_version": RECOVERY_VERSION,
        "recovery_state": "bounded_manual_freshness_recovery_executed_existing_q21i_once" if success else "bounded_manual_freshness_recovery_existing_q21i_failed_or_incomplete",
        "success": success,
        "requested_execute_existing_q21i_once": bool(requested_execute),
        "confirmation_ok": bool(confirmation_ok),
        "blocked_reasons": [],
        "q21y_preflight_state": str(q21y.get("preflight_state") or ""),
        "q21y_ready_for_operator_token": q21y.get("freshness_recovery_ready_for_operator_token") is True,
        "q21y_blockers": list(q21y.get("freshness_recovery_blockers") or []),
        "manual_refresh_confirmation_required": Q21I_REQUIRED_CONFIRMATION,
        "required_next_producer_confirmation": REQUIRED_NEXT_PRODUCER_CONFIRMATION,
        "q21i_tool": Q21I_TOOL,
        "q21i_runner_invoked": True,
        "q21i_result": dict(q21i),
        "prediction_run_id": str(q21i.get("prediction_run_id") or ""),
        "generated_at": str(q21i.get("generated_at") or ""),
        "latest_prediction_artifact_written": latest_written,
        "status_artifact_written": status_written,
        "latest_prediction_artifact_path": str(q21i.get("latest_prediction_artifact_path") or ""),
        "status_artifact_path": str(q21i.get("status_artifact_path") or ""),
        "one_shot_manual_refresh_only": True,
        "producer_loop_shadow_once_still_separate": True,
        **_false_boundary_fields(),
    }


def run_bounded_manual_freshness_recovery_once(
    *,
    operator_acknowledged: bool = False,
    execute_existing_q21i_once: bool = False,
    confirmation: str = "",
    q21y_packet: Mapping[str, Any] | None = None,
    q21i_runner: Q21IRunner | None = None,
) -> dict[str, Any]:
    q21y = dict(q21y_packet) if q21y_packet is not None else run_freshness_recovery_preflight()
    confirmation_ok = confirmation == Q21I_REQUIRED_CONFIRMATION
    blockers: list[str] = []
    if not operator_acknowledged:
        blockers.append("operator_acknowledgement_required")
    if not execute_existing_q21i_once:
        blockers.append("execute_existing_q21i_once_flag_required")
    if not confirmation_ok:
        blockers.append("exact_q21i_confirmation_token_required")
    if q21y.get("freshness_recovery_ready_for_operator_token") is not True:
        blockers.append("q21y_ready_for_operator_token_required")
    if q21y.get("freshness_recovery_blockers") not in ([], None):
        blockers.append("q21y_blockers_must_be_empty")
    if q21y.get("repo_clean") is not True:
        blockers.append("repo_clean_required_before_existing_q21i_execution")
    if blockers:
        return build_blocked_recovery_packet(reasons=blockers, q21y_packet=q21y, requested_execute=execute_existing_q21i_once, confirmation_ok=confirmation_ok)
    runner = q21i_runner or run_one_shot_write
    q21i_result = runner(
        hot_root=DEFAULT_HOT_ROOT,
        operator_acknowledged=True,
        execute_one_shot_write=True,
        confirmation=Q21I_REQUIRED_CONFIRMATION,
        require_clean_tree=True,
    )
    return summarize_recovery_result(q21y_packet=q21y, q21i_result=q21i_result, requested_execute=execute_existing_q21i_once, confirmation_ok=confirmation_ok)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="PS-Q21Z gated one-shot bounded manual freshness recovery through existing PS-Q21I")
    parser.add_argument("--operator-acknowledged", action="store_true")
    parser.add_argument("--execute-existing-q21i-once", action="store_true")
    parser.add_argument("--confirmation", default="")
    args = parser.parse_args(argv)
    result = run_bounded_manual_freshness_recovery_once(
        operator_acknowledged=bool(args.operator_acknowledged),
        execute_existing_q21i_once=bool(args.execute_existing_q21i_once),
        confirmation=str(args.confirmation),
    )
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True, default=str))
    return 0 if result.get("ok") is True and (result.get("success") is True or not args.execute_existing_q21i_once) else 1


if __name__ == "__main__":
    raise SystemExit(main())
