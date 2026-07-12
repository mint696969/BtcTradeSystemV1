# path: ./btcts_next/src/btcts/prediction/market_regime/tests/test_market_regime_future_trace_identity.py
# desc: Pure MR-F5.5 tests for immutable shadow forecast trace identity and outcome-resolver input projection.

from __future__ import annotations

from dataclasses import replace

import pytest

from btcts.prediction.market_regime.contracts import MarketRegimeCode
from btcts.prediction.market_regime.future_baseline_model import FutureBaselineEvidence, forecast_future_market_regime_baseline
from btcts.prediction.market_regime.future_shadow_adapter import MarketRegimeFutureShadowPacket
from btcts.prediction.market_regime.future_trace_identity import (
    MarketRegimeFutureTraceIdentity,
    build_market_regime_future_trace_identity,
    build_market_regime_future_trace_set,
)


def _forecast(horizon: int = 300):
    return forecast_future_market_regime_baseline(FutureBaselineEvidence(
        origin_timestamp="2026-07-12T00:00:00Z",
        origin_current_state=MarketRegimeCode.LOW_VOL_COMPRESSION,
        target_horizon_sec=horizon,
        feature_snapshot_ref="snapshot:abc",
        regime_scores={MarketRegimeCode.BREAKOUT: 0.8, MarketRegimeCode.RANGE: 0.2},
        available_feature_families=("price_structure", "volatility", "liquidity", "microprice", "source_quality", "session_context"),
        source_timestamp_epoch_sec=100.0,
        origin_timestamp_epoch_sec=100.0,
    ))


def test_trace_identity_is_deterministic_and_complete() -> None:
    first = build_market_regime_future_trace_identity(_forecast())
    second = build_market_regime_future_trace_identity(_forecast())
    assert first == second
    assert first.trace_id.startswith("market_regime_future_trace:")
    assert first.expiry_at == "2026-07-12T00:05:00Z"
    payload = first.to_dict()
    for key in ("target_definition_version", "model_id", "logic_version", "parameter_set_id", "feature_snapshot_ref"):
        assert payload[key]
    assert payload["shadow_only"] is True
    assert payload["canonical_replacement"] is False


def test_resolver_projection_preserves_identity_without_writes() -> None:
    trace = build_market_regime_future_trace_identity(_forecast(900))
    projection = trace.to_outcome_resolver_prediction()
    assert projection["run_id"] == trace.trace_id
    assert projection["prediction_id"] == trace.trace_id
    assert projection["horizon_sec"] == 900
    assert projection["horizon_key"] == "900s"
    assert projection["target_definition_version"] == "market_regime_target.900s.v1"
    assert projection["feature_snapshot_ref"] == "snapshot:abc"
    with pytest.raises(TypeError):
        projection["run_id"] = "mutated"


def test_trace_identity_changes_when_material_identity_changes() -> None:
    base = _forecast()
    changed = replace(base, parameter_set_id="different.parameter.set")
    assert build_market_regime_future_trace_identity(base).trace_id != build_market_regime_future_trace_identity(changed).trace_id


def test_abstain_trace_keeps_unknown_state_and_identity() -> None:
    forecast = forecast_future_market_regime_baseline(FutureBaselineEvidence(
        origin_timestamp="2026-07-12T00:00:00Z",
        origin_current_state=MarketRegimeCode.RANGE,
        target_horizon_sec=21600,
        feature_snapshot_ref="snapshot:abc",
        regime_scores={MarketRegimeCode.BREAKOUT: 0.8, MarketRegimeCode.RANGE: 0.2},
        available_feature_families=("price_structure", "volatility", "liquidity", "microprice", "source_quality"),
        source_timestamp_epoch_sec=100.0,
        origin_timestamp_epoch_sec=100.0,
    ))
    trace = build_market_regime_future_trace_identity(forecast)
    assert trace.predicted_future_state is MarketRegimeCode.UNKNOWN
    assert trace.to_outcome_resolver_prediction()["regime_code"] == "UNKNOWN"


def test_trace_set_requires_unique_packet_consistent_identity() -> None:
    forecasts = tuple(_forecast(horizon) for horizon in (300, 900, 1800, 3600, 21600, 43200, 86400))
    packet = MarketRegimeFutureShadowPacket(
        generated_at="2026-07-12T00:00:00Z",
        origin_current_state=MarketRegimeCode.LOW_VOL_COMPRESSION,
        feature_snapshot_ref="snapshot:abc",
        forecasts=forecasts,
    )
    traces = build_market_regime_future_trace_set(packet)
    assert len(traces) == 7
    assert len({item.trace_id for item in traces}) == 7


def test_direct_identity_construction_validates_material_fields() -> None:
    trace = build_market_regime_future_trace_identity(_forecast())
    with pytest.raises(ValueError, match="future_trace_id_mismatch"):
        replace(trace, trace_id="market_regime_future_trace:tampered")
    with pytest.raises(ValueError, match="future_trace_horizon_invalid:600"):
        MarketRegimeFutureTraceIdentity(
            trace_id=trace.trace_id, origin_timestamp=trace.origin_timestamp, expiry_at=trace.expiry_at,
            target_horizon_sec=600, target_horizon_key="600s", target_definition_version="market_regime_target.600s.v1",
            model_id=trace.model_id, logic_version=trace.logic_version, parameter_set_id=trace.parameter_set_id,
            feature_snapshot_ref=trace.feature_snapshot_ref, predicted_future_state=trace.predicted_future_state,
            forecast_status=trace.forecast_status,
        )


def test_noncanonical_equivalent_origin_timestamp_fails_closed() -> None:
    with pytest.raises(ValueError, match="future_trace_origin_timestamp_not_canonical_utc"):
        build_market_regime_future_trace_identity(replace(_forecast(), origin_timestamp="2026-07-12T09:00:00+09:00"))


def test_invalid_origin_timestamp_fails_closed() -> None:
    with pytest.raises(ValueError, match="future_trace_origin_timestamp_timezone_missing"):
        build_market_regime_future_trace_identity(replace(_forecast(), origin_timestamp="2026-07-12T00:00:00"))
