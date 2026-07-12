# path: ./btcts_next/src/btcts/prediction/market_regime/future_shadow_fixture_execution.py
# desc: MR-F5.17 fixture-root-only end-to-end shadow runtime execution and family-readiness re-audit orchestrator.

from __future__ import annotations

import json
from pathlib import Path
from types import MappingProxyType
from typing import Any, Callable, Mapping, Tuple

from .future_shadow_adapter import MarketRegimeFutureShadowPacket
from .future_shadow_evaluation import build_market_regime_future_shadow_evaluation
from .future_shadow_execution_audit import (
    EXPECTED_BOUNDARY_VERSION,
    EXPECTED_DRY_RUN_VERSION,
    EXPECTED_WRITER_VERSION,
    FutureShadowExecutionApprovalArtifact,
    FutureShadowPostWriteAudit,
    FutureShadowSourceAudit,
    build_market_regime_future_shadow_execution_audit,
)
from .future_shadow_execution_boundary import (
    FutureShadowExecutionMode,
    FutureShadowOperatorApproval,
    FutureShadowWriterDesign,
    build_market_regime_future_shadow_execution_boundary,
)
from .future_shadow_readiness import (
    MarketRegimeFamilyCompletionEvidence,
    build_market_regime_future_shadow_readiness,
)
from .future_shadow_runtime_adapter import capture_market_regime_future_shadow_traces
from .future_shadow_runtime_persistence import (
    build_future_shadow_trace_persistence_plan,
    persist_future_shadow_traces_once,
    poll_future_shadow_observations,
)
from .future_shadow_source_batch import (
    FutureShadowObservationWindow,
    build_market_regime_future_shadow_source_batch,
)
from .future_shadow_writer_dry_run import (
    FutureShadowDryRunArtifactIdentity,
    FutureShadowDryRunBatch,
    FutureShadowDryRunPolicy,
    build_market_regime_future_shadow_writer_dry_run,
    deterministic_shadow_row_hash,
)
from .tools.write_future_shadow import write_market_regime_future_shadow_once

FIXTURE_EXECUTION_VERSION = "prediction.market_regime.future_shadow_fixture_execution.mr_f5_17.v1"
FIXTURE_MARKER = ".mr_f5_17_fixture_root"


