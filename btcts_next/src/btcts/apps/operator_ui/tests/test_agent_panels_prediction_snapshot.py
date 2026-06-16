# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_agent_panels_prediction_snapshot.py
# desc: Verify agent_panels can reuse shared prediction snapshot helper safely.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.apps.operator_ui.components.prediction_summary_presenter import (  # noqa: E402
    prediction_snapshot_lines,
)
from btcts.processing.l4_consumer_models.operator_ui import (  # noqa: E402
    PredictionSummaryWidgetModel,
)


def main() -> int:
    widget = PredictionSummaryWidgetModel(
        widget_kind="shared_prediction_summary",
        freshness_key="LIVE",
        horizon_key="short",
        caution_level_key="medium",
        short_horizon_bias_key="bullish",
        continuation_likelihood_key="high",
        mean_reversion_likelihood_key="low",
        regime_transition_risk_key="medium",
        liquidity_deterioration_risk_key="low",
        execution_feasibility_hint_key="caution",
        confidence=0.61,
        market_uid="bitflyer.spot.BTC_JPY",
        event_ts="2026-04-15T12:00:00Z",
        source_kind="market_summary_anchor",
        health_caution_used_key="true",
        notable_tags=["fresh_source"],
        alert_tags=["semantic_review"],
    )

    lines = prediction_snapshot_lines(widget)
    assert "bias=bullish" in lines
    assert "continuation=high" in lines
    assert "mean_reversion=low" in lines
    assert "regime_risk=medium" in lines
    assert "liquidity_risk=low" in lines
    assert "execution_hint=caution" in lines
    assert "caution=medium" in lines
    assert "confidence=0.61" in lines
    assert "health_caution=on" in lines

    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())