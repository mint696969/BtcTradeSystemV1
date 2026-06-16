# path: ./btcts_next/src/btcts/apps/operator_ui/components/prediction_summary_presenter.py
# desc: Shared presenter helpers for PredictionSummary widget model captions and snapshot lines.

from __future__ import annotations


def prediction_compact_reading_line(prediction_widget) -> str:
    if not prediction_widget:
        return "prediction_reading unavailable"

    bias = str(getattr(prediction_widget, "short_horizon_bias_key", None) or "unknown")
    caution = str(getattr(prediction_widget, "caution_level_key", None) or "unknown")
    switch_hint = str(
        getattr(prediction_widget, "scenario_switch_hint_key", None) or "unknown"
    )
    trace_summary = str(
        getattr(prediction_widget, "trace_summary_key", None) or "unknown"
    )

    return (
        f"prediction_reading={bias} / "
        f"caution={caution} / "
        f"switch={switch_hint} / "
        f"trace={trace_summary}"
    )


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

    if prediction_widget.current_regime_state_key != "unknown":
        lines.append(f"scenario_regime={prediction_widget.current_regime_state_key}")
    if prediction_widget.current_hypothesis_health_key != "unknown":
        lines.append(
            f"hypothesis_health={prediction_widget.current_hypothesis_health_key}"
        )
    if prediction_widget.invalidation_state_key != "unknown":
        lines.append(
            f"invalidation_state={prediction_widget.invalidation_state_key}"
        )
    if prediction_widget.scenario_switch_hint_key != "unknown":
        lines.append(
            f"scenario_switch_hint={prediction_widget.scenario_switch_hint_key}"
        )

    if prediction_widget.trace_regime_decision_key != "unknown":
        lines.append(
            f"trace_regime_decision={prediction_widget.trace_regime_decision_key}"
        )
    if prediction_widget.trace_switch_reason_key != "unknown":
        lines.append(
            f"trace_switch_reason={prediction_widget.trace_switch_reason_key}"
        )
    if prediction_widget.trace_summary_key != "unknown":
        lines.append(
            f"trace_summary={prediction_widget.trace_summary_key}"
        )
    if prediction_widget.trace_focus_summary_key != "none":
        lines.append(
            f"trace_focus={prediction_widget.trace_focus_summary_key}"
        )

    return lines