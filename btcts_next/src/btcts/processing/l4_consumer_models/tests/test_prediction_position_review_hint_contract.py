# path: ./btcts_next/src/btcts/processing/l4_consumer_models/tests/test_prediction_position_review_hint_contract.py
# desc: Tests for read-only Position review hint contract models.

from __future__ import annotations

from btcts.processing.l4_consumer_models.contracts import PredictionPositionReviewHint


def test_prediction_position_review_hint_contract_minimal_shape() -> None:
    output = PredictionPositionReviewHint(
        prediction_type="position_review_hint",
        prediction_version="phase4a.position_review_hint.v1",
        source_kind="direction_review_material",
        market_uid="btc_jpy",
        event_ts="2026-05-23T00:00:00Z",
        scenario_ref="scenario.test",
        direction_ref="direction.test",
        position_context_ref="position_context.review_only.test",
        position_state_reading="flat_or_no_live_position_claim",
        management_hint="review_only_wait",
        exposure_risk_hint="low",
        evidence_trace_refs=("direction:test",),
    )

    assert output.prediction_type == "position_review_hint"
    assert output.management_hint == "review_only_wait"
    assert output.review_needed is True
    assert output.evidence_trace_refs == ("direction:test",)


def test_prediction_position_review_hint_contract_is_review_only_read_model() -> None:
    fields = PredictionPositionReviewHint.__dataclass_fields__

    required_fields = [
        "scenario_ref",
        "direction_ref",
        "position_context_ref",
        "position_state_reading",
        "management_hint",
        "exposure_risk_hint",
        "review_needed",
        "evidence_trace_refs",
    ]

    for field_name in required_fields:
        assert field_name in fields


def test_prediction_position_review_hint_contract_does_not_own_execution_or_order_fields() -> None:
    fields = PredictionPositionReviewHint.__dataclass_fields__

    forbidden_fields = [
        "position_size",
        "order_size",
        "order_price",
        "leverage",
        "broker_account",
        "place_order",
        "broker_order",
        "live_order_placement",
        "auto_trade",
    ]

    for field_name in forbidden_fields:
        assert field_name not in fields


def test_prediction_position_review_hint_contract_boundary_terms() -> None:
    dumped = repr(PredictionPositionReviewHint)

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
