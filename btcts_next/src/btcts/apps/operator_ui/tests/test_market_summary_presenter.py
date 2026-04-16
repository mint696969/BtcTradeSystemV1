# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_market_summary_presenter.py
# desc: Verify shared MarketSummary widget presenter caption remains stable.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.apps.operator_ui.components.market_summary_presenter import summary_widget_caption
from btcts.processing.l4_consumer_models.operator_ui import MarketSummaryWidgetModel


def main() -> int:
    widget = MarketSummaryWidgetModel(
        widget_kind="market_summary",
        freshness_key="LIVE",
        trust_key="trusted",
        continuity_key="continuous",
        interpretation_key="allow_structural_use",
        semantic_wiring_key="wired",
        semantic_observer_status_key="healthy",
        semantic_observer_present_key="true",
        semantic_usage_summary_present_key="true",
        semantic_contract_rows_present_key="true",
        semantic_summary_source_key="market_state_semantic_usage_summary",
        semantic_contract_source_key="l3_event_usage_policy",
        semantic_meaning_version_key="l3_event_usage_policy.v1alpha1",
        orderbook_wiring_key="partial",
        orderbook_contract_status_source_key="orderbook_summary_inference",
        semantic_rows_count=2,
        semantic_total_rows=2,
        semantic_active_event_count=1,
        semantic_mapped_event_count=1,
        semantic_unknown_event_count=0,
        semantic_event_family_distribution={"wall": 2},
        semantic_trust_bucket_distribution={"trusted": 2},
        semantic_interpretation_bucket_distribution={"observe_only": 2},
        semantic_consumer_distribution={"health": 2},
        summary_slots_count=1,
        orderbook_summary_slots_present=["near_wall"],
        orderbook_near_wall_present_key="true",
        orderbook_support_present_key="false",
        orderbook_resistance_present_key="false",
        active_event_count=1,
        orderbook_active_event_names=["near_wall_continued"],
        persistence_present_key="false",
        persistence_observable_key="true",
        headline_key="normal",
        notable_tags=["trusted_source"],
        alert_tags=["none"],
        age_sec=1.2,
        event_ts="2026-03-16T13:00:00Z",
        source_kind="market_state_preferred",
        source_series_id="bf-sess-1:series:100",
    )

    caption = summary_widget_caption(widget)
    assert "freshness=LIVE" in caption
    assert "trust=trusted" in caption
    assert "continuity=continuous" in caption
    assert "interpretation=allow_structural_use" in caption
    assert "semantic_wiring=wired" in caption
    assert "observer_status=healthy" in caption
    assert "observer_present=true" in caption
    assert "usage_summary_present=true" in caption
    assert "contract_rows_present=true" in caption
    assert "semantic_source=market_state_semantic_usage_summary" in caption
    assert "semantic_contract=l3_event_usage_policy" in caption
    assert "semantic_version=l3_event_usage_policy.v1alpha1" in caption
    assert "orderbook_wiring=partial" in caption
    assert "orderbook_source=orderbook_summary_inference" in caption
    assert "semantic_rows=2" in caption
    assert "semantic_total_rows=2" in caption
    assert "semantic_active_events=1" in caption
    assert "mapped_events=1" in caption
    assert "unknown_events=0" in caption
    assert "family_dist=wall:2" in caption
    assert "trust_dist=trusted:2" in caption
    assert "interpretation_dist=observe_only:2" in caption
    assert "consumer_dist=health:2" in caption
    assert "summary_slots=1" in caption
    assert "slots_present=near_wall" in caption
    assert "near_wall_present=true" in caption
    assert "support_present=false" in caption
    assert "resistance_present=false" in caption
    assert "active_events=1" in caption
    assert "active_event_names=near_wall_continued" in caption
    assert "persistence_present=false" in caption
    assert "persistence_observable=true" in caption
    assert "source=market_state_preferred" in caption
    assert "series=bf-sess-1:series:100" in caption
    assert "age=1.2s" in caption
    assert "event_ts=2026-03-16T13:00:00Z" in caption
    assert "notable=trusted_source" in caption
    assert "alerts=none" in caption

    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())