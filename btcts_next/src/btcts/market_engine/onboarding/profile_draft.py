# path: ./btcts_next/src/btcts/market_engine/onboarding/profile_draft.py
# desc: Build an initial profile draft summary from classified onboarding observations.

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from btcts.market_engine.onboarding.continuity_probe import ContinuityProbe
from btcts.market_engine.onboarding.stream_classifier import StreamClassifier


@dataclass(frozen=True)
class ProfileDraft:
    profile_name_hint: str
    observed_families: list[str]
    observed_continuity_states: list[str]
    has_snapshot_family: bool
    has_diff_family: bool
    has_boundary_family: bool
    likely_anchor_family: str | None
    known_profile_hints: dict[str, Any] | None
    runtime_candidate_policy: dict[str, Any] | None
    notes: list[str]


class ProfileDraftBuilder:
    def __init__(self) -> None:
        self._classifier = StreamClassifier()
        self._continuity_probe = ContinuityProbe()

    def build(
        self,
        *,
        normalized_events: list[dict[str, Any]],
        profile_name_hint: str,
        profile: Any | None = None,
    ) -> ProfileDraft:
        family_set: set[str] = set()
        continuity_set: set[str] = set()

        for event in normalized_events:
            classified = self._classifier.classify(event)
            family_set.add(classified.family)
            if classified.continuity_state:
                continuity_set.add(classified.continuity_state)

        summary = self._continuity_probe.summarize(normalized_events)

        has_snapshot_family = "snapshot" in family_set
        has_diff_family = "diff" in family_set
        has_boundary_family = "boundary" in family_set

        likely_anchor_family = "snapshot" if has_snapshot_family else None

        known_profile_hints: dict[str, Any] | None = None
        runtime_candidate_policy: dict[str, Any] | None = None
        if profile is not None:
            candidate = profile.audit_policy()
            if isinstance(candidate, dict):
                known_profile_hints = candidate
                runtime_candidate_policy = dict(candidate)

        notes: list[str] = []
        if has_snapshot_family:
            notes.append("snapshot family observed; likely anchor candidate exists")
        if has_diff_family:
            notes.append("diff family observed; profile will need explicit diff attach rules")
        if has_boundary_family:
            notes.append("boundary family observed; stream lifecycle evidence is available for onboarding")
        if summary.stream_started_count > 0:
            notes.append("stream.started observed; session boundaries can be tracked from normalized evidence")
        if summary.expected_discontinuity_count > 0:
            notes.append("expected_continuity=false stream starts were observed; some boundaries are intentionally non-continuous")
        if summary.gap_detected_count > 0:
            notes.append("gap_detected observed; boundary split behavior is required")
        if summary.resync_like_count > 0:
            notes.append("resync-like continuity observed; fresh anchor handling is likely required")
        if has_boundary_family and summary.gap_detected_count == 0 and summary.resync_like_count == 0:
            notes.append("boundary evidence exists, but explicit gap/resync continuity events were not observed in this sample")
        if known_profile_hints is not None:
            notes.append("known venue profile hints are available for comparison against observations")
        if runtime_candidate_policy is not None:
            notes.append("runtime candidate policy was extracted as a review-only bridge to assembler profile")

        if not notes:
            notes.append("observation set is still sparse; collect more normalized events")

        return ProfileDraft(
            profile_name_hint=profile_name_hint,
            observed_families=sorted(family_set),
            observed_continuity_states=sorted(continuity_set),
            has_snapshot_family=has_snapshot_family,
            has_diff_family=has_diff_family,
            has_boundary_family=has_boundary_family,
            likely_anchor_family=likely_anchor_family,
            known_profile_hints=known_profile_hints,
            runtime_candidate_policy=runtime_candidate_policy,
            notes=notes,
        )

    def build_dict(
        self,
        *,
        normalized_events: list[dict[str, Any]],
        profile_name_hint: str,
        profile: Any | None = None,
    ) -> dict[str, Any]:
        draft = self.build(
            normalized_events=normalized_events,
            profile_name_hint=profile_name_hint,
            profile=profile,
        )
        return {
            "profile_name_hint": draft.profile_name_hint,
            "observed_families": draft.observed_families,
            "observed_continuity_states": draft.observed_continuity_states,
            "has_snapshot_family": draft.has_snapshot_family,
            "has_diff_family": draft.has_diff_family,
            "has_boundary_family": draft.has_boundary_family,
            "likely_anchor_family": draft.likely_anchor_family,
            "known_profile_hints": draft.known_profile_hints,
            "runtime_candidate_policy": draft.runtime_candidate_policy,
            "notes": draft.notes,
        }