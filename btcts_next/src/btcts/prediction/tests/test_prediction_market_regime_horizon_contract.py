# path: ./btcts_next/src/btcts/prediction/tests/test_prediction_market_regime_horizon_contract.py
# desc: Exact MarketRegime horizon alignment across Prediction System, OHLCV aggregation, and source coverage contracts.

from __future__ import annotations

from datetime import datetime, timezone

from btcts.apps.operator_ui.components.prediction_warroom_prediction_system_result_builder_runner import (
    OHLCV_SOURCE_QUALITY_IDS,
)
from btcts.prediction.contracts import (
    ParameterSetIdentity,
    PredictionConfidence,
    PredictionFamily,
    PredictionOutput,
    SourceIdentity,
)
from btcts.prediction.horizons import horizon_by_seconds
from btcts.prediction.technical import build_human_technical_summary
from btcts.prediction.horizons import CONTEXT_HORIZONS_SEC
from btcts.prediction.market_regime.horizon_policy import build_default_horizon_policy
from btcts.prediction.ohlcv import TIMEFRAME_SECONDS, aggregate_ohlcv_from_rows
from btcts.prediction.source_artifact_coverage import (
    REQUIRED_SOURCE_IDS,
    build_default_reference_source_registry,
)
from btcts.prediction.system import (
    MARKET_REGIME_MIN_EXACT_HORIZON_CANDLES,
    _TECHNICAL_TIMEFRAME_BY_HORIZON_SEC,
    _attach_market_regime_technical_source_attribution,
    _ohlcv_contract_id,
)
from btcts.prediction.system_contract import DEFAULT_HORIZONS_BY_GROUP, HorizonGroup


def test_market_regime_forecast_horizons_are_exact_prediction_system_horizons() -> None:
    required = {
        horizon.horizon_sec
        for horizon in build_default_horizon_policy().horizons
        if horizon.horizon_sec > 0
    }
    produced = {
        horizon
        for horizons in DEFAULT_HORIZONS_BY_GROUP.values()
        for horizon in horizons
    }

    assert required == {300, 900, 1800, 3600, 21600, 43200, 86400}
    assert required.issubset(produced)
    assert DEFAULT_HORIZONS_BY_GROUP[HorizonGroup.LONG_HORIZON] == (
        14400,
        21600,
        43200,
        86400,
    )
    assert CONTEXT_HORIZONS_SEC == (3600, 14400, 21600, 43200, 86400)


def test_six_and_twelve_hour_horizons_have_exact_ohlcv_and_source_contracts() -> None:
    registry_ids = {entry.source_id for entry in build_default_reference_source_registry()}

    for horizon_sec, source_id in ((21600, "ohlcv_6h"), (43200, "ohlcv_12h")):
        assert horizon_sec in TIMEFRAME_SECONDS
        assert _TECHNICAL_TIMEFRAME_BY_HORIZON_SEC[horizon_sec] == horizon_sec
        assert _ohlcv_contract_id(horizon_sec) == source_id
        assert source_id in REQUIRED_SOURCE_IDS
        assert source_id in registry_ids
        assert source_id in OHLCV_SOURCE_QUALITY_IDS


def test_six_and_twelve_hour_ohlcv_are_real_exact_buckets() -> None:
    rows = [
        {"event_ts": "2026-07-10T00:00:00Z", "price": 100.0, "size": 1.0},
        {"event_ts": "2026-07-10T05:59:00Z", "price": 106.0, "size": 2.0},
        {"event_ts": "2026-07-10T06:01:00Z", "price": 103.0, "size": 3.0},
        {"event_ts": "2026-07-10T11:59:00Z", "price": 112.0, "size": 4.0},
        {"event_ts": "2026-07-10T12:01:00Z", "price": 108.0, "size": 5.0},
    ]

    candles, diagnostics = aggregate_ohlcv_from_rows(
        rows,
        timeframes_sec=(21600, 43200),
        now=datetime(2026, 7, 10, 12, 2, tzinfo=timezone.utc),
    )

    assert diagnostics.blocked_by == ()
    by_timeframe = {}
    for candle in candles:
        by_timeframe.setdefault(candle.timeframe.timeframe_sec, []).append(candle)

    six_hour = by_timeframe[21600]
    assert len(six_hour) == 3
    assert six_hour[0].start_ts == "2026-07-10T00:00:00Z"
    assert six_hour[0].open == 100.0
    assert six_hour[0].close == 106.0
    assert six_hour[1].start_ts == "2026-07-10T06:00:00Z"
    assert six_hour[1].open == 103.0
    assert six_hour[1].close == 112.0

    twelve_hour = by_timeframe[43200]
    assert len(twelve_hour) == 2
    assert twelve_hour[0].start_ts == "2026-07-10T00:00:00Z"
    assert twelve_hour[0].open == 100.0
    assert twelve_hour[0].close == 112.0
    assert twelve_hour[1].start_ts == "2026-07-10T12:00:00Z"
    assert twelve_hour[1].close == 108.0

