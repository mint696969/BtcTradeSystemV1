# path: ./btcts_next/src/btcts/prediction/market_regime/future_shadow_review_contracts.py
# desc: MR-F9.9 immutable human-gated review request, note, and evidence-link contracts for shadow promotion evidence.

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import datetime, timezone
from types import MappingProxyType
from typing import Any, Mapping, Sequence

MARKET_REGIME_FUTURE_SHADOW_REVIEW_CONTRACTS_VERSION = (
    "prediction.market_regime.future_shadow_review_contracts.mr_f9_9.v1"
)

_ALLOWED_NOTE_DECISIONS = {"approve", "reject", "defer"}


def _require_zulu(value: str, error: str) -> str:
    text = str(value or "")
    if not text.endswith("Z"):
        raise ValueError(error)
    try:
        parsed = datetime.fromisoformat(text[:-1] + "+00:00")
    except ValueError as exc:
        raise ValueError(error) from exc
    if parsed.tzinfo != timezone.utc:
        raise ValueError(error)
    return text


def _parse_zulu(value: str, error: str) -> datetime:
    text = _require_zulu(value, error)
    return datetime.fromisoformat(text[:-1] + "+00:00")


def _artifact_ref(value: str, error: str) -> str:
    text = str(value or "").strip()
    if not text:
        raise ValueError(error)
    return text


def _safety_false(artifact: Mapping[str, Any], key: str, error: str) -> None:
    safety = artifact.get("safety")
    if not isinstance(safety, Mapping) or safety.get(key) is not False:
        raise ValueError(error)


@dataclass(frozen=True)
class FutureShadowReviewNote:
    note_id: str
    request_id: str
    author: str
    recorded_at: str
    decision: str
    note_text: str

    def __post_init__(self) -> None:
        for name, value in (
            ("note_id", self.note_id),
            ("request_id", self.request_id),
            ("author", self.author),
            ("note_text", self.note_text),
        ):
            if not str(value).strip():
                raise ValueError(f"future_shadow_review_note_missing:{name}")
        _require_zulu(self.recorded_at, "future_shadow_review_note_recorded_at_invalid")
        if self.decision not in _ALLOWED_NOTE_DECISIONS:
            raise ValueError("future_shadow_review_note_decision_invalid")

    def to_dict(self) -> Mapping[str, Any]:
        return MappingProxyType({
            "schema_version": MARKET_REGIME_FUTURE_SHADOW_REVIEW_CONTRACTS_VERSION,
            "artifact_family": "prediction/market_regime",
            "artifact_kind": "future_shadow_review_note",
            "note_id": self.note_id,
            "request_id": self.request_id,
            "author": self.author,
            "recorded_at": self.recorded_at,
            "decision": self.decision,
            "note_text": self.note_text,
            "runtime_activation_performed": False,
            "parameter_apply_performed": False,
        })


@dataclass(frozen=True)
class FutureShadowReviewLink:
    link_id: str
    request_id: str
    note_id: str
    proposal_ref: str
    execution_diagnostics_ref: str
    outcome_diagnostics_ref: str

    def __post_init__(self) -> None:
        for name, value in (
            ("link_id", self.link_id),
            ("request_id", self.request_id),
            ("note_id", self.note_id),
            ("proposal_ref", self.proposal_ref),
            ("execution_diagnostics_ref", self.execution_diagnostics_ref),
            ("outcome_diagnostics_ref", self.outcome_diagnostics_ref),
        ):
            if not str(value).strip():
                raise ValueError(f"future_shadow_review_link_missing:{name}")

    def to_dict(self) -> Mapping[str, Any]:
        return MappingProxyType({
            "schema_version": MARKET_REGIME_FUTURE_SHADOW_REVIEW_CONTRACTS_VERSION,
            "artifact_family": "prediction/market_regime",
            "artifact_kind": "future_shadow_review_link",
            "link_id": self.link_id,
            "request_id": self.request_id,
            "note_id": self.note_id,
            "proposal_ref": self.proposal_ref,
            "execution_diagnostics_ref": self.execution_diagnostics_ref,
            "outcome_diagnostics_ref": self.outcome_diagnostics_ref,
            "replayable_review_trail": True,
        })


