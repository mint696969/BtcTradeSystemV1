# path: ./btcts_next/src/btcts/prediction/market_regime/runtime_horizon_collection_tick.py
# desc: MR-F9.19L one-tick coordinator for bounded runtime-horizon collection. No loop or scheduler registration.

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable, Mapping

from .runtime_horizon_collection_contract import validate_runtime_horizon_collection_plan
from .runtime_horizon_collection_state import (
    advance_runtime_horizon_collection_state,
    validate_runtime_horizon_collection_state,
    write_runtime_horizon_collection_state,
)

PreflightBuilder = Callable[[], Mapping[str, Any]]
ReadinessBuilder = Callable[[Mapping[str, Any]], Mapping[str, Any]]
Writer = Callable[[Mapping[str, Any]], Mapping[str, Any]]


def execute_runtime_horizon_collection_tick(
    root: str | Path,
    *,
    plan: Mapping[str, Any],
    state: Mapping[str, Any],
    observed_at: str,
    preflight_builder: PreflightBuilder,
    readiness_builder: ReadinessBuilder,
    writer: Writer,
) -> Mapping[str, Any]:
    validate_runtime_horizon_collection_plan(plan)
    validate_runtime_horizon_collection_state(plan=plan, state=state)
    if state.get("status") != "RUNNING" or state.get("active") is not True:
        raise PermissionError("runtime_horizon_collection_tick_running_state_required")
    if not callable(preflight_builder) or not callable(readiness_builder) or not callable(writer):
        raise ValueError("runtime_horizon_collection_tick_callback_invalid")

    preflight = preflight_builder()
    if not isinstance(preflight, Mapping):
        raise ValueError("runtime_horizon_collection_tick_preflight_invalid")
    for key in (
        "runtime_horizon_writer_registered",
        "writer_invoked",
        "writes_dhot",
        "scheduler_enabled",
        "producer_loop_enabled",
        "broker_private_api_allowed",
        "autotrade_trigger_allowed",
        "order_submission_allowed",
    ):
        if preflight.get(key) is not False:
            raise ValueError(f"runtime_horizon_collection_tick_preflight_safety_invalid:{key}")

    unavailable_reason = str(
        preflight.get("collection_preflight_unavailable_reason") or ""
    ).strip()
    if unavailable_reason:
        next_state = advance_runtime_horizon_collection_state(
            plan=plan,
            previous=state,
            event="READINESS_SKIP",
            observed_at=observed_at,
            reason=unavailable_reason,
        )
        write_runtime_horizon_collection_state(root, plan=plan, state=next_state)
        return {
            "event": "READINESS_SKIP",
            "prediction_origin": "",
            "closed_source_timestamp": "",
            "run_id": "",
            "writer_invoked": False,
            "writes_dhot": False,
            "state": next_state,
            "skip_stage": "preflight",
            "skip_reason": unavailable_reason,
        }

    persistence_plan = preflight.get("runtime_horizon_persistence_plan")
    if not isinstance(persistence_plan, Mapping):
        raise ValueError("runtime_horizon_collection_tick_persistence_plan_invalid")
    prediction_origin = str(persistence_plan.get("prediction_origin") or "").strip()
    run_id = str(persistence_plan.get("run_id") or "").strip()
    if not prediction_origin or not run_id:
        raise ValueError("runtime_horizon_collection_tick_identity_missing")
    artifact = preflight.get("runtime_horizon_artifact")
    if not isinstance(artifact, Mapping):
        raise ValueError("runtime_horizon_collection_tick_artifact_invalid")
    horizons = artifact.get("horizons")
    if not isinstance(horizons, (tuple, list)):
        raise ValueError("runtime_horizon_collection_tick_horizons_invalid")
    closed_sources = {
        str(row.get("source_timestamp") or "").strip()
        for row in horizons
        if isinstance(row, Mapping) and int(row.get("horizon_sec") or 0) > 0
    }
    closed_sources.discard("")
    if len(closed_sources) != 1:
        raise ValueError("runtime_horizon_collection_tick_closed_source_identity_invalid")
    closed_source_timestamp = next(iter(closed_sources))

    if (
        prediction_origin in set(state.get("completed_prediction_origins") or ())
        or closed_source_timestamp in set(state.get("completed_closed_source_timestamps") or ())
    ):
        next_state = advance_runtime_horizon_collection_state(
            plan=plan,
            previous=state,
            event="DUPLICATE_ORIGIN_SKIP",
            observed_at=observed_at,
            reason="prediction_origin_already_completed",
        )
        write_runtime_horizon_collection_state(root, plan=plan, state=next_state)
        return {
            "event": "DUPLICATE_ORIGIN_SKIP",
            "prediction_origin": prediction_origin,
            "closed_source_timestamp": closed_source_timestamp,
            "run_id": run_id,
            "writer_invoked": False,
            "writes_dhot": False,
            "state": next_state,
        }

    readiness = readiness_builder(preflight)
    if not isinstance(readiness, Mapping):
        raise ValueError("runtime_horizon_collection_tick_readiness_invalid")
    blockers = tuple(str(item) for item in (readiness.get("blockers") or ()))
    conflicts = tuple(item for item in blockers if item.startswith("destination_conflict:"))
    if conflicts:
        next_state = advance_runtime_horizon_collection_state(
            plan=plan,
            previous=state,
            event="CONFLICT",
            observed_at=observed_at,
            reason=";".join(conflicts),
        )
        write_runtime_horizon_collection_state(root, plan=plan, state=next_state)
        return {
            "event": "CONFLICT",
            "prediction_origin": prediction_origin,
            "run_id": run_id,
            "writer_invoked": False,
            "writes_dhot": False,
            "state": next_state,
        }
    if readiness.get("ready") is not True or blockers:
        next_state = advance_runtime_horizon_collection_state(
            plan=plan,
            previous=state,
            event="READINESS_SKIP",
            observed_at=observed_at,
            reason=";".join(blockers) or "readiness_not_ready",
        )
        write_runtime_horizon_collection_state(root, plan=plan, state=next_state)
        return {
            "event": "READINESS_SKIP",
            "prediction_origin": prediction_origin,
            "run_id": run_id,
            "writer_invoked": False,
            "writes_dhot": False,
            "state": next_state,
        }

    write_result = writer(persistence_plan)
    if not isinstance(write_result, Mapping):
        raise ValueError("runtime_horizon_collection_tick_writer_result_invalid")
    for key in (
        "latest_pointer_created",
        "writer_registered",
        "producer_loop_enabled",
        "scheduler_enabled",
        "websocket_opened",
        "order_submission_allowed",
    ):
        if write_result.get(key) is not False:
            raise ValueError(f"runtime_horizon_collection_tick_writer_safety_invalid:{key}")

    expected_order = tuple(str(item) for item in (persistence_plan.get("write_order") or ()))
    written = tuple(str(item) for item in (write_result.get("written_paths") or ()))
    duplicate = tuple(str(item) for item in (write_result.get("duplicate_paths") or ()))
    if len(expected_order) != 9 or expected_order[-1] != str(persistence_plan.get("manifest_relpath") or ""):
        raise ValueError("runtime_horizon_collection_tick_plan_write_order_invalid")
    if len(set(written)) != len(written) or len(set(duplicate)) != len(duplicate):
        raise ValueError("runtime_horizon_collection_tick_receipt_duplicate_path")
    if set(written).intersection(duplicate):
        raise ValueError("runtime_horizon_collection_tick_receipt_path_overlap")
    if set(written).union(duplicate) != set(expected_order):
        raise ValueError("runtime_horizon_collection_tick_receipt_path_set_mismatch")
    if written != tuple(path for path in expected_order if path in set(written)):
        raise ValueError("runtime_horizon_collection_tick_written_order_mismatch")
    if duplicate != tuple(path for path in expected_order if path in set(duplicate)):
        raise ValueError("runtime_horizon_collection_tick_duplicate_order_mismatch")
    if int(write_result.get("written_count") or 0) != len(written):
        raise ValueError("runtime_horizon_collection_tick_written_count_mismatch")
    if int(write_result.get("duplicate_count") or 0) != len(duplicate):
        raise ValueError("runtime_horizon_collection_tick_duplicate_count_mismatch")
    if str(write_result.get("manifest_relpath") or "") != expected_order[-1]:
        raise ValueError("runtime_horizon_collection_tick_manifest_receipt_mismatch")
    if written and write_result.get("manifest_written_last") is not True:
        raise ValueError("runtime_horizon_collection_tick_manifest_not_last")

    next_state = advance_runtime_horizon_collection_state(
        plan=plan,
        previous=state,
        event="WRITE_OK",
        observed_at=observed_at,
        prediction_origin=prediction_origin,
        closed_source_timestamp=closed_source_timestamp,
        run_id=run_id,
    )
    write_runtime_horizon_collection_state(root, plan=plan, state=next_state)
    return {
        "event": "WRITE_OK",
        "prediction_origin": prediction_origin,
        "closed_source_timestamp": closed_source_timestamp,
        "run_id": run_id,
        "writer_invoked": True,
        "writes_dhot": Path(root).resolve() == Path(str(plan["destination_root"])).resolve(),
        "write_result": dict(write_result),
        "state": next_state,
        "writer_registered": False,
        "scheduler_enabled": False,
        "producer_loop_enabled": False,
        "websocket_opened": False,
        "ui_inference_allowed": False,
        "ui_confidence_recalculation_allowed": False,
        "order_submission_allowed": False,
    }
