# path: ./btcts_next/src/btcts/processing/l4_consumer_models/tests/test_prediction_direction_builder.py
# desc: Tests for read-only Direction prediction builder and snapshot helper.

from __future__ import annotations

from btcts.processing.l4_consumer_models.contracts import (
    PredictionDirectionOutput,
)
from btcts.processing.l4_consumer_models.shared.prediction_direction_builder import (
    PredictionDirectionBuildInput,
    build_prediction_direction_input_from_scenario,
    build_prediction_direction_output,
    prediction_direction_output_to_snapshot,
)


def test_prediction_direction_builder_returns_read_only_contract() -> None:
    output = build_prediction_direction_output(
        PredictionDirectionBuildInput(
            scenario_ref="scenario.test",
            source_kind="scenario_reading",
            market_uid="btc_jpy",
            event_ts="2026-05-17T00:00:00Z",
            primary_direction_bias="up",
            diagnostics={"source": "unit_test"},
        )
    )

    assert isinstance(output, PredictionDirectionOutput)
    assert output.prediction_type == "direction"
    assert output.prediction_version == "phase4a.direction.v1"
    assert output.source_kind == "scenario_reading"
    assert output.market_uid == "btc_jpy"
    assert output.scenario_ref == "scenario.test"
    assert output.primary_direction_bias == "up"

    assert len(output.horizon_direction_readings) == 1
    assert output.horizon_direction_readings[0].horizon_key == "read_only_skeleton"
    assert output.horizon_direction_readings[0].direction_bias == "up"

    assert output.diagnostics["builder_stage"] == "thin_skeleton"
    assert output.diagnostics["read_only_contract"] is True
    assert output.diagnostics["not_position_owner"] is True
    assert output.diagnostics["not_execution_instruction"] is True
    assert output.diagnostics["not_broker_automation"] is True


def test_prediction_direction_builder_does_not_emit_position_or_execution_fields() -> None:
    output = build_prediction_direction_output(
        PredictionDirectionBuildInput(
            scenario_ref="scenario.test",
        )
    )

    fields = output.__dataclass_fields__

    forbidden_fields = [
        "position_size",
        "leverage",
        "entry_price",
        "exit_price",
        "order_price",
        "order_size",
        "broker_account",
    ]

    for field_name in forbidden_fields:
        assert field_name not in fields

    dumped = repr(output).lower()

    forbidden_terms = [
        "place_order",
        "order placement",
        "broker adapter",
        "execution engine",
        "live position mutation",
        "auto trade",
        "autonomous execution",
    ]

    for token in forbidden_terms:
        assert token not in dumped

def test_prediction_direction_input_derivation_from_scenario_is_local_and_read_only() -> None:
    inp = build_prediction_direction_input_from_scenario(
        scenario_ref="scenario.test",
        source_kind="scenario_reading",
        market_uid="btc_jpy",
        event_ts="2026-05-22T00:00:00Z",
        scenario_regime_bias="up",
        diagnostics={"source": "unit_test"},
    )

    assert isinstance(inp, PredictionDirectionBuildInput)
    assert inp.scenario_ref == "scenario.test"
    assert inp.source_kind == "scenario_reading"
    assert inp.market_uid == "btc_jpy"
    assert inp.event_ts == "2026-05-22T00:00:00Z"
    assert inp.primary_direction_bias == "up"

    assert inp.diagnostics is not None
    assert inp.diagnostics["derivation_stage"] == "thin_local_helper"
    assert inp.diagnostics["read_only_contract"] is True
    assert inp.diagnostics["not_runtime_wiring"] is True
    assert inp.diagnostics["not_replay_wiring"] is True
    assert inp.diagnostics["not_ui_wiring"] is True

    output = build_prediction_direction_output(inp)

    assert output.primary_direction_bias == "up"
    assert output.diagnostics["builder_stage"] == "thin_skeleton"


def test_prediction_direction_output_snapshot_is_read_only_local_dict() -> None:
    inp = build_prediction_direction_input_from_scenario(
        scenario_ref="scenario.test",
        source_kind="scenario_reading",
        market_uid="btc_jpy",
        event_ts="2026-05-22T00:00:00Z",
        scenario_regime_bias="down",
    )

    output = build_prediction_direction_output(inp)
    snapshot = prediction_direction_output_to_snapshot(output)

    assert snapshot["prediction_type"] == "direction"
    assert snapshot["prediction_version"] == "phase4a.direction.v1"
    assert snapshot["source_kind"] == "scenario_reading"
    assert snapshot["market_uid"] == "btc_jpy"
    assert snapshot["event_ts"] == "2026-05-22T00:00:00Z"
    assert snapshot["scenario_ref"] == "scenario.test"
    assert snapshot["primary_direction_bias"] == "down"

    assert snapshot["snapshot_stage"] == "direction_read_only_local_snapshot"
    assert snapshot["read_only_contract"] is True
    assert snapshot["not_runtime_wiring"] is True
    assert snapshot["not_replay_wiring"] is True
    assert snapshot["not_ui_wiring"] is True

    readings = snapshot["horizon_direction_readings"]

    assert isinstance(readings, list)
    assert readings[0]["horizon_key"] == "read_only_skeleton"
    assert readings[0]["direction_bias"] == "down"

    assert "position_size" not in snapshot
    assert "order_size" not in snapshot
    assert "broker_account" not in snapshot