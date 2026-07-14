# path: ./btcts_next/src/btcts/prediction/market_regime/tests/test_market_regime_future_origin_evidence_collection_plan.py
# desc: MR-F6.14 tests for fail-closed operational evidence collection readiness planning.

from __future__ import annotations

import pytest

from btcts.prediction.market_regime.future_origin_evidence_collection_plan import (
    OriginEvidenceCollectionPolicy,
    build_origin_evidence_collection_plan,
)
from btcts.prediction.market_regime.future_origin_evidence_runtime_source import (
    MARKET_REGIME_ORIGIN_EVIDENCE_RUNTIME_SOURCE_VERSION,
)


def _policy(**overrides: object) -> OriginEvidenceCollectionPolicy:
    values = dict(
        policy_id="fixture.explicit.v1",
        minimum_origin_batches=20,
        minimum_observed_slots_per_horizon=20,
    )
    values.update(overrides)
    return OriginEvidenceCollectionPolicy(**values)


def _observed(count: int = 0) -> dict[int, int]:
    return {horizon: count for horizon in (300, 900, 1800, 3600, 21600, 43200, 86400)}


def _runtime(*, ready: bool, blockers: tuple[str, ...] = ()) -> dict[str, object]:
    return {
        "schema_version": MARKET_REGIME_ORIGIN_EVIDENCE_RUNTIME_SOURCE_VERSION,
        "artifact_kind": "future_origin_evidence_runtime_source_readiness",
        "runtime_source_ready": ready,
        "blockers": blockers,
        "semantic_substitution_used": False,
        "writer_invoked": False,
        "writes_dhot": False,
        "scheduler_enabled": False,
        "canonical_replacement": False,
        "live_parameter_apply_allowed": False,
    }


def test_current_empty_namespace_and_unready_runtime_fail_closed() -> None:
    result = build_origin_evidence_collection_plan(
        generated_at="2026-07-14T00:00:00Z",
        policy=_policy(),
        runtime_source_readiness=_runtime(
            ready=False,
            blockers=(
                "origin_runtime_source_missing:fast_ma",
                "origin_runtime_source_missing:slow_ma",
            ),
        ),
        existing_artifact_relpaths=(),
        observed_slot_count_by_horizon=_observed(),
        operator_approval_present=False,
    )
    assert result["collection_start_ready"] is False
    assert result["evaluation_ready"] is False
    assert "runtime_source_not_ready" in result["blockers"]
    assert "origin_evidence_namespace_empty" in result["blockers"]
    assert "operator_approval_missing" in result["blockers"]


def test_runtime_ready_without_approval_still_cannot_start_collection() -> None:
    result = build_origin_evidence_collection_plan(
        generated_at="2026-07-14T00:00:00Z",
        policy=_policy(),
        runtime_source_readiness=_runtime(ready=True),
        existing_artifact_relpaths=(),
        observed_slot_count_by_horizon=_observed(),
        operator_approval_present=False,
    )
    assert result["collection_start_ready"] is False
    assert result["writer_activation_performed"] is False
    assert result["writes_dhot"] is False


def test_ready_inputs_only_describe_collection_readiness_without_writing() -> None:
    result = build_origin_evidence_collection_plan(
        generated_at="2026-07-14T00:00:00Z",
        policy=_policy(minimum_origin_batches=2),
        runtime_source_readiness=_runtime(ready=True),
        existing_artifact_relpaths=(
            "prediction/market_regime/future_origin_evidence/date=2026-07-14/batch-a.json",
            "prediction/market_regime/future_origin_evidence/date=2026-07-14/batch-b.json",
        ),
        observed_slot_count_by_horizon=_observed(20),
        operator_approval_present=True,
    )
    assert result["collection_start_ready"] is True
    assert result["evaluation_ready"] is True
    assert result["writer_invoked"] is False
    assert result["writes_dhot"] is False
    assert result["selection_performed"] is False


def test_all_seven_horizon_requirements_are_explicit() -> None:
    result = build_origin_evidence_collection_plan(
        generated_at="2026-07-14T00:00:00Z",
        policy=_policy(),
        runtime_source_readiness=_runtime(ready=True),
        existing_artifact_relpaths=(),
        observed_slot_count_by_horizon=_observed(),
        operator_approval_present=True,
    )
    assert tuple(item["target_horizon_sec"] for item in result["horizon_requirements"]) == (
        300, 900, 1800, 3600, 21600, 43200, 86400,
    )
    assert all(item["minimum_observed_slots"] == 20 for item in result["horizon_requirements"])


