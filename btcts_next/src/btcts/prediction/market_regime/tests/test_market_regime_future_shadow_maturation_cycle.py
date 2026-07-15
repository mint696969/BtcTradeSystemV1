# path: ./btcts_next/src/btcts/prediction/market_regime/tests/test_market_regime_future_shadow_maturation_cycle.py
# desc: MR-F9.5 guards for expiry-gated origin maturation using explicit observations only.

from __future__ import annotations

import pytest

from btcts.prediction.market_regime.contracts import MarketRegimeCode
from btcts.prediction.market_regime.future_baseline_model import FutureBaselineEvidence
from btcts.prediction.market_regime.future_execution_evidence import FutureInferenceMode, RawOutputSemantics
from btcts.prediction.market_regime.future_forecast_contract import FUTURE_MARKET_REGIME_HORIZONS_SEC
from btcts.prediction.market_regime.future_shadow_candidate_pairing import build_future_shadow_candidate_pair
from btcts.prediction.market_regime.future_shadow_maturation_cycle import build_future_shadow_maturation_cycle
from btcts.prediction.market_regime.future_shadow_origin_execution_suite import build_future_shadow_origin_execution_suite
from btcts.prediction.market_regime.future_shadow_origin_receipt import build_future_shadow_origin_receipt
from btcts.prediction.market_regime.future_shadow_pair_execution_plan import FutureExecutionFacts
from btcts.prediction.market_regime.future_shadow_runtime_outcome_intake import FutureShadowPointObservation


def _receipt():
    evidence = {}
    facts = {}
    for horizon in FUTURE_MARKET_REGIME_HORIZONS_SEC:
        item = FutureBaselineEvidence(
            origin_timestamp="2026-07-16T00:00:00Z",
            origin_current_state=MarketRegimeCode.RANGE,
            target_horizon_sec=int(horizon),
            feature_snapshot_ref="snapshot:mr-f9.5",
            regime_scores={MarketRegimeCode.BREAKOUT: 0.61, MarketRegimeCode.RANGE: 0.39},
            available_feature_families=(
                "price_structure", "volatility", "liquidity", "source_quality",
                "microprice", "session_context",
            ),
            source_timestamp_epoch_sec=100.0,
            origin_timestamp_epoch_sec=102.0,
        )
        evidence[int(horizon)] = item
        pair = build_future_shadow_candidate_pair(evidence=item)
        for row in pair["forecasts"]:
            facts[row["trace_id"]] = FutureExecutionFacts(
                inference_mode=FutureInferenceMode.FULL_INFERENCE,
                raw_output_semantics=RawOutputSemantics.SCORE,
                source_freshness_state="FRESH",
                source_age_sec=2.0,
            )
    suite = build_future_shadow_origin_execution_suite(
        evidence_by_horizon=evidence,
        facts_by_trace_id=facts,
    )
    return build_future_shadow_origin_receipt(origin_suite=suite)


def _observation(horizon: int, observed_at: str) -> FutureShadowPointObservation:
    return FutureShadowPointObservation(
        target_horizon_sec=horizon,
        observed_at=observed_at,
        observed_future_state=MarketRegimeCode.RANGE,
        observation_source_ref=f"source:canonical:{horizon}",
    )


def test_partial_expiry_keeps_unexpired_horizons_unresolved() -> None:
    result = build_future_shadow_maturation_cycle(
        origin_receipt=_receipt(),
        observations_by_horizon={300: _observation(300, "2026-07-16T00:05:30Z")},
        polled_at="2026-07-16T00:10:00Z",
    )
    assert result["expired_horizons"] == (300,)
    assert result["pending_horizons"] == (900, 1800, 3600, 21600, 43200, 86400)
    assert result["trace_count"] == 14
    assert result["outcome_intake_report"]["status_counts"]["UNRESOLVED"] == 12
    assert result["would_write"] is False


def test_full_expiry_accepts_all_explicit_observations() -> None:
    observed_at = {
        300: "2026-07-16T00:05:30Z",
        900: "2026-07-16T00:15:30Z",
        1800: "2026-07-16T00:30:30Z",
        3600: "2026-07-16T01:00:30Z",
        21600: "2026-07-16T06:00:30Z",
        43200: "2026-07-16T12:00:30Z",
        86400: "2026-07-17T00:00:30Z",
    }
    observations = {h: _observation(h, ts) for h, ts in observed_at.items()}
    result = build_future_shadow_maturation_cycle(
        origin_receipt=_receipt(),
        observations_by_horizon=observations,
        polled_at="2026-07-17T00:01:00Z",
    )
    assert result["pending_horizons"] == ()
    assert result["expired_horizons"] == tuple(FUTURE_MARKET_REGIME_HORIZONS_SEC)
    assert result["outcome_intake_report"]["full_horizon_window_complete"] is True


def test_observation_before_expiry_fails_closed() -> None:
    with pytest.raises(ValueError, match="observation_before_expiry:900"):
        build_future_shadow_maturation_cycle(
            origin_receipt=_receipt(),
            observations_by_horizon={900: _observation(900, "2026-07-16T00:15:30Z")},
            polled_at="2026-07-16T00:10:00Z",
        )


def test_unknown_observation_horizon_fails_with_specific_error() -> None:
    with pytest.raises(ValueError, match="unknown_observation_horizon:123"):
        build_future_shadow_maturation_cycle(
            origin_receipt=_receipt(),
            observations_by_horizon={123: _observation(300, "2026-07-16T00:05:30Z")},
            polled_at="2026-07-17T00:01:00Z",
        )


def test_tampered_receipt_trace_set_fails_closed() -> None:
    receipt = dict(_receipt())
    receipt["trace_ids"] = tuple(reversed(receipt["trace_ids"]))
    with pytest.raises(ValueError, match="trace_set_mismatch"):
        build_future_shadow_maturation_cycle(
            origin_receipt=receipt,
            observations_by_horizon={},
            polled_at="2026-07-16T00:10:00Z",
        )


def test_no_observation_does_not_infer_historical_state() -> None:
    result = build_future_shadow_maturation_cycle(
        origin_receipt=_receipt(),
        observations_by_horizon={},
        polled_at="2026-07-17T00:01:00Z",
    )
    assert result["outcome_intake_report"]["status_counts"]["UNRESOLVED"] == 14
    assert result["safety"]["historical_state_inference_forbidden"] is True
