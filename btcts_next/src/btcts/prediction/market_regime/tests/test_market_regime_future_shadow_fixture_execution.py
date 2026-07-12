# path: ./btcts_next/src/btcts/prediction/market_regime/tests/test_market_regime_future_shadow_fixture_execution.py
# desc: MR-F5.17 fixture-root end-to-end execution and family-readiness re-audit tests.

from __future__ import annotations

from pathlib import Path

from btcts.prediction.market_regime.contracts import MarketRegimeCode
from btcts.prediction.market_regime.future_baseline_model import FutureBaselineEvidence, forecast_future_market_regime_baseline
from btcts.prediction.market_regime.future_forecast_contract import FUTURE_MARKET_REGIME_HORIZONS_SEC
from btcts.prediction.market_regime.future_shadow_adapter import MarketRegimeFutureShadowPacket
from btcts.prediction.market_regime.future_shadow_execution_boundary import FutureShadowOperatorApproval, FutureShadowWriterDesign
from btcts.prediction.market_regime.future_shadow_fixture_execution import run_market_regime_future_shadow_fixture_execution

CHECKPOINTS = (
    "MR_F5_1_FUTURE_FORECAST_CONTRACT_AND_LEGACY_PATH_AUDIT_ACCEPTED",
    "MR_F5_2_TARGET_DEFINITION_AND_FEATURE_AVAILABILITY_ACCEPTED",
    "MR_F5_3_TRANSPARENT_BASELINE_MODEL_ACCEPTED",
    "MR_F5_4_EXPLICIT_EVIDENCE_ADAPTER_AND_SHADOW_PACKET_ACCEPTED",
    "MR_F5_5_SHADOW_TRACE_AND_OUTCOME_IDENTITY_ACCEPTED",
    "MR_F5_6_SHADOW_OUTCOME_RESOLUTION_AND_EVALUATION_ROW_ACCEPTED",
    "MR_F5_7_SHADOW_EVALUATION_AGGREGATION_AND_CANDIDATE_COMPARISON_ACCEPTED",
)


def _packet() -> MarketRegimeFutureShadowPacket:
    forecasts = tuple(
        forecast_future_market_regime_baseline(FutureBaselineEvidence(
            origin_timestamp="2026-07-12T00:00:00Z",
            origin_current_state=MarketRegimeCode.LOW_VOL_COMPRESSION,
            target_horizon_sec=horizon,
            feature_snapshot_ref="snapshot:mr-f5.17",
            regime_scores={MarketRegimeCode.BREAKOUT: 0.8, MarketRegimeCode.RANGE: 0.2},
            available_feature_families=("price_structure", "volatility", "liquidity", "microprice", "source_quality", "session_context"),
            source_timestamp_epoch_sec=100.0,
            origin_timestamp_epoch_sec=100.0,
        ))
        for horizon in FUTURE_MARKET_REGIME_HORIZONS_SEC
    )
    return MarketRegimeFutureShadowPacket(
        generated_at="2026-07-12T00:00:00Z",
        origin_current_state=MarketRegimeCode.LOW_VOL_COMPRESSION,
        feature_snapshot_ref="snapshot:mr-f5.17",
        forecasts=forecasts,
    )


def _design() -> FutureShadowWriterDesign:
    return FutureShadowWriterDesign(
        writer_id="market-regime-shadow-writer",
        writer_contract_version="writer.v1",
        source_role="hot_data_root", destination_role="hot_data_root",
        artifact_family="prediction/market_regime", artifact_kind="future_shadow_evidence",
        retention_policy_ref="docs/retention/mr-f5.17.md",
        rollback_plan_ref="docs/rollback/mr-f5.17.md",
        dry_run_evidence_refs=("fixture:dry-run",),
        duplicate_prevention_verified=True, atomic_write_verified=True,
        append_only_verified=True, canonical_isolation_verified=True,
    )


