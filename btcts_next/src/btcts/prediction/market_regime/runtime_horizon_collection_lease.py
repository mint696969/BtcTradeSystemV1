# path: ./btcts_next/src/btcts/prediction/market_regime/runtime_horizon_collection_lease.py
# desc: MR-F9.19L atomic single-process lease for bounded runtime-horizon collection. No writer or loop start.

from __future__ import annotations

import json
import os
import secrets
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from .runtime_horizon_collection_contract import validate_runtime_horizon_collection_plan
from .runtime_horizon_collection_state import collection_state_paths

LEASE_SCHEMA_VERSION = "prediction.market_regime.runtime_horizon_collection_lease.mr_f9_19l.v1"


def _parse_utc(value: Any, *, field: str) -> datetime:
    text = str(value or "").strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError as exc:
        raise ValueError(f"runtime_horizon_collection_lease_{field}_invalid") from exc
    if parsed.tzinfo is None:
        raise ValueError(f"runtime_horizon_collection_lease_{field}_timezone_required")
    return parsed.astimezone(timezone.utc).replace(microsecond=0)


def _utc_text(value: datetime) -> str:
    if value.tzinfo is None:
        raise ValueError("runtime_horizon_collection_lease_time_timezone_required")
    return value.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def runtime_horizon_collection_lease_path(
    root: str | Path,
    *,
    plan: Mapping[str, Any],
) -> Path:
    validate_runtime_horizon_collection_plan(plan)
    state_path = collection_state_paths(root, plan)["state"]
    return state_path.with_name("producer_lease.json")


def read_runtime_horizon_collection_lease(
    root: str | Path,
    *,
    plan: Mapping[str, Any],
) -> Mapping[str, Any]:
    path = runtime_horizon_collection_lease_path(root, plan=plan)
    if not path.exists():
        return {}
    payload = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(payload, Mapping):
        raise ValueError("runtime_horizon_collection_lease_payload_invalid")
    if payload.get("schema_version") != LEASE_SCHEMA_VERSION:
        raise ValueError("runtime_horizon_collection_lease_schema_invalid")
    if payload.get("collection_id") != plan.get("collection_id"):
        raise ValueError("runtime_horizon_collection_lease_collection_id_mismatch")
    if payload.get("plan_sha256") != plan.get("plan_sha256"):
        raise ValueError("runtime_horizon_collection_lease_plan_sha_mismatch")
    if not str(payload.get("lease_id") or "").strip():
        raise ValueError("runtime_horizon_collection_lease_id_missing")
    if type(payload.get("pid")) is not int or int(payload["pid"]) <= 0:
        raise ValueError("runtime_horizon_collection_lease_pid_invalid")
    _parse_utc(payload.get("acquired_at"), field="acquired_at")
    _parse_utc(payload.get("heartbeat_at"), field="heartbeat_at")
    return dict(payload)


def acquire_runtime_horizon_collection_lease(
    root: str | Path,
    *,
    plan: Mapping[str, Any],
    acquired_at: str,
    pid: int | None = None,
    lease_id: str | None = None,
) -> Mapping[str, Any]:
    validate_runtime_horizon_collection_plan(plan)
    path = runtime_horizon_collection_lease_path(root, plan=plan)
    path.parent.mkdir(parents=True, exist_ok=True)
    normalized_pid = int(os.getpid() if pid is None else pid)
    if normalized_pid <= 0:
        raise ValueError("runtime_horizon_collection_lease_pid_invalid")
    acquired = _utc_text(_parse_utc(acquired_at, field="acquired_at"))
    normalized_lease_id = str(lease_id or secrets.token_hex(16)).strip()
    if not normalized_lease_id:
        raise ValueError("runtime_horizon_collection_lease_id_missing")
    payload = {
        "schema_version": LEASE_SCHEMA_VERSION,
        "artifact_kind": "market_regime_runtime_horizon_collection_producer_lease",
        "collection_id": plan["collection_id"],
        "plan_sha256": plan["plan_sha256"],
        "lease_id": normalized_lease_id,
        "pid": normalized_pid,
        "acquired_at": acquired,
        "heartbeat_at": acquired,
        "released": False,
        "writer_registered": False,
        "scheduler_enabled": False,
        "detached_process_started": False,
        "writes_dhot": False,
    }
    encoded = (json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")
    try:
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL)
    except FileExistsError as exc:
        existing = read_runtime_horizon_collection_lease(root, plan=plan)
        raise FileExistsError(
            "runtime_horizon_collection_lease_already_held:"
            f"{existing.get('lease_id', '')}:{existing.get('pid', '')}"
        ) from exc
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(encoded)
            handle.flush()
            os.fsync(handle.fileno())
    except Exception:
        path.unlink(missing_ok=True)
        raise
    return dict(payload)


