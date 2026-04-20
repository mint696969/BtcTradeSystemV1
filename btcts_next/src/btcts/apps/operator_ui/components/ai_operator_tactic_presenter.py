# path: ./btcts_next/src/btcts/apps/operator_ui/components/ai_operator_tactic_presenter.py
# desc: Thin presentation helper for operator-side tactic stance wording.

from __future__ import annotations

from btcts.apps.operator_ui.ui_text import get_text


def tactic_stance_section_title(lang: str) -> str:
    return get_text(lang, "ai_operator_tactic_stance_title")


def tactic_stance_support_caption(lang: str) -> str:
    return get_text(lang, "ai_operator_tactic_stance_support")


def advisory_support_caption(lang: str) -> str:
    return get_text(lang, "ai_operator_advisory_support")


def prediction_snapshot_section_title(lang: str) -> str:
    return get_text(lang, "ai_operator_prediction_snapshot_title")


def _bool_token(value: bool) -> str:
    return "true" if value else "false"


def build_tactic_stance_lines(tactic_context: dict | None) -> tuple[str, ...]:
    if not tactic_context:
        return ()

    lines: list[str] = [
        f"operating_stance={tactic_context['primary_tactic_key']}",
        f"scenario_regime={tactic_context['scenario_regime']}",
        f"proposal_state={tactic_context['proposal_state']}",
        f"profile_kind={tactic_context['profile_kind']}",
        f"review_needed={_bool_token(bool(tactic_context['review_needed']))}",
        f"rollback_ready={_bool_token(bool(tactic_context['rollback_ready']))}",
    ]

    selection_bias_tags = tactic_context.get("selection_bias_tags") or ()
    if selection_bias_tags:
        lines.append(
            "selection_bias_tags=" + ",".join(str(item) for item in selection_bias_tags)
        )

    return tuple(lines)


_LABEL_KEYS = {
    "operating_stance": "tactic_stance_label_operating_stance",
    "scenario_regime": "tactic_stance_label_scenario_regime",
    "proposal_state": "tactic_stance_label_proposal_state",
    "profile_kind": "tactic_stance_label_profile_kind",
    "review_needed": "tactic_stance_label_review_needed",
    "rollback_ready": "tactic_stance_label_rollback_ready",
    "selection_bias_tags": "tactic_stance_label_selection_bias_tags",
}


def _display_value(lang: str, key: str, value: str) -> str:
    normalized = str(value).strip()
    lowered = normalized.lower()

    if key in {"review_needed", "rollback_ready"}:
        if lowered == "true":
            return get_text(lang, "tactic_stance_value_true")
        if lowered == "false":
            return get_text(lang, "tactic_stance_value_false")

    return normalized


def build_tactic_stance_display_lines(
    summary_lines: tuple[str, ...],
    lang: str,
) -> tuple[str, ...]:
    out: list[str] = []

    for line in summary_lines or ():
        text = str(line).strip()
        if "=" not in text:
            continue

        key, value = text.split("=", 1)
        key = str(key).strip()
        value = str(value).strip()
        label_key = _LABEL_KEYS.get(key)

        if label_key is None or not value:
            continue

        out.append(
            f"{get_text(lang, label_key)}: "
            f"{_display_value(lang, key, value)}"
        )

    return tuple(out)


def build_tactic_stance_note(tactic_context: dict | None) -> str:
    lines = build_tactic_stance_lines(tactic_context)
    if not lines:
        return ""
    return "tactic_stance_context: " + " | ".join(lines)