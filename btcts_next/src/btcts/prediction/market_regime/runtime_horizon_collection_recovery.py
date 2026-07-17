# path: ./btcts_next/src/btcts/prediction/market_regime/runtime_horizon_collection_recovery.py
# desc: MR-F9.19L read-only recovery of completed runtime-horizon runs from destination manifests.

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from .runtime_horizon_collection_contract import validate_runtime_horizon_collection_plan
from .runtime_horizon_collection_state import (
    advance_runtime_horizon_collection_state,
    validate_runtime_horizon_collection_state,
)

EXPECTED_HORIZONS = (0, 300, 900, 1800, 3600, 21600, 43200, 86400)


def _parse_utc(value: Any, *, field: str) -> datetime:
    text = str(value or "").strip()
    if not text:
        raise ValueError(f"runtime_horizon_collection_recovery_{field}_required")
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError as exc:
        raise ValueError(f"runtime_horizon_collection_recovery_{field}_invalid") from exc
    if parsed.tzinfo is None:
        raise ValueError(f"runtime_horizon_collection_recovery_{field}_timezone_required")
    return parsed.astimezone(timezone.utc).replace(microsecond=0)


def _canonical_digest(payload: Mapping[str, Any]) -> str:
    text = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _read_mapping(path: Path) -> Mapping[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(payload, Mapping):
        raise ValueError(f"runtime_horizon_collection_recovery_payload_invalid:{path}")
    return payload


def inspect_runtime_horizon_run_manifest(
    destination_root: str | Path,
    *,
    manifest_path: str | Path,
) -> Mapping[str, Any]:
    destination = Path(destination_root).resolve()
    manifest_file = Path(manifest_path).resolve()
    try:
        manifest_relpath = str(manifest_file.relative_to(destination)).replace("\\", "/")
    except ValueError as exc:
        raise ValueError("runtime_horizon_collection_recovery_manifest_outside_destination") from exc

    manifest = _read_mapping(manifest_file)
    if manifest.get("artifact_kind") != "market_regime_runtime_horizon_run_manifest":
        raise ValueError("runtime_horizon_collection_recovery_manifest_kind_invalid")
    if manifest.get("prediction_family_id") != "market_regime":
        raise ValueError("runtime_horizon_collection_recovery_prediction_family_invalid")
    if manifest.get("latest_pointer_relpath") is not None:
        raise ValueError("runtime_horizon_collection_recovery_latest_pointer_forbidden")
    if manifest.get("canonical_latest_replacement") is not False:
        raise ValueError("runtime_horizon_collection_recovery_canonical_replacement_forbidden")
    for key in (
        "ui_inference_allowed",
        "ui_confidence_recalculation_allowed",
    ):
        if manifest.get(key) is not False:
            raise ValueError(f"runtime_horizon_collection_recovery_manifest_safety_invalid:{key}")
    if manifest.get("read_only") is not True or manifest.get("non_executing") is not True:
        raise ValueError("runtime_horizon_collection_recovery_manifest_read_only_invalid")

    run_id = str(manifest.get("run_id") or "").strip()
    prediction_origin = str(manifest.get("prediction_origin") or "").strip()
    if not run_id or not prediction_origin:
        raise ValueError("runtime_horizon_collection_recovery_manifest_identity_missing")
    refs = manifest.get("horizon_artifacts")
    if not isinstance(refs, list) or len(refs) != 8:
        raise ValueError("runtime_horizon_collection_recovery_manifest_refs_invalid")

    verified = []
    future_source_timestamps: set[str] = set()
    for expected_horizon, ref in zip(EXPECTED_HORIZONS, refs):
        if not isinstance(ref, Mapping) or int(ref.get("horizon_sec") or 0) != expected_horizon:
            raise ValueError("runtime_horizon_collection_recovery_horizon_order_invalid")
        relpath = str(ref.get("artifact_relpath") or "").strip()
        path = (destination / relpath).resolve()
        try:
            path.relative_to(destination)
        except ValueError as exc:
            raise ValueError("runtime_horizon_collection_recovery_artifact_outside_destination") from exc
        if not path.exists():
            raise FileNotFoundError(f"runtime_horizon_collection_recovery_artifact_missing:{relpath}")
        payload = _read_mapping(path)
        digest = _canonical_digest(payload)
        if digest != str(ref.get("payload_sha256") or ""):
            raise ValueError(f"runtime_horizon_collection_recovery_payload_digest_mismatch:{relpath}")
        if payload.get("run_id") != run_id or payload.get("prediction_origin") != prediction_origin:
            raise ValueError(f"runtime_horizon_collection_recovery_payload_identity_mismatch:{relpath}")
        if int(payload.get("horizon_sec") or 0) != expected_horizon:
            raise ValueError(f"runtime_horizon_collection_recovery_payload_horizon_mismatch:{relpath}")
        horizon = payload.get("horizon")
        if not isinstance(horizon, Mapping):
            raise ValueError(f"runtime_horizon_collection_recovery_horizon_payload_invalid:{relpath}")
        if str(horizon.get("trace_id") or "") != str(ref.get("trace_id") or ""):
            raise ValueError(f"runtime_horizon_collection_recovery_trace_id_mismatch:{relpath}")
        for key in ("ui_inference_allowed", "ui_confidence_recalculation_allowed"):
            if payload.get(key) is not False:
                raise ValueError(f"runtime_horizon_collection_recovery_payload_safety_invalid:{key}:{relpath}")
        if payload.get("read_only") is not True or payload.get("non_executing") is not True:
            raise ValueError(f"runtime_horizon_collection_recovery_payload_read_only_invalid:{relpath}")
        source_timestamp = str(horizon.get("source_timestamp") or "").strip()
        if expected_horizon > 0:
            if not source_timestamp:
                raise ValueError(f"runtime_horizon_collection_recovery_source_timestamp_missing:{relpath}")
            future_source_timestamps.add(source_timestamp)
        verified.append(
            {
                "horizon_sec": expected_horizon,
                "artifact_relpath": relpath,
                "payload_sha256": digest,
                "trace_id": str(ref.get("trace_id") or ""),
                "source_timestamp": source_timestamp,
            }
        )

    if len(future_source_timestamps) != 1:
        raise ValueError("runtime_horizon_collection_recovery_closed_source_identity_invalid")
    closed_source_timestamp = next(iter(future_source_timestamps))
    run_dir = manifest_file.parent
    json_files = sorted(path.name for path in run_dir.glob("*.json"))
    if len(json_files) != 9 or "manifest.json" not in json_files:
        raise ValueError("runtime_horizon_collection_recovery_run_file_set_invalid")
    if (run_dir / "latest.json").exists():
        raise ValueError("runtime_horizon_collection_recovery_latest_pointer_exists")

    return {
        "artifact_kind": "market_regime_runtime_horizon_recovered_run",
        "run_id": run_id,
        "prediction_origin": prediction_origin,
        "closed_source_timestamp": closed_source_timestamp,
        "manifest_relpath": manifest_relpath,
        "verified_horizon_count": len(verified),
        "json_file_count": len(json_files),
        "horizon_artifacts": verified,
        "manifest_semantics_verified": True,
        "payload_digests_verified": True,
        "latest_pointer_exists": False,
        "read_only": True,
        "non_executing": True,
        "writer_invoked": False,
        "writes_dhot": False,
    }


def recover_runtime_horizon_collection_runs(
    destination_root: str | Path,
    *,
    plan: Mapping[str, Any],
) -> Mapping[str, Any]:
    validate_runtime_horizon_collection_plan(plan)
    destination = Path(destination_root).resolve()
    if destination != Path(str(plan["destination_root"])).resolve():
        raise ValueError("runtime_horizon_collection_recovery_destination_mismatch")
    start = _parse_utc(plan["planned_start_utc"], field="planned_start_utc")
    end = _parse_utc(plan["planned_end_utc"], field="planned_end_utc")
    base = destination / "prediction/market_regime/runtime_horizons"
    manifests = sorted(base.glob("date=*/runs/run-*/manifest.json")) if base.exists() else []

    recovered = []
    by_closed_source: dict[str, Mapping[str, Any]] = {}
    ignored_outside_window = 0
    for manifest_path in manifests:
        run = inspect_runtime_horizon_run_manifest(
            destination,
            manifest_path=manifest_path,
        )
        origin = _parse_utc(run["prediction_origin"], field="prediction_origin")
        if origin < start or origin >= end:
            ignored_outside_window += 1
            continue
        closed_source = str(run["closed_source_timestamp"])
        existing = by_closed_source.get(closed_source)
        if existing is not None and existing["run_id"] != run["run_id"]:
            raise ValueError(
                "runtime_horizon_collection_recovery_closed_source_conflict:"
                f"{closed_source}:{existing['run_id']}:{run['run_id']}"
            )
        by_closed_source[closed_source] = run
        recovered.append(run)

    recovered.sort(key=lambda item: (item["closed_source_timestamp"], item["prediction_origin"], item["run_id"]))
    return {
        "artifact_kind": "market_regime_runtime_horizon_collection_recovery_report",
        "collection_id": plan["collection_id"],
        "plan_sha256": plan["plan_sha256"],
        "destination_root": str(destination),
        "manifest_scan_count": len(manifests),
        "ignored_outside_window_count": ignored_outside_window,
        "recovered_run_count": len(recovered),
        "recovered_closed_source_count": len(by_closed_source),
        "recovered_runs": recovered,
        "closed_source_timestamps": sorted(by_closed_source),
        "writer_invoked": False,
        "writes_dhot": False,
        "latest_pointer_created": False,
        "scheduler_enabled": False,
        "producer_loop_enabled": False,
        "websocket_opened": False,
        "ui_inference_allowed": False,
        "ui_confidence_recalculation_allowed": False,
        "order_submission_allowed": False,
    }

def merge_runtime_horizon_collection_recovery_into_state(
    *,
    plan: Mapping[str, Any],
    state: Mapping[str, Any],
    recovery_report: Mapping[str, Any],
    observed_at: str,
) -> Mapping[str, Any]:
    validate_runtime_horizon_collection_plan(plan)
    validate_runtime_horizon_collection_state(plan=plan, state=state)
    if recovery_report.get("collection_id") != plan.get("collection_id"):
        raise ValueError("runtime_horizon_collection_recovery_state_collection_id_mismatch")
    if recovery_report.get("plan_sha256") != plan.get("plan_sha256"):
        raise ValueError("runtime_horizon_collection_recovery_state_plan_sha_mismatch")
    if recovery_report.get("writer_invoked") is not False or recovery_report.get("writes_dhot") is not False:
        raise ValueError("runtime_horizon_collection_recovery_state_report_safety_invalid")

    merged = dict(state)
    known_origins = set(merged.get("completed_prediction_origins") or ())
    known_closed = set(merged.get("completed_closed_source_timestamps") or ())
    recovered_count = 0
    for run in recovery_report.get("recovered_runs") or ():
        if not isinstance(run, Mapping):
            raise ValueError("runtime_horizon_collection_recovery_state_run_invalid")
        origin = str(run.get("prediction_origin") or "").strip()
        closed_source = str(run.get("closed_source_timestamp") or "").strip()
        run_id = str(run.get("run_id") or "").strip()
        if not origin or not closed_source or not run_id:
            raise ValueError("runtime_horizon_collection_recovery_state_run_identity_missing")
        if origin in known_origins or closed_source in known_closed:
            continue
        merged = dict(
            advance_runtime_horizon_collection_state(
                plan=plan,
                previous=merged,
                event="WRITE_OK",
                observed_at=observed_at,
                prediction_origin=origin,
                closed_source_timestamp=closed_source,
                run_id=run_id,
            )
        )
        known_origins.add(origin)
        known_closed.add(closed_source)
        recovered_count += 1

    return {
        "state": merged,
        "recovered_state_entry_count": recovered_count,
        "writer_invoked": False,
        "writes_dhot": False,
    }
