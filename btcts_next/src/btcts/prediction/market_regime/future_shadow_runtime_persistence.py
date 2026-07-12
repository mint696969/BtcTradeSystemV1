# path: ./btcts_next/src/btcts/prediction/market_regime/future_shadow_runtime_persistence.py
# desc: MR-F5.16 disabled-by-default isolated trace persistence and expiry-gated observation polling boundary.

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

from btcts.core.io import atomic_write_text, file_lock
from .contracts import MarketRegimeCode
from .future_forecast_contract import FutureForecastStatus
from .future_shadow_outcome import FutureShadowOutcomeEvidence
from .future_trace_identity import MarketRegimeFutureTraceIdentity

RUNTIME_PERSISTENCE_VERSION = "prediction.market_regime.future_shadow_runtime_persistence.mr_f5_16.v1"
TRACE_NAMESPACE = "prediction/market_regime/future_shadow/runtime_traces"


def _parse_utc(value: str, error: str) -> datetime:
    if not isinstance(value, str) or not value.endswith("Z"):
        raise ValueError(error)
    try:
        parsed = datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError as exc:
        raise ValueError(error) from exc
    if parsed.tzinfo != timezone.utc or parsed.isoformat().replace("+00:00", "Z") != value:
        raise ValueError(error)
    return parsed


def _trace_payload(trace: MarketRegimeFutureTraceIdentity) -> dict[str, Any]:
    if not isinstance(trace, MarketRegimeFutureTraceIdentity):
        raise ValueError("future_shadow_runtime_persistence_trace_invalid")
    payload = trace.to_dict()
    if payload.get("contract_version") != "prediction.market_regime.future_trace_identity.mr_f5_5.v1":
        raise ValueError("future_shadow_runtime_persistence_trace_contract_invalid")
    return payload


def _trace_from_payload(row: Mapping[str, Any]) -> MarketRegimeFutureTraceIdentity:
    try:
        trace = MarketRegimeFutureTraceIdentity(
            trace_id=str(row.get("trace_id") or ""),
            origin_timestamp=str(row.get("origin_timestamp") or ""),
            expiry_at=str(row.get("expiry_at") or ""),
            target_horizon_sec=int(row.get("target_horizon_sec")),
            target_horizon_key=str(row.get("target_horizon_key") or ""),
            target_definition_version=str(row.get("target_definition_version") or ""),
            model_id=str(row.get("model_id") or ""),
            logic_version=str(row.get("logic_version") or ""),
            parameter_set_id=str(row.get("parameter_set_id") or ""),
            feature_snapshot_ref=str(row.get("feature_snapshot_ref") or ""),
            predicted_future_state=MarketRegimeCode(str(row.get("predicted_future_state") or "UNKNOWN")),
            forecast_status=FutureForecastStatus(str(row.get("forecast_status") or "")),
            contract_version=str(row.get("contract_version") or ""),
        )
    except (TypeError, ValueError) as exc:
        raise ValueError("future_shadow_runtime_persistence_plan_row_contract_invalid") from exc
    if trace.to_dict() != dict(row):
        raise ValueError("future_shadow_runtime_persistence_plan_row_contract_mismatch")
    return trace


def build_future_shadow_trace_persistence_plan(
    *, traces: Sequence[MarketRegimeFutureTraceIdentity], generated_at: str
) -> Mapping[str, Any]:
    _parse_utc(generated_at, "future_shadow_runtime_persistence_generated_at_invalid")
    rows = tuple(sorted((_trace_payload(item) for item in traces), key=lambda item: item["trace_id"]))
    if not rows:
        raise ValueError("future_shadow_runtime_persistence_traces_missing")
    trace_ids = tuple(row["trace_id"] for row in rows)
    if len(trace_ids) != len(set(trace_ids)):
        raise ValueError("future_shadow_runtime_persistence_trace_duplicate")
    if any(row["origin_timestamp"] != generated_at for row in rows):
        raise ValueError("future_shadow_runtime_persistence_origin_mismatch")
    digest = hashlib.sha256("|".join(trace_ids).encode("utf-8")).hexdigest()
    partition = generated_at[:10]
    relpath = f"{TRACE_NAMESPACE}/date={partition}/trace-set-{digest}.json"
    return {
        "schema_version": RUNTIME_PERSISTENCE_VERSION,
        "artifact_kind": "future_shadow_runtime_trace_set",
        "generated_at": generated_at,
        "source_role": "hot_data_root",
        "namespace": TRACE_NAMESPACE,
        "artifact_relpath": relpath,
        "trace_count": len(rows),
        "trace_ids": trace_ids,
        "rows": rows,
        "disabled_by_default": True,
        "scheduler_enabled": False,
        "writer_registered": False,
        "canonical_replacement": False,
        "would_write": False,
    }