def test_evaluation_requires_every_horizon_observation_threshold() -> None:
    counts = _observed(20)
    counts[86400] = 19
    result = build_origin_evidence_collection_plan(
        generated_at="2026-07-14T00:00:00Z",
        policy=_policy(minimum_origin_batches=2),
        runtime_source_readiness=_runtime(ready=True),
        existing_artifact_relpaths=(
            "prediction/market_regime/future_origin_evidence/date=2026-07-14/batch-a.json",
            "prediction/market_regime/future_origin_evidence/date=2026-07-14/batch-b.json",
        ),
        observed_slot_count_by_horizon=counts,
        operator_approval_present=True,
    )
    assert result["collection_start_ready"] is True
    assert result["evaluation_ready"] is False
    assert "minimum_observed_slots_not_met:86400" in result["blockers"]


def test_observation_inventory_requires_exact_seven_horizons() -> None:
    with pytest.raises(ValueError, match="observation_horizons_mismatch"):
        build_origin_evidence_collection_plan(
            generated_at="2026-07-14T00:00:00Z",
            policy=_policy(),
            runtime_source_readiness=_runtime(ready=True),
            existing_artifact_relpaths=(),
            observed_slot_count_by_horizon={300: 0},
        )


def test_foreign_or_duplicate_inventory_fails_closed() -> None:
    with pytest.raises(ValueError, match="foreign_artifact_path"):
        build_origin_evidence_collection_plan(
            generated_at="2026-07-14T00:00:00Z", policy=_policy(),
            runtime_source_readiness=_runtime(ready=True),
            existing_artifact_relpaths=("prediction/market_regime/other/x.json",),
            observed_slot_count_by_horizon=_observed(),
        )
    path = "prediction/market_regime/future_origin_evidence/date=2026-07-14/batch-a.json"
    with pytest.raises(ValueError, match="duplicate_artifact_relpath"):
        build_origin_evidence_collection_plan(
            generated_at="2026-07-14T00:00:00Z", policy=_policy(),
            runtime_source_readiness=_runtime(ready=True),
            existing_artifact_relpaths=(path, path),
            observed_slot_count_by_horizon=_observed(),
        )


def test_runtime_readiness_and_blockers_must_be_structurally_consistent() -> None:
    runtime = _runtime(ready=True, blockers=("unexpected",))
    with pytest.raises(ValueError, match="ready_runtime_has_blockers"):
        build_origin_evidence_collection_plan(
            generated_at="2026-07-14T00:00:00Z", policy=_policy(),
            runtime_source_readiness=runtime, existing_artifact_relpaths=(),
            observed_slot_count_by_horizon=_observed(),
        )

    runtime = _runtime(ready=False)
    runtime["blockers"] = "not-a-sequence-of-blockers"
    with pytest.raises(ValueError, match="runtime_blockers_invalid"):
        build_origin_evidence_collection_plan(
            generated_at="2026-07-14T00:00:00Z", policy=_policy(),
            runtime_source_readiness=runtime, existing_artifact_relpaths=(),
            observed_slot_count_by_horizon=_observed(),
        )


def test_policy_and_observation_counts_require_strict_integers() -> None:
    with pytest.raises(ValueError, match="count_invalid"):
        _policy(minimum_origin_batches=1.5)

    counts = _observed()
    counts[300] = 20.0
    with pytest.raises(ValueError, match="observation_inventory_invalid"):
        build_origin_evidence_collection_plan(
            generated_at="2026-07-14T00:00:00Z", policy=_policy(),
            runtime_source_readiness=_runtime(ready=True),
            existing_artifact_relpaths=(),
            observed_slot_count_by_horizon=counts,
        )


def test_policy_requires_exact_horizon_contract_and_positive_counts() -> None:
    with pytest.raises(ValueError, match="horizons_invalid"):
        _policy(required_horizons_sec=(300,))
    with pytest.raises(ValueError, match="count_invalid"):
        _policy(minimum_origin_batches=0)
