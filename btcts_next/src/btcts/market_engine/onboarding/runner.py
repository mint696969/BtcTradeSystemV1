# path: ./btcts_next/src/btcts/market_engine/onboarding/runner.py
# desc: Formal onboarding entrypoint that bundles capture, continuity, and profile draft analysis.

from __future__ import annotations

from dataclasses import asdict
from collections import defaultdict
import re
from statistics import mean
from typing import Any

from btcts.market_engine.onboarding.capture_probe import CaptureProbe
from btcts.market_engine.onboarding.continuity_probe import ContinuityProbe
from btcts.market_engine.onboarding.profile_draft import ProfileDraftBuilder
from btcts.market_engine.onboarding.stream_classifier import StreamClassifier


class OnboardingRunner:
    def __init__(self) -> None:
        self._capture_probe = CaptureProbe()
        self._continuity_probe = ContinuityProbe()
        self._profile_draft_builder = ProfileDraftBuilder()
        self._classifier = StreamClassifier()

    def _logical_stream_group_key(self, event: dict[str, Any]) -> str:
        classified = self._classifier.classify(event)
        stream_session_id = classified.stream_session_id or "missing"

        normalized = stream_session_id
        normalized = re.sub(r"-\d{8}T\d{6}Z-[0-9a-f]+$", "", normalized)
        normalized = normalized.replace("-board_snapshot", "-board")
        normalized = normalized.replace("-board_ws", "-board")

        return normalized

    def _event_sort_key(self, event: dict[str, Any]) -> tuple[int, str, str]:
        classified = self._classifier.classify(event)

        seq = classified.sequence_id
        seq_key = seq if isinstance(seq, int) else 10**18

        payload = event.get("payload")
        payload_dict = payload if isinstance(payload, dict) else {}

        event_ts = str(
            event.get("event_ts")
            or event.get("collector_ts")
            or event.get("ingest_ts")
            or payload_dict.get("event_ts")
            or ""
        )

        record_id = str(event.get("record_id") or "")

        return (seq_key, event_ts, record_id)

    def _build_rebuild_readiness(
        self,
        normalized_events: list[dict[str, Any]],
    ) -> dict[str, Any]:
        grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)

        for event in normalized_events:
            group_key = self._logical_stream_group_key(event)
            grouped[group_key].append(event)

        snapshot_count = 0
        diff_count = 0
        boundary_count = 0

        boundary_then_snapshot_count = 0
        snapshot_to_first_diff_count = 0
        diff_chain_lengths: list[int] = []

        logical_groups_with_snapshot = 0
        logical_groups_with_diff_after_snapshot = 0
        logical_groups_rebuild_ready = 0

        for session_events in grouped.values():
            session_events = sorted(session_events, key=self._event_sort_key)
            session_snapshot_count = 0
            session_diff_count = 0
            session_boundary_count = 0

            session_boundary_then_snapshot_count = 0
            snapshot_after_boundary_pending = False

            session_snapshot_to_first_diff_count = 0
            snapshot_pending_first_diff = False

            current_diff_chain = 0

            for event in session_events:
                classified = self._classifier.classify(event)

                if classified.family == "boundary":
                    session_boundary_count += 1
                    snapshot_after_boundary_pending = True
                    continue

                if classified.family == "snapshot":
                    session_snapshot_count += 1

                    if snapshot_after_boundary_pending:
                        session_boundary_then_snapshot_count += 1
                        snapshot_after_boundary_pending = False

                    if current_diff_chain > 0:
                        diff_chain_lengths.append(current_diff_chain)
                        current_diff_chain = 0

                    # snapshot is treated as a fresh anchor candidate inside the logical stream
                    snapshot_pending_first_diff = True
                    continue

                if classified.family == "diff":
                    session_diff_count += 1

                    if snapshot_pending_first_diff:
                        session_snapshot_to_first_diff_count += 1
                        snapshot_pending_first_diff = False

                    current_diff_chain += 1
                    continue

            if current_diff_chain > 0:
                diff_chain_lengths.append(current_diff_chain)

            snapshot_count += session_snapshot_count
            diff_count += session_diff_count
            boundary_count += session_boundary_count
            boundary_then_snapshot_count += session_boundary_then_snapshot_count
            snapshot_to_first_diff_count += session_snapshot_to_first_diff_count

            if session_snapshot_count > 0:
                logical_groups_with_snapshot += 1
            if session_snapshot_to_first_diff_count > 0:
                logical_groups_with_diff_after_snapshot += 1
            if session_snapshot_count > 0 and session_diff_count > 0:
                logical_groups_rebuild_ready += 1

        return {
            "logical_group_count": len(grouped),
            "snapshot_count": snapshot_count,
            "diff_count": diff_count,
            "boundary_count": boundary_count,
            "boundary_then_snapshot_count": boundary_then_snapshot_count,
            "snapshot_to_first_diff_count": snapshot_to_first_diff_count,
            "diff_chain_count": len(diff_chain_lengths),
            "diff_chain_len_min": min(diff_chain_lengths) if diff_chain_lengths else None,
            "diff_chain_len_max": max(diff_chain_lengths) if diff_chain_lengths else None,
            "diff_chain_len_avg": mean(diff_chain_lengths) if diff_chain_lengths else None,
            "logical_groups_with_snapshot": logical_groups_with_snapshot,
            "logical_groups_with_diff_after_snapshot": logical_groups_with_diff_after_snapshot,
            "logical_groups_rebuild_ready": logical_groups_rebuild_ready,
            "anchor_chain_ready": snapshot_to_first_diff_count > 0,
            "anchor_chain_observation_mode": "logical_group_sorted_by_sequence_then_time",
            "has_anchor_candidates": snapshot_count > 0,
            "has_diff_after_snapshot": snapshot_to_first_diff_count > 0,
            "rebuild_test_ready": logical_groups_rebuild_ready > 0,
        }

    def run(
        self,
        *,
        normalized_events: list[dict[str, Any]],
        profile_name_hint: str,
        profile: Any | None = None,
        capture_limit: int = 20,
    ) -> dict[str, Any]:
        capture_rows = self._capture_probe.sample_dicts(
            normalized_events,
            limit=capture_limit,
        )
        continuity_summary = asdict(
            self._continuity_probe.summarize(normalized_events)
        )
        profile_draft = self._profile_draft_builder.build_dict(
            normalized_events=normalized_events,
            profile_name_hint=profile_name_hint,
            profile=profile,
        )
        rebuild_readiness = self._build_rebuild_readiness(normalized_events)
        snapshot_drift_review_summary = None
        rebuild_review_summary = None

        if profile is not None:
            snapshot_drift_review_summary = profile.build_snapshot_drift_review_summary(
                normalized_events,
                profile_name_hint=profile_name_hint,
            )

            rebuild_review = profile.build_rebuild_review(
                normalized_events=normalized_events,
                profile_name_hint=profile_name_hint,
            )
            if rebuild_review is not None:
                rebuild_review_summary = {
                    "logical_group_key": rebuild_review.get("logical_group_key"),
                    "compare_count": rebuild_review.get("compare_count"),
                    "summary": rebuild_review.get("summary"),
                    "representative_cases": rebuild_review.get("representative_cases"),
                }

        return {
            "profile_name_hint": profile_name_hint,
            "total_events": len(normalized_events),
            "capture_probe": capture_rows,
            "continuity_summary": continuity_summary,
            "rebuild_readiness": rebuild_readiness,
            "snapshot_drift_review_summary": snapshot_drift_review_summary,
            "rebuild_review_summary": rebuild_review_summary,
            "profile_draft": profile_draft,
        }


def run_onboarding(
    *,
    normalized_events: list[dict[str, Any]],
    profile_name_hint: str,
    profile: Any | None = None,
    capture_limit: int = 20,
) -> dict[str, Any]:
    runner = OnboardingRunner()
    return runner.run(
        normalized_events=normalized_events,
        profile_name_hint=profile_name_hint,
        profile=profile,
        capture_limit=capture_limit,
    )