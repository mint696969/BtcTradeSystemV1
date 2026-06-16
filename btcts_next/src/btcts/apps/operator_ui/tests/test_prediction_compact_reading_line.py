# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_prediction_compact_reading_line.py
# desc: Verify prediction presenter exposes a compact reading line for WarRoom / strategy-state use.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.apps.operator_ui.components.prediction_summary_presenter import (  # noqa: E402
    prediction_compact_reading_line,
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
        continuation_likelihood_key="medium",
        mean_reversion_likelihood_key="medium",
        regime_transition_risk_key="low",
        liquidity_deterioration_risk_key="low",
        execution_feasibility_hint_key="favorable",
        confidence=0.68,
        market_uid="bitflyer.spot.BTC_JPY",
        event_ts="2026-04-15T12:00:00Z",
        source_kind="market_summary_anchor",
        health_caution_used_key="false",
        notable_tags=["fresh_source"],
        alert_tags=[],
        current_regime_state_key="continuation",
        current_hypothesis_health_key="healthy",
        invalidation_state_key="stable",
        scenario_switch_hint_key="watch_reversal_path",
        trace_regime_decision_key="continuation_bias",
        trace_switch_reason_key="none",
        trace_summary_key="transition_sign:weakening_continuation / watch_reversal_path",
        trace_focus_summary_key="reversal_watch",
    )

    line = prediction_compact_reading_line(widget)
    assert line == (
        "prediction_reading=bullish / "
        "caution=medium / "
        "switch=watch_reversal_path / "
        "trace=transition_sign:weakening_continuation / watch_reversal_path"
    )

    assert prediction_compact_reading_line(None) == "prediction_reading unavailable"

    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())