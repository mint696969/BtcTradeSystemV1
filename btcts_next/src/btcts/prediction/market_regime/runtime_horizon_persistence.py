# path: ./btcts_next/src/btcts/prediction/market_regime/runtime_horizon_persistence.py
# desc: MR-F9.19C explicit once-only atomic writer for canonical 8-horizon artifacts and run manifest.

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from btcts.core.io import atomic_write_text, file_lock
from btcts.prediction.market_regime.runtime_horizon_persistence_plan import (
    EXPECTED_HORIZONS,
    RUNTIME_HORIZON_NAMESPACE,
    RUNTIME_HORIZON_PERSISTENCE_PLAN_VERSION,
)


def _canonical_text(payload: Mapping[str, Any]) -> str:
    return json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ) + "\n"


def _digest(payload: Mapping[str, Any]) -> str:
    return hashlib.sha256(_canonical_text(payload).rstrip("\n").encode("utf-8")).hexdigest()


def _safe_relpath(value: Any, *, expected_suffix: str | None = None) -> str:
    relpath = str(value or "")
    path = Path(relpath)
    if (
        not relpath.startswith(RUNTIME_HORIZON_NAMESPACE + "/date=")
        or path.is_absolute()
        or ".." in path.parts
        or "\\" in relpath
    ):
        raise ValueError("runtime_horizon_persistence_relpath_invalid")
    if expected_suffix is not None and not relpath.endswith(expected_suffix):
        raise ValueError("runtime_horizon_persistence_relpath_suffix_invalid")
    return relpath


