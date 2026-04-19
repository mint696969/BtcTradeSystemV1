# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_ai_operator_prediction_snapshot.py
# desc: Verify ai_operator_panel can reuse shared prediction snapshot helper safely.

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
        short_horizon_bias_key="bearish",
        continuation_likelihood_key="medium",
        mean_reversion_likelihood_key="low",
        regime_transition_risk_key="medium",
        liquidity_deterioration_risk_key="medium",
        execution_feasibility_hint_key="caution",
        confidence=0.58,
        market_uid="bitflyer.spot.BTC_JPY",
        event_ts="2026-04-15T12:00:00Z",
        source_kind="market_summary_anchor",
        health_caution_used_key="true",
        notable_tags=["fresh_source"],
        alert_tags=["semantic_review"],
        current_regime_state_key="reversal_watch",
        current_hypothesis_health_key="caution_increase",
        invalidation_state_key="caution_increase",
        scenario_switch_hint_key="watch_reversal_path",
        trace_regime_decision_key="transition_sign:weakening_continuation",
        trace_switch_reason_key="watch_reversal_path",
        trace_summary_key="transition_sign:weakening_continuation / watch_reversal_path",
    )

    lines = prediction_snapshot_lines(widget)
    assert "bias=bearish" in lines
    assert "continuation=medium" in lines
    assert "mean_reversion=low" in lines
    assert "regime_risk=medium" in lines
    assert "liquidity_risk=medium" in lines
    assert "execution_hint=caution" in lines
    assert "caution=medium" in lines
    assert "confidence=0.58" in lines
    assert "health_caution=on" in lines
    assert "scenario_regime=reversal_watch" in lines
    assert "hypothesis_health=caution_increase" in lines
    assert "invalidation_state=caution_increase" in lines
    assert "scenario_switch_hint=watch_reversal_path" in lines
    assert "trace_regime_decision=transition_sign:weakening_continuation" in lines
    assert "trace_switch_reason=watch_reversal_path" in lines
    assert (
        "trace_summary=transition_sign:weakening_continuation / watch_reversal_path"
        in lines
    )

    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())