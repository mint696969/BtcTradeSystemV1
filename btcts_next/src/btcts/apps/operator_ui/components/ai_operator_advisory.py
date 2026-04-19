# path: ./btcts_next/src/btcts/apps/operator_ui/components/ai_operator_advisory.py
# desc: AI Operator の advisory answer 読み出しを分離した support boundary。

from __future__ import annotations

from btcts.apps.operator_ui.ai_runtime import generate_answer


def _build_advisory_note(note: str) -> str:
    text = str(note or "").strip()
    if not text:
        return ""

    return (
        "Use the following explanation context when generating the advisory answer.\n"
        "Treat it as supporting context, not as a final decision contract.\n"
        f"{text}"
    )


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
) -> dict:
    advisory_note = _build_advisory_note(note)

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