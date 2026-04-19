# path: ./btcts_next/src/btcts/processing/l4_consumer_models/tests/test_prediction_summary_adapter.py
# desc: Verify prediction summary operator_ui adapter stays thin and wording-free.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.processing.l4_consumer_models.operator_ui import (
    prediction_summary_status_payload,
    prediction_summary_widget_model,
)
from btcts.processing.l4_consumer_models.shared import (
    PredictionSummary,
)


def main() -> int:
    summary = PredictionSummary(
        prediction_type="shared_prediction_summary",
        prediction_version="phase3.v1alpha1",
        source_kind="market_summary_anchor",
        market_uid="bitflyer.spot.BTC_JPY",
        event_ts="2026-04-15T12:00:00Z",
        freshness="LIVE",
        is_stale=False,
        horizon="short",
        confidence=0.75,
        caution_level="medium",
        short_horizon_bias="bullish",
        continuation_likelihood="high",
        mean_reversion_likelihood="medium",
        regime_transition_risk="low",
        liquidity_deterioration_risk="low",
        execution_feasibility_hint="caution",
        evidence={
            "notable_events": ["fresh_source"],
            "alert_candidates": ["interpretation_review_required"],
            "health_digest_present": True,
            "trace_regime_decision": "transition_sign:weakening_continuation",
            "trace_switch_reason": "watch_reversal_path",
        },
        diagnostics={
            "health_digest_present": True,
            "semantic_contract_rows_count": 2,
        },
    )

    widget = prediction_summary_widget_model(summary)
    assert widget.widget_kind == "shared_prediction_summary"
    assert widget.freshness_key == "LIVE"
    assert widget.horizon_key == "short"
    assert widget.caution_level_key == "medium"
    assert widget.short_horizon_bias_key == "bullish"
    assert widget.continuation_likelihood_key == "high"
    assert widget.mean_reversion_likelihood_key == "medium"
    assert widget.regime_transition_risk_key == "low"
    assert widget.liquidity_deterioration_risk_key == "low"
    assert widget.execution_feasibility_hint_key == "caution"
    assert widget.confidence == 0.75
    assert widget.market_uid == "bitflyer.spot.BTC_JPY"
    assert widget.event_ts == "2026-04-15T12:00:00Z"
    assert widget.source_kind == "market_summary_anchor"
    assert widget.health_caution_used_key == "true"
    assert widget.notable_tags == ["fresh_source"]
    assert widget.alert_tags == ["interpretation_review_required"]
    assert widget.trace_regime_decision_key == "transition_sign:weakening_continuation"
    assert widget.trace_switch_reason_key == "watch_reversal_path"
    assert widget.trace_summary_key == "transition_sign:weakening_continuation / watch_reversal_path"
    assert widget.trace_focus_summary_key == "none"
    
    payload = prediction_summary_status_payload(summary)
    assert payload["prediction_type"] == "shared_prediction_summary"
    assert payload["prediction_version"] == "phase3.v1alpha1"
    assert payload["source_kind"] == "market_summary_anchor"
    assert payload["market_uid"] == "bitflyer.spot.BTC_JPY"
    assert payload["freshness"] == "LIVE"
    assert payload["horizon"] == "short"
    assert payload["confidence"] == 0.75
    assert payload["caution_level"] == "medium"
    assert payload["short_horizon_bias"] == "bullish"
    assert payload["continuation_likelihood"] == "high"
    assert payload["mean_reversion_likelihood"] == "medium"
    assert payload["regime_transition_risk"] == "low"
    assert payload["liquidity_deterioration_risk"] == "low"
    assert payload["execution_feasibility_hint"] == "caution"
    assert payload["evidence"]["health_digest_present"] is True
    assert payload["diagnostics"]["health_digest_present"] is True

    empty_widget = prediction_summary_widget_model(None)
    assert empty_widget.widget_kind == "prediction_summary"
    assert empty_widget.caution_level_key == "blocked"
    assert empty_widget.health_caution_used_key == "false"

    empty_payload = prediction_summary_status_payload(None)
    assert empty_payload == {}

    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())