def test_market_regime_output_records_exact_six_and_twelve_hour_technical_sources() -> None:
    rows = [
        {"event_ts": "2026-07-08T00:00:00Z", "price": 98.0, "size": 1.0},
        {"event_ts": "2026-07-08T12:00:00Z", "price": 99.0, "size": 1.0},
        {"event_ts": "2026-07-09T00:00:00Z", "price": 100.0, "size": 1.0},
        {"event_ts": "2026-07-09T06:00:00Z", "price": 101.0, "size": 1.0},
        {"event_ts": "2026-07-09T12:00:00Z", "price": 102.0, "size": 1.0},
        {"event_ts": "2026-07-09T18:00:00Z", "price": 103.0, "size": 1.0},
        {"event_ts": "2026-07-10T00:00:00Z", "price": 104.0, "size": 1.0},
        {"event_ts": "2026-07-10T06:00:00Z", "price": 105.0, "size": 1.0},
        {"event_ts": "2026-07-10T12:00:00Z", "price": 106.0, "size": 1.0},
    ]
    candles, diagnostics = aggregate_ohlcv_from_rows(
        rows,
        timeframes_sec=(21600, 43200),
        now=datetime(2026, 7, 10, 12, 1, tzinfo=timezone.utc),
    )
    assert diagnostics.blocked_by == ()

    base_source = SourceIdentity(
        source_id="rule_based_v0_market_regime",
        source_family="derived_prediction_summary",
    )
    parameter_set = ParameterSetIdentity(
        parameter_set_id="test-market-regime",
        parameter_family="market_regime",
        version="test",
    )

    for horizon_sec, source_id in ((21600, "ohlcv_6h"), (43200, "ohlcv_12h")):
        technical = build_human_technical_summary(candles, timeframe_sec=horizon_sec)
        output = PredictionOutput(
            prediction_id=f"test:{horizon_sec}",
            generated_at="2026-07-10T12:01:00Z",
            family=PredictionFamily.MARKET_REGIME,
            horizon=horizon_by_seconds(horizon_sec),
            parameter_set=parameter_set,
            sources=(base_source,),
            confidence=PredictionConfidence.MEDIUM,
            primary_label="range_candidate",
            score=0.52,
            values={"volatility_state": "normal"},
        )

        annotated = _attach_market_regime_technical_source_attribution(
            (output,),
            technical=technical,
            horizon_sec=horizon_sec,
        )[0]

        assert [source.source_id for source in annotated.sources] == [
            "rule_based_v0_market_regime",
            source_id,
        ]
        assert annotated.values["technical_timeframe_sec"] == horizon_sec
        assert annotated.values["technical_source_id"] == source_id
        assert annotated.values["technical_candle_count"] == technical.candle_count
        assert technical.candle_count >= MARKET_REGIME_MIN_EXACT_HORIZON_CANDLES
        assert annotated.values["technical_summary_usable"] is True
        ledger = annotated.values["source_contribution_ledger"]
        assert ledger[0]["source_id"] == source_id
        assert ledger[0]["evidence_role"] == "exact_horizon_technical_evidence"
        assert ledger[0]["technical_timeframe_sec"] == horizon_sec
        assert ledger[0]["would_send_to_broker"] is False


def test_market_regime_output_does_not_claim_technical_source_when_summary_missing() -> None:
    output = PredictionOutput(
        prediction_id="test:missing",
        generated_at="2026-07-10T12:01:00Z",
        family=PredictionFamily.MARKET_REGIME,
        horizon=horizon_by_seconds(21600),
        parameter_set=ParameterSetIdentity(
            parameter_set_id="test-market-regime",
            parameter_family="market_regime",
            version="test",
        ),
        sources=(
            SourceIdentity(
                source_id="rule_based_v0_market_regime",
                source_family="derived_prediction_summary",
            ),
        ),
    )

    annotated = _attach_market_regime_technical_source_attribution(
        (output,),
        technical=None,
        horizon_sec=21600,
    )[0]

    assert [source.source_id for source in annotated.sources] == ["rule_based_v0_market_regime"]
    assert "technical_source_id" not in annotated.values

def test_market_regime_exact_horizon_history_gate_fails_closed_below_minimum() -> None:
    rows = [
        {"event_ts": "2026-07-10T12:00:00Z", "price": 106.0, "size": 1.0},
    ]
    candles, diagnostics = aggregate_ohlcv_from_rows(
        rows,
        timeframes_sec=(21600,),
        now=datetime(2026, 7, 10, 12, 1, tzinfo=timezone.utc),
    )
    assert diagnostics.blocked_by == ()
    technical = build_human_technical_summary(candles, timeframe_sec=21600)
    assert technical.candle_count == 1

    output = PredictionOutput(
        prediction_id="test:21600:insufficient",
        generated_at="2026-07-10T12:01:00Z",
        family=PredictionFamily.MARKET_REGIME,
        horizon=horizon_by_seconds(21600),
        parameter_set=ParameterSetIdentity(
            parameter_set_id="test-market-regime",
            parameter_family="market_regime",
            version="test",
        ),
        sources=(
            SourceIdentity(
                source_id="rule_based_v0_market_regime",
                source_family="derived_prediction_summary",
            ),
        ),
        confidence=PredictionConfidence.MEDIUM,
        primary_label="range_candidate",
        score=0.52,
    )

    gated = _attach_market_regime_technical_source_attribution(
        (output,),
        technical=technical,
        horizon_sec=21600,
    )[0]

    assert MARKET_REGIME_MIN_EXACT_HORIZON_CANDLES == 5
    assert gated.primary_label == "unknown"
    assert gated.confidence == PredictionConfidence.UNKNOWN
    assert gated.score is None
    assert "insufficient_exact_horizon_candles" in gated.blockers
    assert gated.values["technical_summary_usable"] is False
    assert gated.values["technical_evidence_state"] == "insufficient_exact_horizon_history"
    assert gated.values["candidate_primary_label_before_history_gate"] == "range_candidate"
    assert gated.values["candidate_score_before_history_gate"] == 0.52
