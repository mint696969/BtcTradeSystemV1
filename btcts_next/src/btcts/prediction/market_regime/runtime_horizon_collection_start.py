# path: ./btcts_next/src/btcts/prediction/market_regime/runtime_horizon_collection_start.py
# desc: MR-F9.19N exact-human-authorized foreground start wiring for one bounded runtime-horizon collection.

from __future__ import annotations

import hashlib
import hmac
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Mapping

from .runtime_horizon_collection_adapter import execute_runtime_horizon_collection_adapter_tick
from .runtime_horizon_collection_authorization import (
    validate_runtime_horizon_collection_start_authorization_package,
)
from .runtime_horizon_collection_contract import validate_runtime_horizon_collection_plan
from .runtime_horizon_collection_lease import (
    acquire_runtime_horizon_collection_lease,
    release_runtime_horizon_collection_lease,
)
from .runtime_horizon_collection_loop import run_runtime_horizon_collection_foreground_loop
from .runtime_horizon_collection_recovery import (
    merge_runtime_horizon_collection_recovery_into_state,
    recover_runtime_horizon_collection_runs,
)
from .runtime_horizon_collection_state import (
    TERMINAL_STATUSES,
    advance_runtime_horizon_collection_state,
    build_initial_runtime_horizon_collection_state,
    read_runtime_horizon_collection_state,
    write_runtime_horizon_collection_state,
)

NowProvider = Callable[[], datetime]
SleepFn = Callable[[float], None]
LoopRunner = Callable[..., Mapping[str, Any]]


def _utc_text(value: datetime) -> str:
    if value.tzinfo is None:
        raise ValueError("runtime_horizon_collection_start_now_timezone_required")
    return value.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _validate_safety_contract(*, plan: Mapping[str, Any], package: Mapping[str, Any]) -> None:
    for key in ("foreground_process_required", "human_start_authorization_required"):
        if plan.get(key) is not True:
            raise PermissionError(f"runtime_horizon_collection_start_plan_requirement_missing:{key}")
    for key in ("lease_required", "manifest_recovery_required", "foreground_process_required"):
        if package.get(key) is not True:
            raise PermissionError(f"runtime_horizon_collection_start_package_requirement_missing:{key}")
    for key in (
        "scheduler_registration_allowed",
        "latest_pointer_created",
        "writer_registered",
        "websocket_opened",
        "ui_inference_allowed",
        "ui_confidence_recalculation_allowed",
        "broker_private_api_allowed",
        "autotrade_trigger_allowed",
        "order_submission_allowed",
        "auto_promotion_allowed",
        "live_parameter_apply_allowed",
    ):
        if plan.get(key) is not False:
            raise PermissionError(f"runtime_horizon_collection_start_plan_safety_violation:{key}")
    for key in (
        "writer_registered",
        "latest_pointer_created",
        "scheduler_enabled",
        "detached_process_started",
        "websocket_opened",
        "ui_inference_allowed",
        "ui_confidence_recalculation_allowed",
        "broker_private_api_allowed",
        "autotrade_trigger_allowed",
        "order_submission_allowed",
    ):
        if package.get(key) is not False:
            raise PermissionError(f"runtime_horizon_collection_start_package_safety_violation:{key}")