def _validate_plan(plan: Mapping[str, Any]) -> tuple[tuple[dict[str, Any], ...], dict[str, Any]]:
    if not isinstance(plan, Mapping):
        raise ValueError("runtime_horizon_persistence_plan_invalid")
    if plan.get("schema_version") != RUNTIME_HORIZON_PERSISTENCE_PLAN_VERSION:
        raise ValueError("runtime_horizon_persistence_plan_schema_invalid")
    if plan.get("artifact_kind") != "market_regime_runtime_horizon_persistence_plan":
        raise ValueError("runtime_horizon_persistence_plan_kind_invalid")
    if plan.get("source_role") != "hot_data_root":
        raise ValueError("runtime_horizon_persistence_plan_role_invalid")
    if plan.get("namespace") != RUNTIME_HORIZON_NAMESPACE:
        raise ValueError("runtime_horizon_persistence_plan_namespace_invalid")
    if int(plan.get("horizon_count") or -1) != 8:
        raise ValueError("runtime_horizon_persistence_plan_horizon_count_invalid")

    expected_false = (
        "writer_registered",
        "would_write",
        "latest_pointer_created",
        "canonical_latest_replacement",
        "scheduler_enabled",
        "producer_loop_enabled",
        "websocket_opened",
        "broker_private_api_allowed",
        "autotrade_trigger_allowed",
        "order_submission_allowed",
    )
    if plan.get("disabled_by_default") is not True:
        raise ValueError("runtime_horizon_persistence_plan_safety_invalid:disabled_by_default")
    for key in expected_false:
        if plan.get(key) is not False:
            raise ValueError(f"runtime_horizon_persistence_plan_safety_invalid:{key}")

    atomic = plan.get("atomic_write_contract")
    if not isinstance(atomic, Mapping) or dict(atomic) != {
        "lock_required": True,
        "lock_timeout_sec": 5.0,
        "stale_lock_sec": 60.0,
        "temporary_suffix": ".tmp",
        "replace_operation": "atomic_replace",
        "manifest_written_last": True,
    }:
        raise ValueError("runtime_horizon_persistence_atomic_contract_invalid")

    rows_raw = plan.get("horizon_artifacts")
    if not isinstance(rows_raw, (tuple, list)) or len(rows_raw) != 8:
        raise ValueError("runtime_horizon_persistence_plan_artifacts_invalid")
    rows: list[dict[str, Any]] = []
    for index, item in enumerate(rows_raw):
        if not isinstance(item, Mapping):
            raise ValueError("runtime_horizon_persistence_plan_artifact_row_invalid")
        horizon = int(item.get("horizon_sec"))
        if horizon != EXPECTED_HORIZONS[index]:
            raise ValueError("runtime_horizon_persistence_plan_horizon_identity_invalid")
        trace_id = str(item.get("trace_id") or "")
        if not trace_id:
            raise ValueError("runtime_horizon_persistence_plan_trace_identity_invalid")
        relpath = _safe_relpath(item.get("artifact_relpath"), expected_suffix=f"/horizon={horizon}.json")
        payload = item.get("payload")
        if not isinstance(payload, Mapping):
            raise ValueError("runtime_horizon_persistence_plan_payload_invalid")
        if payload.get("schema_version") != RUNTIME_HORIZON_PERSISTENCE_PLAN_VERSION:
            raise ValueError("runtime_horizon_persistence_payload_schema_invalid")
        if payload.get("artifact_kind") != "market_regime_runtime_horizon":
            raise ValueError("runtime_horizon_persistence_payload_kind_invalid")
        if int(payload.get("horizon_sec")) != horizon:
            raise ValueError("runtime_horizon_persistence_payload_horizon_mismatch")
        horizon_payload = payload.get("horizon")
        if not isinstance(horizon_payload, Mapping):
            raise ValueError("runtime_horizon_persistence_horizon_payload_invalid")
        if str(horizon_payload.get("trace_id") or "") != trace_id:
            raise ValueError("runtime_horizon_persistence_payload_trace_mismatch")
        for key, expected in (
            ("ui_inference_allowed", False),
            ("ui_confidence_recalculation_allowed", False),
            ("read_only", True),
            ("non_executing", True),
        ):
            if payload.get(key) is not expected:
                raise ValueError(f"runtime_horizon_persistence_payload_safety_invalid:{key}")
        digest = str(item.get("payload_sha256") or "")
        if digest != _digest(payload):
            raise ValueError("runtime_horizon_persistence_payload_digest_mismatch")
        rows.append({
            "horizon_sec": horizon,
            "trace_id": trace_id,
            "artifact_relpath": relpath,
            "payload_sha256": digest,
            "payload": dict(payload),
        })

    if len({row["trace_id"] for row in rows}) != 8:
        raise ValueError("runtime_horizon_persistence_plan_trace_identity_invalid")
    if len({row["artifact_relpath"] for row in rows}) != 8:
        raise ValueError("runtime_horizon_persistence_plan_artifact_path_duplicate")

    manifest_relpath = _safe_relpath(plan.get("manifest_relpath"), expected_suffix="/manifest.json")
    manifest = plan.get("manifest_payload")
    if not isinstance(manifest, Mapping):
        raise ValueError("runtime_horizon_persistence_manifest_invalid")
    if manifest.get("schema_version") != RUNTIME_HORIZON_PERSISTENCE_PLAN_VERSION:
        raise ValueError("runtime_horizon_persistence_manifest_schema_invalid")
    if manifest.get("artifact_kind") != "market_regime_runtime_horizon_run_manifest":
        raise ValueError("runtime_horizon_persistence_manifest_kind_invalid")
    if int(manifest.get("horizon_count") or -1) != 8:
        raise ValueError("runtime_horizon_persistence_manifest_horizon_count_invalid")
    if manifest.get("latest_pointer_relpath") is not None:
        raise ValueError("runtime_horizon_persistence_manifest_latest_pointer_invalid")
    for key, expected in (
        ("canonical_latest_replacement", False),
        ("ui_inference_allowed", False),
        ("ui_confidence_recalculation_allowed", False),
        ("read_only", True),
        ("non_executing", True),
    ):
        if manifest.get(key) is not expected:
            raise ValueError(f"runtime_horizon_persistence_manifest_safety_invalid:{key}")

    refs = manifest.get("horizon_artifacts")
    if not isinstance(refs, (tuple, list)) or len(refs) != 8:
        raise ValueError("runtime_horizon_persistence_manifest_refs_invalid")
    expected_refs = [
        {
            "horizon_sec": row["horizon_sec"],
            "trace_id": row["trace_id"],
            "artifact_relpath": row["artifact_relpath"],
            "payload_sha256": row["payload_sha256"],
        }
        for row in rows
    ]
    if [dict(item) for item in refs] != expected_refs:
        raise ValueError("runtime_horizon_persistence_manifest_refs_mismatch")
    if str(plan.get("manifest_payload_sha256") or "") != _digest(manifest):
        raise ValueError("runtime_horizon_persistence_manifest_digest_mismatch")

    write_order = tuple(str(item) for item in (plan.get("write_order") or ()))
    expected_order = tuple(row["artifact_relpath"] for row in rows) + (manifest_relpath,)
    if write_order != expected_order:
        raise ValueError("runtime_horizon_persistence_write_order_invalid")

    return tuple(rows), {
        "artifact_relpath": manifest_relpath,
        "payload_sha256": str(plan["manifest_payload_sha256"]),
        "payload": dict(manifest),
    }


