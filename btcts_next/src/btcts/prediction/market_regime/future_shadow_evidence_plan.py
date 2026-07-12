# path: ./btcts_next/src/btcts/prediction/market_regime/future_shadow_evidence_plan.py
# desc: Pure MR-F5.9 evidence-plan and canonical-migration review criteria for MarketRegime shadow forecasts. No reads or writes.

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from types import MappingProxyType
from typing import Any, Mapping, Tuple

from .future_forecast_contract import FUTURE_MARKET_REGIME_HORIZONS_SEC

MARKET_REGIME_FUTURE_SHADOW_EVIDENCE_PLAN_VERSION = "prediction.market_regime.future_shadow_evidence_plan.mr_f5_9.v1"
_REQUIRED_FEATURE_FAMILIES = (
    "price_structure",
    "volatility",
    "liquidity",
    "source_quality",
)
_LONG_HORIZONS = frozenset({21600, 43200, 86400})
_DEFAULT_MINIMUM_SCORED_ROWS_PER_CANDIDATE_HORIZON = 20
_DEFAULT_MINIMUM_OBSERVATION_WINDOW_SEC = 86400


def _strict_non_negative_int(value: object, error: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError(error)
    return value


def _parse_canonical_utc(value: str, error: str) -> datetime:
    if not isinstance(value, str) or not value.endswith("Z"):
        raise ValueError(error)
    try:
        parsed = datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError as exc:
        raise ValueError(error) from exc
    if parsed.tzinfo != timezone.utc or parsed.isoformat().replace("+00:00", "Z") != value:
        raise ValueError(error)
    return parsed


@dataclass(frozen=True)
class FutureShadowFeatureAvailabilityEvidence:
    horizon_sec: int
    observed_snapshot_count: int
    available_feature_families: Tuple[str, ...]
    first_observed_at: str
    last_observed_at: str
    source_role: str
    source_artifact_refs: Tuple[str, ...]
    lookahead_violations: int = 0

    def __post_init__(self) -> None:
        horizon = int(self.horizon_sec)
        if horizon not in FUTURE_MARKET_REGIME_HORIZONS_SEC:
            raise ValueError(f"future_shadow_evidence_horizon_invalid:{horizon}")
        _strict_non_negative_int(self.observed_snapshot_count, "future_shadow_evidence_snapshot_count_invalid")
        families = tuple(dict.fromkeys(str(item).strip() for item in self.available_feature_families))
        if any(not item for item in families):
            raise ValueError("future_shadow_evidence_feature_family_invalid")
        object.__setattr__(self, "available_feature_families", families)
        refs = tuple(dict.fromkeys(str(item).strip() for item in self.source_artifact_refs))
        if any(not item for item in refs):
            raise ValueError("future_shadow_evidence_source_ref_invalid")
        object.__setattr__(self, "source_artifact_refs", refs)
        first_observed = _parse_canonical_utc(
            self.first_observed_at, "future_shadow_evidence_first_observed_at_invalid"
        )
        last_observed = _parse_canonical_utc(
            self.last_observed_at, "future_shadow_evidence_last_observed_at_invalid"
        )
        if last_observed < first_observed:
            raise ValueError("future_shadow_evidence_feature_time_order_invalid")
        if not isinstance(self.source_role, str) or not self.source_role.strip():
            raise ValueError("future_shadow_evidence_identity_missing:source_role")
        if self.source_role != "hot_data_root":
            raise ValueError("future_shadow_evidence_source_role_invalid")
        _strict_non_negative_int(self.lookahead_violations, "future_shadow_evidence_lookahead_count_invalid")


@dataclass(frozen=True)
class FutureShadowOutcomeCoverageEvidence:
    candidate_key: str
    horizon_sec: int
    total_rows: int
    scored_rows: int
    unresolved_rows: int
    invalidated_rows: int
    abstained_rows: int
    observation_window_sec: int
    first_origin_at: str
    last_resolved_at: str
    evaluation_artifact_refs: Tuple[str, ...]

    def __post_init__(self) -> None:
        if not self.candidate_key.strip():
            raise ValueError("future_shadow_evidence_candidate_key_missing")
        if int(self.horizon_sec) not in FUTURE_MARKET_REGIME_HORIZONS_SEC:
            raise ValueError("future_shadow_evidence_coverage_horizon_invalid")
        numeric = (
            self.total_rows, self.scored_rows, self.unresolved_rows,
            self.invalidated_rows, self.abstained_rows, self.observation_window_sec,
        )
        for value in numeric:
            _strict_non_negative_int(value, "future_shadow_evidence_coverage_count_invalid")
        classified = int(self.scored_rows) + int(self.unresolved_rows) + int(self.invalidated_rows) + int(self.abstained_rows)
        if classified != int(self.total_rows):
            raise ValueError("future_shadow_evidence_coverage_total_mismatch")
        refs = tuple(dict.fromkeys(str(item).strip() for item in self.evaluation_artifact_refs))
        if any(not item for item in refs):
            raise ValueError("future_shadow_evidence_evaluation_ref_invalid")
        object.__setattr__(self, "evaluation_artifact_refs", refs)
        first_origin = _parse_canonical_utc(
            self.first_origin_at, "future_shadow_evidence_first_origin_at_invalid"
        )
        last_resolved = _parse_canonical_utc(
            self.last_resolved_at, "future_shadow_evidence_last_resolved_at_invalid"
        )
        if last_resolved < first_origin:
            raise ValueError("future_shadow_evidence_coverage_time_order_invalid")
        actual_window = int((last_resolved - first_origin).total_seconds())
        if actual_window != self.observation_window_sec:
            raise ValueError("future_shadow_evidence_observation_window_mismatch")


@dataclass(frozen=True)
class CanonicalMigrationReviewEvidence:
    reviewer_ids: Tuple[str, ...]
    review_artifact_refs: Tuple[str, ...]
    current_state_behavior_unchanged: bool
    exact_horizon_projection_verified: bool
    legacy_fallback_removal_plan_reviewed: bool
    rollback_plan_verified: bool
    operator_ui_impact_reviewed: bool
    outcome_identity_compatibility_verified: bool
    calibrated_probability_claim_absent: bool

    def __post_init__(self) -> None:
        reviewers = tuple(dict.fromkeys(str(item).strip() for item in self.reviewer_ids))
        refs = tuple(dict.fromkeys(str(item).strip() for item in self.review_artifact_refs))
        if not reviewers or any(not item for item in reviewers):
            raise ValueError("future_shadow_evidence_reviewer_invalid")
        if not refs or any(not item for item in refs):
            raise ValueError("future_shadow_evidence_review_ref_invalid")
        object.__setattr__(self, "reviewer_ids", reviewers)
        object.__setattr__(self, "review_artifact_refs", refs)
        for name in (
            "current_state_behavior_unchanged",
            "exact_horizon_projection_verified",
            "legacy_fallback_removal_plan_reviewed",
            "rollback_plan_verified",
            "operator_ui_impact_reviewed",
            "outcome_identity_compatibility_verified",
            "calibrated_probability_claim_absent",
        ):
            if type(getattr(self, name)) is not bool:
                raise ValueError(f"future_shadow_evidence_review_boolean_invalid:{name}")


def build_market_regime_future_shadow_evidence_plan(
    *,
    feature_evidence: Tuple[FutureShadowFeatureAvailabilityEvidence, ...],
    outcome_coverage: Tuple[FutureShadowOutcomeCoverageEvidence, ...],
    migration_review: CanonicalMigrationReviewEvidence | None,
    minimum_scored_rows_per_candidate_horizon: int = _DEFAULT_MINIMUM_SCORED_ROWS_PER_CANDIDATE_HORIZON,
    minimum_observation_window_sec: int = _DEFAULT_MINIMUM_OBSERVATION_WINDOW_SEC,
) -> Mapping[str, Any]:
    minimum_rows = _strict_non_negative_int(
        minimum_scored_rows_per_candidate_horizon, "future_shadow_evidence_minimum_invalid"
    )
    minimum_window = _strict_non_negative_int(
        minimum_observation_window_sec, "future_shadow_evidence_minimum_invalid"
    )
    if minimum_rows <= 0 or minimum_window <= 0:
        raise ValueError("future_shadow_evidence_minimum_invalid")

    feature_by_horizon = {int(item.horizon_sec): item for item in feature_evidence}
    if len(feature_by_horizon) != len(feature_evidence):
        raise ValueError("future_shadow_evidence_duplicate_feature_horizon")

    feature_blockers: list[str] = []
    for horizon in FUTURE_MARKET_REGIME_HORIZONS_SEC:
        item = feature_by_horizon.get(int(horizon))
        if item is None:
            feature_blockers.append(f"feature_evidence_missing:{horizon}")
            continue
        required = set(_REQUIRED_FEATURE_FAMILIES)
        if int(horizon) in _LONG_HORIZONS:
            required.add("session_context")
        missing = tuple(sorted(required - set(item.available_feature_families)))
        for family in missing:
            feature_blockers.append(f"required_feature_missing:{horizon}:{family}")
        if int(item.observed_snapshot_count) <= 0:
            feature_blockers.append(f"representative_snapshot_absent:{horizon}")
        if int(item.lookahead_violations) != 0:
            feature_blockers.append(f"lookahead_violation_present:{horizon}")
        if not item.source_artifact_refs:
            feature_blockers.append(f"feature_source_refs_absent:{horizon}")

    coverage_keys: set[tuple[str, int]] = set()
    coverage_blockers: list[str] = []
    candidates: set[str] = set()
    for item in outcome_coverage:
        key = (item.candidate_key, int(item.horizon_sec))
        if key in coverage_keys:
            raise ValueError("future_shadow_evidence_duplicate_candidate_horizon")
        coverage_keys.add(key)
        candidates.add(item.candidate_key)
        if int(item.scored_rows) < minimum_rows:
            coverage_blockers.append(f"scored_rows_below_minimum:{item.candidate_key}:{item.horizon_sec}")
        if int(item.observation_window_sec) < minimum_window:
            coverage_blockers.append(f"observation_window_below_minimum:{item.candidate_key}:{item.horizon_sec}")
        if not item.evaluation_artifact_refs:
            coverage_blockers.append(f"evaluation_refs_absent:{item.candidate_key}:{item.horizon_sec}")

    if len(candidates) < 2:
        coverage_blockers.append("fewer_than_two_shadow_candidates")
    for candidate in sorted(candidates):
        for horizon in FUTURE_MARKET_REGIME_HORIZONS_SEC:
            if (candidate, int(horizon)) not in coverage_keys:
                coverage_blockers.append(f"candidate_horizon_coverage_missing:{candidate}:{horizon}")

    review_blockers: list[str] = []
    if migration_review is None:
        review_blockers.append("canonical_migration_review_absent")
    else:
        for name in (
            "current_state_behavior_unchanged",
            "exact_horizon_projection_verified",
            "legacy_fallback_removal_plan_reviewed",
            "rollback_plan_verified",
            "operator_ui_impact_reviewed",
            "outcome_identity_compatibility_verified",
            "calibrated_probability_claim_absent",
        ):
            if getattr(migration_review, name) is not True:
                review_blockers.append(f"canonical_migration_review_incomplete:{name}")

    blockers = tuple(feature_blockers + coverage_blockers + review_blockers)
    ready = not blockers
    return MappingProxyType({
        "schema_version": MARKET_REGIME_FUTURE_SHADOW_EVIDENCE_PLAN_VERSION,
        "artifact_family": "prediction/market_regime",
        "artifact_kind": "future_shadow_evidence_plan",
        "source_role": "hot_data_root",
        "legacy_canonical_records_count_as_shadow_evidence": False,
        "required_horizons_sec": tuple(int(item) for item in FUTURE_MARKET_REGIME_HORIZONS_SEC),
        "minimum_scored_rows_per_candidate_horizon": minimum_rows,
        "minimum_observation_window_sec": minimum_window,
        "feature_availability_proven": not feature_blockers,
        "shadow_outcome_coverage_proven": not coverage_blockers,
        "canonical_migration_review_completed": not review_blockers,
        "ready_for_family_completion_review": ready,
        "blockers": blockers,
        "feature_blockers": tuple(feature_blockers),
        "coverage_blockers": tuple(coverage_blockers),
        "review_blockers": tuple(review_blockers),
        "candidate_count": len(candidates),
        "feature_horizon_count": len(feature_by_horizon),
        "candidate_horizon_count": len(coverage_keys),
        "safety": MappingProxyType({
            "read_only_plan": True,
            "writes_dhot": False,
            "manufactures_evidence": False,
            "canonical_replacement": False,
            "parameter_auto_promotion_allowed": False,
            "live_parameter_apply_allowed": False,
            "ui_change": False,
            "human_gate_required": True,
        }),
    })
