# path: ./btcts_next/src/btcts/prediction/market_regime/runtime_horizon_collection_state.py
# desc: MR-F9.19L restart-safe atomic state/progress persistence for bounded 24-hour runtime-horizon collection. No loop, scheduler, or market write.

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from .runtime_horizon_collection_contract import (
    RUNTIME_HORIZON_COLLECTION_CONTRACT_VERSION,
    validate_runtime_horizon_collection_plan,
)

RUNTIME_HORIZON_COLLECTION_STATE_VERSION = (
    "prediction.market_regime.runtime_horizon_collection_state.mr_f9_19l.v1"
)
TERMINAL_STATUSES = {"COMPLETED", "FAILED_CONFLICT", "FAILED_CONTRACT"}


def _utc_now_text() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _atomic_write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(
        json.dumps(dict(payload), ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )
    tmp.replace(path)


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    payload = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(payload, Mapping):
        raise ValueError("runtime_horizon_collection_state_payload_invalid")
    return dict(payload)


def collection_state_paths(root: str | Path, plan: Mapping[str, Any]) -> Mapping[str, Path]:
    validate_runtime_horizon_collection_plan(plan)
    base = Path(root)
    return {
        "state": base / str(plan["state_relpath"]),
        "progress": base / str(plan["progress_relpath"]),
        "completion_receipt": base / str(plan["completion_receipt_relpath"]),
    }


def build_initial_runtime_horizon_collection_state(
    *,
    plan: Mapping[str, Any],
    created_at: str | None = None,
) -> Mapping[str, Any]:
    validate_runtime_horizon_collection_plan(plan)
    now = str(created_at or _utc_now_text())
    return {
        "schema_version": RUNTIME_HORIZON_COLLECTION_STATE_VERSION,
        "contract_version": RUNTIME_HORIZON_COLLECTION_CONTRACT_VERSION,
        "artifact_kind": "market_regime_runtime_horizon_collection_state",
        "collection_id": plan["collection_id"],
        "plan_sha256": plan["plan_sha256"],
        "planned_start_utc": plan["planned_start_utc"],
        "planned_end_utc": plan["planned_end_utc"],
        "created_at": now,
        "updated_at": now,
        "status": "PLANNED",
        "active": False,
        "iteration_count": 0,
        "written_origin_count": 0,
        "duplicate_origin_skip_count": 0,
        "readiness_skip_count": 0,
        "error_count": 0,
        "completed_prediction_origins": [],
        "completed_closed_source_timestamps": [],
        "latest_prediction_origin": "",
        "latest_run_id": "",
        "last_skip_reason": "",
        "last_error": "",
        "stop_requested": False,
        "completion_receipt_written": False,
        "writer_registered": False,
        "scheduler_enabled": False,
        "producer_loop_enabled": False,
        "latest_pointer_created": False,
        "websocket_opened": False,
        "ui_inference_allowed": False,
        "ui_confidence_recalculation_allowed": False,
        "broker_private_api_allowed": False,
        "autotrade_trigger_allowed": False,
        "order_submission_allowed": False,
    }


def validate_runtime_horizon_collection_state(
    *,
    plan: Mapping[str, Any],
    state: Mapping[str, Any],
) -> None:
    validate_runtime_horizon_collection_plan(plan)
    if not isinstance(state, Mapping):
        raise ValueError("runtime_horizon_collection_state_invalid")
    if state.get("schema_version") != RUNTIME_HORIZON_COLLECTION_STATE_VERSION:
        raise ValueError("runtime_horizon_collection_state_schema_invalid")
    if state.get("collection_id") != plan.get("collection_id"):
        raise ValueError("runtime_horizon_collection_state_collection_id_mismatch")
    if state.get("plan_sha256") != plan.get("plan_sha256"):
        raise ValueError("runtime_horizon_collection_state_plan_sha_mismatch")

    origins = list(state.get("completed_prediction_origins") or [])
    if any(not isinstance(item, str) or not item for item in origins):
        raise ValueError("runtime_horizon_collection_state_origin_invalid")
    if len(origins) != len(set(origins)):
        raise ValueError("runtime_horizon_collection_state_duplicate_origin")
    if int(state.get("written_origin_count") or 0) != len(origins):
        raise ValueError("runtime_horizon_collection_state_written_count_mismatch")
    closed_sources = list(state.get("completed_closed_source_timestamps") or [])
    if any(not isinstance(item, str) or not item for item in closed_sources):
        raise ValueError("runtime_horizon_collection_state_closed_source_invalid")
    if len(closed_sources) != len(set(closed_sources)):
        raise ValueError("runtime_horizon_collection_state_duplicate_closed_source")
    if len(closed_sources) != len(origins):
        raise ValueError("runtime_horizon_collection_state_closed_source_count_mismatch")
    for key in (
        "iteration_count",
        "written_origin_count",
        "duplicate_origin_skip_count",
        "readiness_skip_count",
        "error_count",
    ):
        value = state.get(key)
        if type(value) is not int or value < 0:
            raise ValueError(f"runtime_horizon_collection_state_{key}_invalid")
    for key in (
        "writer_registered",
        "scheduler_enabled",
        "producer_loop_enabled",
        "latest_pointer_created",
        "websocket_opened",
        "ui_inference_allowed",
        "ui_confidence_recalculation_allowed",
        "broker_private_api_allowed",
        "autotrade_trigger_allowed",
        "order_submission_allowed",
    ):
        if state.get(key) is not False:
            raise ValueError(f"runtime_horizon_collection_state_safety_violation:{key}")


def read_runtime_horizon_collection_state(
    root: str | Path,
    *,
    plan: Mapping[str, Any],
) -> Mapping[str, Any]:
    paths = collection_state_paths(root, plan)
    payload = _read_json(paths["state"])
    if not payload:
        return {}
    validate_runtime_horizon_collection_state(plan=plan, state=payload)
    return payload


def write_runtime_horizon_collection_state(
    root: str | Path,
    *,
    plan: Mapping[str, Any],
    state: Mapping[str, Any],
) -> Mapping[str, Any]:
    validate_runtime_horizon_collection_state(plan=plan, state=state)
    paths = collection_state_paths(root, plan)
    _atomic_write_json(paths["state"], state)
    progress = {
        "schema_version": RUNTIME_HORIZON_COLLECTION_STATE_VERSION,
        "artifact_kind": "market_regime_runtime_horizon_collection_progress",
        "collection_id": state["collection_id"],
        "plan_sha256": state["plan_sha256"],
        "status": state["status"],
        "active": state["active"],
        "updated_at": state["updated_at"],
        "iteration_count": state["iteration_count"],
        "written_origin_count": state["written_origin_count"],
        "duplicate_origin_skip_count": state["duplicate_origin_skip_count"],
        "readiness_skip_count": state["readiness_skip_count"],
        "error_count": state["error_count"],
        "latest_prediction_origin": state["latest_prediction_origin"],
        "latest_closed_source_timestamp": (state["completed_closed_source_timestamps"][-1] if state["completed_closed_source_timestamps"] else ""),
        "latest_run_id": state["latest_run_id"],
        "last_skip_reason": state["last_skip_reason"],
        "last_error": state["last_error"],
        "planned_start_utc": state["planned_start_utc"],
        "planned_end_utc": state["planned_end_utc"],
        "latest_pointer_created": False,
        "scheduler_enabled": False,
        "producer_loop_enabled": False,
        "websocket_opened": False,
        "ui_inference_allowed": False,
        "order_submission_allowed": False,
    }
    _atomic_write_json(paths["progress"], progress)
    return {
        "ok": True,
        "state_relpath": str(plan["state_relpath"]),
        "progress_relpath": str(plan["progress_relpath"]),
        "status": state["status"],
        "written_origin_count": state["written_origin_count"],
        "writer_invoked": False,
        "writes_dhot": False,
    }


def advance_runtime_horizon_collection_state(
    *,
    plan: Mapping[str, Any],
    previous: Mapping[str, Any],
    event: str,
    observed_at: str,
    prediction_origin: str = "",
    closed_source_timestamp: str = "",
    run_id: str = "",
    reason: str = "",
) -> Mapping[str, Any]:
    validate_runtime_horizon_collection_state(plan=plan, state=previous)
    state = dict(previous)
    if str(state.get("status")) in TERMINAL_STATUSES:
        raise ValueError("runtime_horizon_collection_state_terminal")

    normalized = str(event or "").strip().upper()
    state["updated_at"] = str(observed_at)
    if normalized == "START":
        if state["status"] not in {"PLANNED", "PAUSED"}:
            raise ValueError("runtime_horizon_collection_start_transition_invalid")
        state["status"] = "RUNNING"
        state["active"] = True
    elif normalized == "WRITE_OK":
        if state["status"] != "RUNNING" or not state["active"]:
            raise ValueError("runtime_horizon_collection_write_transition_invalid")
        origin = str(prediction_origin).strip()
        if not origin:
            raise ValueError("runtime_horizon_collection_prediction_origin_required")
        if origin in state["completed_prediction_origins"]:
            raise ValueError("runtime_horizon_collection_origin_already_completed")
        closed_source = str(closed_source_timestamp).strip()
        if not closed_source:
            raise ValueError("runtime_horizon_collection_closed_source_required")
        if closed_source in state["completed_closed_source_timestamps"]:
            raise ValueError("runtime_horizon_collection_closed_source_already_completed")
        state["iteration_count"] += 1
        state["completed_prediction_origins"] = [*state["completed_prediction_origins"], origin]
        state["completed_closed_source_timestamps"] = [*state["completed_closed_source_timestamps"], closed_source]
        state["written_origin_count"] += 1
        state["latest_prediction_origin"] = origin
        state["latest_run_id"] = str(run_id).strip()
        state["last_skip_reason"] = ""
        state["last_error"] = ""
    elif normalized == "DUPLICATE_ORIGIN_SKIP":
        state["iteration_count"] += 1
        state["duplicate_origin_skip_count"] += 1
        state["last_skip_reason"] = str(reason or "duplicate_origin")
    elif normalized == "READINESS_SKIP":
        state["iteration_count"] += 1
        state["readiness_skip_count"] += 1
        state["last_skip_reason"] = str(reason or "readiness_not_ready")
    elif normalized == "PAUSE":
        state["status"] = "PAUSED"
        state["active"] = False
        state["last_skip_reason"] = str(reason or "operator_pause")
    elif normalized == "CONFLICT":
        state["status"] = "FAILED_CONFLICT"
        state["active"] = False
        state["error_count"] += 1
        state["last_error"] = str(reason or "destination_conflict")
    elif normalized == "CONTRACT_ERROR":
        state["status"] = "FAILED_CONTRACT"
        state["active"] = False
        state["error_count"] += 1
        state["last_error"] = str(reason or "contract_error")
    elif normalized == "COMPLETE":
        state["status"] = "COMPLETED"
        state["active"] = False
    else:
        raise ValueError("runtime_horizon_collection_event_invalid")

    validate_runtime_horizon_collection_state(plan=plan, state=state)
    return state


def write_runtime_horizon_collection_completion_receipt(
    root: str | Path,
    *,
    plan: Mapping[str, Any],
    state: Mapping[str, Any],
) -> Mapping[str, Any]:
    validate_runtime_horizon_collection_state(plan=plan, state=state)
    if state.get("status") != "COMPLETED" or state.get("active") is not False:
        raise ValueError("runtime_horizon_collection_completion_state_required")
    paths = collection_state_paths(root, plan)
    receipt = {
        "schema_version": RUNTIME_HORIZON_COLLECTION_STATE_VERSION,
        "artifact_kind": "market_regime_runtime_horizon_collection_completion_receipt",
        "collection_id": state["collection_id"],
        "plan_sha256": state["plan_sha256"],
        "planned_start_utc": state["planned_start_utc"],
        "planned_end_utc": state["planned_end_utc"],
        "completed_at": state["updated_at"],
        "written_origin_count": state["written_origin_count"],
        "duplicate_origin_skip_count": state["duplicate_origin_skip_count"],
        "readiness_skip_count": state["readiness_skip_count"],
        "error_count": state["error_count"],
        "latest_prediction_origin": state["latest_prediction_origin"],
        "latest_closed_source_timestamp": (state["completed_closed_source_timestamps"][-1] if state["completed_closed_source_timestamps"] else ""),
        "latest_run_id": state["latest_run_id"],
        "latest_pointer_created": False,
        "scheduler_enabled": False,
        "producer_loop_enabled": False,
        "websocket_opened": False,
        "ui_inference_allowed": False,
        "order_submission_allowed": False,
    }
    _atomic_write_json(paths["completion_receipt"], receipt)
    return {
        "ok": True,
        "completion_receipt_relpath": str(plan["completion_receipt_relpath"]),
        "written_origin_count": state["written_origin_count"],
        "writer_invoked": False,
        "writes_dhot": False,
    }

def request_runtime_horizon_collection_stop(
    root: str | Path,
    *,
    plan: Mapping[str, Any],
    requested_at: str | None = None,
) -> Mapping[str, Any]:
    state = read_runtime_horizon_collection_state(root, plan=plan)
    if not state:
        raise FileNotFoundError("runtime_horizon_collection_stop_state_missing")
    if state["status"] in TERMINAL_STATUSES:
        return {
            "ok": True,
            "already_terminal": True,
            "status": state["status"],
            "stop_requested": bool(state.get("stop_requested")),
            "writer_invoked": False,
            "writes_dhot": False,
        }
    updated = dict(state)
    updated["stop_requested"] = True
    updated["updated_at"] = str(requested_at or _utc_now_text())
    write_runtime_horizon_collection_state(root, plan=plan, state=updated)
    return {
        "ok": True,
        "already_terminal": False,
        "status": updated["status"],
        "stop_requested": True,
        "writer_invoked": False,
        "writes_dhot": False,
    }
