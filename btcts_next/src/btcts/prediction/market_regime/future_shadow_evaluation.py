# path: ./btcts_next/src/btcts/prediction/market_regime/future_shadow_evaluation.py
# desc: Pure MR-F5.7 aggregation and human-gated comparison for immutable shadow future-evaluation rows. No reads or writes.

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from types import MappingProxyType
from typing import Any, Iterable, Mapping, Tuple

from .future_forecast_contract import FUTURE_MARKET_REGIME_HORIZONS_SEC
from .future_shadow_outcome import FutureShadowOutcomeStatus

MARKET_REGIME_FUTURE_SHADOW_EVALUATION_VERSION = "prediction.market_regime.future_shadow_evaluation.mr_f5_7.v1"
_SCORED = {
    FutureShadowOutcomeStatus.CORRECT.value: 1.0,
    FutureShadowOutcomeStatus.PARTIAL.value: 0.5,
    FutureShadowOutcomeStatus.INCORRECT.value: 0.0,
}
_ALL = tuple(item.value for item in FutureShadowOutcomeStatus)


@dataclass(frozen=True)
class FutureShadowCandidateKey:
    model_id: str
    logic_version: str
    parameter_set_id: str

    def __post_init__(self) -> None:
        if not self.model_id.strip() or not self.logic_version.strip() or not self.parameter_set_id.strip():
            raise ValueError("future_shadow_candidate_identity_missing")

    @property
    def key(self) -> str:
        return f"{self.model_id}|{self.logic_version}|{self.parameter_set_id}"


@dataclass(frozen=True)
class FutureShadowCandidateSummary:
    candidate: FutureShadowCandidateKey
    total_rows: int
    scored_rows: int
    unresolved_rows: int
    invalidated_rows: int
    abstained_rows: int
    correct_rows: int
    partial_rows: int
    incorrect_rows: int
    weighted_score: float | None
    insufficient_sample: bool
    minimum_scored_samples: int

    def to_dict(self) -> Mapping[str, Any]:
        return MappingProxyType({
            "candidate_key": self.candidate.key,
            "model_id": self.candidate.model_id,
            "logic_version": self.candidate.logic_version,
            "parameter_set_id": self.candidate.parameter_set_id,
            "total_rows": self.total_rows,
            "scored_rows": self.scored_rows,
            "unresolved_rows": self.unresolved_rows,
            "invalidated_rows": self.invalidated_rows,
            "abstained_rows": self.abstained_rows,
            "correct_rows": self.correct_rows,
            "partial_rows": self.partial_rows,
            "incorrect_rows": self.incorrect_rows,
            "weighted_score": self.weighted_score,
            "insufficient_sample": self.insufficient_sample,
            "minimum_scored_samples": self.minimum_scored_samples,
        })


def _validate_row(row: Mapping[str, Any]) -> None:
    if row.get("schema_version") != "prediction.market_regime.future_shadow_outcome.mr_f5_6.v1":
        raise ValueError("future_shadow_evaluation_schema_version_invalid")
    if row.get("artifact_family") != "prediction/market_regime":
        raise ValueError("future_shadow_evaluation_artifact_family_invalid")
    if row.get("artifact_kind") != "future_shadow_evaluation_row":
        raise ValueError("future_shadow_evaluation_artifact_kind_invalid")
    if row.get("shadow_only") is not True or row.get("canonical_replacement") is not False:
        raise ValueError("future_shadow_evaluation_safety_boundary_invalid")
    if row.get("ledger_append_allowed") is not False:
        raise ValueError("future_shadow_evaluation_ledger_boundary_invalid")
    horizon = int(row.get("target_horizon_sec") or 0)
    if horizon not in FUTURE_MARKET_REGIME_HORIZONS_SEC:
        raise ValueError(f"future_shadow_evaluation_horizon_invalid:{horizon}")
    if str(row.get("target_horizon_key") or "") != f"{horizon}s":
        raise ValueError("future_shadow_evaluation_horizon_key_mismatch")
    if str(row.get("target_definition_version") or "") != f"market_regime_target.{horizon}s.v1":
        raise ValueError("future_shadow_evaluation_target_definition_mismatch")
    status = str(row.get("outcome_status") or "")
    if status not in _ALL:
        raise ValueError(f"future_shadow_evaluation_status_invalid:{status}")
    for key in ("trace_id", "model_id", "logic_version", "parameter_set_id", "target_definition_version", "feature_snapshot_ref"):
        if not str(row.get(key) or "").strip():
            raise ValueError(f"future_shadow_evaluation_identity_missing:{key}")


def _candidate_key(row: Mapping[str, Any]) -> FutureShadowCandidateKey:
    return FutureShadowCandidateKey(
        model_id=str(row["model_id"]),
        logic_version=str(row["logic_version"]),
        parameter_set_id=str(row["parameter_set_id"]),
    )


