# path: ./btcts_next/src/btcts/processing/l3_market_semantics/orderbook/semantic_profile.py
# desc: Orderbook semantic threshold profile and normalization helpers.

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping


@dataclass(frozen=True)
class OrderbookSemanticProfile:
    pressure_threshold: float = 0.20
    wall_ratio_threshold: float = 0.30
    wall_near_rank_threshold: int = 5
    pull_threshold: float = 0.20
    pull_near_levels: int = 3
    strong_pull_threshold: float = 0.40

    @classmethod
    def from_policy(
        cls,
        policy: Mapping[str, Any] | None,
        *,
        levels: int,
    ) -> "OrderbookSemanticProfile":
        raw = dict(policy or {})

        pull_near_levels_raw = raw.get("pull_near_levels")
        if pull_near_levels_raw is None:
            pull_near_levels = min(3, levels)
        else:
            pull_near_levels = int(pull_near_levels_raw)

        return cls(
            pressure_threshold=float(raw.get("pressure_threshold", cls.pressure_threshold)),
            wall_ratio_threshold=float(raw.get("wall_ratio_threshold", cls.wall_ratio_threshold)),
            wall_near_rank_threshold=int(raw.get("wall_near_rank_threshold", cls.wall_near_rank_threshold)),
            pull_threshold=float(raw.get("pull_threshold", cls.pull_threshold)),
            pull_near_levels=pull_near_levels,
            strong_pull_threshold=float(raw.get("strong_pull_threshold", cls.strong_pull_threshold)),
        )

    def to_policy(self) -> dict[str, float | int]:
        return {
            "pressure_threshold": self.pressure_threshold,
            "wall_ratio_threshold": self.wall_ratio_threshold,
            "wall_near_rank_threshold": self.wall_near_rank_threshold,
            "pull_threshold": self.pull_threshold,
            "pull_near_levels": self.pull_near_levels,
            "strong_pull_threshold": self.strong_pull_threshold,
        }


def resolve_orderbook_semantic_policy(
    *,
    baseline_policy: Mapping[str, Any] | None = None,
    override_policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    resolved: dict[str, Any] = {}

    if baseline_policy:
        resolved.update(dict(baseline_policy))

    if override_policy:
        resolved.update(dict(override_policy))

    return resolved