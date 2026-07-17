# path: ./btcts_next/src/btcts/prediction/market_regime/runtime_horizon_collection_loop.py
# desc: MR-F9.19L explicit foreground, bounded, restart-safe runtime-horizon collection loop. No scheduler registration or detached start.

from __future__ import annotations

import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Mapping

from .runtime_horizon_collection_cadence import (
    collection_cadence_sleep_seconds,
    collection_start_wait_seconds,
)
from .runtime_horizon_collection_contract import validate_runtime_horizon_collection_plan
from .runtime_horizon_collection_lease import (
    acquire_runtime_horizon_collection_lease,
    heartbeat_runtime_horizon_collection_lease,
    release_runtime_horizon_collection_lease,
    read_runtime_horizon_collection_lease,
)
from .runtime_horizon_collection_state import (
    TERMINAL_STATUSES,
    advance_runtime_horizon_collection_state,
    build_initial_runtime_horizon_collection_state,
    read_runtime_horizon_collection_state,
    validate_runtime_horizon_collection_state,
    write_runtime_horizon_collection_completion_receipt,
    write_runtime_horizon_collection_state,
)

NowProvider = Callable[[], datetime]
SleepFn = Callable[[float], None]
TickExecutor = Callable[[Mapping[str, Any], str], Mapping[str, Any]]


def _utc_text(value: datetime) -> str:
    if value.tzinfo is None:
        raise ValueError("runtime_horizon_collection_loop_now_timezone_required")
    return value.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _parse_utc(value: str) -> datetime:
    text = str(value or "").strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    parsed = datetime.fromisoformat(text)
    if parsed.tzinfo is None:
        raise ValueError("runtime_horizon_collection_loop_plan_time_timezone_required")
    return parsed.astimezone(timezone.utc).replace(microsecond=0)


