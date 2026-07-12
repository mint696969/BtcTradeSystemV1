# path: ./btcts_next/src/btcts/prediction/market_regime/future_shadow_writer_dry_run.py
# desc: Pure MR-F5.11 disabled-by-default writer dry-run schema and artifact isolation plan. No runtime reads or writes.

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from types import MappingProxyType
from typing import Any, Mapping, Tuple

MARKET_REGIME_FUTURE_SHADOW_WRITER_DRY_RUN_VERSION = "prediction.market_regime.future_shadow_writer_dry_run.mr_f5_11.v1"


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


def _non_empty_tuple(values: Tuple[str, ...], error: str) -> Tuple[str, ...]:
    normalized = tuple(dict.fromkeys(str(item).strip() for item in values))
    if not normalized or any(not item for item in normalized):
        raise ValueError(error)
    return normalized


@dataclass(frozen=True)
class FutureShadowDryRunArtifactIdentity:
    artifact_family: str
    artifact_kind: str
    schema_version: str
    source_role: str
    destination_role: str
    namespace: str
    partition_key: str

    def __post_init__(self) -> None:
        for name in (
            "artifact_family", "artifact_kind", "schema_version", "source_role",
            "destination_role", "namespace", "partition_key",
        ):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"future_shadow_dry_run_identity_missing:{name}")
        if self.artifact_family != "prediction/market_regime":
            raise ValueError("future_shadow_dry_run_artifact_family_invalid")
        if self.artifact_kind != "future_shadow_evidence":
            raise ValueError("future_shadow_dry_run_artifact_kind_invalid")
        if self.schema_version != "prediction.market_regime.future_shadow_outcome.mr_f5_6.v1":
            raise ValueError("future_shadow_dry_run_schema_version_invalid")
        if self.source_role != "hot_data_root" or self.destination_role != "hot_data_root":
            raise ValueError("future_shadow_dry_run_data_role_invalid")
        if self.namespace != "prediction/market_regime/future_shadow":
            raise ValueError("future_shadow_dry_run_namespace_invalid")
        try:
            parsed_partition = datetime.strptime(self.partition_key, "%Y-%m-%d").date()
        except ValueError as exc:
            raise ValueError("future_shadow_dry_run_partition_key_invalid") from exc
        if parsed_partition.isoformat() != self.partition_key:
            raise ValueError("future_shadow_dry_run_partition_key_invalid")


@dataclass(frozen=True)
class FutureShadowDryRunPolicy:
    disabled_by_default: bool
    scheduler_registration_allowed: bool
    canonical_path_overlap_allowed: bool
    append_only_required: bool
    atomic_temp_then_replace_required: bool
    duplicate_prevention_required: bool
    retention_policy_ref: str
    rollback_plan_ref: str
    maximum_batch_rows: int

    def __post_init__(self) -> None:
        for name in (
            "disabled_by_default", "scheduler_registration_allowed",
            "canonical_path_overlap_allowed", "append_only_required",
            "atomic_temp_then_replace_required", "duplicate_prevention_required",
        ):
            if type(getattr(self, name)) is not bool:
                raise ValueError(f"future_shadow_dry_run_policy_boolean_invalid:{name}")
        if self.disabled_by_default is not True:
            raise ValueError("future_shadow_dry_run_must_be_disabled_by_default")
        if self.scheduler_registration_allowed is not False:
            raise ValueError("future_shadow_dry_run_scheduler_registration_forbidden")
        if self.canonical_path_overlap_allowed is not False:
            raise ValueError("future_shadow_dry_run_canonical_overlap_forbidden")
        if self.append_only_required is not True:
            raise ValueError("future_shadow_dry_run_append_only_required")
        if self.atomic_temp_then_replace_required is not True:
            raise ValueError("future_shadow_dry_run_atomic_write_required")
        if self.duplicate_prevention_required is not True:
            raise ValueError("future_shadow_dry_run_duplicate_prevention_required")
        for name in ("retention_policy_ref", "rollback_plan_ref"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"future_shadow_dry_run_policy_ref_missing:{name}")
        if isinstance(self.maximum_batch_rows, bool) or not isinstance(self.maximum_batch_rows, int) or self.maximum_batch_rows <= 0:
            raise ValueError("future_shadow_dry_run_maximum_batch_rows_invalid")


