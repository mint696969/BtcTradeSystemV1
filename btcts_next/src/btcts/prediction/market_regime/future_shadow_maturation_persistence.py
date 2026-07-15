# path: ./btcts_next/src/btcts/prediction/market_regime/future_shadow_maturation_persistence.py
# desc: MR-F9.6 disabled-by-default immutable persistence for shadow maturation snapshots.

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from btcts.core.io import atomic_write_text, file_lock

MARKET_REGIME_FUTURE_SHADOW_MATURATION_PERSISTENCE_VERSION = (
    "prediction.market_regime.future_shadow_maturation_persistence.mr_f9_6.v1"
)
MATURATION_NAMESPACE = "prediction/market_regime/future_shadow/maturation"


def build_future_shadow_maturation_persistence_plan(
    *, maturation_cycle: Mapping[str, Any]
) -> Mapping[str, Any]:
    if maturation_cycle.get("artifact_kind") != "future_shadow_maturation_cycle":
        raise ValueError("future_shadow_maturation_persistence_cycle_kind_invalid")
    receipt_id = str(maturation_cycle.get("receipt_id") or "")
    suite_id = str(maturation_cycle.get("suite_id") or "")
    origin = str(maturation_cycle.get("prediction_origin") or "")
    polled_at = str(maturation_cycle.get("polled_at") or "")
    if not receipt_id or not suite_id or not origin.endswith("Z") or not polled_at.endswith("Z"):
        raise ValueError("future_shadow_maturation_persistence_identity_invalid")
    intake = maturation_cycle.get("outcome_intake_report")
    if not isinstance(intake, Mapping):
        raise ValueError("future_shadow_maturation_persistence_intake_invalid")
    rows = intake.get("outcome_rows")
    if not isinstance(rows, Sequence) or isinstance(rows, (str, bytes)):
        raise ValueError("future_shadow_maturation_persistence_rows_invalid")
    normalized_rows = tuple(sorted((dict(row) for row in rows), key=lambda row: str(row.get("trace_id") or "")))
    trace_ids = tuple(str(row.get("trace_id") or "") for row in normalized_rows)
    if any(not trace_id for trace_id in trace_ids) or len(trace_ids) != len(set(trace_ids)):
        raise ValueError("future_shadow_maturation_persistence_trace_ids_invalid")
    if int(maturation_cycle.get("trace_count") or 0) != len(normalized_rows):
        raise ValueError("future_shadow_maturation_persistence_trace_count_mismatch")
    if int(intake.get("trace_count") or 0) != len(normalized_rows):
        raise ValueError("future_shadow_maturation_persistence_intake_count_mismatch")
    if str(intake.get("prediction_origin") or "") != origin:
        raise ValueError("future_shadow_maturation_persistence_origin_mismatch")
    if str(intake.get("resolved_at") or "") != polled_at:
        raise ValueError("future_shadow_maturation_persistence_polled_at_mismatch")

    status_counts: dict[str, int] = {}
    for row in normalized_rows:
        status = str(row.get("outcome_status") or "")
        if not status:
            raise ValueError("future_shadow_maturation_persistence_status_missing")
        status_counts[status] = status_counts.get(status, 0) + 1
    intake_counts = dict(intake.get("status_counts") or {})
    if dict(sorted(status_counts.items())) != dict(sorted((str(k), int(v)) for k, v in intake_counts.items())):
        raise ValueError("future_shadow_maturation_persistence_status_counts_mismatch")

    digest_basis = "|".join((receipt_id, polled_at, *trace_ids))
    digest = hashlib.sha256(digest_basis.encode("utf-8")).hexdigest()[:32]
    relpath = (
        f"{MATURATION_NAMESPACE}/date={origin[:10]}/"
        f"maturation-{digest}.json"
    )
    return {
        "schema_version": MARKET_REGIME_FUTURE_SHADOW_MATURATION_PERSISTENCE_VERSION,
        "artifact_family": "prediction/market_regime",
        "artifact_kind": "future_shadow_maturation_snapshot",
        "receipt_id": receipt_id,
        "suite_id": suite_id,
        "prediction_origin": origin,
        "polled_at": polled_at,
        "artifact_relpath": relpath,
        "trace_count": len(normalized_rows),
        "trace_ids": trace_ids,
        "expired_horizons": tuple(maturation_cycle.get("expired_horizons") or ()),
        "pending_horizons": tuple(maturation_cycle.get("pending_horizons") or ()),
        "observation_horizons": tuple(maturation_cycle.get("observation_horizons") or ()),
        "status_counts": dict(sorted(status_counts.items())),
        "outcome_rows": normalized_rows,
        "disabled_by_default": True,
        "scheduler_enabled": False,
        "writer_registered": False,
        "canonical_outcome_ledger_append": False,
        "canonical_replacement": False,
        "parameter_auto_promotion_allowed": False,
        "live_parameter_apply_allowed": False,
        "would_write": False,
    }


