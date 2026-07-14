# path: ./btcts_next/src/btcts/prediction/market_regime/future_origin_evidence_dry_run_writer_adapter.py
# desc: MR-F6.20 public writer preflight adapter. No write-function import or filesystem mutation.

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from types import MappingProxyType
from typing import Any, Mapping, Sequence

from .future_origin_evidence_execution_plan import (
    MARKET_REGIME_ORIGIN_EVIDENCE_EXECUTION_PLAN_VERSION,
)
from .future_origin_evidence_writer import (
    MARKET_REGIME_ORIGIN_EVIDENCE_WRITER_VERSION,
    preflight_origin_evidence_write,
)

MARKET_REGIME_ORIGIN_EVIDENCE_DRY_RUN_WRITER_ADAPTER_VERSION = (
    "prediction.market_regime.origin_evidence_dry_run_writer_adapter.mr_f6_20.v1"
)


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


def _canonical_hash(payload: Mapping[str, Any]) -> str:
    text = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _recompute_execution_plan_hash(plan: Mapping[str, Any]) -> str:
    identity = {
        "request_id": plan.get("request_id"),
        "request_hash": plan.get("request_hash"),
        "boundary_snapshot_hash": plan.get("boundary_snapshot_hash"),
        "planned_at": plan.get("planned_at"),
        "writer_id": plan.get("writer_id"),
        "writer_contract_version": plan.get("writer_contract_version"),
        "writer_contract_schema_version": plan.get("writer_contract_schema_version"),
        "approval_id": plan.get("approval_id"),
        "approval_requested_at": plan.get("approval_requested_at"),
        "approval_expires_at": plan.get("approval_expires_at"),
        "artifact_relpath": plan.get("artifact_relpath"),
        "dedupe_key": plan.get("dedupe_key"),
        "target_horizons_sec": tuple(plan.get("target_horizons_sec") or ()),
        "bundle_ids": tuple(plan.get("bundle_ids") or ()),
        "write_plan_bundle_ids": tuple(plan.get("write_plan_bundle_ids") or ()),
        "forecast_parameter_set_ids": tuple(plan.get("forecast_parameter_set_ids") or ()),
        "enabled_acknowledgement_present": plan.get("enabled_acknowledgement_present"),
        "once_acknowledgement_present": plan.get("once_acknowledgement_present"),
        "destination_artifact_exists": plan.get("destination_artifact_exists"),
        "destination_artifact_matches_request": plan.get("destination_artifact_matches_request"),
    }
    return _canonical_hash(identity)


