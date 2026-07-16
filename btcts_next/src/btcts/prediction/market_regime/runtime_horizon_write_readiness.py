# path: ./btcts_next/src/btcts/prediction/market_regime/runtime_horizon_write_readiness.py
# desc: MR-F9.19F build-only D-hot write-readiness report for canonical horizon artifacts. No writes.

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from btcts.prediction.market_regime.runtime_horizon_persistence_plan import (
    EXPECTED_HORIZONS,
    RUNTIME_HORIZON_NAMESPACE,
    RUNTIME_HORIZON_PERSISTENCE_PLAN_VERSION,
)

RUNTIME_HORIZON_WRITE_READINESS_VERSION = (
    "prediction.market_regime.runtime_horizon_write_readiness.mr_f9_19f.v1"
)


def _canonical_text(payload: Mapping[str, Any]) -> str:
    return json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ) + "\n"


def _safe_relpath(value: Any) -> str:
    relpath = str(value or "")
    path = Path(relpath)
    if (
        not relpath.startswith(RUNTIME_HORIZON_NAMESPACE + "/date=")
        or path.is_absolute()
        or ".." in path.parts
        or "\\" in relpath
    ):
        raise ValueError("runtime_horizon_write_readiness_relpath_invalid")
    return relpath


def _path_state(path: Path, expected_text: str) -> str:
    if not path.exists():
        return "missing"
    existing = path.read_text(encoding="utf-8-sig")
    return "duplicate" if existing == expected_text else "conflict"


