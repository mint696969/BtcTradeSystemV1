# path: ./btcts_next/src/btcts/prediction/market_regime/tests/test_market_regime_future_shadow_review_contracts.py
# desc: MR-F9.9 guards for blocked and pending human review contracts with replayable evidence links.

from __future__ import annotations

import pytest

from btcts.prediction.market_regime.future_shadow_review_contracts import (
    FutureShadowReviewNote,
    build_future_shadow_review_link,
    build_future_shadow_review_request,
)


def _proposal(decision: str = "winner"):
    selected = "shadow" if decision == "winner" else None
    blockers = ("minimum_observed_slots_not_met",) if decision == "insufficient_evidence" else ()
    return {
        "artifact_kind": "future_shadow_comparison_proposal",
        "comparison": {
            "candidate_count": 2,
            "decision": {
                "decision": decision,
                "selected_candidate_id": selected,
                "rollback_candidate_id": "active",
            },
        },
        "proposal": {
            "decision": decision,
            "selected_candidate_id": selected,
            "rollback_candidate_id": "active",
            "comparison_blockers": blockers,
            "human_approval_required": True,
            "proposal_is_not_runtime_activation": True,
        },
        "safety": {
            "writes_dhot": False,
            "auto_promotion_allowed": False,
            "live_parameter_apply_allowed": False,
        },
    }


def _execution():
    return {
        "artifact_kind": "future_execution_diagnostics_report",
        "origin_count": 4,
        "trace_count": 56,
        "safety": {
            "writes_dhot": False,
            "writer_invoked": False,
            "scheduler_enabled": False,
            "auto_promotion_allowed": False,
            "live_parameter_apply_allowed": False,
        },
    }


def _outcome():
    return {
        "artifact_kind": "future_outcome_persistence_diagnostics_report",
        "snapshot_count": 8,
        "receipt_count": 4,
        "trace_count": 56,
        "safety": {
            "writes_dhot": False,
            "writer_invoked": False,
            "scheduler_enabled": False,
            "canonical_outcome_ledger_append": False,
            "auto_promotion_allowed": False,
            "live_parameter_apply_allowed": False,
        },
    }


def _request(decision: str = "winner"):
    return build_future_shadow_review_request(
        proposal=_proposal(decision),
        execution_diagnostics=_execution(),
        outcome_diagnostics=_outcome(),
        proposal_ref="artifact:proposal:1",
        execution_diagnostics_ref="artifact:execution-diagnostics:1",
        outcome_diagnostics_ref="artifact:outcome-diagnostics:1",
        review_scope_id="mr-f9:shadow-promotion",
        requested_at="2026-07-16T01:00:00Z",
    )


def test_winner_proposal_creates_pending_human_review_without_activation() -> None:
    request = _request("winner")
    assert request["review_status"] == "PENDING_HUMAN_REVIEW"
    assert request["selected_candidate_id"] == "shadow"
    assert request["review_note_required"] is True
    assert request["auto_promotion_allowed"] is False
    assert request["live_parameter_apply_allowed"] is False
    assert request["runtime_activation_performed"] is False


def test_insufficient_evidence_creates_blocked_review() -> None:
    request = _request("insufficient_evidence")
    assert request["review_status"] == "BLOCKED_INSUFFICIENT_EVIDENCE"
    assert request["review_note_required"] is False
    assert request["review_link_required"] is False
    assert request["comparison_blockers"] == ("minimum_observed_slots_not_met",)


def test_note_and_link_create_replayable_trail() -> None:
    request = _request("winner")
    note = FutureShadowReviewNote(
        note_id="review-note:1",
        request_id=request["request_id"],
        author="operator:mint",
        recorded_at="2026-07-16T01:10:00Z",
        decision="defer",
        note_text="More mature OOS evidence is required.",
    )
    note_payload = note.to_dict()
    link = build_future_shadow_review_link(request=request, note=note)
    assert note_payload["runtime_activation_performed"] is False
    assert link["request_id"] == request["request_id"]
    assert link["note_id"] == "review-note:1"
    assert link["replayable_review_trail"] is True


