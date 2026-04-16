# path: ./btcts_next/src/btcts/apps/operator_ui/components/prediction_summary_presenter.py
# desc: Shared presenter helpers for PredictionSummary widget model captions and snapshot lines.

from __future__ import annotations


def prediction_snapshot_lines(prediction_widget) -> list[str]:
    if not prediction_widget:
        return []

    lines: list[str] = [
        f"bias={prediction_widget.short_horizon_bias_key}",
        f"continuation={prediction_widget.continuation_likelihood_key}",
        f"mean_reversion={prediction_widget.mean_reversion_likelihood_key}",
        f"regime_risk={prediction_widget.regime_transition_risk_key}",
        f"liquidity_risk={prediction_widget.liquidity_deterioration_risk_key}",
        f"execution_hint={prediction_widget.execution_feasibility_hint_key}",
        f"caution={prediction_widget.caution_level_key}",
        f"confidence={prediction_widget.confidence:.2f}",
    ]
    if prediction_widget.health_caution_used_key == "true":
        lines.append("health_caution=on")
    return lines