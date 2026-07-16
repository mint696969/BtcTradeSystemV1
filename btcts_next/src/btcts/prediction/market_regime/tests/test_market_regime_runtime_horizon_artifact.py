# path: ./btcts_next/src/btcts/prediction/market_regime/tests/test_market_regime_runtime_horizon_artifact.py
# desc: MR-F9.18A canonical 8-horizon runtime artifact contract tests.

from __future__ import annotations

import pytest

from btcts.prediction.market_regime.contracts import EvidenceQuality, FreshnessState, MarketRegimeCode, MarketRegimePrediction
from btcts.prediction.market_regime.future_baseline_model import FutureBaselineEvidence, forecast_future_market_regime_baseline
from btcts.prediction.market_regime.future_forecast_contract import FUTURE_MARKET_REGIME_HORIZONS_SEC
from btcts.prediction.market_regime.future_shadow_adapter import MarketRegimeFutureShadowPacket
from btcts.prediction.market_regime.runtime_horizon_artifact import build_market_regime_runtime_horizon_artifact

ORIGIN = "2026-07-16T08:00:00Z"
SOURCE = "2026-07-16T07:59:00Z"


def _current() -> MarketRegimePrediction:
    return MarketRegimePrediction(
        horizon_label="現在",
        horizon_sec=0,
        regime_code=MarketRegimeCode.RANGE,
        confidence_percent=65,
        evidence_quality=EvidenceQuality.PARTIAL,
        freshness_state=FreshnessState.LIVE,
        parameter_set_id="market_regime_engine_parameter_set.v1",
        diagnostic_record={
            "classifier_version": "classifier.v1",
            "current_state_estimator_version": "current-estimator.v1",
            "current_state_source_cutoff_time": ORIGIN,
            "current_state_window_age_sec": 5,
            "current_state_label_source": "current_state_estimator",
            "current_state_source_currentness_verified": True,
        },
    )


def _future_packet() -> MarketRegimeFutureShadowPacket:
    forecasts = []
    for index, horizon in enumerate(FUTURE_MARKET_REGIME_HORIZONS_SEC):
        scores = {
            MarketRegimeCode.UP_TREND: 0.75 - index * 0.01,
            MarketRegimeCode.RANGE: 0.25 + index * 0.01,
        }
        forecasts.append(forecast_future_market_regime_baseline(FutureBaselineEvidence(
            origin_timestamp=ORIGIN,
            origin_current_state=MarketRegimeCode.RANGE,
            target_horizon_sec=horizon,
            feature_snapshot_ref="snapshot:mr-f9.18a",
            regime_scores=scores,
            available_feature_families=(
                "price_structure", "volatility", "liquidity", "microprice",
                "source_quality", "session_context", "macro_context",
                "orderflow", "cross_venue", "change_point",
            ),
            source_timestamp_epoch_sec=100.0,
            origin_timestamp_epoch_sec=100.0,
        )))
    return MarketRegimeFutureShadowPacket(
        generated_at=ORIGIN,
        origin_current_state=MarketRegimeCode.RANGE,
        feature_snapshot_ref="snapshot:mr-f9.18a",
        forecasts=tuple(forecasts),
    )


def test_artifact_has_current_plus_seven_independent_future_horizons() -> None:
    artifact = build_market_regime_runtime_horizon_artifact(current_prediction=_current(), future_packet=_future_packet(), future_source_timestamp=SOURCE, future_source_currentness_verified=True)
    rows = artifact["horizons"]
    assert artifact["horizon_count"] == 8
    assert tuple(row["horizon_sec"] for row in rows) == (0, *FUTURE_MARKET_REGIME_HORIZONS_SEC)
    assert len({row["trace_id"] for row in rows}) == 8
    assert rows[0]["inference_mode"] == "current_state_estimation"
    assert all(row["inference_mode"] == "horizon_specific_future_model" for row in rows[1:])


def test_uncalibrated_scores_are_not_exposed_as_display_probability() -> None:
    artifact = build_market_regime_runtime_horizon_artifact(current_prediction=_current(), future_packet=_future_packet(), future_source_timestamp=SOURCE, future_source_currentness_verified=True)
    assert all(row["display_confidence_percent"] is None for row in artifact["horizons"])
    assert all(row["calibrated_probability_claim"] is False for row in artifact["horizons"])
    assert artifact["runtime_card_confidence_replacement"] is False


def test_push_contract_is_receive_only_and_non_executing() -> None:
    artifact = build_market_regime_runtime_horizon_artifact(current_prediction=_current(), future_packet=_future_packet(), future_source_timestamp=SOURCE, future_source_currentness_verified=True)
    assert artifact["push_ready"] is True
    assert artifact["push_topic"] == "prediction.family.market_regime"
    assert artifact["ui_inference_allowed"] is False
    assert artifact["ui_confidence_recalculation_allowed"] is False
    assert artifact["safety"]["websocket_opened"] is False
    assert artifact["safety"]["writes_dhot"] is False
    assert artifact["safety"]["order_submission_allowed"] is False
    with pytest.raises(TypeError):
        artifact["push_ready"] = False


def test_non_current_prediction_fails_closed() -> None:
    bad = MarketRegimePrediction(horizon_label="5分後", horizon_sec=300)
    with pytest.raises(ValueError, match="runtime_horizon_current_prediction_required"):
        build_market_regime_runtime_horizon_artifact(current_prediction=bad, future_packet=_future_packet(), future_source_timestamp=SOURCE, future_source_currentness_verified=True)

def test_freshness_and_abstain_semantics_are_not_conflated() -> None:
    artifact = build_market_regime_runtime_horizon_artifact(current_prediction=_current(), future_packet=_future_packet(), future_source_timestamp=SOURCE, future_source_currentness_verified=True)
    current = artifact["horizons"][0]
    future = artifact["horizons"][1:]
    assert current["source_age_semantics"] == "age_reported_by_current_state_source"
    assert current["source_currentness_verified"] is True
    assert current["display_freshness_claim_allowed"] is True
    assert all(row["source_timestamp"] == SOURCE for row in future)
    assert all(row["source_age_sec"] == 60.0 for row in future)
    assert all(row["source_age_semantics"] == "age_from_selected_source_to_prediction_origin" for row in future)
    assert all(row["source_currentness_verified"] is True for row in future)
    assert all(row["source_freshness_state"] == "LIVE" for row in future)
    assert all(row["display_freshness_claim_allowed"] is False for row in future)
    assert all(row["fallback_used"] is False for row in future)
    assert all(row["abstained"] is False for row in future)
    assert artifact["runtime_card_freshness_replacement"] is False

def test_future_source_after_origin_fails_closed() -> None:
    with pytest.raises(ValueError, match="future_source_after_origin"):
        build_market_regime_runtime_horizon_artifact(
            current_prediction=_current(),
            future_packet=_future_packet(),
            future_source_timestamp="2026-07-16T08:00:01Z",
            future_source_currentness_verified=True,
        )

def test_non_latest_future_source_is_explicitly_stale() -> None:
    artifact = build_market_regime_runtime_horizon_artifact(
        current_prediction=_current(),
        future_packet=_future_packet(),
        future_source_timestamp=SOURCE,
        future_source_currentness_verified=False,
    )
    future = artifact["horizons"][1:]
    assert all(row["source_timestamp"] == SOURCE for row in future)
    assert all(row["source_currentness_verified"] is False for row in future)
    assert all(row["source_freshness_state"] == "STALE_SOURCE_WINDOW" for row in future)
    assert all(row["display_freshness_claim_allowed"] is False for row in future)
