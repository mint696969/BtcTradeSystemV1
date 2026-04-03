# path: ./btcts_next/src/btcts/market_engine/assembler/profiles/base.py
# desc: Abstract exchange profile contract for Market Engine assembly and venue-specific rebuild policy.

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from btcts.processing.l3_market_semantics.continuity.models import BookState
from btcts.processing.l3_market_semantics.continuity.models import SeriesState
from btcts.market_engine.types import BoundaryReason


class ExchangeProfile(ABC):
    profile_name: str

    @abstractmethod
    def classify_event(self, normalized_event: dict[str, Any]) -> str:
        """Return canonical family such as snapshot / diff / boundary / trade / unknown."""

    @abstractmethod
    def message_family(self, normalized_event: dict[str, Any]) -> str:
        """Return venue-level message family for routing and diagnostics."""

    @abstractmethod
    def is_boundary_event(self, normalized_event: dict[str, Any]) -> bool:
        """Return True when the event forces boundary handling."""

    @abstractmethod
    def boundary_reason(self, normalized_event: dict[str, Any]) -> BoundaryReason:
        """Return the semantic reason for a boundary split or trust transition."""

    @abstractmethod
    def is_anchor_candidate(self, normalized_event: dict[str, Any]) -> bool:
        """Return True when the event can become a new anchor snapshot."""

    @abstractmethod
    def can_attach_diff(
        self,
        book_state: BookState,
        normalized_event: dict[str, Any],
        series_state: SeriesState,
    ) -> bool:
        """Return True when a diff may be safely attached to the current assembled state."""

    @abstractmethod
    def apply_anchor(self, book_state: BookState, normalized_event: dict[str, Any]) -> BookState:
        """Apply an anchor snapshot and return the updated book state."""

    @abstractmethod
    def apply_diff(self, book_state: BookState, normalized_event: dict[str, Any]) -> BookState:
        """Apply a diff event and return the updated book state."""

    @abstractmethod
    def build_zone_policy(self, book_state: BookState) -> dict[str, Any]:
        """Return near/far zone policy metadata for the current book state."""

    @abstractmethod
    def validate_rebuild_state(self, book_state: BookState) -> bool:
        """Return True when the rebuilt state is semantically acceptable for downstream use."""

    def review_policy(self) -> dict[str, Any]:
        """Return venue review posture metadata for Layer3/onboarding use."""
        return {}

    def audit_policy(self) -> dict[str, Any]:
        """Return profile hints for onboarding/audit bridges."""
        return self.review_policy()

    def build_snapshot_drift_review_summary(
        self,
        normalized_events: list[dict[str, Any]],
        *,
        profile_name_hint: str,
    ) -> dict[str, Any] | None:
        """Return venue-specific snapshot drift review summary for onboarding."""
        return None

    def build_rebuild_review(
        self,
        *,
        normalized_events: list[dict[str, Any]],
        profile_name_hint: str,
    ) -> dict[str, Any] | None:
        """Return venue-specific rebuild review for onboarding."""
        return None