def _approval() -> FutureShadowOperatorApproval:
    return FutureShadowOperatorApproval(
        approval_id="approval:mr-f5.17:fixture", operator_ids=("operator:fixture",),
        requested_at="2026-07-12T00:00:00Z", expires_at="2026-07-14T00:00:00Z",
        approved_writer_id="market-regime-shadow-writer",
        approved_writer_contract_version="writer.v1",
        approved_artifact_family="prediction/market_regime",
        approved_artifact_kind="future_shadow_evidence",
        approved_source_role="hot_data_root", approved_destination_role="hot_data_root",
        approval_artifact_refs=("fixture:approval",),
        dry_run_reviewed=True, retention_reviewed=True, rollback_reviewed=True,
        canonical_isolation_reviewed=True, limited_shadow_scope_reviewed=True,
    )


def test_fixture_root_end_to_end_executes_exact_chain_but_does_not_claim_family_ready(tmp_path: Path) -> None:
    result = run_market_regime_future_shadow_fixture_execution(
        tmp_path,
        packet=_packet(),
        polled_at="2026-07-13T00:01:00Z",
        observation_reader=lambda trace, at: {
            "observation_available": True,
            "observed_at": trace.expiry_at,
            "observed_future_state": MarketRegimeCode.BREAKOUT,
            "observation_source_ref": f"fixture:closed-candle:{trace.target_horizon_key}",
        },
        writer_design=_design(),
        operator_approval=_approval(),
        accepted_checkpoints=CHECKPOINTS,
    )
    assert result["mr_f5_fixture_execution_completed"] is True
    assert result["trace_count"] == len(FUTURE_MARKET_REGIME_HORIZONS_SEC)
    assert result["exact_row_count"] == len(FUTURE_MARKET_REGIME_HORIZONS_SEC)
    assert result["fixture_execution_audit"]["real_shadow_evidence_accepted"] is True
    assert result["fixture_shadow_evidence_accepted"] is True
    assert result["real_shadow_evidence_accepted"] is False
    assert result["family_readiness"]["family_ready_for_next_family"] is False
    assert "representative_feature_availability_not_proven" in result["family_readiness"]["blockers"]
    assert "shadow_candidate_comparison_not_ready" in result["family_readiness"]["blockers"]
    assert "canonical_migration_review_not_completed" in result["family_readiness"]["blockers"]
    assert result["real_d_hot_modified"] is False
    assert (tmp_path / result["trace_artifact_relpath"]).exists()
    assert (tmp_path / result["shadow_artifact_relpath"]).exists()


def test_fixture_execution_rejects_nonempty_unmarked_root(tmp_path: Path) -> None:
    (tmp_path / "existing.txt").write_text("not a fixture root", encoding="utf-8")
    try:
        run_market_regime_future_shadow_fixture_execution(
            tmp_path, packet=_packet(), polled_at="2026-07-13T00:01:00Z",
            observation_reader=lambda trace, at: None,
            writer_design=_design(), operator_approval=_approval(), accepted_checkpoints=CHECKPOINTS,
        )
    except ValueError as exc:
        assert str(exc) == "future_shadow_fixture_root_marker_missing"
    else:
        raise AssertionError("nonempty unmarked root must be rejected")


def test_fixture_execution_is_idempotent_on_same_root(tmp_path: Path) -> None:
    kwargs = dict(
        packet=_packet(), polled_at="2026-07-13T00:01:00Z",
        observation_reader=lambda trace, at: {
            "observation_available": True, "observed_at": trace.expiry_at,
            "observed_future_state": MarketRegimeCode.BREAKOUT,
            "observation_source_ref": "fixture:closed-candle",
        },
        writer_design=_design(), operator_approval=_approval(), accepted_checkpoints=CHECKPOINTS,
    )
    first = run_market_regime_future_shadow_fixture_execution(tmp_path, **kwargs)
    second = run_market_regime_future_shadow_fixture_execution(tmp_path, **kwargs)
    assert first["shadow_artifact_relpath"] == second["shadow_artifact_relpath"]
    assert second["trace_persisted"] is True
    assert second["shadow_batch_written"] is True
