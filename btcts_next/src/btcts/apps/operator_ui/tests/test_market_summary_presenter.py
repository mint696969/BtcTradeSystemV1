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
    assert "source=market_state_preferred" in caption
    assert "notable=trusted_source" in caption
    assert "alerts=none" in caption

    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())