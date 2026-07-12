# path: ./btcts_next/src/btcts/prediction/market_regime/tests/test_market_regime_future_shadow_writer_dry_run.py
# desc: MR-F5.11 disabled-by-default writer dry-run schema and artifact isolation tests.

from __future__ import annotations

import pytest

from btcts.prediction.market_regime.future_shadow_writer_dry_run import (
    FutureShadowDryRunArtifactIdentity,
    FutureShadowDryRunBatch,
    FutureShadowDryRunPolicy,
    build_market_regime_future_shadow_writer_dry_run,
    deterministic_shadow_row_hash,
)


def _identity(**overrides) -> FutureShadowDryRunArtifactIdentity:
    values = {
        "artifact_family": "prediction/market_regime",
        "artifact_kind": "future_shadow_evidence",
        "schema_version": "prediction.market_regime.future_shadow_outcome.mr_f5_6.v1",
        "source_role": "hot_data_root",
        "destination_role": "hot_data_root",
        "namespace": "prediction/market_regime/future_shadow",
        "partition_key": "2026-07-12",
    }
    values.update(overrides)
    return FutureShadowDryRunArtifactIdentity(**values)


def _policy(**overrides) -> FutureShadowDryRunPolicy:
    values = {
        "disabled_by_default": True,
        "scheduler_registration_allowed": False,
        "canonical_path_overlap_allowed": False,
        "append_only_required": True,
        "atomic_temp_then_replace_required": True,
        "duplicate_prevention_required": True,
        "retention_policy_ref": "docs/retention/mr-f5.11.md",
        "rollback_plan_ref": "docs/rollback/mr-f5.11.md",
        "maximum_batch_rows": 100,
    }
    values.update(overrides)
    return FutureShadowDryRunPolicy(**values)


def _row(trace: str) -> dict:
    return {
        "schema_version": "prediction.market_regime.future_shadow_outcome.mr_f5_6.v1",
        "artifact_family": "prediction/market_regime",
        "artifact_kind": "future_shadow_evaluation_row",
        "trace_id": trace,
        "target_horizon_sec": 300,
        "model_id": "model.v1",
        "logic_version": "logic.v1",
        "parameter_set_id": "params.v1",
        "feature_snapshot_ref": f"snapshot:{trace}",
        "outcome_status": "CORRECT",
    }


def _batch() -> FutureShadowDryRunBatch:
    hashes = tuple(deterministic_shadow_row_hash(_row(trace)) for trace in ("t1", "t2"))
    return FutureShadowDryRunBatch(
        generated_at="2026-07-12T12:00:00Z",
        writer_id="market-regime-shadow-writer",
        writer_contract_version="writer.v1",
        trace_ids=("t1", "t2"),
        row_payload_hashes=hashes,
        artifact_identity=_identity(),
        policy=_policy(),
    )


def test_dry_run_is_disabled_isolated_and_never_counts_as_real_evidence() -> None:
    plan = build_market_regime_future_shadow_writer_dry_run(batch=_batch())
    assert plan["dry_run_only"] is True
    assert plan["counts_as_real_shadow_evidence"] is False
    assert plan["execution_performed"] is False
    assert plan["writer_registered"] is False
    assert plan["write_allowed"] is False
    assert plan["write_plan"]["canonical_path_overlap_allowed"] is False


def test_deterministic_hash_and_dedupe_key_are_stable() -> None:
    row = _row("stable")
    assert deterministic_shadow_row_hash(row) == deterministic_shadow_row_hash(dict(reversed(tuple(row.items()))))
    first = build_market_regime_future_shadow_writer_dry_run(batch=_batch())
    reversed_batch = FutureShadowDryRunBatch(
        generated_at="2026-07-12T12:00:00Z",
        writer_id="market-regime-shadow-writer",
        writer_contract_version="writer.v1",
        trace_ids=("t2", "t1"),
        row_payload_hashes=(
            deterministic_shadow_row_hash(_row("t2")),
            deterministic_shadow_row_hash(_row("t1")),
        ),
        artifact_identity=_identity(),
        policy=_policy(),
    )
    second = build_market_regime_future_shadow_writer_dry_run(batch=reversed_batch)
    assert first["dedupe_key"] == second["dedupe_key"]
    assert len(first["dedupe_key"]) == 64