def test_blocked_request_cannot_receive_decision_link() -> None:
    request = _request("insufficient_evidence")
    note = FutureShadowReviewNote(
        note_id="review-note:blocked",
        request_id=request["request_id"],
        author="operator:mint",
        recorded_at="2026-07-16T01:10:00Z",
        decision="approve",
        note_text="This must not activate a blocked request.",
    )
    with pytest.raises(ValueError, match="blocked_request_forbidden"):
        build_future_shadow_review_link(request=request, note=note)


def test_review_note_causality_and_nonwinner_approval_fail_closed() -> None:
    winner = _request("winner")
    early_note = FutureShadowReviewNote(
        note_id="review-note:early",
        request_id=winner["request_id"],
        author="operator:mint",
        recorded_at="2026-07-16T00:59:59Z",
        decision="defer",
        note_text="This note predates the request.",
    )
    with pytest.raises(ValueError, match="note_before_request"):
        build_future_shadow_review_link(request=winner, note=early_note)

    tie = _request("tie")
    approve_tie = FutureShadowReviewNote(
        note_id="review-note:approve-tie",
        request_id=tie["request_id"],
        author="operator:mint",
        recorded_at="2026-07-16T01:10:00Z",
        decision="approve",
        note_text="A tie has no selected winner to approve.",
    )
    with pytest.raises(ValueError, match="approve_nonwinner_forbidden"):
        build_future_shadow_review_link(request=tie, note=approve_tie)


def test_proposal_internal_decision_mismatch_and_unsafe_diagnostics_fail_closed() -> None:
    mismatched = _proposal("winner")
    mismatched["comparison"]["decision"]["decision"] = "tie"
    with pytest.raises(ValueError, match="decision_mismatch"):
        build_future_shadow_review_request(
            proposal=mismatched,
            execution_diagnostics=_execution(),
            outcome_diagnostics=_outcome(),
            proposal_ref="artifact:proposal:1",
            execution_diagnostics_ref="artifact:execution:1",
            outcome_diagnostics_ref="artifact:outcome:1",
            review_scope_id="mr-f9:shadow-promotion",
            requested_at="2026-07-16T01:00:00Z",
        )

    unsafe_execution = _execution()
    unsafe_execution["safety"]["live_parameter_apply_allowed"] = True
    with pytest.raises(ValueError, match="execution_live_apply_invalid"):
        build_future_shadow_review_request(
            proposal=_proposal("winner"),
            execution_diagnostics=unsafe_execution,
            outcome_diagnostics=_outcome(),
            proposal_ref="artifact:proposal:1",
            execution_diagnostics_ref="artifact:execution:1",
            outcome_diagnostics_ref="artifact:outcome:1",
            review_scope_id="mr-f9:shadow-promotion",
            requested_at="2026-07-16T01:00:00Z",
        )


def test_unsafe_proposal_and_missing_insufficient_blockers_fail_closed() -> None:
    unsafe = _proposal("winner")
    unsafe["safety"]["auto_promotion_allowed"] = True
    with pytest.raises(ValueError, match="auto_promotion_invalid"):
        build_future_shadow_review_request(
            proposal=unsafe,
            execution_diagnostics=_execution(),
            outcome_diagnostics=_outcome(),
            proposal_ref="artifact:proposal:1",
            execution_diagnostics_ref="artifact:execution:1",
            outcome_diagnostics_ref="artifact:outcome:1",
            review_scope_id="mr-f9:shadow-promotion",
            requested_at="2026-07-16T01:00:00Z",
        )
    insufficient = _proposal("insufficient_evidence")
    insufficient["proposal"]["comparison_blockers"] = ()
    with pytest.raises(ValueError, match="insufficient_without_blockers"):
        build_future_shadow_review_request(
            proposal=insufficient,
            execution_diagnostics=_execution(),
            outcome_diagnostics=_outcome(),
            proposal_ref="artifact:proposal:1",
            execution_diagnostics_ref="artifact:execution:1",
            outcome_diagnostics_ref="artifact:outcome:1",
            review_scope_id="mr-f9:shadow-promotion",
            requested_at="2026-07-16T01:00:00Z",
        )
