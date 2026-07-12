# path: ./btcts_next/src/btcts/prediction/market_regime/tools/write_future_shadow.py
# desc: Explicit once-only MR-F5.12 isolated future-shadow artifact writer. Disabled by default; no CLI or scheduler registration.

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence

from btcts.core.io import atomic_write_text, file_lock
from btcts.prediction.market_regime.future_shadow_writer_dry_run import deterministic_shadow_row_hash

MARKET_REGIME_FUTURE_SHADOW_WRITER_VERSION = "prediction.market_regime.future_shadow_writer.mr_f5_12.v1"
FUTURE_SHADOW_NAMESPACE = "prediction/market_regime/future_shadow"


def _canonical_json(payload: Mapping[str, Any]) -> str:
    return json.dumps(dict(payload), ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"


def _parse_canonical_utc(value: str, error: str) -> datetime:
    if not isinstance(value, str) or not value.endswith("Z"):
        raise ValueError(error)
    try:
        parsed = datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError as exc:
        raise ValueError(error) from exc
    if parsed.tzinfo != timezone.utc or parsed.isoformat().replace("+00:00", "Z") != value:
        raise ValueError(error)
    return parsed


def _expected_dedupe_key(dry_run_plan: Mapping[str, Any]) -> str:
    source = "|".join((
        str(dry_run_plan.get("writer_id") or ""),
        str(dry_run_plan.get("writer_contract_version") or ""),
        str(dry_run_plan.get("namespace") or ""),
        str(dry_run_plan.get("partition_key") or ""),
        *(str(item) for item in tuple(dry_run_plan.get("trace_ids") or ())),
        *(str(item) for item in tuple(dry_run_plan.get("row_payload_hashes") or ())),
    ))
    return hashlib.sha256(source.encode("utf-8")).hexdigest()


def _validate_boundary(
    boundary: Mapping[str, Any], dry_run_plan: Mapping[str, Any], executed_at: str
) -> None:
    if not isinstance(boundary, Mapping):
        raise ValueError("future_shadow_writer_boundary_missing")
    if boundary.get("schema_version") != "prediction.market_regime.future_shadow_execution_boundary.mr_f5_10.v1":
        raise ValueError("future_shadow_writer_boundary_schema_invalid")
    if boundary.get("artifact_kind") != "future_shadow_execution_boundary":
        raise ValueError("future_shadow_writer_boundary_kind_invalid")
    if boundary.get("mode") != "approved_shadow_write":
        raise PermissionError("future_shadow_writer_boundary_mode_invalid")
    if boundary.get("write_allowed") is not True:
        raise PermissionError("future_shadow_writer_boundary_not_approved")
    if boundary.get("decision") != "approved_shadow_write_boundary_satisfied":
        raise PermissionError("future_shadow_writer_boundary_decision_invalid")
    if boundary.get("execution_performed") is not False:
        raise ValueError("future_shadow_writer_boundary_execution_state_invalid")
    if str(boundary.get("writer_id") or "") != str(dry_run_plan.get("writer_id") or ""):
        raise PermissionError("future_shadow_writer_boundary_writer_mismatch")
    if str(boundary.get("writer_contract_version") or "") != str(dry_run_plan.get("writer_contract_version") or ""):
        raise PermissionError("future_shadow_writer_boundary_contract_mismatch")
    requested = _parse_canonical_utc(
        str(boundary.get("approval_requested_at") or ""),
        "future_shadow_writer_approval_requested_at_invalid",
    )
    expires = _parse_canonical_utc(
        str(boundary.get("approval_expires_at") or ""),
        "future_shadow_writer_approval_expires_at_invalid",
    )
    executed = _parse_canonical_utc(executed_at, "future_shadow_writer_executed_at_invalid")
    if executed < requested:
        raise PermissionError("future_shadow_writer_approval_not_yet_valid")
    if executed >= expires:
        raise PermissionError("future_shadow_writer_approval_expired")
    if not str(boundary.get("approval_id") or "").strip():
        raise PermissionError("future_shadow_writer_approval_id_missing")


def _validate_plan(dry_run_plan: Mapping[str, Any]) -> None:
    if not isinstance(dry_run_plan, Mapping):
        raise ValueError("future_shadow_writer_dry_run_plan_missing")
    if dry_run_plan.get("schema_version") != "prediction.market_regime.future_shadow_writer_dry_run.mr_f5_11.v1":
        raise ValueError("future_shadow_writer_dry_run_schema_invalid")
    if dry_run_plan.get("artifact_kind") != "future_shadow_writer_dry_run":
        raise ValueError("future_shadow_writer_dry_run_kind_invalid")
    if dry_run_plan.get("dry_run_only") is not True:
        raise ValueError("future_shadow_writer_dry_run_flag_invalid")
    if dry_run_plan.get("writer_registered") is not False:
        raise ValueError("future_shadow_writer_registration_state_invalid")
    if dry_run_plan.get("execution_performed") is not False:
        raise ValueError("future_shadow_writer_dry_run_execution_state_invalid")
    if dry_run_plan.get("namespace") != FUTURE_SHADOW_NAMESPACE:
        raise ValueError("future_shadow_writer_namespace_invalid")
    if dry_run_plan.get("source_role") != "hot_data_root" or dry_run_plan.get("destination_role") != "hot_data_root":
        raise ValueError("future_shadow_writer_data_role_invalid")
    write_plan = dry_run_plan.get("write_plan")
    if not isinstance(write_plan, Mapping):
        raise ValueError("future_shadow_writer_write_plan_missing")
    required = {
        "disabled_by_default": True,
        "scheduler_registration_allowed": False,
        "canonical_path_overlap_allowed": False,
        "append_only_required": True,
        "atomic_temp_then_replace_required": True,
        "duplicate_prevention_required": True,
    }
    for key, expected in required.items():
        if write_plan.get(key) is not expected:
            raise ValueError(f"future_shadow_writer_write_plan_invalid:{key}")
    if dry_run_plan.get("target_schema_version") != "prediction.market_regime.future_shadow_outcome.mr_f5_6.v1":
        raise ValueError("future_shadow_writer_target_schema_invalid")
    partition = str(dry_run_plan.get("partition_key") or "")
    try:
        parsed_partition = datetime.strptime(partition, "%Y-%m-%d").date()
    except ValueError as exc:
        raise ValueError("future_shadow_writer_partition_key_invalid") from exc
    if parsed_partition.isoformat() != partition:
        raise ValueError("future_shadow_writer_partition_key_invalid")
    generated = _parse_canonical_utc(
        str(dry_run_plan.get("generated_at") or ""),
        "future_shadow_writer_generated_at_invalid",
    )
    if generated.date().isoformat() != partition:
        raise ValueError("future_shadow_writer_partition_generated_at_mismatch")
    if str(dry_run_plan.get("dedupe_key") or "") != _expected_dedupe_key(dry_run_plan):
        raise ValueError("future_shadow_writer_dedupe_key_mismatch")


def _validated_rows(rows: Sequence[Mapping[str, Any]], dry_run_plan: Mapping[str, Any]) -> tuple[dict[str, Any], ...]:
    if isinstance(rows, (str, bytes)) or not isinstance(rows, Sequence) or not rows:
        raise ValueError("future_shadow_writer_rows_missing")
    expected_trace_ids = tuple(dry_run_plan.get("trace_ids") or ())
    expected_hashes = tuple(dry_run_plan.get("row_payload_hashes") or ())
    if len(rows) != len(expected_trace_ids) or len(rows) != len(expected_hashes):
        raise ValueError("future_shadow_writer_row_count_mismatch")

    by_trace: dict[str, dict[str, Any]] = {}
    for raw in rows:
        if not isinstance(raw, Mapping):
            raise ValueError("future_shadow_writer_row_not_mapping")
        row = dict(raw)
        trace_id = str(row.get("trace_id") or "").strip()
        if not trace_id:
            raise ValueError("future_shadow_writer_trace_id_missing")
        if trace_id in by_trace:
            raise ValueError("future_shadow_writer_duplicate_trace_id")
        by_trace[trace_id] = row

    ordered: list[dict[str, Any]] = []
    for trace_id, expected_hash in zip(expected_trace_ids, expected_hashes):
        row = by_trace.get(str(trace_id))
        if row is None:
            raise ValueError("future_shadow_writer_trace_set_mismatch")
        if deterministic_shadow_row_hash(row) != str(expected_hash):
            raise ValueError("future_shadow_writer_payload_hash_mismatch")
        ordered.append(row)
    return tuple(ordered)


def future_shadow_batch_relpath(dry_run_plan: Mapping[str, Any]) -> str:
    partition = str(dry_run_plan.get("partition_key") or "")
    dedupe_key = str(dry_run_plan.get("dedupe_key") or "")
    if len(dedupe_key) != 64 or any(ch not in "0123456789abcdef" for ch in dedupe_key):
        raise ValueError("future_shadow_writer_dedupe_key_invalid")
    if len(partition) != 10 or partition[4:5] != "-" or partition[7:8] != "-":
        raise ValueError("future_shadow_writer_partition_key_invalid")
    return f"{FUTURE_SHADOW_NAMESPACE}/date={partition}/batch-{dedupe_key}.json"


def preflight_market_regime_future_shadow_write(
    *,
    dry_run_plan: Mapping[str, Any],
    approved_boundary: Mapping[str, Any],
    rows: Sequence[Mapping[str, Any]],
    executed_at: str,
) -> dict[str, Any]:
    _validate_plan(dry_run_plan)
    _validate_boundary(approved_boundary, dry_run_plan, executed_at)
    validated_rows = _validated_rows(rows, dry_run_plan)
    relpath = future_shadow_batch_relpath(dry_run_plan)
    return {
        "ok": True,
        "writer_version": MARKET_REGIME_FUTURE_SHADOW_WRITER_VERSION,
        "preflight_only": True,
        "would_write": False,
        "write_allowed": True,
        "artifact_relpath": relpath,
        "row_count": len(validated_rows),
        "dedupe_key": str(dry_run_plan["dedupe_key"]),
        "approval_id": str(approved_boundary["approval_id"]),
        "executed_at": executed_at,
        "writer_id": str(dry_run_plan["writer_id"]),
        "scheduler_enabled": False,
        "writer_registered": False,
        "canonical_replacement": False,
        "counts_as_real_shadow_evidence": False,
        "broker_private_api_allowed": False,
        "autotrade_trigger_allowed": False,
        "would_send_to_broker": False,
    }


def write_market_regime_future_shadow_once(
    root: str | Path,
    *,
    dry_run_plan: Mapping[str, Any],
    approved_boundary: Mapping[str, Any],
    rows: Sequence[Mapping[str, Any]],
    executed_at: str,
    enabled: bool = False,
    once: bool = False,
) -> dict[str, Any]:
    if type(enabled) is not bool or type(once) is not bool:
        raise ValueError("future_shadow_writer_enable_flags_invalid")
    if enabled is not True:
        raise PermissionError("future_shadow_writer_disabled_by_default")
    if once is not True:
        raise PermissionError("future_shadow_writer_once_ack_required")

    preflight = preflight_market_regime_future_shadow_write(
        dry_run_plan=dry_run_plan,
        approved_boundary=approved_boundary,
        rows=rows,
        executed_at=executed_at,
    )
    validated_rows = _validated_rows(rows, dry_run_plan)
    relpath = str(preflight["artifact_relpath"])
    path = Path(root) / relpath
    payload = {
        "schema_version": MARKET_REGIME_FUTURE_SHADOW_WRITER_VERSION,
        "artifact_family": "prediction/market_regime",
        "artifact_kind": "future_shadow_evidence_batch",
        "generated_at": str(dry_run_plan["generated_at"]),
        "writer_id": str(dry_run_plan["writer_id"]),
        "writer_contract_version": str(dry_run_plan["writer_contract_version"]),
        "approval_id": str(approved_boundary["approval_id"]),
        "executed_at": executed_at,
        "dedupe_key": str(dry_run_plan["dedupe_key"]),
        "partition_key": str(dry_run_plan["partition_key"]),
        "target_schema_version": str(dry_run_plan["target_schema_version"]),
        "row_count": len(validated_rows),
        "rows": list(validated_rows),
        "append_only": True,
        "canonical_isolated": True,
        "scheduler_enabled": False,
        "writer_registered": False,
        "parameter_auto_promotion_allowed": False,
        "live_parameter_apply_allowed": False,
        "would_send_to_broker": False,
    }
    text = _canonical_json(payload)

    with file_lock(path, timeout_sec=5.0, stale_sec=60.0):
        if path.exists():
            existing = path.read_text(encoding="utf-8-sig")
            if existing != text:
                raise RuntimeError("future_shadow_writer_existing_artifact_conflict")
            return {
                **preflight,
                "preflight_only": False,
                "would_write": False,
                "written": False,
                "duplicate": True,
                "artifact_exists": True,
                "counts_as_real_shadow_evidence": False,
            }
        atomic_write_text(path, text)

    return {
        **preflight,
        "preflight_only": False,
        "would_write": True,
        "written": True,
        "duplicate": False,
        "artifact_exists": True,
        "counts_as_real_shadow_evidence": False,
    }
