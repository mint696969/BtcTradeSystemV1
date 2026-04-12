# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_health_chart_panels_semantic_observer_caption.py
# desc: Verify health semantic observer caption stays contract-aware and additive.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.apps.operator_ui.components.health_chart_panels import (  # noqa: E402
    build_semantic_contract_observer_caption,
)


def main() -> int:
    caption = build_semantic_contract_observer_caption(
        layer3_semantic_usage_summary={
            "source_kind": "market_state_semantic_usage_summary",
            "contract_source": "l3_event_usage_policy",
            "meaning_version": "l3_event_usage_policy.v1alpha1",
            "observer_status": "healthy",
            "mapped_event_count": 1,
            "unknown_event_count": 1,
            "event_family_distribution": {
                "support_resistance": 1,
                "unknown": 1,
            },
            "trust_bucket_distribution": {
                "degraded": 1,
                "trusted": 1,
            },
            "interpretation_bucket_distribution": {
                "allow_structural_use": 1,
                "observe_only": 1,
            },
            "consumer_distribution": {
                "ai": 2,
                "alert": 2,
                "execution": 1,
                "strategy": 1,
                "ui": 2,
            },
        },
        layer3_semantic_usage_rows=[
            {"event_family": "wall", "usage_grade": "strong"},
            {"event_family": "pressure", "usage_grade": "watch_weak"},
        ],
        layer3_orderbook_runtime_summary={
            "active_event_contracts": [
                {
                    "event_name": "near_wall_continued",
                    "event_family": "wall",
                    "meaning_version": "l3_event_usage_policy.v1alpha1",
                    "trust_bucket": "trusted",
                    "interpretation_bucket": "allow_structural_use",
                    "consumer_allowed": [
                        "ui",
                        "alert",
                        "ai",
                        "strategy",
                        "execution",
                    ],
                },
                {
                    "event_name": "support_candidate",
                    "event_family": "support_resistance",
                    "meaning_version": "l3_event_usage_policy.v1alpha1",
                    "trust_bucket": "degraded",
                    "interpretation_bucket": "observe_only",
                    "consumer_allowed": ["ui", "alert", "ai"],
                },
            ]
        },
    )

    assert "semantic_observer=healthy" in caption
    assert "summary_source=market_state_semantic_usage_summary" in caption
    assert "summary_contract=l3_event_usage_policy" in caption
    assert "summary_version=l3_event_usage_policy.v1alpha1" in caption
    assert "family_rows=2" in caption
    assert "active_events=2" in caption
    assert "mapped_events=1" in caption
    assert "family_dist=support_resistance:1,unknown:1" in caption
    assert "active_versions=l3_event_usage_policy.v1alpha1" in caption
    assert "trust_dist=degraded:1,trusted:1" in caption
    assert "interpretation_dist=allow_structural_use:1,observe_only:1" in caption
    assert "consumers=ai:2,alert:2,execution:1,strategy:1,ui:2" in caption
    assert "unknown_events=1" in caption

    summary_first = build_semantic_contract_observer_caption(
        layer3_semantic_usage_summary={
            "source_kind": "market_state_semantic_usage_summary",
            "contract_source": "l3_event_usage_policy",
            "meaning_version": "l3_event_usage_policy.v1alpha1",
            "observer_status": "healthy",
            "active_event_count": 2,
            "mapped_event_count": 1,
            "unknown_event_count": 1,
            "event_family_distribution": {
                "support_resistance": 1,
                "unknown": 1,
            },
            "trust_bucket_distribution": {
                "degraded": 1,
                "trusted": 1,
            },
            "interpretation_bucket_distribution": {
                "observe_only": 2,
            },
            "consumer_distribution": {
                "ai": 2,
                "alert": 2,
                "ui": 2,
            },
        },
        layer3_semantic_usage_rows=[
            {"event_family": "wall", "usage_grade": "strong"},
        ],
        layer3_orderbook_runtime_summary={
            "active_event_contracts": [
                {
                    "event_name": "near_wall_continued",
                    "event_family": "wall",
                    "meaning_version": "l3_event_usage_policy.v1alpha1",
                    "trust_bucket": "trusted",
                    "interpretation_bucket": "allow_structural_use",
                    "consumer_allowed": [
                        "ui",
                        "alert",
                        "ai",
                        "strategy",
                        "execution",
                    ],
                },
                {
                    "event_name": "support_candidate",
                    "event_family": "support_resistance",
                    "meaning_version": "l3_event_usage_policy.v1alpha1",
                    "trust_bucket": "degraded",
                    "interpretation_bucket": "observe_only",
                    "consumer_allowed": ["ui", "alert", "ai"],
                },
            ]
        },
    )

    assert "active_events=2" in summary_first
    assert "mapped_events=1" in summary_first
    assert "family_dist=support_resistance:1,unknown:1" in summary_first
    assert "trust_dist=degraded:1,trusted:1" in summary_first
    assert "interpretation_dist=observe_only:2" in summary_first
    assert "consumers=ai:2,alert:2,ui:2" in summary_first

    empty = build_semantic_contract_observer_caption(
        layer3_semantic_usage_summary={},
        layer3_semantic_usage_rows=[],
        layer3_orderbook_runtime_summary={},
    )
    assert "semantic_observer=unknown" in empty
    assert "summary_contract=unknown" in empty
    assert "summary_version=unknown" in empty
    assert "family_rows=0" in empty
    assert "active_events=0" in empty
    assert "mapped_events=0" in empty
    assert "family_dist=none" in empty
    assert "active_versions=none" in empty
    assert "trust_dist=none" in empty
    assert "interpretation_dist=none" in empty
    assert "consumers=none" in empty
    assert "unknown_events=0" in empty

    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())