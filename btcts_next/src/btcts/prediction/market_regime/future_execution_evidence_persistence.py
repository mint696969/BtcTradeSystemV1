# path: ./btcts_next/src/btcts/prediction/market_regime/future_execution_evidence_persistence.py
# desc: MR-F9.3 disabled-by-default, duplicate-safe persistence for origin execution evidence suites.

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from btcts.core.io import atomic_write_text, file_lock

EXECUTION_EVIDENCE_PERSISTENCE_VERSION = (
    "prediction.market_regime.future_execution_evidence_persistence.mr_f9_3.v1"
)
EXECUTION_EVIDENCE_NAMESPACE = "prediction/market_regime/future_shadow/execution_evidence"


def build_future_execution_evidence_persistence_plan(
    *, origin_suite: Mapping[str, Any]
) -> Mapping[str, Any]:
    if origin_suite.get("artifact_kind") != "future_shadow_origin_execution_suite":
        raise ValueError("future_execution_evidence_persistence_suite_kind_invalid")
    origin = str(origin_suite.get("prediction_origin") or "")
    suite_id = str(origin_suite.get("suite_id") or "")
    if not origin.endswith("Z") or not suite_id:
        raise ValueError("future_execution_evidence_persistence_suite_identity_invalid")
    pair_plans = origin_suite.get("pair_plans")
    if not isinstance(pair_plans, Sequence) or isinstance(pair_plans, (str, bytes)):
        raise ValueError("future_execution_evidence_persistence_pair_plans_invalid")

    rows: list[Mapping[str, Any]] = []
    for plan in pair_plans:
        if not isinstance(plan, Mapping):
            raise ValueError("future_execution_evidence_persistence_pair_plan_invalid")
        plan_rows = plan.get("rows")
        if not isinstance(plan_rows, Sequence) or isinstance(plan_rows, (str, bytes)):
            raise ValueError("future_execution_evidence_persistence_rows_invalid")
        for row in plan_rows:
            if not isinstance(row, Mapping):
                raise ValueError("future_execution_evidence_persistence_row_invalid")
            rows.append(dict(row))

    rows_sorted = tuple(sorted(rows, key=lambda item: str(item.get("trace_id") or "")))
    if not rows_sorted:
        raise ValueError("future_execution_evidence_persistence_rows_missing")
    trace_ids = tuple(str(row.get("trace_id") or "") for row in rows_sorted)
    if any(not item for item in trace_ids) or len(trace_ids) != len(set(trace_ids)):
        raise ValueError("future_execution_evidence_persistence_trace_ids_invalid")
    if any(str(row.get("prediction_origin") or "") != origin for row in rows_sorted):
        raise ValueError("future_execution_evidence_persistence_origin_mismatch")
    if int(origin_suite.get("evidence_count") or 0) != len(rows_sorted):
        raise ValueError("future_execution_evidence_persistence_count_mismatch")
    if tuple(origin_suite.get("trace_ids") or ()) != trace_ids:
        raise ValueError("future_execution_evidence_persistence_trace_set_mismatch")

    digest = hashlib.sha256("|".join(trace_ids).encode("utf-8")).hexdigest()[:32]
    relpath = (
        f"{EXECUTION_EVIDENCE_NAMESPACE}/date={origin[:10]}/"
        f"origin-suite-{digest}.json"
    )
    return {
        "schema_version": EXECUTION_EVIDENCE_PERSISTENCE_VERSION,
        "artifact_kind": "future_shadow_origin_execution_evidence_set",
        "generated_at": origin,
        "suite_id": suite_id,
        "source_role": "hot_data_root",
        "namespace": EXECUTION_EVIDENCE_NAMESPACE,
        "artifact_relpath": relpath,
        "evidence_count": len(rows_sorted),
        "trace_ids": trace_ids,
        "rows": rows_sorted,
        "disabled_by_default": True,
        "scheduler_enabled": False,
        "writer_registered": False,
        "canonical_replacement": False,
        "parameter_auto_promotion_allowed": False,
        "live_parameter_apply_allowed": False,
        "would_write": False,
    }


