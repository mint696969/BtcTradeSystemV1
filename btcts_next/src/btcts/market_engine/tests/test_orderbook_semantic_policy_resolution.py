# path: ./btcts_next/src/btcts/market_engine/tests/test_orderbook_semantic_policy_resolution.py
# desc: Verify orderbook semantic baseline/override resolution through replay pipeline profile wiring.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[3]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.market_engine.profiles import create_exchange_profile
from btcts.processing.l3_market_semantics.orderbook import resolve_orderbook_semantic_policy
from btcts.replay.replay_pipeline import ReplayPipeline


def main() -> int:
    profile = create_exchange_profile("bitflyer")

    baseline = profile.orderbook_semantic_policy()
    assert baseline["wall_near_rank_threshold"] == 5
    assert baseline["wall_ratio_threshold"] == 0.30
    assert baseline["pressure_threshold"] == 0.20

    merged = resolve_orderbook_semantic_policy(
        baseline_policy=baseline,
        override_policy={
            "wall_near_rank_threshold": 8,
            "wall_ratio_threshold": 0.32,
        },
    )
    assert merged["wall_near_rank_threshold"] == 8
    assert merged["wall_ratio_threshold"] == 0.32
    assert merged["pressure_threshold"] == 0.20
    assert merged["pull_threshold"] == 0.20

    pipeline_from_profile = ReplayPipeline(
        exchange_profile=profile,
    )
    assert pipeline_from_profile.semantic_policy["wall_near_rank_threshold"] == 5
    assert pipeline_from_profile.semantic_policy["wall_ratio_threshold"] == 0.30
    assert pipeline_from_profile.semantic_policy["pressure_threshold"] == 0.20

    pipeline_with_override = ReplayPipeline(
        exchange_profile=profile,
        semantic_policy={
            "wall_near_rank_threshold": 8,
            "wall_ratio_threshold": 0.32,
        },
    )
    assert pipeline_with_override.semantic_policy["wall_near_rank_threshold"] == 8
    assert pipeline_with_override.semantic_policy["wall_ratio_threshold"] == 0.32
    assert pipeline_with_override.semantic_policy["pressure_threshold"] == 0.20
    assert pipeline_with_override.semantic_policy["pull_threshold"] == 0.20

    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())