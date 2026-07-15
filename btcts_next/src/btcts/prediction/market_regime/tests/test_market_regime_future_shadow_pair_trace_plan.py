# path: ./btcts_next/src/btcts/prediction/market_regime/tests/test_market_regime_future_shadow_pair_trace_plan.py
# desc: MR-F8.6 tests for paired forecast to disabled trace-persistence-plan bridging.

from __future__ import annotations

import pytest

from btcts.prediction.market_regime.contracts import MarketRegimeCode
from btcts.prediction.market_regime.future_baseline_model import FutureBaselineEvidence
from btcts.prediction.market_regime.future_shadow_candidate_pairing import build_future_shadow_candidate_pair
from btcts.prediction.market_regime.future_shadow_pair_trace_plan import build_future_shadow_pair_trace_plan


def pair() -> dict:
    evidence = FutureBaselineEvidence(
        origin_timestamp="2026-07-15T00:00:00Z",
        origin_current_state=MarketRegimeCode.RANGE,
        target_horizon_sec=900,
        feature_snapshot_ref="snapshot:mr-f8.6-trace-plan",
        regime_scores={MarketRegimeCode.BREAKOUT: 0.44, MarketRegimeCode.RANGE: 0.34, MarketRegimeCode.UP_TREND: 0.22},
        available_feature_families=("price_structure", "volatility", "liquidity", "source_quality", "microprice"),
        source_timestamp_epoch_sec=100.0,
        origin_timestamp_epoch_sec=100.0,
    )
    return dict(build_future_shadow_candidate_pair(evidence=evidence))


def test_builds_disabled_append_only_trace_plan() -> None:
    result = build_future_shadow_pair_trace_plan(pair=pair())
    assert result["trace_count"] == 2
    assert len(result["parameter_set_ids"]) == 2
    assert result["persistence_plan"]["would_write"] is False
    assert result["persistence_plan"]["scheduler_enabled"] is False
    assert result["safety"]["writer_invoked"] is False


def test_tampered_trace_identity_fails_closed() -> None:
    payload = pair()
    rows = list(payload["forecasts"])
    rows[0] = {**dict(rows[0]), "feature_snapshot_ref": "tampered"}
    payload["forecasts"] = tuple(rows)
    with pytest.raises(ValueError, match="forecast_contract_invalid|slot_identity_mismatch"):
        build_future_shadow_pair_trace_plan(pair=payload)


def test_duplicate_parameter_set_fails_closed() -> None:
    payload = pair()
    rows = [dict(item) for item in payload["forecasts"]]
    rows[1]["parameter_set_id"] = rows[0]["parameter_set_id"]
    payload["forecasts"] = tuple(rows)
    with pytest.raises(ValueError, match="forecast_contract_invalid|duplicate_parameter_set"):
        build_future_shadow_pair_trace_plan(pair=payload)


def test_wrong_artifact_kind_is_rejected() -> None:
    payload = pair()
    payload["artifact_kind"] = "wrong"
    with pytest.raises(ValueError, match="pair_kind_invalid"):
        build_future_shadow_pair_trace_plan(pair=payload)
