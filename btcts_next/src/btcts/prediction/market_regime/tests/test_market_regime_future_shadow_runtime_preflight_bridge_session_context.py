# path: ./btcts_next/src/btcts/prediction/market_regime/tests/test_market_regime_future_shadow_runtime_preflight_bridge_session_context.py
# desc: MR-F9.18A5 guard that long-horizon preflight receives explicit session_context availability.

from __future__ import annotations

from types import MappingProxyType

from btcts.prediction.market_regime.contracts import MarketRegimeCode
from btcts.prediction.market_regime.future_baseline_model import FutureBaselineEvidence, forecast_future_market_regime_baseline
from btcts.prediction.market_regime.future_forecast_contract import FUTURE_MARKET_REGIME_HORIZONS_SEC
from btcts.prediction.market_regime.future_shadow_adapter import MarketRegimeFutureShadowPacket
from btcts.prediction.market_regime.future_shadow_runtime_preflight_bridge import build_future_shadow_runtime_preflight_report


def test_bridge_source_declares_session_context_for_long_horizons(monkeypatch) -> None:
    captured = []

    def fake_build_pair(*, evidence: FutureBaselineEvidence, candidates=None, precomputed_forecasts=None):
        captured.append(evidence)
        return MappingProxyType({
            "schema_version": "test",
            "slot_identity": MappingProxyType({
                "prediction_origin": evidence.origin_timestamp,
                "target_horizon_sec": evidence.target_horizon_sec,
                "feature_snapshot_ref": evidence.feature_snapshot_ref,
            }),
            "candidate_identities": (),
            "forecasts": (),
        })

    def fake_trace_plan(*, pair):
        return MappingProxyType({"pair": pair})

    generated_at = "2026-07-16T09:00:00Z"
    feature_snapshot_ref = "snapshot:test"
    forecasts = tuple(
        forecast_future_market_regime_baseline(
            FutureBaselineEvidence(
                origin_timestamp=generated_at,
                origin_current_state=MarketRegimeCode.RANGE,
                target_horizon_sec=horizon,
                feature_snapshot_ref=feature_snapshot_ref,
                regime_scores={MarketRegimeCode.RANGE: 0.7, MarketRegimeCode.UP_TREND: 0.3},
                available_feature_families=(
                    "price_structure",
                    "volatility",
                    "liquidity",
                    "source_quality",
                    "microprice",
                    "session_context",
                ),
                source_timestamp_epoch_sec=1.0,
                origin_timestamp_epoch_sec=1.0,
            )
        )
        for horizon in FUTURE_MARKET_REGIME_HORIZONS_SEC
    )
    packet = MarketRegimeFutureShadowPacket(
        generated_at=generated_at,
        origin_current_state=MarketRegimeCode.RANGE,
        feature_snapshot_ref=feature_snapshot_ref,
        forecasts=forecasts,
    )

    class FeatureInputs:
        source_timestamp = "2026-07-16T09:00:00Z"
        source_timestamp_epoch_sec = 1.0

    monkeypatch.setattr(
        "btcts.prediction.market_regime.future_shadow_runtime_preflight_bridge._validate_runtime_bundle",
        lambda runtime_bundle: FeatureInputs(),
    )
    monkeypatch.setattr(
        "btcts.prediction.market_regime.future_shadow_runtime_preflight_bridge.build_market_regime_origin_evidence_bundles",
        lambda **kwargs: tuple(
            MappingProxyType({
                "bundle_id": f"bundle:{horizon}",
                "prediction_origin": "2026-07-16T09:00:00Z",
                "target_horizon_sec": horizon,
                "feature_snapshot_ref": "snapshot:test",
                "candidate_probability_by_state": {"RANGE": 0.7, "UP_TREND": 0.3},
            })
            for horizon in (300, 900, 1800, 3600, 21600, 43200, 86400)
        ),
    )
    monkeypatch.setattr(
        "btcts.prediction.market_regime.future_shadow_runtime_preflight_bridge.build_future_shadow_candidate_pair",
        fake_build_pair,
    )
    monkeypatch.setattr(
        "btcts.prediction.market_regime.future_shadow_runtime_preflight_bridge.build_future_shadow_pair_trace_plan",
        fake_trace_plan,
    )
    monkeypatch.setattr(
        "btcts.prediction.market_regime.future_shadow_runtime_preflight_bridge._origin_epoch",
        lambda value: 1.0,
    )

    runtime_bundle = {
        "feature_bundle_generated_at": packet.generated_at,
        "feature_snapshot_ref": packet.feature_snapshot_ref,
    }
    result = build_future_shadow_runtime_preflight_report(
        packet=packet,
        signal_score_report={"horizons": []},
        runtime_bundle=runtime_bundle,
    )

    assert result["pair_count"] == 7
    assert len(captured) == 7
    assert all("session_context" in item.available_feature_families for item in captured)
    assert all("price_structure" in item.available_feature_families for item in captured)
    assert all("volatility" in item.available_feature_families for item in captured)
