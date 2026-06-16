# path: ./btcts_next/src/btcts/processing/l4_consumer_models/tests/test_prediction_tactic_operation_builder.py
# desc: Verify Phase 4-A tactic operation builder stays review-driven and rollback-safe.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.processing.l4_consumer_models.shared import (  # noqa: E402
    PredictionTacticOperationBuildInput,
    TacticParameterSetRef,
    TacticReviewRecord,
    build_prediction_tactic_operation_record,
)


def main() -> int:
    candidate_ref = TacticParameterSetRef(
        set_id="candidate-continuation-follow",
        set_version="v2",
        profile_kind="candidate",
        baseline_ref="baseline-default",
        rollback_parent_set_id="baseline-default",
        comparison_group="phase4a-entry",
        is_active_candidate=True,
    )

    review_record = TacticReviewRecord(
        review_id="review-001",
        review_ts="2026-04-20T10:00:00Z",
        market_uid="bitflyer.spot.BTC_JPY",
        scenario_ref="bitflyer.spot.BTC_JPY@2026-04-20T10:00:00Z",
        proposal_ref="proposal:bitflyer.spot.BTC_JPY@2026-04-20T10:00:00Z",
        selected_tactic_key="continuation_follow",
        selected_parameter_set_ref=candidate_ref,
        decision_state="adopted",
        decision_reason="continuation_bias_with_manageable_risk",
        comparison_refs=("baseline-default", "candidate-continuation-follow"),
        rollback_target_ref="baseline-default",
        selection_trace={
            "trace_type": "tactic_selection_trace",
            "primary_tactic_key": "continuation_follow",
            "promotion_gate_state": "allowed",
            "can_promote_active_tactic": True,
            "overlay_primary_ref": "prefer_continuation_follow",
            "overlay_support_tactic_keys": ("continuation_follow",),
            "overlay_application_mode": "primary_only",
        },
        parameter_trace={
            "active_set_id": "candidate-continuation-follow",
            "profile_kind": "candidate",
            "adoption_ready": True,
            "rollback_target_ref": "baseline-default",
        },
        diagnostics={"source": "unit_test"},
    )

    operation = build_prediction_tactic_operation_record(
        PredictionTacticOperationBuildInput(
            review_record=review_record,
            operation_ts="2026-04-20T10:01:00Z",
            diagnostics={"caller": "unit_test"},
        )
    )

    assert operation.operation_type == "tactic_operation_record"
    assert operation.operation_version == "phase3.v1alpha1"
    assert operation.operation_id == (
        "review-001:adopt:2026-04-20T10:01:00Z"
    )
    assert operation.operation_ts == "2026-04-20T10:01:00Z"
    assert operation.market_uid == "bitflyer.spot.BTC_JPY"
    assert operation.review_ref == "review-001"
    assert operation.operation_state == "adopt"
    assert operation.selected_tactic_key == "continuation_follow"
    assert operation.selected_parameter_set_ref.set_id == (
        "candidate-continuation-follow"
    )
    assert operation.comparison_refs == (
        "baseline-default",
        "candidate-continuation-follow",
    )
    assert operation.rollback_target_ref == "baseline-default"
    assert operation.operation_reason == "continuation_bias_with_manageable_risk"
    assert operation.selection_trace == {
        "trace_type": "tactic_selection_trace",
        "primary_tactic_key": "continuation_follow",
        "promotion_gate_state": "allowed",
        "can_promote_active_tactic": True,
        "overlay_primary_ref": "prefer_continuation_follow",
        "overlay_support_tactic_keys": ("continuation_follow",),
        "overlay_application_mode": "primary_only",
    }
    assert operation.parameter_trace == {
        "active_set_id": "candidate-continuation-follow",
        "profile_kind": "candidate",
        "adoption_ready": True,
        "rollback_target_ref": "baseline-default",
    }
    assert operation.diagnostics["builder_type"] == (
        "prediction_tactic_operation_record"
    )
    assert operation.diagnostics["review_present"] is True
    assert operation.diagnostics["comparison_ref_count"] == 2
    assert operation.diagnostics["adoption_ready"] is True
    assert operation.diagnostics["rollback_target_available"] is True
    assert (
        operation.diagnostics["selected_set_id"]
        == "candidate-continuation-follow"
    )
    assert operation.diagnostics["caller"] == "unit_test"

    rollback_review = TacticReviewRecord(
        review_id="review-rollback",
        selected_tactic_key="observe_only",
        selected_parameter_set_ref=candidate_ref,
        decision_state="rolled_back",
        rollback_target_ref="baseline-default",
    )
    rollback_operation = build_prediction_tactic_operation_record(
        PredictionTacticOperationBuildInput(
            review_record=rollback_review,
            operation_ts="2026-04-20T10:02:00Z",
        )
    )
    assert rollback_operation.operation_state == "rollback"
    assert rollback_operation.rollback_target_ref == "baseline-default"

    empty = build_prediction_tactic_operation_record(
        PredictionTacticOperationBuildInput()
    )
    assert empty.operation_id is None
    assert empty.review_ref is None
    assert empty.operation_state == "hold"
    assert empty.selected_tactic_key == "observe_only"
    assert empty.selected_parameter_set_ref.set_id == "default"
    assert empty.comparison_refs == ()
    assert empty.rollback_target_ref is None
    assert empty.selection_trace == {}
    assert empty.parameter_trace == {}
    assert empty.diagnostics["review_present"] is False
    assert empty.diagnostics["adoption_ready"] is False
    assert empty.diagnostics["rollback_target_available"] is False
    assert empty.diagnostics["selected_set_id"] == "default"

    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())