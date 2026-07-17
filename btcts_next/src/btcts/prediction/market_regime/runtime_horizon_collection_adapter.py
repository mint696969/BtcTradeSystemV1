# path: ./btcts_next/src/btcts/prediction/market_regime/runtime_horizon_collection_adapter.py
# desc: MR-F9.19L explicit adapter connecting one collection tick to fresh preflight/readiness/guarded writer. No loop or scheduler.

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

from .runtime_horizon_collection_contract import validate_runtime_horizon_collection_plan
from .runtime_horizon_collection_tick import execute_runtime_horizon_collection_tick
from .runtime_horizon_persistence import persist_runtime_horizon_plan_once
from .runtime_horizon_write_readiness import build_runtime_horizon_write_readiness_report
from .tools.shadow_runtime_preflight_once import build_shadow_runtime_preflight_once


def execute_runtime_horizon_collection_adapter_tick(
    state_root: str | Path,
    *,
    plan: Mapping[str, Any],
    state: Mapping[str, Any],
    observed_at: str,
    collection_start_authorized: bool = False,
) -> Mapping[str, Any]:
    validate_runtime_horizon_collection_plan(plan)
    if type(collection_start_authorized) is not bool:
        raise ValueError("runtime_horizon_collection_adapter_authorization_flag_invalid")
    if collection_start_authorized is not True:
        raise PermissionError("runtime_horizon_collection_adapter_start_authorization_required")

    source = Path(str(plan["source_root"])).resolve()
    destination = Path(str(plan["destination_root"])).resolve()
    candidate = str(plan["shadow_candidate_id"])
    operator = str(plan["operator_id"])

    def preflight_builder() -> Mapping[str, Any]:
        return build_shadow_runtime_preflight_once(
            hot_root=source,
            generated_at=observed_at,
            shadow_candidate_id=candidate,
        )

    def readiness_builder(preflight: Mapping[str, Any]) -> Mapping[str, Any]:
        destination_bound = dict(preflight)
        destination_bound["hot_root"] = str(destination)
        return build_runtime_horizon_write_readiness_report(
            preflight=destination_bound,
            destination_root=destination,
            operator_id=operator,
            enabled_acknowledged=True,
            once_acknowledged=True,
        )

    def writer(persistence_plan: Mapping[str, Any]) -> Mapping[str, Any]:
        return persist_runtime_horizon_plan_once(
            destination,
            plan=persistence_plan,
            enabled=True,
            once=True,
        )

    result = execute_runtime_horizon_collection_tick(
        state_root,
        plan=plan,
        state=state,
        observed_at=observed_at,
        preflight_builder=preflight_builder,
        readiness_builder=readiness_builder,
        writer=writer,
    )
    return {
        **dict(result),
        "source_root": str(source),
        "destination_root": str(destination),
        "collection_start_authorized": True,
        "writes_dhot": bool(result.get("writer_invoked")) and source == destination,
        "writer_registered": False,
        "scheduler_enabled": False,
        "producer_loop_enabled": False,
        "detached_process_started": False,
        "latest_pointer_created": False,
        "websocket_opened": False,
        "ui_inference_allowed": False,
        "ui_confidence_recalculation_allowed": False,
        "broker_private_api_allowed": False,
        "autotrade_trigger_allowed": False,
        "order_submission_allowed": False,
    }