def persist_future_execution_evidence_once(
    root: str | Path,
    *,
    plan: Mapping[str, Any],
    enabled: bool = False,
    once: bool = False,
) -> Mapping[str, Any]:
    if type(enabled) is not bool or type(once) is not bool:
        raise ValueError("future_execution_evidence_persistence_flags_invalid")
    if enabled is not True:
        raise PermissionError("future_execution_evidence_persistence_disabled_by_default")
    if once is not True:
        raise PermissionError("future_execution_evidence_persistence_once_ack_required")
    if plan.get("schema_version") != EXECUTION_EVIDENCE_PERSISTENCE_VERSION:
        raise ValueError("future_execution_evidence_persistence_plan_schema_invalid")
    if plan.get("artifact_kind") != "future_shadow_origin_execution_evidence_set":
        raise ValueError("future_execution_evidence_persistence_plan_kind_invalid")
    if plan.get("source_role") != "hot_data_root" or plan.get("namespace") != EXECUTION_EVIDENCE_NAMESPACE:
        raise ValueError("future_execution_evidence_persistence_plan_role_invalid")
    for key, expected in {
        "disabled_by_default": True,
        "scheduler_enabled": False,
        "writer_registered": False,
        "canonical_replacement": False,
        "parameter_auto_promotion_allowed": False,
        "live_parameter_apply_allowed": False,
        "would_write": False,
    }.items():
        if plan.get(key) is not expected:
            raise ValueError("future_execution_evidence_persistence_plan_safety_invalid")

    relpath = str(plan.get("artifact_relpath") or "")
    relpath_path = Path(relpath)
    if (
        not relpath.startswith(EXECUTION_EVIDENCE_NAMESPACE + "/date=")
        or relpath_path.is_absolute()
        or ".." in relpath_path.parts
        or "\\" in relpath
    ):
        raise ValueError("future_execution_evidence_persistence_relpath_invalid")
    rows = tuple(plan.get("rows") or ())
    trace_ids = tuple(str(row.get("trace_id") or "") for row in rows if isinstance(row, Mapping))
    if len(rows) != len(trace_ids) or any(not item for item in trace_ids):
        raise ValueError("future_execution_evidence_persistence_rows_invalid")
    if trace_ids != tuple(plan.get("trace_ids") or ()):
        raise ValueError("future_execution_evidence_persistence_trace_set_mismatch")
    if len(trace_ids) != len(set(trace_ids)):
        raise ValueError("future_execution_evidence_persistence_trace_ids_invalid")
    if int(plan.get("evidence_count") or 0) != len(rows):
        raise ValueError("future_execution_evidence_persistence_count_mismatch")
    generated_at = str(plan.get("generated_at") or "")
    if any(str(row.get("prediction_origin") or "") != generated_at for row in rows):
        raise ValueError("future_execution_evidence_persistence_origin_mismatch")
    expected_digest = hashlib.sha256("|".join(trace_ids).encode("utf-8")).hexdigest()[:32]
    expected_relpath = (
        f"{EXECUTION_EVIDENCE_NAMESPACE}/date={generated_at[:10]}/"
        f"origin-suite-{expected_digest}.json"
    )
    if relpath != expected_relpath:
        raise ValueError("future_execution_evidence_persistence_relpath_mismatch")

    payload = {
        key: plan[key]
        for key in (
            "schema_version", "artifact_kind", "generated_at", "suite_id", "source_role",
            "namespace", "evidence_count", "trace_ids", "rows", "scheduler_enabled",
            "writer_registered", "canonical_replacement", "parameter_auto_promotion_allowed",
            "live_parameter_apply_allowed",
        )
    }
    text = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"
    path = Path(root) / relpath
    with file_lock(path, timeout_sec=5.0, stale_sec=60.0):
        if path.exists():
            existing = path.read_text(encoding="utf-8-sig")
            if existing != text:
                raise RuntimeError("future_execution_evidence_persistence_existing_conflict")
            return {"written": False, "duplicate": True, "artifact_relpath": relpath}
        atomic_write_text(path, text)
    return {"written": True, "duplicate": False, "artifact_relpath": relpath}
