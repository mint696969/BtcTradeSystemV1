# path: ./btcts_next/src/btcts/replay/prediction_evaluation_report.py
# desc: Build compact prediction evaluation reports from replay-side evaluation entries.

from __future__ import annotations

from typing import Any

from btcts.processing.l4_consumer_models.shared._value_utils import (
    safe_float,
    safe_str,
)


def _bump(counter: dict[str, int], key: str | None) -> None:
    normalized = safe_str(key) or "unknown"
    counter[normalized] = counter.get(normalized, 0) + 1


def _average(values: list[float]) -> float | None:
    if not values:
        return None
    return round(sum(values) / len(values), 2)


def build_prediction_evaluation_report(name: str, entries: list[dict]) -> dict:
    regime_alignment_counts: dict[str, int] = {}
    replay_priority_counts: dict[str, int] = {}
    confidence_gap_signal_counts: dict[str, int] = {}
    confidence_bias_hint_counts: dict[str, int] = {}
    caution_bias_hint_counts: dict[str, int] = {}
    scenario_trace_regime_decision_counts: dict[str, int] = {}
    scenario_trace_switch_reason_counts: dict[str, int] = {}

    confidence_gap_values: list[float] = []
    caution_gap_values: list[float] = []

    high_priority_count = 0
    matched_count = 0
    partial_count = 0
    missed_count = 0

    for entry in entries:
        if not isinstance(entry, dict):
            continue

        regime_alignment = safe_str(entry.get("regime_alignment"))
        replay_priority = safe_str(entry.get("replay_priority"))
        confidence_gap_signal = safe_str(entry.get("confidence_gap_signal"))
        confidence_bias_hint = safe_str(entry.get("confidence_bias_hint"))
        caution_bias_hint = safe_str(entry.get("caution_bias_hint"))
        scenario_trace = entry.get("predicted_scenario_trace") or {}
        scenario_trace_regime_decision = None
        scenario_trace_switch_reason = None
        if isinstance(scenario_trace, dict):
            scenario_trace_regime_decision = safe_str(
                scenario_trace.get("regime_decision")
            )
            scenario_trace_switch_reason = safe_str(
                scenario_trace.get("switch_reason")
            )

        _bump(regime_alignment_counts, regime_alignment)
        _bump(replay_priority_counts, replay_priority)
        _bump(confidence_gap_signal_counts, confidence_gap_signal)
        _bump(confidence_bias_hint_counts, confidence_bias_hint)
        _bump(caution_bias_hint_counts, caution_bias_hint)
        _bump(
            scenario_trace_regime_decision_counts,
            scenario_trace_regime_decision,
        )
        _bump(
            scenario_trace_switch_reason_counts,
            scenario_trace_switch_reason,
        )

        if regime_alignment == "matched":
            matched_count += 1
        elif regime_alignment == "partial":
            partial_count += 1
        elif regime_alignment == "missed":
            missed_count += 1

        if replay_priority == "high":
            high_priority_count += 1

        confidence_gap = safe_float(entry.get("confidence_gap"))
        if confidence_gap is not None:
            confidence_gap_values.append(confidence_gap)

        caution_gap = safe_float(entry.get("caution_gap"))
        if caution_gap is not None:
            caution_gap_values.append(caution_gap)

    return {
        "name": name,
        "entry_type": "prediction_evaluation_report",
        "entry_version": "phase3.v1alpha1",
        "entry_count": len(entries),
        "matched_count": matched_count,
        "partial_count": partial_count,
        "missed_count": missed_count,
        "high_priority_count": high_priority_count,
        "average_confidence_gap": _average(confidence_gap_values),
        "average_caution_gap": _average(caution_gap_values),
        "regime_alignment_counts": dict(sorted(regime_alignment_counts.items())),
        "replay_priority_counts": dict(sorted(replay_priority_counts.items())),
        "confidence_gap_signal_counts": dict(
            sorted(confidence_gap_signal_counts.items())
        ),
        "confidence_bias_hint_counts": dict(
            sorted(confidence_bias_hint_counts.items())
        ),
        "caution_bias_hint_counts": dict(sorted(caution_bias_hint_counts.items())),
        "scenario_trace_regime_decision_counts": dict(
            sorted(scenario_trace_regime_decision_counts.items())
        ),
        "scenario_trace_switch_reason_counts": dict(
            sorted(scenario_trace_switch_reason_counts.items())
        ),
    }