def heartbeat_runtime_horizon_collection_lease(
    root: str | Path,
    *,
    plan: Mapping[str, Any],
    lease_id: str,
    heartbeat_at: str,
    pid: int | None = None,
) -> Mapping[str, Any]:
    path = runtime_horizon_collection_lease_path(root, plan=plan)
    existing = read_runtime_horizon_collection_lease(root, plan=plan)
    if not existing:
        raise FileNotFoundError("runtime_horizon_collection_lease_missing")
    if existing["lease_id"] != str(lease_id):
        raise PermissionError("runtime_horizon_collection_lease_id_mismatch")
    expected_pid = int(os.getpid() if pid is None else pid)
    if existing["pid"] != expected_pid:
        raise PermissionError("runtime_horizon_collection_lease_pid_mismatch")
    heartbeat = _parse_utc(heartbeat_at, field="heartbeat_at")
    previous = _parse_utc(existing["heartbeat_at"], field="heartbeat_at")
    if heartbeat < previous:
        raise ValueError("runtime_horizon_collection_lease_heartbeat_regressed")
    updated = {**existing, "heartbeat_at": _utc_text(heartbeat)}
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(updated, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    tmp.replace(path)
    return updated


def release_runtime_horizon_collection_lease(
    root: str | Path,
    *,
    plan: Mapping[str, Any],
    lease_id: str,
    pid: int | None = None,
) -> Mapping[str, Any]:
    path = runtime_horizon_collection_lease_path(root, plan=plan)
    existing = read_runtime_horizon_collection_lease(root, plan=plan)
    if not existing:
        return {"ok": True, "already_released": True, "writer_invoked": False, "writes_dhot": False}
    if existing["lease_id"] != str(lease_id):
        raise PermissionError("runtime_horizon_collection_lease_id_mismatch")
    expected_pid = int(os.getpid() if pid is None else pid)
    if existing["pid"] != expected_pid:
        raise PermissionError("runtime_horizon_collection_lease_pid_mismatch")
    path.unlink()
    return {"ok": True, "already_released": False, "lease_id": lease_id, "writer_invoked": False, "writes_dhot": False}


def recover_stale_runtime_horizon_collection_lease(
    root: str | Path,
    *,
    plan: Mapping[str, Any],
    expected_lease_id: str,
    observed_at: str,
    minimum_stale_sec: int,
) -> Mapping[str, Any]:
    if type(minimum_stale_sec) is not int or minimum_stale_sec < 120:
        raise ValueError("runtime_horizon_collection_lease_minimum_stale_sec_invalid")
    path = runtime_horizon_collection_lease_path(root, plan=plan)
    existing = read_runtime_horizon_collection_lease(root, plan=plan)
    if not existing:
        return {"ok": True, "already_absent": True, "writer_invoked": False, "writes_dhot": False}
    if existing["lease_id"] != str(expected_lease_id):
        raise PermissionError("runtime_horizon_collection_lease_expected_id_mismatch")
    observed = _parse_utc(observed_at, field="observed_at")
    heartbeat = _parse_utc(existing["heartbeat_at"], field="heartbeat_at")
    age_sec = int((observed - heartbeat).total_seconds())
    if age_sec < minimum_stale_sec:
        raise PermissionError(f"runtime_horizon_collection_lease_not_stale:{age_sec}")
    path.unlink()
    return {
        "ok": True,
        "already_absent": False,
        "recovered_lease_id": existing["lease_id"],
        "recovered_pid": existing["pid"],
        "stale_age_sec": age_sec,
        "writer_invoked": False,
        "writes_dhot": False,
    }
