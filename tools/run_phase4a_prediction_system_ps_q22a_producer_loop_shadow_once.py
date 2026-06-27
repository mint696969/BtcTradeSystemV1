# path: ./tools/run_phase4a_prediction_system_ps_q22a_producer_loop_shadow_once.py
# desc: PS-Q22A exact-token producer-loop shadow once wrapper. Default no-write/no-runner; no scheduler/trigger/broker/AutoTrade.

from __future__ import annotations

import argparse
from collections.abc import Callable
import json
from pathlib import Path
import subprocess
import sys
from typing import Any, Mapping

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC = REPO_ROOT / "btcts_next" / "src"
for candidate in (REPO_ROOT, SRC):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

from btcts.apps.operator_ui.components.prediction_warroom_l4_latest_adapter import DEFAULT_HOT_LATEST_ROOT_HINT  # noqa: E402
from btcts.apps.operator_ui.components.prediction_warroom_non_ui_scheduled_producer_runner import (  # noqa: E402
    build_prediction_warroom_non_ui_scheduled_producer_runner,
)
from tools.verify_phase4a_prediction_system_ps_q21u_scheduler_producer_registration_preflight import (  # noqa: E402
    REQUIRED_NEXT_PRODUCER_CONFIRMATION,
)
from tools.verify_phase4a_prediction_system_ps_q21x_producer_loop_shadow_preflight_no_enablement import (  # noqa: E402
    run_shadow_preflight,
)

SHADOW_ONCE_VERSION = "prediction_warroom.producer_loop_shadow_once.ps_q22a.v1"
REQUIRED_SHADOW_ONCE_CONFIRMATION = "ENABLE_DISABLED_PRODUCER_LOOP_SHADOW_ONCE_WITH_ROLLBACK_PLAN"
if REQUIRED_SHADOW_ONCE_CONFIRMATION != REQUIRED_NEXT_PRODUCER_CONFIRMATION:
    raise RuntimeError("shadow once confirmation token mismatch")
ProducerRunner = Callable[..., Any]


def _as_mapping(value: Any) -> Mapping[str, Any]:
    if hasattr(value, "to_dict"):
        converted = value.to_dict()
        return converted if isinstance(converted, Mapping) else {}
    return value if isinstance(value, Mapping) else {}


def _false_boundary() -> dict[str, Any]:
    return {
        "producer_loop_enabled": False,
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
        "latest_prediction_artifact_written": False,
    }


def _repo_clean() -> bool:
    proc = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=False)
    return proc.stdout.strip() == ""


def run_producer_loop_shadow_once(
    *,
    operator_acknowledged: bool = False,
    execute_shadow_once: bool = False,
    confirmation: str = "",
    q21x_packet: Mapping[str, Any] | None = None,
    producer_runner: ProducerRunner | None = None,
    repo_clean: bool | None = None,
) -> dict[str, Any]:
    q21x = dict(q21x_packet) if q21x_packet is not None else run_shadow_preflight()
    blockers: list[str] = []
    if not operator_acknowledged:
        blockers.append("operator_acknowledgement_required")
    if not execute_shadow_once:
        blockers.append("execute_shadow_once_flag_required")
    if confirmation != REQUIRED_SHADOW_ONCE_CONFIRMATION:
        blockers.append("exact_shadow_once_confirmation_token_required")
    repo_is_clean = _repo_clean() if repo_clean is None else bool(repo_clean)
    if not repo_is_clean:
        blockers.append("repo_clean_required_before_shadow_once")
    if q21x.get("ok") is not True:
        blockers.append("q21x_packet_ok_required")
    if q21x.get("shadow_preflight_ready_for_one_shot") is not True:
        blockers.append("q21x_shadow_preflight_ready_required")
    if q21x.get("shadow_preflight_blockers") not in ([], None):
        blockers.append("q21x_shadow_preflight_blockers_must_be_empty")
    if q21x.get("latest_prediction_non_stale") is not True:
        blockers.append("latest_prediction_non_stale_required_before_shadow_once")
    if q21x.get("latest_status_success_observed") is not True:
        blockers.append("latest_status_success_required_before_shadow_once")
    if q21x.get("d_hot_lock_artifact_exists") is not False:
        blockers.append("d_hot_lock_absent_required_before_shadow_once")
    if str(q21x.get("task_state") or "") != "Disabled":
        blockers.append("ps_q21w_task_state_disabled_required")
    try:
        trigger_count = int(q21x.get("task_trigger_count") or 0)
    except Exception:
        trigger_count = -1
    if trigger_count != 0:
        blockers.append("ps_q21w_task_trigger_count_zero_required")
    if blockers:
        return {
            "ok": True,
            "shadow_once_version": SHADOW_ONCE_VERSION,
            "shadow_once_state": "producer_loop_shadow_once_blocked_no_write",
            "success": False,
            "blocked_reasons": blockers,
            "q21x_preflight": q21x,
            "producer_runner_invoked": False,
            "status_artifact_written": False,
            "required_next_producer_confirmation": REQUIRED_SHADOW_ONCE_CONFIRMATION,
            **_false_boundary(),
        }
    runner = producer_runner or build_prediction_warroom_non_ui_scheduled_producer_runner
    packet = _as_mapping(runner(
        hot_latest_root_hint=DEFAULT_HOT_LATEST_ROOT_HINT,
        operator_acknowledged=True,
        allow_status_artifact_write=True,
        execute_status_artifact_write=True,
        allow_guard_test_root=False,
    ))
    status_written = packet.get("status_artifact_written") is True
    success = status_written and packet.get("producer_enabled") is False and packet.get("scheduler_enabled") is False and packet.get("would_send_to_broker") is False
    return {
        "ok": True,
        "shadow_once_version": SHADOW_ONCE_VERSION,
        "shadow_once_state": "producer_loop_shadow_once_executed_status_write_only" if success else "producer_loop_shadow_once_failed_or_incomplete",
        "success": success,
        "blocked_reasons": [],
        "q21x_preflight": q21x,
        "producer_runner_invoked": True,
        "producer_runner_packet": dict(packet),
        "status_artifact_written": status_written,
        "status_artifact_path": str(packet.get("status_artifact_path") or ""),
        "producer_state": str(packet.get("runner_state") or ""),
        "required_next_producer_confirmation": REQUIRED_SHADOW_ONCE_CONFIRMATION,
        **_false_boundary(),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="PS-Q22A producer-loop shadow once wrapper")
    parser.add_argument("--operator-acknowledged", action="store_true")
    parser.add_argument("--execute-shadow-once", action="store_true")
    parser.add_argument("--confirmation", default="")
    args = parser.parse_args(argv)
    result = run_producer_loop_shadow_once(
        operator_acknowledged=args.operator_acknowledged,
        execute_shadow_once=args.execute_shadow_once,
        confirmation=args.confirmation,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True, default=str))
    return 0 if result.get("ok") is True and (result.get("success") is True or not args.execute_shadow_once) else 1


if __name__ == "__main__":
    raise SystemExit(main())