def run_authorized_runtime_horizon_collection_start(
    control_root: str | Path,
    *,
    plan: Mapping[str, Any],
    authorization_package: Mapping[str, Any],
    provided_authorization_text: str,
    expected_root: str | Path,
    now_provider: NowProvider,
    sleep_fn: SleepFn = time.sleep,
    pid: int | None = None,
    lease_id: str | None = None,
    loop_runner: LoopRunner = run_runtime_horizon_collection_foreground_loop,
) -> Mapping[str, Any]:
    validate_runtime_horizon_collection_plan(plan)
    if not isinstance(authorization_package, Mapping):
        raise ValueError("runtime_horizon_collection_start_authorization_package_invalid")
    if not callable(now_provider) or not callable(sleep_fn) or not callable(loop_runner):
        raise ValueError("runtime_horizon_collection_start_callback_invalid")

    control = Path(control_root).resolve()
    expected = Path(expected_root).resolve()
    source = Path(str(plan["source_root"])).resolve()
    destination = Path(str(plan["destination_root"])).resolve()
    if control != expected or source != expected or destination != expected:
        raise PermissionError("runtime_horizon_collection_start_root_binding_mismatch")

    _validate_safety_contract(plan=plan, package=authorization_package)
    observed_now = now_provider()
    observed_at = _utc_text(observed_now)
    planned_start = datetime.fromisoformat(
        str(plan["planned_start_utc"]).replace("Z", "+00:00")
    ).astimezone(timezone.utc).replace(microsecond=0)
    validate_runtime_horizon_collection_start_authorization_package(
        package=authorization_package,
        plan=plan,
        now=observed_at,
        expected_dhot_root=expected,
    )

    expected_text = str(authorization_package.get("expected_authorization_text") or "")
    provided_text = str(provided_authorization_text or "")
    if not expected_text or not hmac.compare_digest(provided_text, expected_text):
        raise PermissionError("runtime_horizon_collection_start_exact_authorization_text_mismatch")
    digest = hashlib.sha256(provided_text.encode("utf-8")).hexdigest()
    expected_digest = str(authorization_package.get("expected_authorization_text_sha256") or "")
    if not hmac.compare_digest(digest, expected_digest):
        raise PermissionError("runtime_horizon_collection_start_authorization_text_digest_mismatch")

    normalized_pid = int(os.getpid() if pid is None else pid)
    lease = acquire_runtime_horizon_collection_lease(
        control,
        plan=plan,
        acquired_at=observed_at,
        pid=normalized_pid,
        lease_id=lease_id,
    )

    try:
        persisted = read_runtime_horizon_collection_state(control, plan=plan)
        if persisted:
            state = dict(persisted)
            if state["status"] in TERMINAL_STATUSES:
                raise PermissionError("runtime_horizon_collection_start_terminal_state")
        else:
            state = dict(build_initial_runtime_horizon_collection_state(plan=plan, created_at=observed_at))

        if state["status"] not in {"PLANNED", "PAUSED", "RUNNING"}:
            raise PermissionError("runtime_horizon_collection_start_state_not_restartable")
        if state["status"] == "RUNNING" and state["active"] is not True:
            raise PermissionError("runtime_horizon_collection_start_state_not_restartable")

        recovery = recover_runtime_horizon_collection_runs(destination, plan=plan)
        recovered_run_count = int(recovery.get("recovered_run_count") or 0)
        if recovered_run_count > 0 and state["status"] in {"PLANNED", "PAUSED"}:
            if observed_now.astimezone(timezone.utc).replace(microsecond=0) < planned_start:
                raise PermissionError(
                    "runtime_horizon_collection_start_recovery_before_planned_start"
                )
            state = dict(
                advance_runtime_horizon_collection_state(
                    plan=plan,
                    previous=state,
                    event="START",
                    observed_at=observed_at,
                )
            )

        merged = merge_runtime_horizon_collection_recovery_into_state(
            plan=plan,
            state=state,
            recovery_report=recovery,
            observed_at=observed_at,
        )
        state = dict(merged["state"])
        write_runtime_horizon_collection_state(control, plan=plan, state=state)
    except Exception:
        release_runtime_horizon_collection_lease(
            control,
            plan=plan,
            lease_id=str(lease["lease_id"]),
            pid=normalized_pid,
        )
        raise

    def tick_executor(current_state: Mapping[str, Any], tick_at: str) -> Mapping[str, Any]:
        return execute_runtime_horizon_collection_adapter_tick(
            control,
            plan=plan,
            state=current_state,
            observed_at=tick_at,
            collection_start_authorized=True,
        )

    try:
        result = loop_runner(
            control,
            plan=plan,
            tick_executor=tick_executor,
            now_provider=now_provider,
            sleep_fn=sleep_fn,
            lease_required=True,
            lease_id=str(lease["lease_id"]),
            lease_pid=normalized_pid,
            cadence_anchored=True,
            preacquired_lease=lease,
        )
        if not isinstance(result, Mapping):
            raise ValueError("runtime_horizon_collection_start_loop_result_invalid")
    except Exception:
        release_runtime_horizon_collection_lease(
            control,
            plan=plan,
            lease_id=str(lease["lease_id"]),
            pid=normalized_pid,
        )
        raise
    return {
        **dict(result),
        "event": "AUTHORIZED_FOREGROUND_START_RETURNED",
        "authorization_verified": True,
        "authorization_package_sha256": authorization_package["authorization_package_sha256"],
        "recovery_completed_before_loop": True,
        "recovered_state_persisted_before_loop": True,
        "recovered_state_entry_count": int(merged["recovered_state_entry_count"]),
        "lease_required": True,
        "lease_preacquired": True,
        "cadence_anchored": True,
        "foreground_process": True,
        "scheduler_enabled": False,
        "detached_process_started": False,
        "latest_pointer_created": False,
        "websocket_opened": False,
        "ui_inference_allowed": False,
        "ui_confidence_recalculation_allowed": False,
        "broker_private_api_allowed": False,
        "autotrade_trigger_allowed": False,
        "order_submission_allowed": False,
    }
