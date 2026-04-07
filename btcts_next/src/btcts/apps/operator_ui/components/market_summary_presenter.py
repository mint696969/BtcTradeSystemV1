# path: ./btcts_next/src/btcts/apps/operator_ui/components/market_summary_presenter.py
# desc: Shared presenter helpers for MarketSummary widget model captions.

from __future__ import annotations


def summary_widget_caption(summary_widget) -> str:
    notable_text = "-" if not summary_widget.notable_tags else ",".join(summary_widget.notable_tags)
    alert_text = "-" if not summary_widget.alert_tags else ",".join(summary_widget.alert_tags)

    return (
        "summary_widget "
        f"freshness={summary_widget.freshness_key} / "
        f"trust={summary_widget.trust_key or '-'} / "
        f"continuity={summary_widget.continuity_key or '-'} / "
        f"interpretation={summary_widget.interpretation_key or '-'} / "
        f"source={summary_widget.source_kind} / "
        f"notable={notable_text} / "
        f"alerts={alert_text}"
    )