def persist_future_shadow_maturation_once(
    root: str | Path,
    *,
    plan: Mapping[str, Any],
    enabled: bool = False,
    once: bool = False,
) -> Mapping[str, Any]:
    if type(enabled) is not bool or type(once) is not bool:
        raise ValueError("future_shadow_maturation_persistence_flags_invalid")
    if enabled is not True:
        raise PermissionError("future_shadow_maturation_persistence_disabled_by_default")
    if once is not True:
        raise PermissionError("future_shadow_maturation_persistence_once_ack_required")
    if plan.get("schema_version") != MARKET_REGIME_FUTURE_SHADOW_MATURATION_PERSISTENCE_VERSION:
        raise ValueError("future_shadow_maturation_persistence_schema_invalid")
    if plan.get("artifact_kind") != "future_shadow_maturation_snapshot":
        raise ValueError("future_shadow_maturation_persistence_kind_invalid")
    for key, expected in {
        "disabled_by_default": True,
        "scheduler_enabled": False,
        "writer_registered": False,
        "canonical_outcome_ledger_append": False,
        "canonical_replacement": False,
        "parameter_auto_promotion_allowed": False,
        "live_parameter_apply_allowed": False,
        "would_write": False,
    }.items():
        if plan.get(key) is not expected:
            raise ValueError("future_shadow_maturation_persistence_safety_invalid")

    relpath = str(plan.get("artifact_relpath") or "")
    rel = Path(relpath)
    if (
        not relpath.startswith(MATURATION_NAMESPACE + "/date=")
        or rel.is_absolute()
        or ".." in rel.parts
        or "\\" in relpath
    ):
        raise ValueError("future_shadow_maturation_persistence_relpath_invalid")
    rows = tuple(plan.get("outcome_rows") or ())
    trace_ids = tuple(str(row.get("trace_id") or "") for row in rows if isinstance(row, Mapping))
    if len(rows) != len(trace_ids) or any(not trace_id for trace_id in trace_ids):
        raise ValueError("future_shadow_maturation_persistence_rows_invalid")
    if trace_ids != tuple(plan.get("trace_ids") or ()):
        raise ValueError("future_shadow_maturation_persistence_trace_set_mismatch")
    if len(trace_ids) != len(set(trace_ids)):
        raise ValueError("future_shadow_maturation_persistence_trace_ids_invalid")
    if int(plan.get("trace_count") or 0) != len(rows):
        raise ValueError("future_shadow_maturation_persistence_trace_count_mismatch")

    digest_basis = "|".join((str(plan.get("receipt_id") or ""), str(plan.get("polled_at") or ""), *trace_ids))
    expected_digest = hashlib.sha256(digest_basis.encode("utf-8")).hexdigest()[:32]
    expected_relpath = (
        f"{MATURATION_NAMESPACE}/date={str(plan.get('prediction_origin') or '')[:10]}/"
        f"maturation-{expected_digest}.json"
    )
    if relpath != expected_relpath:
        raise ValueError("future_shadow_maturation_persistence_relpath_mismatch")

    payload_keys = (
        "schema_version", "artifact_family", "artifact_kind", "receipt_id", "suite_id",
        "prediction_origin", "polled_at", "trace_count", "trace_ids", "expired_horizons",
        "pending_horizons", "observation_horizons", "status_counts", "outcome_rows",
        "scheduler_enabled", "writer_registered", "canonical_outcome_ledger_append",
        "canonical_replacement", "parameter_auto_promotion_allowed", "live_parameter_apply_allowed",
    )
    payload = {key: plan[key] for key in payload_keys}
    text = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"
    path = Path(root) / relpath
    with file_lock(path, timeout_sec=5.0, stale_sec=60.0):
        if path.exists():
            existing = path.read_text(encoding="utf-8-sig")
            if existing != text:
                raise RuntimeError("future_shadow_maturation_persistence_existing_conflict")
            return {"written": False, "duplicate": True, "artifact_relpath": relpath}
        atomic_write_text(path, text)
    return {"written": True, "duplicate": False, "artifact_relpath": relpath}
