# path: ./btcts_next/src/btcts/prediction/market_regime/runtime_horizon_collection_contract.py
# desc: MR-F9.19L pure bounded 24-hour runtime-horizon collection contract. No loop, scheduler, or writes.

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Mapping

RUNTIME_HORIZON_COLLECTION_CONTRACT_VERSION = (
    "prediction.market_regime.runtime_horizon_collection_contract.mr_f9_19l.v1"
)
COLLECTION_DURATION_SEC = 86_400
COLLECTION_CADENCE_SEC = 60
EXPECTED_HORIZON_COUNT = 8
EXPECTED_FILES_PER_ORIGIN = 9
MAX_COLLECTION_TICKS = COLLECTION_DURATION_SEC // COLLECTION_CADENCE_SEC + 2


def _parse_utc(value: Any, *, field: str) -> datetime:
    text = str(value or "").strip()
    if not text:
        raise ValueError(f"runtime_horizon_collection_{field}_required")
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError as exc:
        raise ValueError(f"runtime_horizon_collection_{field}_invalid") from exc
    if parsed.tzinfo is None:
        raise ValueError(f"runtime_horizon_collection_{field}_timezone_required")
    return parsed.astimezone(timezone.utc).replace(microsecond=0)


def _utc_text(value: datetime) -> str:
    return value.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _canonical_digest(payload: Mapping[str, Any]) -> str:
    text = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def build_runtime_horizon_collection_plan(
    *,
    source_root: str | Path,
    destination_root: str | Path,
    shadow_candidate_id: str,
    operator_id: str,
    planned_start_utc: str,
    duration_sec: int = COLLECTION_DURATION_SEC,
    cadence_sec: int = COLLECTION_CADENCE_SEC,
) -> Mapping[str, Any]:
    source = Path(source_root).resolve()
    destination = Path(destination_root).resolve()
    candidate = str(shadow_candidate_id).strip()
    operator = str(operator_id).strip()
    start = _parse_utc(planned_start_utc, field="planned_start_utc")

    if not candidate:
        raise ValueError("runtime_horizon_collection_shadow_candidate_id_required")
    if not operator:
        raise ValueError("runtime_horizon_collection_operator_id_required")
    if type(duration_sec) is not int or duration_sec != COLLECTION_DURATION_SEC:
        raise ValueError("runtime_horizon_collection_duration_must_equal_86400")
    if type(cadence_sec) is not int or cadence_sec != COLLECTION_CADENCE_SEC:
        raise ValueError("runtime_horizon_collection_cadence_must_equal_60")
    if duration_sec % cadence_sec:
        raise ValueError("runtime_horizon_collection_tick_count_invalid")

    end = start + timedelta(seconds=duration_sec)
    identity = {
        "schema_version": RUNTIME_HORIZON_COLLECTION_CONTRACT_VERSION,
        "source_root": str(source),
        "destination_root": str(destination),
        "shadow_candidate_id": candidate,
        "operator_id": operator,
        "planned_start_utc": _utc_text(start),
        "planned_end_utc": _utc_text(end),
        "duration_sec": duration_sec,
        "cadence_sec": cadence_sec,
    }
    collection_id = "mr-f9-24h-" + _canonical_digest(identity)[:20]
    state_relpath = (
        "prediction/market_regime/runtime_horizon_collections/"
        f"collection_id={collection_id}/state.json"
    )
    progress_relpath = (
        "prediction/market_regime/runtime_horizon_collections/"
        f"collection_id={collection_id}/progress.json"
    )
    receipt_relpath = (
        "prediction/market_regime/runtime_horizon_collections/"
        f"collection_id={collection_id}/completion_receipt.json"
    )

    plan = {
        **identity,
        "artifact_kind": "market_regime_runtime_horizon_collection_plan",
        "collection_id": collection_id,
        "expected_tick_count": duration_sec // cadence_sec,
        "maximum_loop_iterations": MAX_COLLECTION_TICKS,
        "expected_horizon_count_per_origin": EXPECTED_HORIZON_COUNT,
        "expected_files_per_origin": EXPECTED_FILES_PER_ORIGIN,
        "state_relpath": state_relpath,
        "progress_relpath": progress_relpath,
        "completion_receipt_relpath": receipt_relpath,
        "origin_identity_policy": "one_origin_per_latest_closed_60s_candle",
        "duplicate_origin_policy": "skip_without_write",
        "readiness_failure_policy": "record_skip_and_continue",
        "destination_conflict_policy": "fail_closed_and_stop",
        "restart_policy": "resume_from_persisted_state_without_rewriting_completed_origins",
        "completion_policy": "planned_end_reached_and_no_active_write",
        "foreground_process_required": True,
        "scheduler_registration_allowed": False,
        "latest_pointer_created": False,
        "writer_registered": False,
        "websocket_opened": False,
        "ui_inference_allowed": False,
        "ui_confidence_recalculation_allowed": False,
        "broker_private_api_allowed": False,
        "autotrade_trigger_allowed": False,
        "order_submission_allowed": False,
        "auto_promotion_allowed": False,
        "live_parameter_apply_allowed": False,
        "disabled_by_default": True,
        "human_start_authorization_required": True,
        "collection_started": False,
        "collection_completed": False,
        "writer_invoked": False,
        "writes_dhot": False,
    }
    return {**plan, "plan_sha256": _canonical_digest(plan)}


def validate_runtime_horizon_collection_plan(plan: Mapping[str, Any]) -> None:
    if not isinstance(plan, Mapping):
        raise ValueError("runtime_horizon_collection_plan_invalid")
    if plan.get("schema_version") != RUNTIME_HORIZON_COLLECTION_CONTRACT_VERSION:
        raise ValueError("runtime_horizon_collection_plan_schema_invalid")
    if plan.get("artifact_kind") != "market_regime_runtime_horizon_collection_plan":
        raise ValueError("runtime_horizon_collection_plan_kind_invalid")

    rebuilt = build_runtime_horizon_collection_plan(
        source_root=str(plan.get("source_root") or ""),
        destination_root=str(plan.get("destination_root") or ""),
        shadow_candidate_id=str(plan.get("shadow_candidate_id") or ""),
        operator_id=str(plan.get("operator_id") or ""),
        planned_start_utc=str(plan.get("planned_start_utc") or ""),
        duration_sec=int(plan.get("duration_sec") or 0),
        cadence_sec=int(plan.get("cadence_sec") or 0),
    )
    if dict(plan) != dict(rebuilt):
        raise ValueError("runtime_horizon_collection_plan_digest_or_contract_mismatch")