def build_future_shadow_review_request(
    *,
    proposal: Mapping[str, Any],
    execution_diagnostics: Mapping[str, Any],
    outcome_diagnostics: Mapping[str, Any],
    proposal_ref: str,
    execution_diagnostics_ref: str,
    outcome_diagnostics_ref: str,
    review_scope_id: str,
    requested_at: str,
) -> Mapping[str, Any]:
    if proposal.get("artifact_kind") != "future_shadow_comparison_proposal":
        raise ValueError("future_shadow_review_proposal_kind_invalid")
    if execution_diagnostics.get("artifact_kind") != "future_execution_diagnostics_report":
        raise ValueError("future_shadow_review_execution_diagnostics_kind_invalid")
    if outcome_diagnostics.get("artifact_kind") != "future_outcome_persistence_diagnostics_report":
        raise ValueError("future_shadow_review_outcome_diagnostics_kind_invalid")
    scope = str(review_scope_id or "").strip()
    if not scope:
        raise ValueError("future_shadow_review_scope_missing")
    requested = _require_zulu(requested_at, "future_shadow_review_requested_at_invalid")
    proposal_ref = _artifact_ref(proposal_ref, "future_shadow_review_proposal_ref_missing")
    execution_ref = _artifact_ref(
        execution_diagnostics_ref,
        "future_shadow_review_execution_diagnostics_ref_missing",
    )
    outcome_ref = _artifact_ref(
        outcome_diagnostics_ref,
        "future_shadow_review_outcome_diagnostics_ref_missing",
    )

    _safety_false(proposal, "auto_promotion_allowed", "future_shadow_review_proposal_auto_promotion_invalid")
    _safety_false(proposal, "live_parameter_apply_allowed", "future_shadow_review_proposal_live_apply_invalid")
    _safety_false(proposal, "writes_dhot", "future_shadow_review_proposal_write_invalid")
    _safety_false(execution_diagnostics, "writer_invoked", "future_shadow_review_execution_writer_invalid")
    _safety_false(execution_diagnostics, "writes_dhot", "future_shadow_review_execution_write_invalid")
    _safety_false(execution_diagnostics, "scheduler_enabled", "future_shadow_review_execution_scheduler_invalid")
    _safety_false(execution_diagnostics, "auto_promotion_allowed", "future_shadow_review_execution_auto_promotion_invalid")
    _safety_false(execution_diagnostics, "live_parameter_apply_allowed", "future_shadow_review_execution_live_apply_invalid")
    _safety_false(outcome_diagnostics, "writer_invoked", "future_shadow_review_outcome_writer_invalid")
    _safety_false(outcome_diagnostics, "writes_dhot", "future_shadow_review_outcome_write_invalid")
    _safety_false(outcome_diagnostics, "scheduler_enabled", "future_shadow_review_outcome_scheduler_invalid")
    _safety_false(outcome_diagnostics, "canonical_outcome_ledger_append", "future_shadow_review_ledger_append_invalid")
    _safety_false(outcome_diagnostics, "auto_promotion_allowed", "future_shadow_review_outcome_auto_promotion_invalid")
    _safety_false(outcome_diagnostics, "live_parameter_apply_allowed", "future_shadow_review_outcome_live_apply_invalid")

    proposal_payload = proposal.get("proposal")
    comparison = proposal.get("comparison")
    if not isinstance(proposal_payload, Mapping) or not isinstance(comparison, Mapping):
        raise ValueError("future_shadow_review_proposal_payload_invalid")
    decision = str(proposal_payload.get("decision") or "")
    if decision not in {"winner", "tie", "insufficient_evidence"}:
        raise ValueError("future_shadow_review_decision_invalid")
    comparison_decision = comparison.get("decision")
    if not isinstance(comparison_decision, Mapping):
        raise ValueError("future_shadow_review_comparison_decision_missing")
    selected = proposal_payload.get("selected_candidate_id")
    rollback = str(proposal_payload.get("rollback_candidate_id") or "")
    if str(comparison_decision.get("decision") or "") != decision:
        raise ValueError("future_shadow_review_decision_mismatch")
    if comparison_decision.get("selected_candidate_id") != selected:
        raise ValueError("future_shadow_review_selected_candidate_mismatch")
    if str(comparison_decision.get("rollback_candidate_id") or "") != rollback:
        raise ValueError("future_shadow_review_rollback_candidate_mismatch")
    if not rollback:
        raise ValueError("future_shadow_review_rollback_missing")
    if decision == "winner" and not str(selected or "").strip():
        raise ValueError("future_shadow_review_winner_selection_missing")
    if decision != "winner" and selected is not None:
        raise ValueError("future_shadow_review_nonwinner_selection_forbidden")
    if proposal_payload.get("human_approval_required") is not True:
        raise ValueError("future_shadow_review_human_gate_missing")
    if proposal_payload.get("proposal_is_not_runtime_activation") is not True:
        raise ValueError("future_shadow_review_activation_separation_missing")

    blockers = tuple(str(item) for item in proposal_payload.get("comparison_blockers") or ())
    if decision == "insufficient_evidence" and not blockers:
        raise ValueError("future_shadow_review_insufficient_without_blockers")
    review_status = (
        "BLOCKED_INSUFFICIENT_EVIDENCE"
        if decision == "insufficient_evidence"
        else "PENDING_HUMAN_REVIEW"
    )
    digest_basis = "|".join((scope, requested, proposal_ref, execution_ref, outcome_ref))
    request_id = "review-request:" + hashlib.sha256(digest_basis.encode("utf-8")).hexdigest()[:32]

    return MappingProxyType({
        "schema_version": MARKET_REGIME_FUTURE_SHADOW_REVIEW_CONTRACTS_VERSION,
        "artifact_family": "prediction/market_regime",
        "artifact_kind": "future_shadow_review_request",
        "request_id": request_id,
        "review_scope_id": scope,
        "requested_at": requested,
        "review_status": review_status,
        "proposal_decision": decision,
        "selected_candidate_id": selected,
        "rollback_candidate_id": rollback,
        "comparison_blockers": blockers,
        "proposal_ref": proposal_ref,
        "execution_diagnostics_ref": execution_ref,
        "outcome_diagnostics_ref": outcome_ref,
        "execution_origin_count": int(execution_diagnostics.get("origin_count") or 0),
        "execution_trace_count": int(execution_diagnostics.get("trace_count") or 0),
        "outcome_snapshot_count": int(outcome_diagnostics.get("snapshot_count") or 0),
        "outcome_receipt_count": int(outcome_diagnostics.get("receipt_count") or 0),
        "outcome_trace_count": int(outcome_diagnostics.get("trace_count") or 0),
        "review_note_required": review_status == "PENDING_HUMAN_REVIEW",
        "review_link_required": review_status == "PENDING_HUMAN_REVIEW",
        "human_approval_required": True,
        "approved_by": None,
        "approved_at": None,
        "auto_promotion_allowed": False,
        "live_parameter_apply_allowed": False,
        "runtime_activation_performed": False,
        "would_write": False,
        "safety": MappingProxyType({
            "read_only_inputs": True,
            "writes_dhot": False,
            "writer_invoked": False,
            "scheduler_enabled": False,
            "auto_promotion_allowed": False,
            "live_parameter_apply_allowed": False,
            "human_gate_required": True,
        }),
    })