def build_runtime_horizon_write_readiness_report(
    *,
    preflight: Mapping[str, Any],
    destination_root: str | Path,
    operator_id: str,
    enabled_acknowledged: bool = False,
    once_acknowledged: bool = False,
) -> Mapping[str, Any]:
    if not isinstance(preflight, Mapping):
        raise ValueError("runtime_horizon_write_readiness_preflight_invalid")
    if type(enabled_acknowledged) is not bool or type(once_acknowledged) is not bool:
        raise ValueError("runtime_horizon_write_readiness_ack_flags_invalid")

    operator = str(operator_id).strip()
    destination = Path(destination_root).resolve()
    preflight_root = Path(str(preflight.get("hot_root") or "")).resolve()
    if destination != preflight_root:
        raise ValueError("runtime_horizon_write_readiness_destination_root_mismatch")

    artifact = preflight.get("runtime_horizon_artifact")
    plan = preflight.get("runtime_horizon_persistence_plan")
    if not isinstance(artifact, Mapping):
        raise ValueError("runtime_horizon_write_readiness_artifact_invalid")
    if not isinstance(plan, Mapping):
        raise ValueError("runtime_horizon_write_readiness_plan_invalid")
    if preflight.get("runtime_horizon_artifact_built") is not True:
        raise ValueError("runtime_horizon_write_readiness_artifact_not_built")
    if preflight.get("runtime_horizon_persistence_plan_built") is not True:
        raise ValueError("runtime_horizon_write_readiness_plan_not_built")

    for key in (
        "runtime_horizon_artifact_persisted",
        "runtime_horizon_writer_registered",
        "writer_invoked",
        "writes_dhot",
        "scheduler_enabled",
        "producer_loop_enabled",
        "broker_private_api_allowed",
        "autotrade_trigger_allowed",
        "order_submission_allowed",
        "auto_promotion_allowed",
        "live_parameter_apply_allowed",
    ):
        if preflight.get(key) is not False:
            raise ValueError(f"runtime_horizon_write_readiness_preflight_safety_invalid:{key}")

    if plan.get("schema_version") != RUNTIME_HORIZON_PERSISTENCE_PLAN_VERSION:
        raise ValueError("runtime_horizon_write_readiness_plan_schema_invalid")
    if int(plan.get("horizon_count") or -1) != 8:
        raise ValueError("runtime_horizon_write_readiness_horizon_count_invalid")
    if plan.get("writer_registered") is not False or plan.get("would_write") is not False:
        raise ValueError("runtime_horizon_write_readiness_plan_activation_invalid")

    rows = artifact.get("horizons")
    if not isinstance(rows, (tuple, list)) or len(rows) != 8:
        raise ValueError("runtime_horizon_write_readiness_horizons_invalid")
    horizons = [int(row.get("horizon_sec")) for row in rows if isinstance(row, Mapping)]
    if horizons != list(EXPECTED_HORIZONS):
        raise ValueError("runtime_horizon_write_readiness_horizon_identity_invalid")

    source_checks = []
    for row in rows:
        if not isinstance(row, Mapping):
            raise ValueError("runtime_horizon_write_readiness_horizon_row_invalid")
        current = row.get("source_currentness_verified") is True
        freshness = str(row.get("source_freshness_state") or "")
        live = current and freshness == "LIVE"
        source_checks.append({
            "horizon_sec": int(row["horizon_sec"]),
            "source_timestamp": str(row.get("source_timestamp") or ""),
            "source_currentness_verified": current,
            "source_freshness_state": freshness,
            "ready": live,
        })

    artifact_rows = plan.get("horizon_artifacts")
    if not isinstance(artifact_rows, (tuple, list)) or len(artifact_rows) != 8:
        raise ValueError("runtime_horizon_write_readiness_plan_artifacts_invalid")

    destination_checks = []
    for item in artifact_rows:
        if not isinstance(item, Mapping) or not isinstance(item.get("payload"), Mapping):
            raise ValueError("runtime_horizon_write_readiness_plan_artifact_invalid")
        relpath = _safe_relpath(item.get("artifact_relpath"))
        state = _path_state(destination / relpath, _canonical_text(item["payload"]))
        destination_checks.append({
            "horizon_sec": int(item["horizon_sec"]),
            "artifact_relpath": relpath,
            "state": state,
        })

    manifest_relpath = _safe_relpath(plan.get("manifest_relpath"))
    manifest_payload = plan.get("manifest_payload")
    if not isinstance(manifest_payload, Mapping):
        raise ValueError("runtime_horizon_write_readiness_manifest_invalid")
    destination_checks.append({
        "horizon_sec": None,
        "artifact_relpath": manifest_relpath,
        "state": _path_state(destination / manifest_relpath, _canonical_text(manifest_payload)),
    })

    write_order = tuple(str(item) for item in (plan.get("write_order") or ()))
    expected_order = tuple(item["artifact_relpath"] for item in destination_checks)
    if write_order != expected_order or write_order[-1] != manifest_relpath:
        raise ValueError("runtime_horizon_write_readiness_write_order_invalid")

    blockers = []
    if not operator:
        blockers.append("operator_id_missing")
    if enabled_acknowledged is not True:
        blockers.append("enabled_ack_missing")
    if once_acknowledged is not True:
        blockers.append("once_ack_missing")
    stale = [item["horizon_sec"] for item in source_checks if item["ready"] is not True]
    if stale:
        blockers.append("source_not_current:" + ",".join(str(item) for item in stale))
    conflicts = [item["artifact_relpath"] for item in destination_checks if item["state"] == "conflict"]
    if conflicts:
        blockers.append("destination_conflict:" + ",".join(conflicts))

    state_counts = {
        state: sum(item["state"] == state for item in destination_checks)
        for state in ("missing", "duplicate", "conflict")
    }
    return {
        "schema_version": RUNTIME_HORIZON_WRITE_READINESS_VERSION,
        "artifact_kind": "market_regime_runtime_horizon_write_readiness_report",
        "destination_root": str(destination),
        "prediction_origin": str(plan.get("prediction_origin") or ""),
        "run_id": str(plan.get("run_id") or ""),
        "operator_id": operator,
        "enabled_acknowledged": enabled_acknowledged,
        "once_acknowledged": once_acknowledged,
        "source_checks": tuple(source_checks),
        "destination_checks": tuple(destination_checks),
        "destination_state_counts": state_counts,
        "manifest_written_last_planned": True,
        "ready": not blockers,
        "blockers": tuple(blockers),
        "build_only": True,
        "writer_invoked": False,
        "writes_dhot": False,
        "writer_registered": False,
        "latest_pointer_created": False,
        "scheduler_enabled": False,
        "producer_loop_enabled": False,
        "websocket_opened": False,
        "ui_inference_allowed": False,
        "ui_confidence_recalculation_allowed": False,
        "broker_private_api_allowed": False,
        "autotrade_trigger_allowed": False,
        "order_submission_allowed": False,
    }