def _summary(candidate: FutureShadowCandidateKey, rows: Tuple[Mapping[str, Any], ...], minimum_scored_samples: int) -> FutureShadowCandidateSummary:
    counts = {status: 0 for status in _ALL}
    for row in rows:
        counts[str(row["outcome_status"])] += 1
    scored = counts[FutureShadowOutcomeStatus.CORRECT.value] + counts[FutureShadowOutcomeStatus.PARTIAL.value] + counts[FutureShadowOutcomeStatus.INCORRECT.value]
    score_sum = (
        counts[FutureShadowOutcomeStatus.CORRECT.value] * 1.0
        + counts[FutureShadowOutcomeStatus.PARTIAL.value] * 0.5
    )
    return FutureShadowCandidateSummary(
        candidate=candidate,
        total_rows=len(rows),
        scored_rows=scored,
        unresolved_rows=counts[FutureShadowOutcomeStatus.UNRESOLVED.value],
        invalidated_rows=counts[FutureShadowOutcomeStatus.INVALIDATED.value],
        abstained_rows=counts[FutureShadowOutcomeStatus.ABSTAINED.value],
        correct_rows=counts[FutureShadowOutcomeStatus.CORRECT.value],
        partial_rows=counts[FutureShadowOutcomeStatus.PARTIAL.value],
        incorrect_rows=counts[FutureShadowOutcomeStatus.INCORRECT.value],
        weighted_score=round(score_sum / scored, 4) if scored else None,
        insufficient_sample=scored < minimum_scored_samples,
        minimum_scored_samples=minimum_scored_samples,
    )


def build_market_regime_future_shadow_evaluation(
    *,
    rows: Iterable[Mapping[str, Any]],
    minimum_scored_samples: int = 20,
) -> Mapping[str, Any]:
    minimum = int(minimum_scored_samples)
    if minimum <= 0:
        raise ValueError("future_shadow_evaluation_minimum_samples_invalid")
    safe_rows: list[Mapping[str, Any]] = []
    seen_trace_ids: set[str] = set()
    for row in rows:
        if not isinstance(row, Mapping):
            raise ValueError("future_shadow_evaluation_row_not_mapping")
        _validate_row(row)
        trace_id = str(row["trace_id"])
        if trace_id in seen_trace_ids:
            raise ValueError(f"future_shadow_evaluation_duplicate_trace_id:{trace_id}")
        seen_trace_ids.add(trace_id)
        safe_rows.append(row)

    by_candidate: dict[FutureShadowCandidateKey, list[Mapping[str, Any]]] = defaultdict(list)
    by_candidate_horizon: dict[tuple[FutureShadowCandidateKey, int], list[Mapping[str, Any]]] = defaultdict(list)
    for row in safe_rows:
        candidate = _candidate_key(row)
        horizon = int(row["target_horizon_sec"])
        by_candidate[candidate].append(row)
        by_candidate_horizon[(candidate, horizon)].append(row)

    candidate_summaries = tuple(
        _summary(candidate, tuple(by_candidate[candidate]), minimum)
        for candidate in sorted(by_candidate, key=lambda item: item.key)
    )
    comparable = tuple(item for item in candidate_summaries if not item.insufficient_sample and item.weighted_score is not None)
    scored_horizons_by_candidate = {
        candidate: frozenset(
            horizon
            for (row_candidate, horizon), horizon_rows in by_candidate_horizon.items()
            if row_candidate == candidate
            and _summary(candidate, tuple(horizon_rows), minimum).insufficient_sample is False
        )
        for candidate in by_candidate
    }
    comparable_horizon_sets = {scored_horizons_by_candidate[item.candidate] for item in comparable}
    same_horizon_coverage = len(comparable_horizon_sets) == 1 and bool(next(iter(comparable_horizon_sets), frozenset()))
    comparison_ready = len(comparable) >= 2 and same_horizon_coverage
    comparison_blockers = (
        ()
        if comparison_ready
        else (
            ("fewer_than_two_candidates_with_minimum_scored_samples",)
            if len(comparable) < 2
            else ("candidate_horizon_coverage_mismatch",)
        )
    )
    ranked = tuple(sorted(comparable, key=lambda item: (item.weighted_score if item.weighted_score is not None else -1.0, item.scored_rows, item.candidate.key), reverse=True))

    horizon_rows = []
    for candidate, horizon in sorted(by_candidate_horizon, key=lambda item: (item[0].key, item[1])):
        view = _summary(candidate, tuple(by_candidate_horizon[(candidate, horizon)]), minimum)
        payload = dict(view.to_dict())
        payload["target_horizon_sec"] = horizon
        payload["target_horizon_key"] = f"{horizon}s"
        horizon_rows.append(MappingProxyType(payload))

    recommendations = tuple(MappingProxyType({
        "candidate_key": item.candidate.key,
        "rank": index + 1,
        "recommendation": "human_review" if comparison_ready else "keep_collecting",
        "weighted_score": item.weighted_score,
        "scored_rows": item.scored_rows,
        "human_gate_required": True,
        "auto_promotion_allowed": False,
        "auto_apply_allowed": False,
    }) for index, item in enumerate(ranked if comparison_ready else candidate_summaries))

    return MappingProxyType({
        "schema_version": MARKET_REGIME_FUTURE_SHADOW_EVALUATION_VERSION,
        "artifact_family": "prediction/market_regime",
        "artifact_kind": "future_shadow_evaluation_summary",
        "row_count": len(safe_rows),
        "candidate_count": len(candidate_summaries),
        "comparable_candidate_count": len(comparable),
        "minimum_scored_samples": minimum,
        "comparison_ready": comparison_ready,
        "comparison_blockers": comparison_blockers,
        "candidate_summaries": tuple(item.to_dict() for item in candidate_summaries),
        "by_candidate_horizon": tuple(horizon_rows),
        "recommendations": recommendations,
        "promotion_candidates": (),
        "safety": MappingProxyType({
            "shadow_only": True,
            "read_only_inputs": True,
            "writes_dhot": False,
            "ledger_append_allowed": False,
            "parameter_auto_promotion_allowed": False,
            "live_parameter_apply_allowed": False,
            "human_gate_required": True,
            "canonical_replacement": False,
        }),
    })