@dataclass(frozen=True)
class FutureShadowDryRunBatch:
    generated_at: str
    writer_id: str
    writer_contract_version: str
    trace_ids: Tuple[str, ...]
    row_payload_hashes: Tuple[str, ...]
    artifact_identity: FutureShadowDryRunArtifactIdentity
    policy: FutureShadowDryRunPolicy

    def __post_init__(self) -> None:
        generated = _parse_canonical_utc(self.generated_at, "future_shadow_dry_run_generated_at_invalid")
        if generated.date().isoformat() != self.artifact_identity.partition_key:
            raise ValueError("future_shadow_dry_run_partition_generated_at_mismatch")
        for name in ("writer_id", "writer_contract_version"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"future_shadow_dry_run_writer_identity_missing:{name}")
        trace_ids = _non_empty_tuple(self.trace_ids, "future_shadow_dry_run_trace_ids_missing")
        hashes = _non_empty_tuple(self.row_payload_hashes, "future_shadow_dry_run_payload_hashes_missing")
        if len(trace_ids) != len(self.trace_ids):
            raise ValueError("future_shadow_dry_run_duplicate_trace_id")
        if len(hashes) != len(self.row_payload_hashes):
            raise ValueError("future_shadow_dry_run_duplicate_payload_hash")
        if len(trace_ids) != len(hashes):
            raise ValueError("future_shadow_dry_run_trace_hash_count_mismatch")
        if len(trace_ids) > self.policy.maximum_batch_rows:
            raise ValueError("future_shadow_dry_run_batch_limit_exceeded")
        for value in hashes:
            if len(value) != 64 or any(ch not in "0123456789abcdef" for ch in value):
                raise ValueError("future_shadow_dry_run_payload_hash_invalid")
        ordered_pairs = tuple(sorted(zip(trace_ids, hashes), key=lambda item: item[0]))
        object.__setattr__(self, "trace_ids", tuple(item[0] for item in ordered_pairs))
        object.__setattr__(self, "row_payload_hashes", tuple(item[1] for item in ordered_pairs))


def deterministic_shadow_row_hash(row: Mapping[str, Any]) -> str:
    if not isinstance(row, Mapping):
        raise ValueError("future_shadow_dry_run_row_not_mapping")
    required = (
        "schema_version", "artifact_family", "artifact_kind", "trace_id",
        "target_horizon_sec", "model_id", "logic_version", "parameter_set_id",
        "feature_snapshot_ref", "outcome_status",
    )
    for key in required:
        if key not in row or row[key] in (None, ""):
            raise ValueError(f"future_shadow_dry_run_row_identity_missing:{key}")
    canonical = json.dumps(dict(row), ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def build_market_regime_future_shadow_writer_dry_run(
    *,
    batch: FutureShadowDryRunBatch,
) -> Mapping[str, Any]:
    dedupe_source = "|".join((
        batch.writer_id,
        batch.writer_contract_version,
        batch.artifact_identity.namespace,
        batch.artifact_identity.partition_key,
        *batch.trace_ids,
        *batch.row_payload_hashes,
    ))
    dedupe_key = hashlib.sha256(dedupe_source.encode("utf-8")).hexdigest()

    return MappingProxyType({
        "schema_version": MARKET_REGIME_FUTURE_SHADOW_WRITER_DRY_RUN_VERSION,
        "artifact_family": "prediction/market_regime",
        "artifact_kind": "future_shadow_writer_dry_run",
        "writer_id": batch.writer_id,
        "writer_contract_version": batch.writer_contract_version,
        "generated_at": batch.generated_at,
        "source_role": batch.artifact_identity.source_role,
        "destination_role": batch.artifact_identity.destination_role,
        "namespace": batch.artifact_identity.namespace,
        "partition_key": batch.artifact_identity.partition_key,
        "target_artifact_family": batch.artifact_identity.artifact_family,
        "target_artifact_kind": batch.artifact_identity.artifact_kind,
        "target_schema_version": batch.artifact_identity.schema_version,
        "trace_ids": batch.trace_ids,
        "row_payload_hashes": batch.row_payload_hashes,
        "row_count": len(batch.trace_ids),
        "dedupe_key": dedupe_key,
        "retention_policy_ref": batch.policy.retention_policy_ref,
        "rollback_plan_ref": batch.policy.rollback_plan_ref,
        "write_plan": MappingProxyType({
            "disabled_by_default": True,
            "scheduler_registration_allowed": False,
            "canonical_path_overlap_allowed": False,
            "append_only_required": True,
            "atomic_temp_then_replace_required": True,
            "duplicate_prevention_required": True,
            "maximum_batch_rows": batch.policy.maximum_batch_rows,
        }),
        "dry_run_only": True,
        "counts_as_real_shadow_evidence": False,
        "execution_performed": False,
        "writer_registered": False,
        "write_allowed": False,
        "safety": MappingProxyType({
            "pure_plan": True,
            "runtime_reader_invoked": False,
            "writer_invoked": False,
            "writes_dhot": False,
            "canonical_replacement": False,
            "parameter_auto_promotion_allowed": False,
            "live_parameter_apply_allowed": False,
            "ui_change": False,
        }),
    })