def invoke_origin_evidence_writer_preflight_dry_run(
    *,
    execution_plan: Mapping[str, Any],
    writer_plan: Mapping[str, Any],
    approval: Mapping[str, Any],
    bundles: Sequence[Mapping[str, Any]],
    executed_at: str,
    expected_execution_plan_hash: str,
    expected_writer_id: str,
    expected_writer_contract_version: str,
) -> Mapping[str, Any]:
    if not isinstance(execution_plan, Mapping):
        raise ValueError("origin_evidence_dry_run_adapter_execution_plan_type_invalid")
    if execution_plan.get("schema_version") != MARKET_REGIME_ORIGIN_EVIDENCE_EXECUTION_PLAN_VERSION:
        raise ValueError("origin_evidence_dry_run_adapter_execution_plan_schema_mismatch")
    if execution_plan.get("artifact_kind") != "future_origin_evidence_dry_run_execution_plan":
        raise ValueError("origin_evidence_dry_run_adapter_execution_plan_kind_mismatch")
    if not isinstance(writer_plan, Mapping):
        raise ValueError("origin_evidence_dry_run_adapter_writer_plan_type_invalid")
    if not isinstance(approval, Mapping):
        raise ValueError("origin_evidence_dry_run_adapter_approval_type_invalid")
    if isinstance(bundles, (str, bytes)) or not isinstance(bundles, Sequence) or not bundles:
        raise ValueError("origin_evidence_dry_run_adapter_bundles_invalid")

    expected_execution_plan_hash = str(expected_execution_plan_hash or "").strip()
    expected_writer_id = str(expected_writer_id or "").strip()
    expected_writer_contract_version = str(expected_writer_contract_version or "").strip()
    if not expected_execution_plan_hash:
        raise ValueError("origin_evidence_dry_run_adapter_expected_plan_hash_missing")
    if not expected_writer_id or not expected_writer_contract_version:
        raise ValueError("origin_evidence_dry_run_adapter_expected_writer_scope_missing")

    execution_plan_hash = str(execution_plan.get("execution_plan_hash") or "").strip()
    execution_plan_id = str(execution_plan.get("execution_plan_id") or "").strip()
    recomputed_plan_hash = _recompute_execution_plan_hash(execution_plan)
    if execution_plan_hash != recomputed_plan_hash:
        raise ValueError("origin_evidence_dry_run_adapter_execution_plan_hash_mismatch")
    if execution_plan_hash != expected_execution_plan_hash:
        raise PermissionError("origin_evidence_dry_run_adapter_external_plan_hash_mismatch")
    if execution_plan_id != f"origin-evidence-execution-plan:{execution_plan_hash}":
        raise ValueError("origin_evidence_dry_run_adapter_execution_plan_id_mismatch")

    for field in (
        "dry_run_only",
        "execution_plan_ready",
        "enabled_acknowledgement_present",
        "once_acknowledgement_present",
        "human_gate_required",
    ):
        if execution_plan.get(field) is not True:
            raise ValueError(f"origin_evidence_dry_run_adapter_plan_not_ready:{field}")
    for field in (
        "execution_authorized_by_this_artifact",
        "writer_imported",
        "writer_invoked",
        "execution_performed",
        "writes_dhot",
        "scheduler_enabled",
        "counts_as_real_shadow_evidence",
        "candidate_selection_performed",
        "live_parameter_apply_allowed",
        "auto_promotion_allowed",
        "canonical_replacement_allowed",
    ):
        if execution_plan.get(field) is not False:
            raise ValueError(f"origin_evidence_dry_run_adapter_unsafe_plan_flag:{field}")
    if execution_plan.get("blockers") != ():
        raise ValueError("origin_evidence_dry_run_adapter_plan_blockers_present")
    if execution_plan.get("destination_artifact_exists") is not False:
        raise ValueError("origin_evidence_dry_run_adapter_destination_not_absent")
    if execution_plan.get("destination_artifact_matches_request") is not False:
        raise ValueError("origin_evidence_dry_run_adapter_destination_match_invalid")

    writer_id = str(execution_plan.get("writer_id") or "").strip()
    writer_contract_version = str(execution_plan.get("writer_contract_version") or "").strip()
    writer_schema = str(execution_plan.get("writer_contract_schema_version") or "").strip()
    if writer_id != expected_writer_id or writer_contract_version != expected_writer_contract_version:
        raise PermissionError("origin_evidence_dry_run_adapter_writer_scope_mismatch")
    if writer_schema != MARKET_REGIME_ORIGIN_EVIDENCE_WRITER_VERSION:
        raise ValueError("origin_evidence_dry_run_adapter_writer_schema_mismatch")
    if writer_plan.get("schema_version") != writer_schema:
        raise ValueError("origin_evidence_dry_run_adapter_writer_plan_schema_mismatch")
    if writer_plan.get("artifact_kind") != "future_origin_evidence_write_plan":
        raise ValueError("origin_evidence_dry_run_adapter_writer_plan_kind_mismatch")
    if writer_plan.get("writer_id") != writer_id:
        raise ValueError("origin_evidence_dry_run_adapter_writer_plan_id_mismatch")
    if writer_plan.get("writer_contract_version") != writer_contract_version:
        raise ValueError("origin_evidence_dry_run_adapter_writer_plan_contract_mismatch")

    planned = _parse_canonical_utc(
        str(execution_plan.get("planned_at") or ""),
        "origin_evidence_dry_run_adapter_planned_at_invalid",
    )
    executed = _parse_canonical_utc(
        executed_at,
        "origin_evidence_dry_run_adapter_executed_at_invalid",
    )
    approval_requested_at = str(execution_plan.get("approval_requested_at") or "").strip()
    approval_expires_at = str(execution_plan.get("approval_expires_at") or "").strip()
    requested = _parse_canonical_utc(
        approval_requested_at,
        "origin_evidence_dry_run_adapter_approval_requested_at_invalid",
    )
    expires = _parse_canonical_utc(
        approval_expires_at,
        "origin_evidence_dry_run_adapter_approval_expires_at_invalid",
    )
    if executed < planned:
        raise ValueError("origin_evidence_dry_run_adapter_before_execution_plan")
    if executed < requested or executed >= expires:
        raise PermissionError("origin_evidence_dry_run_adapter_approval_not_active")

    approval_id = str(execution_plan.get("approval_id") or "").strip()
    if approval.get("approval_id") != approval_id:
        raise ValueError("origin_evidence_dry_run_adapter_approval_id_mismatch")
    if approval.get("requested_at") != approval_requested_at:
        raise ValueError("origin_evidence_dry_run_adapter_approval_requested_at_mismatch")
    if approval.get("expires_at") != approval_expires_at:
        raise ValueError("origin_evidence_dry_run_adapter_approval_expires_at_mismatch")
    if approval.get("approved_writer_id") != writer_id:
        raise PermissionError("origin_evidence_dry_run_adapter_approval_writer_id_mismatch")
    if approval.get("approved_writer_contract_version") != writer_contract_version:
        raise PermissionError("origin_evidence_dry_run_adapter_approval_writer_contract_mismatch")

    bundle_ids = tuple(str(bundle.get("bundle_id") or "").strip() for bundle in bundles)
    execution_bundle_ids = tuple(str(item) for item in execution_plan.get("bundle_ids") or ())
    writer_order_ids = tuple(str(item) for item in execution_plan.get("write_plan_bundle_ids") or ())
    writer_plan_ids = tuple(str(item) for item in writer_plan.get("bundle_ids") or ())
    if (
        any(not item for item in bundle_ids)
        or len(set(bundle_ids)) != len(bundle_ids)
        or set(bundle_ids) != set(execution_bundle_ids)
        or writer_plan_ids != writer_order_ids
        or set(writer_plan_ids) != set(bundle_ids)
    ):
        raise ValueError("origin_evidence_dry_run_adapter_bundle_identity_mismatch")
    if type(writer_plan.get("row_count")) is not int:
        raise ValueError("origin_evidence_dry_run_adapter_writer_plan_row_count_type_invalid")
    if writer_plan.get("row_count") != len(bundle_ids):
        raise ValueError("origin_evidence_dry_run_adapter_writer_plan_row_count_mismatch")
    if writer_plan.get("dedupe_key") != execution_plan.get("dedupe_key"):
        raise ValueError("origin_evidence_dry_run_adapter_dedupe_key_mismatch")

    writer_preflight = preflight_origin_evidence_write(
        plan=writer_plan,
        approval=approval,
        bundles=bundles,
        executed_at=executed_at,
    )
    if writer_preflight.get("preflight_only") is not True:
        raise RuntimeError("origin_evidence_dry_run_adapter_preflight_boundary_breached")
    if writer_preflight.get("write_allowed") is not True:
        raise RuntimeError("origin_evidence_dry_run_adapter_preflight_not_allowed")
    if writer_preflight.get("would_write") is not False:
        raise RuntimeError("origin_evidence_dry_run_adapter_preflight_would_write_invalid")

    expected_relpath = str(execution_plan.get("artifact_relpath") or "").strip()
    if writer_preflight.get("artifact_relpath") != expected_relpath:
        raise ValueError("origin_evidence_dry_run_adapter_artifact_relpath_mismatch")
    if writer_preflight.get("dedupe_key") != execution_plan.get("dedupe_key"):
        raise ValueError("origin_evidence_dry_run_adapter_preflight_dedupe_key_mismatch")
    if writer_preflight.get("approval_id") != approval_id:
        raise ValueError("origin_evidence_dry_run_adapter_preflight_approval_id_mismatch")
    if writer_preflight.get("row_count") != len(bundle_ids):
        raise ValueError("origin_evidence_dry_run_adapter_preflight_row_count_mismatch")

    preflight_snapshot = {
        "preflight_only": writer_preflight.get("preflight_only"),
        "write_allowed": writer_preflight.get("write_allowed"),
        "would_write": writer_preflight.get("would_write"),
        "artifact_relpath": writer_preflight.get("artifact_relpath"),
        "row_count": writer_preflight.get("row_count"),
        "dedupe_key": writer_preflight.get("dedupe_key"),
        "approval_id": writer_preflight.get("approval_id"),
        "scheduler_enabled": writer_preflight.get("scheduler_enabled"),
        "writer_registered": writer_preflight.get("writer_registered"),
        "canonical_replacement": writer_preflight.get("canonical_replacement"),
        "counts_as_real_shadow_evidence": writer_preflight.get("counts_as_real_shadow_evidence"),
    }
    preflight_snapshot_hash = _canonical_hash(preflight_snapshot)
    result_identity = {
        "execution_plan_id": execution_plan_id,
        "execution_plan_hash": execution_plan_hash,
        "executed_at": executed_at,
        "writer_id": writer_id,
        "writer_contract_version": writer_contract_version,
        "approval_id": approval_id,
        "artifact_relpath": expected_relpath,
        "dedupe_key": execution_plan.get("dedupe_key"),
        "bundle_ids": execution_bundle_ids,
        "preflight_snapshot_hash": preflight_snapshot_hash,
    }
    result_hash = _canonical_hash(result_identity)

    return MappingProxyType({
        "schema_version": MARKET_REGIME_ORIGIN_EVIDENCE_DRY_RUN_WRITER_ADAPTER_VERSION,
        "artifact_family": "prediction/market_regime",
        "artifact_kind": "future_origin_evidence_dry_run_writer_adapter_result",
        "adapter_result_id": f"origin-evidence-dry-run-writer-adapter:{result_hash}",
        "adapter_result_hash": result_hash,
        "execution_plan_id": execution_plan_id,
        "execution_plan_hash": execution_plan_hash,
        "executed_at": executed_at,
        "writer_id": writer_id,
        "writer_contract_version": writer_contract_version,
        "approval_id": approval_id,
        "artifact_relpath": expected_relpath,
        "dedupe_key": execution_plan.get("dedupe_key"),
        "bundle_ids": execution_bundle_ids,
        "row_count": len(bundle_ids),
        "preflight_snapshot": MappingProxyType(preflight_snapshot),
        "preflight_snapshot_hash": preflight_snapshot_hash,
        "dry_run_contract_exercised": True,
        "writer_preflight_invoked": True,
        "writer_write_function_imported": False,
        "writer_write_function_invoked": False,
        "writer_invoked": False,
        "execution_performed": False,
        "filesystem_write_performed": False,
        "writes_dhot": False,
        "scheduler_enabled": False,
        "counts_as_real_shadow_evidence": False,
        "candidate_selection_performed": False,
        "live_parameter_apply_allowed": False,
        "auto_promotion_allowed": False,
        "canonical_replacement_allowed": False,
        "human_gate_required": True,
    })
