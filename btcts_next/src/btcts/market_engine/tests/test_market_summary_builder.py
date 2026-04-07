# path: ./btcts_next/src/btcts/market_engine/tests/test_market_summary_builder.py
# desc: Verify shared L4 market summary builder builds a reusable wording-free bundle.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[3]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.processing.l4_consumer_models.shared import (
    MarketSummaryBuildInput,
    build_market_summary,
)


def main() -> int:
    row = {
        "exchange": "bitflyer",
        "symbol_raw": "BTC_JPY",
        "market_uid": "bitflyer.spot.BTC_JPY",
        "source_series_id": "bf-sess-1:series:100",
        "collector_ts": "2026-04-06T12:00:00Z",
        "trust_state": "provisional",
        "continuity_state": "resynced",
        "interpretation_bucket": "observe_only",
        "interpretation_reason": "recent_resync",
    }
    diagnostics = {
        "source_kind": "market_state_preferred",
        "preferred_row_age_sec": 12.0,
        "preferred_row_freshness": "LIVE",
        "preferred_row_source_series_id": "bf-sess-1:series:100",
    }

    summary = build_market_summary(
        MarketSummaryBuildInput(
            market_state_row=row,
            diagnostics=diagnostics,
        )
    )

    assert summary.summary_type == "market_summary"
    assert summary.exchange == "bitflyer"
    assert summary.symbol_raw == "BTC_JPY"
    assert summary.market_uid == "bitflyer.spot.BTC_JPY"
    assert summary.source_kind == "market_state_preferred"
    assert summary.source_series_id == "bf-sess-1:series:100"
    assert summary.event_ts == "2026-04-06T12:00:00Z"
    assert summary.age_sec == 12.0
    assert summary.freshness == "LIVE"
    assert summary.is_stale is False
    assert summary.trust_state == "provisional"
    assert summary.continuity_state == "resynced"
    assert summary.interpretation_bucket == "observe_only"
    assert summary.interpretation_reason == "recent_resync"

    assert "fresh_source" in summary.notable_events
    assert "trust_degraded" in summary.notable_events
    assert "resync_recent" in summary.notable_events
    assert "review_required" in summary.notable_events

    assert "trust_not_trusted" in summary.alert_candidates
    assert "interpretation_review_required" in summary.alert_candidates

    empty = build_market_summary(MarketSummaryBuildInput())
    assert empty.source_kind == "unknown"
    assert empty.freshness == "UNKNOWN"
    assert empty.is_stale is None
    assert empty.notable_events == []
    assert empty.alert_candidates == []

    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())