# path: ./btcts_next/src/btcts/processing/l4_consumer_models/tests/test_prediction_direction_contract_boundary.py
# desc: Boundary tests for read-only Direction contract responsibility.

from __future__ import annotations

from btcts.processing.l4_consumer_models.contracts import (
    PredictionDirectionOutput,
)


def test_prediction_direction_contract_boundary_terms() -> None:
    dumped = repr(PredictionDirectionOutput)

    forbidden = [
        "place_order",
        "order placement",
        "broker adapter",
        "execution engine",
        "live position mutation",
        "auto trade",
        "autonomous execution",
    ]

    for token in forbidden:
        assert token not in dumped.lower()


def test_prediction_direction_contract_is_not_position_owner() -> None:
    fields = PredictionDirectionOutput.__dataclass_fields__

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


def test_prediction_direction_contract_is_read_model_only() -> None:
    fields = PredictionDirectionOutput.__dataclass_fields__

    required_fields = [
        "scenario_ref",
        "primary_direction_bias",
        "horizon_direction_readings",
        "evidence_trace_refs",
    ]

    for field_name in required_fields:
        assert field_name in fields