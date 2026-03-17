# path: ./btcts_next/src/btcts/market_engine/onboarding/rebuild_validator.py
# desc: Validate assembled orderbook snapshots against anchor-like expectations during exchange onboarding.

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class RebuildValidationResult:
    ok: bool
    checks: dict[str, bool]
    details: dict[str, Any]


class RebuildValidator:
    def validate_top_of_book(
        self,
        *,
        assembled_book: dict[str, Any],
        reference_snapshot: dict[str, Any],
    ) -> RebuildValidationResult:
        assembled_best_bid = assembled_book.get("best_bid")
        assembled_best_ask = assembled_book.get("best_ask")

        ref_best_bid = reference_snapshot.get("best_bid")
        ref_best_ask = reference_snapshot.get("best_ask")

        checks = {
            "assembled_has_best_bid": assembled_best_bid is not None,
            "assembled_has_best_ask": assembled_best_ask is not None,
            "reference_has_best_bid": ref_best_bid is not None,
            "reference_has_best_ask": ref_best_ask is not None,
            "best_bid_matches": assembled_best_bid == ref_best_bid,
            "best_ask_matches": assembled_best_ask == ref_best_ask,
        }

        ok = all(checks.values())
        return RebuildValidationResult(
            ok=ok,
            checks=checks,
            details={
                "assembled_best_bid": assembled_best_bid,
                "assembled_best_ask": assembled_best_ask,
                "reference_best_bid": ref_best_bid,
                "reference_best_ask": ref_best_ask,
            },
        )

    def validate_not_crossed(self, *, assembled_book: dict[str, Any]) -> RebuildValidationResult:
        best_bid = assembled_book.get("best_bid")
        best_ask = assembled_book.get("best_ask")

        checks = {
            "has_best_bid": best_bid is not None,
            "has_best_ask": best_ask is not None,
            "not_crossed": (
                best_bid is not None
                and best_ask is not None
                and float(best_bid) <= float(best_ask)
            ),
        }
        ok = all(checks.values())
        return RebuildValidationResult(
            ok=ok,
            checks=checks,
            details={
                "best_bid": best_bid,
                "best_ask": best_ask,
            },
        )