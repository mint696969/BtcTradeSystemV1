# path: ./btcts_next/src/btcts/apps/operator_ui/components/ai_operator_display_payloads.py
# desc: AI Operator の補助表示 payload（watch caption / summary caption / prediction lines）を組み立てる境界。

from __future__ import annotations

from btcts.apps.operator_ui.components.ai_operator_tactic_context import (
    build_operator_tactic_context,
)
from btcts.apps.operator_ui.components.ai_operator_tactic_presenter import (
    build_tactic_stance_lines,
    build_tactic_stance_note,
)
from btcts.apps.operator_ui.components.market_summary_presenter import (
    summary_widget_caption,
)
from btcts.apps.operator_ui.components.prediction_summary_presenter import (
    prediction_snapshot_lines,
)


def _build_prediction_explanation_note(prediction_lines: list[str]) -> str:
    if not prediction_lines:
        return ""

    selected: dict[str, str] = {}
    for line in prediction_lines:
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = str(key).strip()
        value = str(value).strip()
        if not key or not value:
            continue
        if key in {
            "scenario_switch_hint",
            "trace_summary",
            "trace_focus",
            "invalidation_state",
            "hypothesis_health",
            "caution",
            "confidence",
        }:
            selected[key] = value

    ordered_keys = (
        "scenario_switch_hint",
        "invalidation_state",
        "hypothesis_health",
        "trace_summary",
        "trace_focus",
        "caution",
        "confidence",
    )
    focus_lines = [
        f"{key}={selected[key]}"
        for key in ordered_keys
        if key in selected
    ]
    if not focus_lines:
        return ""

    return "prediction_context: " + " | ".join(focus_lines)


def _build_watch_explanation_note(watch_note_caption: str | None) -> str:
    text = str(watch_note_caption or "").strip()
    if not text:
        return ""

    return f"watch_context: caption={text}"


def _build_summary_explanation_note(summary_caption: str | None) -> str:
    text = str(summary_caption or "").strip()
    if not text:
        return ""

    return f"summary_context: caption={text}"


def _build_operator_explanation_note(
    *,
    watch_note_caption: str | None,
    summary_caption: str | None,
    prediction_explanation_note: str,
    tactic_explanation_note: str,
) -> str:
    parts: list[str] = []

    watch_explanation_note = _build_watch_explanation_note(watch_note_caption)
    if watch_explanation_note:
        parts.append(watch_explanation_note)

    summary_explanation_note = _build_summary_explanation_note(summary_caption)
    if summary_explanation_note:
        parts.append(summary_explanation_note)

    if prediction_explanation_note:
        parts.append(prediction_explanation_note)

    if tactic_explanation_note:
        parts.append(tactic_explanation_note)

    return "\n".join(parts)


def build_operator_display_payloads(
    *,
    summary_widget,
    prediction_widget,
    watch_note: dict | None,
    is_live_market: bool,
    tactic_context: dict | None = None,
) -> dict:
    watch_note_caption = None
    if watch_note and not is_live_market:
        watch_note_caption = (
            f"watch ts={watch_note.get('ts')} / "
            f"regime={watch_note.get('regime')} / "
            f"action={watch_note.get('action')} / "
            f"risk={watch_note.get('risk')}"
        )

    summary_caption = None
    if summary_widget:
        summary_caption = summary_widget_caption(summary_widget)

    prediction_lines = prediction_snapshot_lines(prediction_widget)
    prediction_explanation_note = _build_prediction_explanation_note(
        prediction_lines
    )
    normalized_tactic_context = build_operator_tactic_context(tactic_context)
    tactic_summary_lines = build_tactic_stance_lines(normalized_tactic_context)
    tactic_explanation_note = build_tactic_stance_note(normalized_tactic_context)
    operator_explanation_note = _build_operator_explanation_note(
        watch_note_caption=watch_note_caption,
        summary_caption=summary_caption,
        prediction_explanation_note=prediction_explanation_note,
        tactic_explanation_note=tactic_explanation_note,
    )

    return {
        "watch_note_caption": watch_note_caption,
        "summary_caption": summary_caption,
        "prediction_lines": prediction_lines,
        "prediction_explanation_note": prediction_explanation_note,
        "tactic_context": normalized_tactic_context,
        "tactic_summary_lines": tactic_summary_lines,
        "tactic_explanation_note": tactic_explanation_note,
        "operator_explanation_note": operator_explanation_note,
    }