def run_market_regime_future_shadow_fixture_execution(
    fixture_root: str | Path,
    *,
    packet: MarketRegimeFutureShadowPacket,
    polled_at: str,
    observation_reader: Callable,
    writer_design: FutureShadowWriterDesign,
    operator_approval: FutureShadowOperatorApproval,
    accepted_checkpoints: Tuple[str, ...],
    representative_feature_availability_proven: bool = False,
    canonical_migration_review_completed: bool = False,
) -> Mapping[str, Any]:
    root = Path(fixture_root)
    if str(root).strip() in ("", "."):
        raise ValueError("future_shadow_fixture_root_unsafe")
    if root.exists() and not root.is_dir():
        raise ValueError("future_shadow_fixture_root_invalid")
    marker = root / FIXTURE_MARKER
    if root.exists():
        entries = tuple(root.iterdir())
        if entries and not marker.is_file():
            raise ValueError("future_shadow_fixture_root_marker_missing")
    else:
        root.mkdir(parents=True, exist_ok=False)
    if not marker.exists():
        marker.write_text(FIXTURE_EXECUTION_VERSION + "\n", encoding="utf-8", newline="")
    elif marker.read_text(encoding="utf-8") != FIXTURE_EXECUTION_VERSION + "\n":
        raise ValueError("future_shadow_fixture_root_marker_invalid")

    traces = capture_market_regime_future_shadow_traces(packet)
    trace_plan = build_future_shadow_trace_persistence_plan(
        traces=traces, generated_at=packet.generated_at
    )
    trace_write = persist_future_shadow_traces_once(
        root, plan=trace_plan, enabled=True, once=True
    )

    evidence = poll_future_shadow_observations(
        traces=traces, polled_at=polled_at, observation_reader=observation_reader
    )
    window = FutureShadowObservationWindow(
        window_id=f"fixture:{packet.generated_at}",
        opened_at=packet.generated_at,
        evaluated_at=polled_at,
        source_role="hot_data_root",
        source_refs=(str(trace_write["artifact_relpath"]),),
        minimum_resolved_rows=len(traces),
    )
    source_batch = build_market_regime_future_shadow_source_batch(
        traces=traces,
        evidence_by_trace_id=evidence,
        observation_window=window,
    )
    rows = tuple(dict(item) for item in source_batch["rows"])
    if source_batch["write_approval_candidate"] is not True:
        raise RuntimeError("future_shadow_fixture_source_batch_not_ready")

    dry_batch = FutureShadowDryRunBatch(
        generated_at=polled_at,
        writer_id=writer_design.writer_id,
        writer_contract_version=writer_design.writer_contract_version,
        trace_ids=tuple(row["trace_id"] for row in rows),
        row_payload_hashes=tuple(deterministic_shadow_row_hash(row) for row in rows),
        artifact_identity=FutureShadowDryRunArtifactIdentity(
            artifact_family="prediction/market_regime",
            artifact_kind="future_shadow_evidence",
            schema_version="prediction.market_regime.future_shadow_outcome.mr_f5_6.v1",
            source_role="hot_data_root",
            destination_role="hot_data_root",
            namespace="prediction/market_regime/future_shadow",
            partition_key=polled_at[:10],
        ),
        policy=FutureShadowDryRunPolicy(
            disabled_by_default=True,
            scheduler_registration_allowed=False,
            canonical_path_overlap_allowed=False,
            append_only_required=True,
            atomic_temp_then_replace_required=True,
            duplicate_prevention_required=True,
            retention_policy_ref=writer_design.retention_policy_ref,
            rollback_plan_ref=writer_design.rollback_plan_ref,
            maximum_batch_rows=max(len(rows), 1),
        ),
    )
    dry_run = build_market_regime_future_shadow_writer_dry_run(batch=dry_batch)
    boundary = build_market_regime_future_shadow_execution_boundary(
        mode=FutureShadowExecutionMode.APPROVED_SHADOW_WRITE,
        writer_design=writer_design,
        operator_approval=operator_approval,
        evaluated_at=polled_at,
    )
    write_result = write_market_regime_future_shadow_once(
        root,
        dry_run_plan=dry_run,
        approved_boundary=boundary,
        rows=rows,
        executed_at=polled_at,
        enabled=True,
        once=True,
    )
    artifact_path = root / str(write_result["artifact_relpath"])
    payload = json.loads(artifact_path.read_text(encoding="utf-8"))
    persisted_rows = tuple(dict(item) for item in payload["rows"])
    if persisted_rows != rows:
        raise RuntimeError("future_shadow_fixture_persisted_rows_mismatch")
    exact_count = sum(
        1 for row in persisted_rows
        if row.get("schema_version") == "prediction.market_regime.future_shadow_outcome.mr_f5_6.v1"
    )
    if exact_count != len(rows):
        raise RuntimeError("future_shadow_fixture_exact_row_count_mismatch")

    approval_artifact = FutureShadowExecutionApprovalArtifact(
        approval_id=operator_approval.approval_id,
        operator_ids=operator_approval.operator_ids,
        approved_at=operator_approval.requested_at,
        expires_at=operator_approval.expires_at,
        boundary_schema_version=EXPECTED_BOUNDARY_VERSION,
        dry_run_schema_version=EXPECTED_DRY_RUN_VERSION,
        writer_version=EXPECTED_WRITER_VERSION,
        source_role="hot_data_root",
        destination_role="hot_data_root",
        approved_artifact_refs=operator_approval.approval_artifact_refs,
        retention_policy_ref=writer_design.retention_policy_ref,
        rollback_plan_ref=writer_design.rollback_plan_ref,
        limited_batch_scope_ref=f"fixture:{dry_run['dedupe_key']}",
        preflight_artifact_ref=f"fixture-preflight:{dry_run['dedupe_key']}",
        operator_explicit_write_ack=True,
    )
    execution_audit = build_market_regime_future_shadow_execution_audit(
        source_audit=FutureShadowSourceAudit(
            inspected_at=polled_at,
            source_role="hot_data_root",
            source_artifact_refs=(str(write_result["artifact_relpath"]),),
            discovered_row_count=len(payload["rows"]),
            canonical_row_count=0,
            legacy_row_count=0,
            exact_schema_row_count=exact_count,
            trace_identity_verified_count=exact_count,
            outcome_identity_verified_count=exact_count,
            lookahead_violation_count=0,
        ),
        approval=approval_artifact,
        post_write_audit=FutureShadowPostWriteAudit(
            audited_at=polled_at,
            artifact_ref=str(write_result["artifact_relpath"]),
            artifact_schema_version=EXPECTED_WRITER_VERSION,
            writer_version=EXPECTED_WRITER_VERSION,
            row_count=len(payload["rows"]),
            exact_schema_row_count=exact_count,
            trace_identity_verified_count=exact_count,
            outcome_identity_verified_count=exact_count,
            dedupe_key_verified=payload["dedupe_key"] == dry_run["dedupe_key"],
            canonical_isolation_verified=payload["canonical_isolated"] is True,
            append_only_verified=payload["append_only"] is True,
            scheduler_disabled_verified=payload["scheduler_enabled"] is False,
            canonical_replacement_absent=True,
        ),
        evaluated_at=polled_at,
    )

    evaluation = build_market_regime_future_shadow_evaluation(
        rows=rows, minimum_scored_samples=max(len(rows), 1)
    )
    readiness = build_market_regime_future_shadow_readiness(
        evaluation_summary=evaluation,
        completion_evidence=MarketRegimeFamilyCompletionEvidence(
            accepted_checkpoints=accepted_checkpoints,
            representative_feature_availability_proven=representative_feature_availability_proven,
            shadow_observation_window_completed=True,
            shadow_evaluation_row_count=len(rows),
            comparison_ready=bool(evaluation["comparison_ready"]),
            canonical_migration_review_completed=canonical_migration_review_completed,
        ),
    )

    return MappingProxyType({
        "schema_version": FIXTURE_EXECUTION_VERSION,
        "artifact_kind": "future_shadow_fixture_execution",
        "fixture_root_only": True,
        "trace_count": len(traces),
        "exact_row_count": len(rows),
        "trace_artifact_relpath": trace_write["artifact_relpath"],
        "shadow_artifact_relpath": write_result["artifact_relpath"],
        "trace_persisted": bool(trace_write["written"] or trace_write["duplicate"]),
        "shadow_batch_written": bool(write_result["written"] or write_result["duplicate"]),
        "fixture_execution_audit": execution_audit,
        "fixture_shadow_evidence_accepted": bool(execution_audit["real_shadow_evidence_accepted"]),
        "real_shadow_evidence_accepted": False,
        "evaluation_summary": evaluation,
        "family_readiness": readiness,
        "mr_f5_fixture_execution_completed": True,
        "real_d_hot_modified": False,
        "safety": MappingProxyType({
            "fixture_root_only": True,
            "real_d_hot_read": False,
            "real_d_hot_write": False,
            "scheduler_registered": False,
            "canonical_replacement": False,
            "parameter_auto_promotion_allowed": False,
            "live_parameter_apply_allowed": False,
            "ui_change": False,
        }),
    })