def run_runtime_horizon_collection_foreground_loop(
    root: str | Path,
    *,
    plan: Mapping[str, Any],
    tick_executor: TickExecutor,
    now_provider: NowProvider,
    sleep_fn: SleepFn = time.sleep,
    lease_required: bool = False,
    lease_id: str | None = None,
    lease_pid: int | None = None,
    cadence_anchored: bool = False,
    preacquired_lease: Mapping[str, Any] | None = None,
) -> Mapping[str, Any]:
    validate_runtime_horizon_collection_plan(plan)
    if not callable(tick_executor) or not callable(now_provider) or not callable(sleep_fn):
        raise ValueError("runtime_horizon_collection_loop_callback_invalid")
    if type(lease_required) is not bool:
        raise ValueError("runtime_horizon_collection_loop_lease_required_invalid")
    if type(cadence_anchored) is not bool:
        raise ValueError("runtime_horizon_collection_loop_cadence_anchored_invalid")
    if preacquired_lease is not None and not isinstance(preacquired_lease, Mapping):
        raise ValueError("runtime_horizon_collection_loop_preacquired_lease_invalid")
    if preacquired_lease is not None and lease_required is not True:
        raise ValueError("runtime_horizon_collection_loop_preacquired_lease_requires_lease")

    planned_start = _parse_utc(str(plan["planned_start_utc"]))
    planned_end = _parse_utc(str(plan["planned_end_utc"]))
    persisted = read_runtime_horizon_collection_state(root, plan=plan)
    initial_start_at = ""
    if persisted:
        state = dict(persisted)
        validate_runtime_horizon_collection_state(plan=plan, state=state)
        if state["status"] in TERMINAL_STATUSES:
            return {
                "ok": state["status"] == "COMPLETED",
                "event": "ALREADY_TERMINAL",
                "state": state,
                "writer_registered": False,
                "scheduler_enabled": False,
                "detached_process_started": False,
                "latest_pointer_created": False,
                "websocket_opened": False,
                "ui_inference_allowed": False,
                "order_submission_allowed": False,
            }
    lease: Mapping[str, Any] = {}
    lease_acquired = False
    if preacquired_lease is not None:
        existing_lease = read_runtime_horizon_collection_lease(root, plan=plan)
        if dict(existing_lease) != dict(preacquired_lease):
            raise PermissionError("runtime_horizon_collection_loop_preacquired_lease_mismatch")
        if str(existing_lease["lease_id"]) != str(lease_id or ""):
            raise PermissionError("runtime_horizon_collection_loop_preacquired_lease_id_mismatch")
        if lease_pid is not None and int(existing_lease["pid"]) != int(lease_pid):
            raise PermissionError("runtime_horizon_collection_loop_preacquired_lease_pid_mismatch")
        lease = dict(existing_lease)
        lease_acquired = True
        lease_acquired_at = str(existing_lease["acquired_at"])
    elif lease_required:
        lease_acquired_at = _utc_text(now_provider())
        lease = acquire_runtime_horizon_collection_lease(
            root,
            plan=plan,
            acquired_at=lease_acquired_at,
            pid=lease_pid,
            lease_id=lease_id,
        )
        lease_acquired = True
    else:
        lease_acquired_at = ""

    if not persisted:
        initial_start_at = lease_acquired_at or _utc_text(now_provider())
        state = dict(
            build_initial_runtime_horizon_collection_state(
                plan=plan,
                created_at=initial_start_at,
            )
        )
        write_runtime_horizon_collection_state(root, plan=plan, state=state)

    if state["status"] in {"PLANNED", "PAUSED"}:
        if cadence_anchored:
            before_start = now_provider()
            start_wait = collection_start_wait_seconds(
                planned_start=planned_start,
                observed_at=before_start,
            )
            if start_wait > 0:
                sleep_fn(start_wait)
            started_at = _utc_text(now_provider())
        else:
            started_at = initial_start_at or _utc_text(now_provider())
        state = dict(
            advance_runtime_horizon_collection_state(
                plan=plan,
                previous=state,
                event="START",
                observed_at=started_at,
            )
        )
        write_runtime_horizon_collection_state(root, plan=plan, state=state)
    elif state["status"] != "RUNNING" or state["active"] is not True:
        raise PermissionError("runtime_horizon_collection_loop_running_state_invalid")

    planned_end = _parse_utc(str(plan["planned_end_utc"]))
    maximum_iterations = int(plan["maximum_loop_iterations"])
    cadence_sec = int(plan["cadence_sec"])
    loop_iterations = 0
    last_tick: Mapping[str, Any] = {}
    stop_reason = ""

    while True:
        persisted_now = read_runtime_horizon_collection_state(root, plan=plan)
        if persisted_now:
            validate_runtime_horizon_collection_state(plan=plan, state=persisted_now)
            for key in (
                "iteration_count",
                "written_origin_count",
                "duplicate_origin_skip_count",
                "readiness_skip_count",
                "error_count",
            ):
                if int(persisted_now[key]) < int(state[key]):
                    raise ValueError(
                        f"runtime_horizon_collection_loop_persisted_counter_regressed:{key}"
                    )
            if persisted_now["completed_prediction_origins"] != state["completed_prediction_origins"]:
                raise ValueError(
                    "runtime_horizon_collection_loop_persisted_origins_diverged"
                )
            if persisted_now["completed_closed_source_timestamps"] != state["completed_closed_source_timestamps"]:
                raise ValueError(
                    "runtime_horizon_collection_loop_persisted_closed_sources_diverged"
                )
            state = dict(persisted_now)

        now = now_provider()
        now_text = _utc_text(now)
        if lease_acquired:
            lease = heartbeat_runtime_horizon_collection_lease(
                root,
                plan=plan,
                lease_id=str(lease["lease_id"]),
                heartbeat_at=now_text,
                pid=lease_pid,
            )
        if now.astimezone(timezone.utc).replace(microsecond=0) >= planned_end:
            state = dict(
                advance_runtime_horizon_collection_state(
                    plan=plan,
                    previous=state,
                    event="COMPLETE",
                    observed_at=now_text,
                )
            )
            write_runtime_horizon_collection_state(root, plan=plan, state=state)
            write_runtime_horizon_collection_completion_receipt(root, plan=plan, state=state)
            stop_reason = "planned_end_reached"
            break

        if bool(state.get("stop_requested")):
            state = dict(
                advance_runtime_horizon_collection_state(
                    plan=plan,
                    previous=state,
                    event="PAUSE",
                    observed_at=now_text,
                    reason="stop_requested",
                )
            )
            write_runtime_horizon_collection_state(root, plan=plan, state=state)
            stop_reason = "stop_requested"
            break

        if loop_iterations >= maximum_iterations:
            state = dict(
                advance_runtime_horizon_collection_state(
                    plan=plan,
                    previous=state,
                    event="CONTRACT_ERROR",
                    observed_at=now_text,
                    reason="maximum_loop_iterations_exceeded",
                )
            )
            write_runtime_horizon_collection_state(root, plan=plan, state=state)
            stop_reason = "maximum_loop_iterations_exceeded"
            break

        try:
            last_tick = tick_executor(state, now_text)
            if not isinstance(last_tick, Mapping) or not isinstance(last_tick.get("state"), Mapping):
                raise ValueError("runtime_horizon_collection_loop_tick_result_invalid")
            state = dict(last_tick["state"])
            validate_runtime_horizon_collection_state(plan=plan, state=state)
        except Exception as exc:
            state = dict(
                advance_runtime_horizon_collection_state(
                    plan=plan,
                    previous=state,
                    event="CONTRACT_ERROR",
                    observed_at=now_text,
                    reason=f"{type(exc).__name__}:{exc}",
                )
            )
            write_runtime_horizon_collection_state(root, plan=plan, state=state)
            stop_reason = "tick_exception"
            break

        loop_iterations += 1
        if state["status"] in TERMINAL_STATUSES:
            stop_reason = str(state["status"]).lower()
            break
        if state["status"] == "PAUSED" or state["active"] is not True:
            stop_reason = "paused"
            break
        if cadence_anchored:
            after_tick = now_provider()
            cadence_sleep = collection_cadence_sleep_seconds(
                planned_start=planned_start,
                planned_end=planned_end,
                observed_at=after_tick,
                cadence_sec=cadence_sec,
            )
            if cadence_sleep > 0:
                sleep_fn(cadence_sleep)
        else:
            sleep_fn(float(cadence_sec))

    lease_released = False
    if lease_acquired and (
        state["status"] in TERMINAL_STATUSES
        or stop_reason in {"stop_requested", "paused"}
    ):
        release_runtime_horizon_collection_lease(
            root,
            plan=plan,
            lease_id=str(lease["lease_id"]),
            pid=lease_pid,
        )
        lease_released = True

    return {
        "ok": state["status"] == "COMPLETED",
        "event": "LOOP_STOPPED",
        "stop_reason": stop_reason,
        "loop_iterations": loop_iterations,
        "state": state,
        "last_tick": dict(last_tick),
        "lease_required": lease_required,
        "lease_id": str(lease.get("lease_id") or ""),
        "lease_acquired": lease_acquired,
        "lease_released": lease_released,
        "cadence_anchored": cadence_anchored,
        "writer_registered": False,
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
