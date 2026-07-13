# path: ./btcts_next/src/btcts/prediction/market_regime/future_origin_evidence_writer.py
# desc: Disabled-by-default MR-F6.6 append-only writer for prediction-origin evidence bundles.

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from types import MappingProxyType
from typing import Any, Mapping, Sequence

from btcts.core.io import atomic_write_text, file_lock
from .future_mandatory_baseline_origin_evidence import MARKET_REGIME_ORIGIN_EVIDENCE_VERSION

MARKET_REGIME_ORIGIN_EVIDENCE_WRITER_VERSION = (
    "prediction.market_regime.origin_evidence_writer.mr_f6_6.v1"
)
ORIGIN_EVIDENCE_NAMESPACE = "prediction/market_regime/future_origin_evidence"


def _json_compatible(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {str(key): _json_compatible(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [_json_compatible(item) for item in value]
    if isinstance(value, list):
        return [_json_compatible(item) for item in value]
    return value


def _canonical_json(payload: Mapping[str, Any]) -> str:
    return json.dumps(_json_compatible(payload), ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"


def _parse_utc(value: str, error: str) -> datetime:
    if not isinstance(value, str) or not value.endswith("Z"):
        raise ValueError(error)
    try:
        parsed = datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError as exc:
        raise ValueError(error) from exc
    if parsed.tzinfo != timezone.utc:
        raise ValueError(error)
    return parsed


def deterministic_origin_bundle_hash(bundle: Mapping[str, Any]) -> str:
    if not isinstance(bundle, Mapping):
        raise ValueError("origin_evidence_writer_bundle_not_mapping")
    required = (
        "schema_version", "artifact_family", "artifact_kind", "bundle_id", "trace_id",
        "model_id", "logic_version", "parameter_set_id", "target_horizon_sec",
        "target_definition_version", "prediction_origin", "feature_snapshot_ref",
        "feature_snapshot", "candidate_probability_by_state",
    )
    for key in required:
        if key not in bundle or bundle[key] in (None, ""):
            raise ValueError(f"origin_evidence_writer_bundle_identity_missing:{key}")
    if bundle["schema_version"] != MARKET_REGIME_ORIGIN_EVIDENCE_VERSION:
        raise ValueError("origin_evidence_writer_bundle_schema_invalid")
    if bundle["artifact_kind"] != "future_origin_evidence_bundle":
        raise ValueError("origin_evidence_writer_bundle_kind_invalid")
    if bundle.get("append_only_required") is not True or bundle.get("canonical_isolated") is not True:
        raise ValueError("origin_evidence_writer_bundle_safety_invalid")
    if bundle.get("historical_backfill_allowed") is not False:
        raise ValueError("origin_evidence_writer_historical_backfill_forbidden")
    canonical = json.dumps(_json_compatible(bundle), ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def build_origin_evidence_write_plan(
    *,
    generated_at: str,
    writer_id: str,
    writer_contract_version: str,
    bundles: Sequence[Mapping[str, Any]],
    maximum_batch_rows: int = 100,
) -> Mapping[str, Any]:
    generated = _parse_utc(generated_at, "origin_evidence_writer_generated_at_invalid")
    if not writer_id.strip() or not writer_contract_version.strip():
        raise ValueError("origin_evidence_writer_identity_missing")
    if isinstance(maximum_batch_rows, bool) or maximum_batch_rows <= 0:
        raise ValueError("origin_evidence_writer_batch_limit_invalid")
    if isinstance(bundles, (str, bytes)) or not isinstance(bundles, Sequence) or not bundles:
        raise ValueError("origin_evidence_writer_bundles_missing")
    if len(bundles) > maximum_batch_rows:
        raise ValueError("origin_evidence_writer_batch_limit_exceeded")
    pairs = []
    for bundle in bundles:
        bundle_id = str(bundle.get("bundle_id") or "").strip()
        if not bundle_id:
            raise ValueError("origin_evidence_writer_bundle_id_missing")
        pairs.append((bundle_id, deterministic_origin_bundle_hash(bundle)))
    if len({item[0] for item in pairs}) != len(pairs):
        raise ValueError("origin_evidence_writer_duplicate_bundle_id")
    ordered = tuple(sorted(pairs))
    partition = generated.date().isoformat()
    dedupe_source = "|".join((writer_id, writer_contract_version, ORIGIN_EVIDENCE_NAMESPACE, partition, *(x for pair in ordered for x in pair)))
    dedupe_key = hashlib.sha256(dedupe_source.encode("utf-8")).hexdigest()
    return MappingProxyType({
        "schema_version": MARKET_REGIME_ORIGIN_EVIDENCE_WRITER_VERSION,
        "artifact_kind": "future_origin_evidence_write_plan",
        "writer_id": writer_id,
        "writer_contract_version": writer_contract_version,
        "generated_at": generated_at,
        "partition_key": partition,
        "namespace": ORIGIN_EVIDENCE_NAMESPACE,
        "bundle_ids": tuple(item[0] for item in ordered),
        "bundle_hashes": tuple(item[1] for item in ordered),
        "row_count": len(ordered),
        "dedupe_key": dedupe_key,
        "disabled_by_default": True,
        "scheduler_registration_allowed": False,
        "canonical_path_overlap_allowed": False,
        "append_only_required": True,
        "duplicate_prevention_required": True,
        "execution_performed": False,
        "write_allowed": False,
    })


def build_origin_evidence_approval(
    *, approval_id: str, operator_ids: Sequence[str], requested_at: str, expires_at: str,
    approved_writer_id: str, approved_writer_contract_version: str,
) -> Mapping[str, Any]:
    requested = _parse_utc(requested_at, "origin_evidence_writer_approval_requested_at_invalid")
    expires = _parse_utc(expires_at, "origin_evidence_writer_approval_expires_at_invalid")
    if expires <= requested:
        raise ValueError("origin_evidence_writer_approval_window_invalid")
    operators = tuple(dict.fromkeys(str(item).strip() for item in operator_ids))
    if not approval_id.strip() or not operators or any(not item for item in operators):
        raise ValueError("origin_evidence_writer_approval_identity_missing")
    return MappingProxyType({
        "schema_version": MARKET_REGIME_ORIGIN_EVIDENCE_WRITER_VERSION,
        "artifact_kind": "future_origin_evidence_operator_approval",
        "approval_id": approval_id,
        "operator_ids": operators,
        "requested_at": requested_at,
        "expires_at": expires_at,
        "approved_writer_id": approved_writer_id,
        "approved_writer_contract_version": approved_writer_contract_version,
        "dry_run_reviewed": True,
        "canonical_isolation_reviewed": True,
        "limited_shadow_scope_reviewed": True,
        "write_performed": False,
    })


def _validated_bundles(bundles: Sequence[Mapping[str, Any]], plan: Mapping[str, Any]) -> tuple[dict[str, Any], ...]:
    by_id = {str(bundle.get("bundle_id") or ""): _json_compatible(bundle) for bundle in bundles}
    if len(by_id) != len(bundles):
        raise ValueError("origin_evidence_writer_duplicate_bundle_id")
    plan_ids = tuple(str(item) for item in plan.get("bundle_ids", ()))
    plan_hashes = tuple(str(item) for item in plan.get("bundle_hashes", ()))
    if not plan_ids or len(plan_ids) != len(plan_hashes):
        raise ValueError("origin_evidence_writer_plan_bundle_identity_invalid")
    if int(plan.get("row_count") or 0) != len(plan_ids):
        raise ValueError("origin_evidence_writer_plan_row_count_mismatch")
    if set(by_id) != set(plan_ids):
        raise ValueError("origin_evidence_writer_bundle_set_mismatch")
    ordered = []
    for bundle_id, expected_hash in zip(plan_ids, plan_hashes):
        bundle = by_id[bundle_id]
        if deterministic_origin_bundle_hash(bundle) != expected_hash:
            raise ValueError("origin_evidence_writer_bundle_hash_mismatch")
        ordered.append(bundle)
    return tuple(ordered)


def preflight_origin_evidence_write(*, plan: Mapping[str, Any], approval: Mapping[str, Any], bundles: Sequence[Mapping[str, Any]], executed_at: str) -> Mapping[str, Any]:
    if plan.get("schema_version") != MARKET_REGIME_ORIGIN_EVIDENCE_WRITER_VERSION or plan.get("artifact_kind") != "future_origin_evidence_write_plan":
        raise ValueError("origin_evidence_writer_plan_invalid")
    if plan.get("namespace") != ORIGIN_EVIDENCE_NAMESPACE or plan.get("execution_performed") is not False:
        raise ValueError("origin_evidence_writer_plan_safety_invalid")
    if approval.get("schema_version") != MARKET_REGIME_ORIGIN_EVIDENCE_WRITER_VERSION or approval.get("artifact_kind") != "future_origin_evidence_operator_approval":
        raise ValueError("origin_evidence_writer_approval_invalid")
    if approval.get("approved_writer_id") != plan.get("writer_id") or approval.get("approved_writer_contract_version") != plan.get("writer_contract_version"):
        raise PermissionError("origin_evidence_writer_approval_scope_mismatch")
    executed = _parse_utc(executed_at, "origin_evidence_writer_executed_at_invalid")
    requested = _parse_utc(str(approval.get("requested_at") or ""), "origin_evidence_writer_approval_requested_at_invalid")
    expires = _parse_utc(str(approval.get("expires_at") or ""), "origin_evidence_writer_approval_expires_at_invalid")
    if executed < requested or executed >= expires:
        raise PermissionError("origin_evidence_writer_approval_not_active")
    validated = _validated_bundles(bundles, plan)
    relpath = f"{ORIGIN_EVIDENCE_NAMESPACE}/date={plan['partition_key']}/batch-{plan['dedupe_key']}.json"
    return MappingProxyType({
        "ok": True,
        "preflight_only": True,
        "write_allowed": True,
        "would_write": False,
        "artifact_relpath": relpath,
        "row_count": len(validated),
        "dedupe_key": plan["dedupe_key"],
        "approval_id": approval["approval_id"],
        "scheduler_enabled": False,
        "writer_registered": False,
        "canonical_replacement": False,
        "counts_as_real_shadow_evidence": False,
    })


def write_origin_evidence_once(root: str | Path, *, plan: Mapping[str, Any], approval: Mapping[str, Any], bundles: Sequence[Mapping[str, Any]], executed_at: str, enabled: bool = False, once: bool = False) -> Mapping[str, Any]:
    if enabled is not True:
        raise PermissionError("origin_evidence_writer_disabled_by_default")
    if once is not True:
        raise PermissionError("origin_evidence_writer_once_ack_required")
    preflight = preflight_origin_evidence_write(plan=plan, approval=approval, bundles=bundles, executed_at=executed_at)
    validated = _validated_bundles(bundles, plan)
    path = Path(root) / str(preflight["artifact_relpath"])
    payload = {
        "schema_version": MARKET_REGIME_ORIGIN_EVIDENCE_WRITER_VERSION,
        "artifact_family": "prediction/market_regime",
        "artifact_kind": "future_origin_evidence_batch",
        "generated_at": plan["generated_at"],
        "executed_at": executed_at,
        "approval_id": approval["approval_id"],
        "writer_id": plan["writer_id"],
        "writer_contract_version": plan["writer_contract_version"],
        "partition_key": plan["partition_key"],
        "dedupe_key": plan["dedupe_key"],
        "row_count": len(validated),
        "rows": list(validated),
        "append_only": True,
        "canonical_isolated": True,
        "historical_backfill_allowed": False,
        "scheduler_enabled": False,
        "writer_registered": False,
        "parameter_auto_promotion_allowed": False,
        "live_parameter_apply_allowed": False,
    }
    text = _canonical_json(payload)
    with file_lock(path, timeout_sec=5.0, stale_sec=60.0):
        if path.exists():
            existing = path.read_text(encoding="utf-8-sig")
            if existing != text:
                raise RuntimeError("origin_evidence_writer_existing_artifact_conflict")
            return MappingProxyType({**dict(preflight), "preflight_only": False, "written": False, "duplicate": True})
        atomic_write_text(path, text)
    return MappingProxyType({**dict(preflight), "preflight_only": False, "would_write": True, "written": True, "duplicate": False})
