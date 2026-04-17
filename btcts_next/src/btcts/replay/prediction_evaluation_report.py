# path: ./btcts_next/src/btcts/replay/prediction_evaluation_report.py
# desc: Build compact prediction evaluation reports from replay-side evaluation entries.

from __future__ import annotations

from typing import Any


def _safe_str(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _safe_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except Exception:
        return None


def _bump(counter: dict[str, int], key: str | None) -> None:
    normalized = _safe_str(key) or "unknown"
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

    confidence_gap_values: list[float] = []
    caution_gap_values: list[float] = []

    high_priority_count = 0
    matched_count = 0
    partial_count = 0
    missed_count = 0

    for entry in entries:
        if not isinstance(entry, dict):
            continue

        regime_alignment = _safe_str(entry.get("regime_alignment"))
        replay_priority = _safe_str(entry.get("replay_priority"))
        confidence_gap_signal = _safe_str(entry.get("confidence_gap_signal"))
        confidence_bias_hint = _safe_str(entry.get("confidence_bias_hint"))
        caution_bias_hint = _safe_str(entry.get("caution_bias_hint"))

        _bump(regime_alignment_counts, regime_alignment)
        _bump(replay_priority_counts, replay_priority)
        _bump(confidence_gap_signal_counts, confidence_gap_signal)
        _bump(confidence_bias_hint_counts, confidence_bias_hint)
        _bump(caution_bias_hint_counts, caution_bias_hint)

        if regime_alignment == "matched":
            matched_count += 1
        elif regime_alignment == "partial":
            partial_count += 1
        elif regime_alignment == "missed":
            missed_count += 1

        if replay_priority == "high":
            high_priority_count += 1

        confidence_gap = _safe_float(entry.get("confidence_gap"))
        if confidence_gap is not None:
            confidence_gap_values.append(confidence_gap)

        caution_gap = _safe_float(entry.get("caution_gap"))
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
    }