def build_future_shadow_review_link(
    *,
    request: Mapping[str, Any],
    note: FutureShadowReviewNote,
) -> Mapping[str, Any]:
    if request.get("artifact_kind") != "future_shadow_review_request":
        raise ValueError("future_shadow_review_link_request_kind_invalid")
    if note.request_id != str(request.get("request_id") or ""):
        raise ValueError("future_shadow_review_link_request_mismatch")
    if request.get("review_status") != "PENDING_HUMAN_REVIEW":
        raise ValueError("future_shadow_review_link_blocked_request_forbidden")
    requested_at = _parse_zulu(
        str(request.get("requested_at") or ""),
        "future_shadow_review_link_requested_at_invalid",
    )
    recorded_at = _parse_zulu(
        note.recorded_at,
        "future_shadow_review_link_note_recorded_at_invalid",
    )
    if recorded_at < requested_at:
        raise ValueError("future_shadow_review_link_note_before_request")
    if note.decision == "approve" and request.get("proposal_decision") != "winner":
        raise ValueError("future_shadow_review_link_approve_nonwinner_forbidden")
    digest_basis = "|".join((note.request_id, note.note_id))
    link = FutureShadowReviewLink(
        link_id="review-link:" + hashlib.sha256(digest_basis.encode("utf-8")).hexdigest()[:32],
        request_id=note.request_id,
        note_id=note.note_id,
        proposal_ref=str(request["proposal_ref"]),
        execution_diagnostics_ref=str(request["execution_diagnostics_ref"]),
        outcome_diagnostics_ref=str(request["outcome_diagnostics_ref"]),
    )
    return link.to_dict()
