# path: ./btcts_next/src/btcts/prediction/market_regime/runtime_horizon_collection_authorization.py
# desc: MR-F9.19L read-only exact human start authorization package for one bounded 24h D-hot collection.

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Mapping

from .runtime_horizon_collection_contract import (
    COLLECTION_CADENCE_SEC,
    COLLECTION_DURATION_SEC,
    validate_runtime_horizon_collection_plan,
)

COLLECTION_START_AUTHORIZATION_VERSION = (
    "prediction.market_regime.runtime_horizon_collection_authorization.mr_f9_19l.v1"
)
MAX_COLLECTION_START_AUTHORIZATION_TTL_SEC = 300


def _digest(value: Mapping[str, Any]) -> str:
    text = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _parse_utc(value: Any, *, field: str) -> datetime:
    text = str(value or "").strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError as exc:
        raise ValueError(f"runtime_horizon_collection_authorization_{field}_invalid") from exc
    if parsed.tzinfo is None:
        raise ValueError(f"runtime_horizon_collection_authorization_{field}_timezone_required")
    return parsed.astimezone(timezone.utc).replace(microsecond=0)


def _utc_text(value: datetime) -> str:
    return value.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def build_runtime_horizon_collection_start_authorization_package(
    *,
    plan: Mapping[str, Any],
    created_at: str,
    expected_dhot_root: str | Path,
    ttl_sec: int = 300,
) -> Mapping[str, Any]:
    validate_runtime_horizon_collection_plan(plan)
    if type(ttl_sec) is not int or ttl_sec <= 0 or ttl_sec > MAX_COLLECTION_START_AUTHORIZATION_TTL_SEC:
        raise ValueError("runtime_horizon_collection_authorization_ttl_invalid")

    source = Path(str(plan["source_root"])).resolve()
    destination = Path(str(plan["destination_root"])).resolve()
    expected = Path(expected_dhot_root).resolve()
    if source != expected or destination != expected:
        raise ValueError("runtime_horizon_collection_authorization_root_not_dhot")
    if int(plan["duration_sec"]) != COLLECTION_DURATION_SEC:
        raise ValueError("runtime_horizon_collection_authorization_duration_invalid")
    if int(plan["cadence_sec"]) != COLLECTION_CADENCE_SEC:
        raise ValueError("runtime_horizon_collection_authorization_cadence_invalid")
    if plan.get("human_start_authorization_required") is not True:
        raise ValueError("runtime_horizon_collection_authorization_human_gate_missing")
    if plan.get("foreground_process_required") is not True:
        raise ValueError("runtime_horizon_collection_authorization_foreground_required")

    created = _parse_utc(created_at, field="created_at")
    planned_start = _parse_utc(plan["planned_start_utc"], field="planned_start_utc")
    if created > planned_start:
        raise ValueError("runtime_horizon_collection_authorization_created_after_planned_start")
    if (planned_start - created).total_seconds() > MAX_COLLECTION_START_AUTHORIZATION_TTL_SEC:
        raise ValueError("runtime_horizon_collection_authorization_start_too_far")
    expires = created + timedelta(seconds=ttl_sec)
    if planned_start > expires:
        raise ValueError("runtime_horizon_collection_authorization_expires_before_start")

    authorization_text = (
        "AUTHORIZE MR-F9 24H D-HOT COLLECTION "
        f"collection_id={plan['collection_id']} "
        f"plan_sha256={plan['plan_sha256']} "
        f"operator_id={plan['operator_id']} "
        f"duration_sec={plan['duration_sec']} cadence_sec={plan['cadence_sec']}"
    )
    body = {
        "schema_version": COLLECTION_START_AUTHORIZATION_VERSION,
        "artifact_kind": "market_regime_runtime_horizon_collection_start_authorization_package",
        "collection_id": plan["collection_id"],
        "plan_sha256": plan["plan_sha256"],
        "source_root": str(expected),
        "destination_root": str(expected),
        "shadow_candidate_id": plan["shadow_candidate_id"],
        "operator_id": plan["operator_id"],
        "planned_start_utc": plan["planned_start_utc"],
        "planned_end_utc": plan["planned_end_utc"],
        "duration_sec": plan["duration_sec"],
        "cadence_sec": plan["cadence_sec"],
        "created_at": _utc_text(created),
        "expires_at": _utc_text(expires),
        "ttl_sec": ttl_sec,
        "expected_authorization_text": authorization_text,
        "expected_authorization_text_sha256": hashlib.sha256(authorization_text.encode("utf-8")).hexdigest(),
        "human_authorized": False,
        "awaiting_explicit_human_authorization": True,
        "lease_required": True,
        "manifest_recovery_required": True,
        "foreground_process_required": True,
        "writer_invoked": False,
        "writes_dhot": False,
        "writer_registered": False,
        "latest_pointer_created": False,
        "scheduler_enabled": False,
        "detached_process_started": False,
        "websocket_opened": False,
        "ui_inference_allowed": False,
        "ui_confidence_recalculation_allowed": False,
        "broker_private_api_allowed": False,
        "autotrade_trigger_allowed": False,
        "order_submission_allowed": False,
    }
    return {**body, "authorization_package_sha256": _digest(body)}


def validate_runtime_horizon_collection_start_authorization_package(
    *,
    package: Mapping[str, Any],
    plan: Mapping[str, Any],
    now: str,
    expected_dhot_root: str | Path,
) -> None:
    if not isinstance(package, Mapping):
        raise ValueError("runtime_horizon_collection_authorization_package_invalid")
    rebuilt = build_runtime_horizon_collection_start_authorization_package(
        plan=plan,
        created_at=str(package.get("created_at") or ""),
        expected_dhot_root=expected_dhot_root,
        ttl_sec=int(package.get("ttl_sec") or 0),
    )
    if dict(package) != dict(rebuilt):
        raise ValueError("runtime_horizon_collection_authorization_package_mismatch")
    current = _parse_utc(now, field="now")
    created = _parse_utc(package["created_at"], field="created_at")
    expires = _parse_utc(package["expires_at"], field="expires_at")
    if current < created:
        raise ValueError("runtime_horizon_collection_authorization_not_yet_valid")
    if current > expires:
        raise PermissionError("runtime_horizon_collection_authorization_expired")
