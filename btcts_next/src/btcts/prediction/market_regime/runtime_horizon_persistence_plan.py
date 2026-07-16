# path: ./btcts_next/src/btcts/prediction/market_regime/runtime_horizon_persistence_plan.py
# desc: MR-F9.19B pure build-only persistence ownership and atomic-write plan for canonical 8-horizon artifacts.

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any, Mapping

RUNTIME_HORIZON_PERSISTENCE_PLAN_VERSION = (
    "prediction.market_regime.runtime_horizon_persistence_plan.mr_f9_19b.v1"
)
RUNTIME_HORIZON_NAMESPACE = "prediction/market_regime/runtime_horizons"
EXPECTED_HORIZONS = (0, 300, 900, 1800, 3600, 21600, 43200, 86400)


def _canonical_utc(value: str, field: str) -> str:
    try:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(f"runtime_horizon_persistence_timestamp_invalid:{field}") from exc
    if parsed.tzinfo is None:
        raise ValueError(f"runtime_horizon_persistence_timestamp_timezone_missing:{field}")
    return (
        parsed.astimezone(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


def _safe_run_id(prediction_origin: str, digest: str) -> str:
    compact = prediction_origin.replace("-", "").replace(":", "")
    return f"run-{compact}-{digest[:12]}"


def _json_native(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {str(key): _json_native(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [_json_native(item) for item in value]
    return value


def _payload_digest(payload: Mapping[str, Any]) -> str:
    text = json.dumps(
        _json_native(payload),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _validate_runtime_artifact(artifact: Mapping[str, Any]) -> tuple[str, tuple[Mapping[str, Any], ...]]:
    if not isinstance(artifact, Mapping):
        raise ValueError("runtime_horizon_persistence_artifact_invalid")
    origin = _canonical_utc(str(artifact.get("prediction_origin") or ""), "prediction_origin")
    if int(artifact.get("horizon_count") or -1) != 8:
        raise ValueError("runtime_horizon_persistence_horizon_count_invalid")
    rows_raw = artifact.get("horizons")
    if not isinstance(rows_raw, (tuple, list)) or len(rows_raw) != 8:
        raise ValueError("runtime_horizon_persistence_horizons_invalid")
    rows = tuple(rows_raw)
    if any(not isinstance(row, Mapping) for row in rows):
        raise ValueError("runtime_horizon_persistence_horizon_row_invalid")
    horizons = tuple(int(row.get("horizon_sec")) for row in rows)
    if horizons != EXPECTED_HORIZONS:
        raise ValueError("runtime_horizon_persistence_horizon_identity_invalid")
    trace_ids = tuple(str(row.get("trace_id") or "") for row in rows)
    if any(not value for value in trace_ids) or len(trace_ids) != len(set(trace_ids)):
        raise ValueError("runtime_horizon_persistence_trace_identity_invalid")
    if any(str(row.get("prediction_origin") or "") != origin for row in rows):
        raise ValueError("runtime_horizon_persistence_origin_mismatch")
    if artifact.get("ui_inference_allowed") is not False:
        raise ValueError("runtime_horizon_persistence_ui_inference_boundary_invalid")
    if artifact.get("ui_confidence_recalculation_allowed") is not False:
        raise ValueError("runtime_horizon_persistence_ui_confidence_boundary_invalid")
    safety = artifact.get("safety") if isinstance(artifact.get("safety"), Mapping) else {}
    for key in (
        "writes_dhot",
        "scheduler_enabled",
        "producer_loop_enabled",
        "websocket_opened",
        "broker_private_api_allowed",
        "autotrade_trigger_allowed",
        "order_submission_allowed",
        "canonical_replacement",
    ):
        if safety.get(key) is not False:
            raise ValueError(f"runtime_horizon_persistence_safety_invalid:{key}")
    return origin, rows


def build_runtime_horizon_persistence_plan(
    *, artifact: Mapping[str, Any]
) -> Mapping[str, Any]:
    prediction_origin, rows = _validate_runtime_artifact(artifact)
    artifact_digest = _payload_digest(artifact)
    run_id = _safe_run_id(prediction_origin, artifact_digest)
    partition = prediction_origin[:10]
    run_prefix = f"{RUNTIME_HORIZON_NAMESPACE}/date={partition}/runs/{run_id}"

    horizon_artifacts = []
    for row in rows:
        horizon = int(row["horizon_sec"])
        relpath = f"{run_prefix}/horizon={horizon}.json"
        payload = {
            "schema_version": RUNTIME_HORIZON_PERSISTENCE_PLAN_VERSION,
            "artifact_kind": "market_regime_runtime_horizon",
            "prediction_family_id": "market_regime",
            "prediction_origin": prediction_origin,
            "run_id": run_id,
            "horizon_sec": horizon,
            "horizon": _json_native(row),
            "ui_inference_allowed": False,
            "ui_confidence_recalculation_allowed": False,
            "read_only": True,
            "non_executing": True,
        }
        horizon_artifacts.append({
            "horizon_sec": horizon,
            "trace_id": str(row["trace_id"]),
            "artifact_relpath": relpath,
            "payload_sha256": _payload_digest(payload),
            "payload": payload,
        })

    manifest_relpath = f"{run_prefix}/manifest.json"
    manifest_payload = {
        "schema_version": RUNTIME_HORIZON_PERSISTENCE_PLAN_VERSION,
        "artifact_kind": "market_regime_runtime_horizon_run_manifest",
        "prediction_family_id": "market_regime",
        "prediction_origin": prediction_origin,
        "run_id": run_id,
        "horizon_count": 8,
        "horizon_artifacts": [
            {
                "horizon_sec": item["horizon_sec"],
                "trace_id": item["trace_id"],
                "artifact_relpath": item["artifact_relpath"],
                "payload_sha256": item["payload_sha256"],
            }
            for item in horizon_artifacts
        ],
        "latest_pointer_relpath": None,
        "canonical_latest_replacement": False,
        "ui_inference_allowed": False,
        "ui_confidence_recalculation_allowed": False,
        "read_only": True,
        "non_executing": True,
    }
    write_order = tuple(
        item["artifact_relpath"] for item in horizon_artifacts
    ) + (manifest_relpath,)
    return {
        "schema_version": RUNTIME_HORIZON_PERSISTENCE_PLAN_VERSION,
        "artifact_kind": "market_regime_runtime_horizon_persistence_plan",
        "source_role": "hot_data_root",
        "namespace": RUNTIME_HORIZON_NAMESPACE,
        "prediction_origin": prediction_origin,
        "run_id": run_id,
        "horizon_count": 8,
        "horizon_artifacts": tuple(horizon_artifacts),
        "manifest_relpath": manifest_relpath,
        "manifest_payload_sha256": _payload_digest(manifest_payload),
        "manifest_payload": manifest_payload,
        "write_order": write_order,
        "atomic_write_contract": {
            "lock_required": True,
            "lock_timeout_sec": 5.0,
            "stale_lock_sec": 60.0,
            "temporary_suffix": ".tmp",
            "replace_operation": "atomic_replace",
            "manifest_written_last": True,
        },
        "disabled_by_default": True,
        "writer_registered": False,
        "would_write": False,
        "latest_pointer_created": False,
        "canonical_latest_replacement": False,
        "scheduler_enabled": False,
        "producer_loop_enabled": False,
        "websocket_opened": False,
        "broker_private_api_allowed": False,
        "autotrade_trigger_allowed": False,
        "order_submission_allowed": False,
    }