def persist_future_shadow_traces_once(
    root: str | Path,
    *, plan: Mapping[str, Any], enabled: bool = False, once: bool = False
) -> Mapping[str, Any]:
    if type(enabled) is not bool or type(once) is not bool:
        raise ValueError("future_shadow_runtime_persistence_flags_invalid")
    if enabled is not True:
        raise PermissionError("future_shadow_runtime_persistence_disabled_by_default")
    if once is not True:
        raise PermissionError("future_shadow_runtime_persistence_once_ack_required")
    if plan.get("schema_version") != RUNTIME_PERSISTENCE_VERSION:
        raise ValueError("future_shadow_runtime_persistence_plan_schema_invalid")
    if plan.get("artifact_kind") != "future_shadow_runtime_trace_set":
        raise ValueError("future_shadow_runtime_persistence_plan_kind_invalid")
    if plan.get("source_role") != "hot_data_root" or plan.get("namespace") != TRACE_NAMESPACE:
        raise ValueError("future_shadow_runtime_persistence_plan_role_invalid")
    expected_safety = {
        "disabled_by_default": True,
        "scheduler_enabled": False,
        "writer_registered": False,
        "canonical_replacement": False,
        "would_write": False,
    }
    if any(plan.get(key) is not value for key, value in expected_safety.items()):
        raise ValueError("future_shadow_runtime_persistence_plan_safety_invalid")
    relpath = str(plan.get("artifact_relpath") or "")
    relpath_path = Path(relpath)
    if (
        not relpath.startswith(TRACE_NAMESPACE + "/date=")
        or relpath_path.is_absolute()
        or ".." in relpath_path.parts
        or "\\" in relpath
    ):
        raise ValueError("future_shadow_runtime_persistence_relpath_invalid")
    rows = tuple(plan.get("rows") or ())
    if not rows or any(not isinstance(item, Mapping) for item in rows):
        raise ValueError("future_shadow_runtime_persistence_plan_rows_invalid")
    validated_traces = tuple(_trace_from_payload(item) for item in rows)
    trace_ids = tuple(item.trace_id for item in validated_traces)
    if any(not item for item in trace_ids) or len(trace_ids) != len(set(trace_ids)):
        raise ValueError("future_shadow_runtime_persistence_plan_trace_ids_invalid")
    if tuple(plan.get("trace_ids") or ()) != trace_ids:
        raise ValueError("future_shadow_runtime_persistence_plan_trace_set_mismatch")
    if plan.get("trace_count") != len(rows):
        raise ValueError("future_shadow_runtime_persistence_plan_trace_count_mismatch")
    generated_at = str(plan.get("generated_at") or "")
    _parse_utc(generated_at, "future_shadow_runtime_persistence_generated_at_invalid")
    if any(str(item.get("origin_timestamp") or "") != generated_at for item in rows):
        raise ValueError("future_shadow_runtime_persistence_origin_mismatch")
    expected_digest = hashlib.sha256("|".join(trace_ids).encode("utf-8")).hexdigest()
    expected_relpath = (
        f"{TRACE_NAMESPACE}/date={generated_at[:10]}/trace-set-{expected_digest}.json"
    )
    if relpath != expected_relpath:
        raise ValueError("future_shadow_runtime_persistence_relpath_mismatch")
    payload = {
        key: plan[key]
        for key in (
            "schema_version", "artifact_kind", "generated_at", "source_role", "namespace",
            "trace_count", "trace_ids", "rows", "scheduler_enabled", "writer_registered",
            "canonical_replacement",
        )
    }
    text = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"
    path = Path(root) / relpath
    with file_lock(path, timeout_sec=5.0, stale_sec=60.0):
        if path.exists():
            existing = path.read_text(encoding="utf-8-sig")
            if existing != text:
                raise RuntimeError("future_shadow_runtime_persistence_existing_conflict")
            return {"written": False, "duplicate": True, "artifact_relpath": relpath}
        atomic_write_text(path, text)
    return {"written": True, "duplicate": False, "artifact_relpath": relpath}


def poll_future_shadow_observations(
    *,
    traces: Sequence[MarketRegimeFutureTraceIdentity],
    polled_at: str,
    observation_reader: Callable[[MarketRegimeFutureTraceIdentity, str], Mapping[str, Any] | None],
) -> Mapping[str, FutureShadowOutcomeEvidence]:
    effective = _parse_utc(polled_at, "future_shadow_runtime_poll_polled_at_invalid")
    if not callable(observation_reader):
        raise ValueError("future_shadow_runtime_poll_reader_invalid")
    trace_rows = tuple(traces)
    if not trace_rows:
        raise ValueError("future_shadow_runtime_poll_traces_missing")
    if any(not isinstance(item, MarketRegimeFutureTraceIdentity) for item in trace_rows):
        raise ValueError("future_shadow_runtime_poll_trace_invalid")
    trace_ids = tuple(item.trace_id for item in trace_rows)
    if len(trace_ids) != len(set(trace_ids)):
        raise ValueError("future_shadow_runtime_poll_trace_duplicate")
    result: dict[str, FutureShadowOutcomeEvidence] = {}
    for trace in sorted(trace_rows, key=lambda item: item.trace_id):
        expiry = _parse_utc(trace.expiry_at, "future_shadow_runtime_poll_expiry_invalid")
        if effective < expiry:
            continue
        raw = observation_reader(trace, polled_at)
        if raw is None:
            continue
        if not isinstance(raw, Mapping):
            raise ValueError("future_shadow_runtime_poll_observation_invalid")
        available = raw.get("observation_available")
        if type(available) is not bool:
            raise ValueError("future_shadow_runtime_poll_available_invalid")
        source_ref = str(raw.get("observation_source_ref") or "")
        observed_at = str(raw.get("observed_at") or polled_at) if available else ""
        observed_state_raw = raw.get("observed_future_state")
        try:
            observed_state = (
                observed_state_raw
                if isinstance(observed_state_raw, MarketRegimeCode)
                else MarketRegimeCode(str(observed_state_raw or "UNKNOWN"))
            )
        except ValueError as exc:
            raise ValueError("future_shadow_runtime_poll_observed_state_invalid") from exc
        invalidated = raw.get("invalidated", False)
        if type(invalidated) is not bool:
            raise ValueError("future_shadow_runtime_poll_invalidated_flag_invalid")
        evidence = FutureShadowOutcomeEvidence(
            resolved_at=polled_at,
            observation_available=available,
            observed_at=observed_at,
            observed_future_state=observed_state if available else MarketRegimeCode.UNKNOWN,
            invalidated=invalidated,
            invalidation_reason=str(raw.get("invalidation_reason") or ""),
            observation_source_ref=source_ref if available else "",
        )
        result[trace.trace_id] = evidence
    return result