def test_duplicate_trace_or_hash_fails_closed() -> None:
    value = deterministic_shadow_row_hash(_row("t1"))
    with pytest.raises(ValueError, match="future_shadow_dry_run_duplicate_trace_id"):
        FutureShadowDryRunBatch(
            generated_at="2026-07-12T12:00:00Z", writer_id="w", writer_contract_version="v1",
            trace_ids=("t1", "t1"), row_payload_hashes=(value, value), artifact_identity=_identity(), policy=_policy(),
        )


def test_batch_limit_and_hash_shape_fail_closed() -> None:
    value = deterministic_shadow_row_hash(_row("t1"))
    with pytest.raises(ValueError, match="future_shadow_dry_run_batch_limit_exceeded"):
        FutureShadowDryRunBatch(
            generated_at="2026-07-12T12:00:00Z", writer_id="w", writer_contract_version="v1",
            trace_ids=("t1", "t2"), row_payload_hashes=(value, deterministic_shadow_row_hash(_row("t2"))),
            artifact_identity=_identity(), policy=_policy(maximum_batch_rows=1),
        )
    with pytest.raises(ValueError, match="future_shadow_dry_run_payload_hash_invalid"):
        FutureShadowDryRunBatch(
            generated_at="2026-07-12T12:00:00Z", writer_id="w", writer_contract_version="v1",
            trace_ids=("t1",), row_payload_hashes=("bad",), artifact_identity=_identity(), policy=_policy(),
        )


def test_policy_cannot_enable_scheduler_or_canonical_overlap() -> None:
    with pytest.raises(ValueError, match="future_shadow_dry_run_scheduler_registration_forbidden"):
        _policy(scheduler_registration_allowed=True)
    with pytest.raises(ValueError, match="future_shadow_dry_run_canonical_overlap_forbidden"):
        _policy(canonical_path_overlap_allowed=True)


def test_schema_and_partition_identity_fail_closed() -> None:
    with pytest.raises(ValueError, match="future_shadow_dry_run_schema_version_invalid"):
        _identity(schema_version="wrong")
    with pytest.raises(ValueError, match="future_shadow_dry_run_partition_key_invalid"):
        _identity(partition_key="2026-7-12")
    with pytest.raises(ValueError, match="future_shadow_dry_run_partition_generated_at_mismatch"):
        FutureShadowDryRunBatch(
            generated_at="2026-07-13T00:00:00Z",
            writer_id="w", writer_contract_version="v1",
            trace_ids=("t1",),
            row_payload_hashes=(deterministic_shadow_row_hash(_row("t1")),),
            artifact_identity=_identity(), policy=_policy(),
        )


def test_physical_or_cold_roles_and_wrong_namespace_are_rejected() -> None:
    with pytest.raises(ValueError, match="future_shadow_dry_run_data_role_invalid"):
        _identity(source_role="cold_data_root")
    with pytest.raises(ValueError, match="future_shadow_dry_run_data_role_invalid"):
        _identity(destination_role="D:/btc_ts_hot")
    with pytest.raises(ValueError, match="future_shadow_dry_run_namespace_invalid"):
        _identity(namespace="prediction/latest")


def test_public_plan_is_immutable() -> None:
    plan = build_market_regime_future_shadow_writer_dry_run(batch=_batch())
    with pytest.raises(TypeError): plan["write_allowed"] = True
    with pytest.raises(TypeError): plan["write_plan"]["disabled_by_default"] = False
    with pytest.raises(TypeError): plan["safety"]["writes_dhot"] = True