def _existing_state(path: Path, expected_text: str) -> str:
    if not path.exists():
        return "missing"
    existing = path.read_text(encoding="utf-8-sig")
    return "duplicate" if existing == expected_text else "conflict"


def persist_runtime_horizon_plan_once(
    root: str | Path,
    *,
    plan: Mapping[str, Any],
    enabled: bool = False,
    once: bool = False,
) -> Mapping[str, Any]:
    if type(enabled) is not bool or type(once) is not bool:
        raise ValueError("runtime_horizon_persistence_flags_invalid")
    if enabled is not True:
        raise PermissionError("runtime_horizon_persistence_disabled_by_default")
    if once is not True:
        raise PermissionError("runtime_horizon_persistence_once_ack_required")

    rows, manifest = _validate_plan(plan)
    root_path = Path(root)
    manifest_path = root_path / manifest["artifact_relpath"]
    atomic = plan["atomic_write_contract"]

    payloads: list[tuple[str, Path, str]] = []
    for row in rows:
        payloads.append((row["artifact_relpath"], root_path / row["artifact_relpath"], _canonical_text(row["payload"])))
    manifest_text = _canonical_text(manifest["payload"])

    with file_lock(
        manifest_path,
        timeout_sec=float(atomic["lock_timeout_sec"]),
        stale_sec=float(atomic["stale_lock_sec"]),
    ):
        states = [(relpath, path, text, _existing_state(path, text)) for relpath, path, text in payloads]
        manifest_state = _existing_state(manifest_path, manifest_text)
        conflicts = [relpath for relpath, _, _, state in states if state == "conflict"]
        if manifest_state == "conflict":
            conflicts.append(manifest["artifact_relpath"])
        if conflicts:
            raise RuntimeError(
                "runtime_horizon_persistence_existing_conflict:" + ",".join(conflicts)
            )

        written_paths: list[str] = []
        duplicate_paths: list[str] = []
        for relpath, path, text, state in states:
            if state == "duplicate":
                duplicate_paths.append(relpath)
                continue
            atomic_write_text(path, text)
            written_paths.append(relpath)

        if manifest_state == "duplicate":
            duplicate_paths.append(manifest["artifact_relpath"])
        else:
            atomic_write_text(manifest_path, manifest_text)
            written_paths.append(manifest["artifact_relpath"])

    return {
        "written": bool(written_paths),
        "duplicate": not written_paths,
        "written_count": len(written_paths),
        "duplicate_count": len(duplicate_paths),
        "written_paths": tuple(written_paths),
        "duplicate_paths": tuple(duplicate_paths),
        "manifest_relpath": manifest["artifact_relpath"],
        "manifest_written_last": bool(written_paths) and written_paths[-1] == manifest["artifact_relpath"],
        "latest_pointer_created": False,
        "writer_registered": False,
        "producer_loop_enabled": False,
        "scheduler_enabled": False,
        "websocket_opened": False,
        "order_submission_allowed": False,
    }
