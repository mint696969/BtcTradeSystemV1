# path: ./btcts_next/src/btcts/apps/operator_ui/components/ai_operator_advisory.py
# desc: AI Operator の advisory answer 読み出しを分離した support boundary。

from __future__ import annotations

from btcts.apps.operator_ui.ai_runtime import generate_answer
from btcts.apps.operator_ui.components.ai_operator_tactic_presenter import (
    build_tactic_advisory_interpretation_lines_from_summary,
    select_primary_tactic_advisory_interpretation_line,
)


def _build_advisory_note(
    note: str,
    *,
    tactic_summary_lines: tuple[str, ...] = (),
    tactic_interpretation_lines: tuple[str, ...] = (),
    primary_tactic_interpretation_line: str = "",
    tactic_primary_summary_line: str = "",
) -> str:
    text = str(note or "").strip()
    normalized_tactic_lines = tuple(
        str(line).strip()
        for line in (tactic_summary_lines or ())
        if str(line).strip()
    )

    parts: list[str] = [
        "Use the following explanation context when generating the advisory answer.",
        "Treat it as supporting context, not as a final decision contract.",
        "Treat any tactic stance context as an operating stance proposal, not as an execution instruction.",
    ]

    normalized_tactic_interpretation_lines = tuple(
        str(line).strip()
        for line in (tactic_interpretation_lines or ())
        if str(line).strip()
    )
    if not normalized_tactic_interpretation_lines and normalized_tactic_lines:
        normalized_tactic_interpretation_lines = (
            build_tactic_advisory_interpretation_lines_from_summary(
                normalized_tactic_lines
            )
        )

    primary_tactic_interpretation = str(
        primary_tactic_interpretation_line or ""
    ).strip()
    if not primary_tactic_interpretation:
        primary_tactic_interpretation = (
            select_primary_tactic_advisory_interpretation_line(
                normalized_tactic_interpretation_lines
            )
        )

    normalized_tactic_primary_summary_line = str(
        tactic_primary_summary_line or ""
    ).strip()

    if normalized_tactic_lines:
        parts.append("Use the following tactic stance summary lines as ordered supporting context.")
        parts.append(
            "tactic_stance_summary_lines: " + " | ".join(normalized_tactic_lines)
        )

    if normalized_tactic_primary_summary_line:
        parts.append(
            "primary_tactic_stance_summary: "
            + normalized_tactic_primary_summary_line
        )

    if normalized_tactic_interpretation_lines:
        parts.append(
            "Treat the following tactic stance interpretation as review guidance, not as a final decision."
        )

        if primary_tactic_interpretation:
            parts.append(
                "primary_tactic_stance_interpretation: "
                + primary_tactic_interpretation
            )

        parts.append(
            "tactic_stance_interpretation: "
            + " | ".join(normalized_tactic_interpretation_lines)
        )

    if text:
        parts.append(text)

    if len(parts) == 3:
        return ""

    return "\n".join(parts)


def read_operator_advisory_answer(
    *,
    lang: str,
    ai_mode: str,
    operator_prompt: str,
    intent: str,
    style: str,
    state: dict,
    memory: list[dict],
    note: str = "",
    tactic_summary_lines: tuple[str, ...] = (),
    tactic_interpretation_lines: tuple[str, ...] = (),
    primary_tactic_interpretation_line: str = "",
    tactic_primary_summary_line: str = "",
) -> dict:
    advisory_note = _build_advisory_note(
        note,
        tactic_summary_lines=tactic_summary_lines,
        tactic_interpretation_lines=tactic_interpretation_lines,
        primary_tactic_interpretation_line=primary_tactic_interpretation_line,
        tactic_primary_summary_line=tactic_primary_summary_line,
    )

    answer, runtime_source = generate_answer(
        mode=ai_mode,
        lang=lang,
        prompt=operator_prompt,
        state=state,
        note=advisory_note,
        memory=memory,
        intent=intent,
        style=style,
    )

    return {
        "answer": answer,
        "runtime_source": runtime_source,
        "advisory_note_used": advisory_note,
    }