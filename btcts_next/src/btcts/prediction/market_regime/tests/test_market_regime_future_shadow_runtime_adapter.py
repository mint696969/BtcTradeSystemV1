# path: ./btcts_next/src/btcts/prediction/market_regime/tests/test_market_regime_future_shadow_runtime_adapter.py
# desc: MR-F5.15 runtime trace capture and target-observation adapter tests.

from __future__ import annotations

import pytest

from btcts.prediction.market_regime.contracts import MarketRegimeCode
from btcts.prediction.market_regime.future_baseline_model import FutureBaselineEvidence, forecast_future_market_regime_baseline
from btcts.prediction.market_regime.future_forecast_contract import FUTURE_MARKET_REGIME_HORIZONS_SEC
from btcts.prediction.market_regime.future_shadow_adapter import MarketRegimeFutureShadowPacket
from btcts.prediction.market_regime.future_shadow_runtime_adapter import (
    build_market_regime_future_shadow_evidence_by_trace,
    build_market_regime_future_shadow_runtime_bridge,
    capture_market_regime_future_shadow_traces,
)


def _packet() -> MarketRegimeFutureShadowPacket:
    forecasts = []
    for horizon in FUTURE_MARKET_REGIME_HORIZONS_SEC:
        forecasts.append(forecast_future_market_regime_baseline(FutureBaselineEvidence(
            origin_timestamp="2026-07-12T00:00:00Z",
            origin_current_state=MarketRegimeCode.LOW_VOL_COMPRESSION,
            target_horizon_sec=horizon,
            feature_snapshot_ref="snapshot:mr-f5.15",
            regime_scores={MarketRegimeCode.BREAKOUT: 0.8, MarketRegimeCode.RANGE: 0.2},
            available_feature_families=(
                "price_structure", "volatility", "liquidity", "microprice",
                "source_quality", "session_context",
            ),
            source_timestamp_epoch_sec=100.0,
            origin_timestamp_epoch_sec=100.0,
        )))
    return MarketRegimeFutureShadowPacket(
        generated_at="2026-07-12T00:00:00Z",
        origin_current_state=MarketRegimeCode.LOW_VOL_COMPRESSION,
        feature_snapshot_ref="snapshot:mr-f5.15",
        forecasts=tuple(forecasts),
    )


def test_packet_forecasts_capture_exact_deterministic_traces() -> None:
    traces = capture_market_regime_future_shadow_traces(_packet())
    assert len(traces) == len(FUTURE_MARKET_REGIME_HORIZONS_SEC)
    assert tuple(item.trace_id for item in traces) == tuple(sorted(item.trace_id for item in traces))
    assert all(item.feature_snapshot_ref == "snapshot:mr-f5.15" for item in traces)


def test_target_observations_are_keyed_by_exact_trace_id() -> None:
    traces = capture_market_regime_future_shadow_traces(_packet())
    observations = {
        trace.trace_id: {
            "observation_at": trace.expiry_at,
            "observation_available": True,
            "observed_regime_code": "BREAKOUT",
            "source_refs": [f"derived:candle:{trace.target_horizon_sec}"],
        }
        for trace in traces
    }
    evidence = build_market_regime_future_shadow_evidence_by_trace(
        traces=traces, observations_by_trace_id=observations
    )
    assert set(evidence) == {item.trace_id for item in traces}
    assert all(item.observed_future_state is MarketRegimeCode.BREAKOUT for item in evidence.values())


def test_missing_observation_keeps_bridge_not_ready() -> None:
    packet = _packet()
    traces = capture_market_regime_future_shadow_traces(packet)
    bridge = build_market_regime_future_shadow_runtime_bridge(
        packet=packet,
        observations_by_trace_id={
            traces[0].trace_id: {
                "observation_at": traces[0].expiry_at,
                "observation_available": True,
                "observed_regime_code": "BREAKOUT",
                "source_refs": ["derived:candle"],
            }
        },
    )
    assert bridge["runtime_bridge_ready"] is False
    assert bridge["missing_evidence_trace_ids"] == tuple(
        item.trace_id for item in traces[1:]
    )


def test_unknown_trace_and_invalid_observation_fail_closed() -> None:
    traces = capture_market_regime_future_shadow_traces(_packet())
    with pytest.raises(ValueError, match="future_shadow_runtime_unknown_observation_trace"):
        build_market_regime_future_shadow_evidence_by_trace(
            traces=traces,
            observations_by_trace_id={"unknown": {"observation_available": False}},
        )
    with pytest.raises(ValueError, match="future_shadow_runtime_observation_available_invalid"):
        build_market_regime_future_shadow_evidence_by_trace(
            traces=traces,
            observations_by_trace_id={traces[0].trace_id: {"observation_available": "yes"}},
        )


def test_invalidation_fields_follow_outcome_evidence_contract() -> None:
    traces = capture_market_regime_future_shadow_traces(_packet())
    evidence = build_market_regime_future_shadow_evidence_by_trace(
        traces=traces,
        observations_by_trace_id={
            traces[0].trace_id: {
                "observation_at": traces[0].expiry_at,
                "observation_available": False,
                "invalidated": True,
                "invalidation_reasons": ["source_quality_failed"],
            }
        },
    )
    item = evidence[traces[0].trace_id]
    assert item.invalidated is True
    assert item.invalidation_reason == "source_quality_failed"
    with pytest.raises(ValueError, match="future_shadow_runtime_invalidation_reason_missing"):
        build_market_regime_future_shadow_evidence_by_trace(
            traces=traces,
            observations_by_trace_id={
                traces[0].trace_id: {
                    "observation_at": traces[0].expiry_at,
                    "observation_available": False,
                    "invalidated": True,
                }
            },
        )


def test_unavailable_observation_remains_unresolved_evidence() -> None:
    traces = capture_market_regime_future_shadow_traces(_packet())
    evidence = build_market_regime_future_shadow_evidence_by_trace(
        traces=traces,
        observations_by_trace_id={
            traces[0].trace_id: {
                "observation_at": traces[0].expiry_at,
                "observation_available": False,
                "observed_regime_code": "UNKNOWN",
            }
        },
    )
    assert evidence[traces[0].trace_id].observation_available is False
    assert evidence[traces[0].trace_id].observation_source_ref == ""


def test_bridge_is_immutable_and_never_performs_io() -> None:
    packet = _packet()
    traces = capture_market_regime_future_shadow_traces(packet)
    observations = {
        trace.trace_id: {
            "observation_at": trace.expiry_at,
            "observation_available": True,
            "observed_regime_code": "BREAKOUT",
            "source_refs": ["derived:candle"],
        }
        for trace in traces
    }
    bridge = build_market_regime_future_shadow_runtime_bridge(
        packet=packet, observations_by_trace_id=observations
    )
    assert bridge["runtime_bridge_ready"] is True
    assert bridge["safety"]["writes_dhot"] is False
    with pytest.raises(TypeError): bridge["runtime_bridge_ready"] = False
    with pytest.raises(TypeError): bridge["evidence_by_trace_id"][traces[0].trace_id] = None
