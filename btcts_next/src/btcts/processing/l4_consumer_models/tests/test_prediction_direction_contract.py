# path: ./btcts_next/src/btcts/processing/l4_consumer_models/tests/test_prediction_direction_contract.py
# desc: Tests for read-only Direction prediction contract models.

from __future__ import annotations

from btcts.processing.l4_consumer_models.contracts import (
    HorizonDirectionReading,
    PredictionDirectionOutput,
)


def test_prediction_direction_contract_minimal_shape() -> None:
    output = PredictionDirectionOutput(
        prediction_type="direction",
        prediction_version="phase4a.direction.v1",
        source_kind="scenario_reading",
        market_uid="btc_jpy",
        event_ts="2026-05-17T00:00:00Z",
        scenario_ref="scenario.test",
        primary_direction_bias="up",
        horizon_direction_readings=(
            HorizonDirectionReading(
                horizon_key="short",
                direction_bias="up",
                confidence=0.7,
                continuation_balance=0.6,
                reversal_balance=0.4,
                turning_point_risk=0.2,
            ),
        ),
    )

    assert output.prediction_type == "direction"
    assert output.primary_direction_bias == "up"

    assert len(output.horizon_direction_readings) == 1

    reading = output.horizon_direction_readings[0]

    assert reading.horizon_key == "short"
    assert reading.direction_bias == "up"

    assert output.continuation_reversal_balance == 0.0
    assert output.turning_point_risk == 0.0


def test_prediction_direction_contract_is_read_only_interpretation() -> None:
    output = PredictionDirectionOutput(
        prediction_type="direction",
        prediction_version="phase4a.direction.v1",
        source_kind="scenario_reading",
        market_uid="btc_jpy",
        event_ts="2026-05-17T00:00:00Z",
        scenario_ref="scenario.test",
        primary_direction_bias="neutral",
    )

    dumped = repr(output)

    assert "execution instruction" not in dumped.lower()
    assert "broker/order automation" not in dumped.lower()