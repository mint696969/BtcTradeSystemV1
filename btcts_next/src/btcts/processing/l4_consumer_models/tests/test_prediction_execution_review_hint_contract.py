# path: ./btcts_next/src/btcts/processing/l4_consumer_models/tests/test_prediction_execution_review_hint_contract.py
# desc: Tests for read-only Execution review hint contract models.

from __future__ import annotations

from btcts.processing.l4_consumer_models.contracts import PredictionExecutionReviewHint


def test_prediction_execution_review_hint_contract_minimal_shape() -> None:
    output = PredictionExecutionReviewHint(
        prediction_type="execution_review_hint",
        prediction_version="phase4a.execution_review_hint.v1",
        source_kind="position_review_material",
        market_uid="btc_jpy",
        event_ts="2026-05-23T00:00:00Z",
        scenario_ref="scenario.test",
        direction_ref="direction.test",
        position_ref="position_review_hint.test",
        execution_context_ref="execution_context.review_only.test",
        timing_hint="review_only_wait_for_confirmation",
        urgency_hint="low",
        passive_aggressive_hint="passive_review_only",
        feasibility_hint="feasible_for_review_only",
        evidence_trace_refs=("position:test",),
    )

    assert output.prediction_type == "execution_review_hint"
    assert output.timing_hint == "review_only_wait_for_confirmation"
    assert output.review_needed is True
    assert output.evidence_trace_refs == ("position:test",)


def test_prediction_execution_review_hint_contract_is_review_only_read_model() -> None:
    fields = PredictionExecutionReviewHint.__dataclass_fields__

    required_fields = [
        "scenario_ref",
        "direction_ref",
        "position_ref",
        "execution_context_ref",
        "timing_hint",
        "urgency_hint",
        "passive_aggressive_hint",
        "feasibility_hint",
        "review_needed",
        "evidence_trace_refs",
    ]

    for field_name in required_fields:
        assert field_name in fields


def test_prediction_execution_review_hint_contract_does_not_own_broker_or_order_fields() -> None:
    fields = PredictionExecutionReviewHint.__dataclass_fields__

    forbidden_fields = [
        "order_size",
        "order_price",
        "leverage",
        "broker_account",
        "place_order",
        "broker_order",
        "live_order_placement",
        "auto_trade",
        "account_mutation",
        "broker_adapter_operation",
    ]

    for field_name in forbidden_fields:
        assert field_name not in fields


def test_prediction_execution_review_hint_contract_boundary_terms() -> None:
    dumped = repr(PredictionExecutionReviewHint)

    forbidden = [
        "place_order",
        "order placement",
        "broker adapter",
        "account mutation",
        "live order placement",
        "auto trade",
        "autonomous trading decision",
    ]

    for token in forbidden:
        assert token not in dumped.lower()
