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


def tactic_interpretation_support_caption(lang: str) -> str:
    return get_text(lang, "ai_operator_tactic_interpretation_support")


def build_tactic_interpretation_display_lines(
    interpretation_lines: tuple[str, ...],
    lang: str,
) -> tuple[str, ...]:
    prefix = get_text(lang, "ai_operator_tactic_interpretation_prefix")
    return tuple(
        f"{prefix}: {str(line).strip()}"
        for line in (interpretation_lines or ())
        if str(line).strip()
    )


def _bool_token(value: bool) -> str:
    return "true" if value else "false"


def build_tactic_interpretation_lines(
    tactic_context: dict | None,
) -> tuple[str, ...]:
    if not tactic_context:
        return ()

    lines: list[str] = []

    comparison_relation = str(
        tactic_context.get("comparison_relation") or ""
    ).strip()
    if comparison_relation == "candidate_vs_baseline":
        lines.append(
            "current set is being compared as a candidate relative to baseline"
        )
    elif comparison_relation == "baseline_self_reference":
        lines.append("current set is being read as baseline self-reference")
    elif comparison_relation == "profile_vs_baseline":
        lines.append("current set is being read as a profile relative to baseline")

    overlay_influence = str(
        tactic_context.get("overlay_influence") or ""
    ).strip()
    if overlay_influence == "overlay_bias":
        lines.append(
            "overlay influence is present, so the stance should be read as context-shaped"
        )

    rollback_target_ref = str(
        tactic_context.get("rollback_target_ref") or ""
    ).strip()
    if rollback_target_ref:
        lines.append(f"rollback review target is available: {rollback_target_ref}")

    if bool(tactic_context.get("adoption_ready")):
        lines.append(
            "current set is adoption-ready for review, not an automatic decision"
        )

    return tuple(lines)


def build_primary_tactic_interpretation_line(
    tactic_context: dict | None,
) -> str:
    lines = build_tactic_interpretation_lines(tactic_context)
    if not lines:
        return ""

    priority_prefixes = (
        "overlay influence is present",
        "current set is being compared",
        "rollback review target is available",
        "current set is adoption-ready",
    )
    for prefix in priority_prefixes:
        for line in lines:
            if str(line).startswith(prefix):
                return str(line)

    return str(lines[0])


def build_tactic_primary_summary_line(
    tactic_context: dict | None,
) -> str:
    if not tactic_context:
        return ""

    operating_stance = str(tactic_context.get("primary_tactic_key") or "").strip()
    if not operating_stance:
        return ""

    parts: list[str] = [operating_stance]

    comparison_relation = str(
        tactic_context.get("comparison_relation") or ""
    ).strip()
    if comparison_relation == "candidate_vs_baseline":
        parts.append("candidate_vs_baseline")
    elif comparison_relation == "baseline_self_reference":
        parts.append("baseline_self_reference")
    elif comparison_relation == "profile_vs_baseline":
        parts.append("profile_vs_baseline")

    primary_interpretation = build_primary_tactic_interpretation_line(tactic_context)
    if primary_interpretation:
        parts.append(primary_interpretation)

    parts.append("review_only")

    return " | ".join(parts)


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
        f"adoption_ready={_bool_token(bool(tactic_context['adoption_ready']))}",
        "rollback_target_available="
        + _bool_token(bool(tactic_context["rollback_target_available"])),
        f"selected_set_id={tactic_context['selected_set_id']}",
    ]

    rollback_target_ref = str(tactic_context.get("rollback_target_ref") or "").strip()
    if rollback_target_ref:
        lines.append(f"rollback_target_ref={rollback_target_ref}")

    comparison_relation = str(
        tactic_context.get("comparison_relation") or ""
    ).strip()
    if comparison_relation:
        lines.append(f"comparison_relation={comparison_relation}")

    overlay_influence = str(
        tactic_context.get("overlay_influence") or ""
    ).strip()
    if overlay_influence and overlay_influence != "none":
        lines.append(f"overlay_influence={overlay_influence}")

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
    "adoption_ready": "tactic_stance_label_adoption_ready",
    "rollback_target_available": "tactic_stance_label_rollback_target_available",
    "selected_set_id": "tactic_stance_label_selected_set_id",
    "rollback_target_ref": "tactic_stance_label_rollback_target_ref",
    "comparison_relation": "tactic_stance_label_comparison_relation",
    "overlay_influence": "tactic_stance_label_overlay_influence",
    "selection_bias_tags": "tactic_stance_label_selection_bias_tags",
}


def _display_value(lang: str, key: str, value: str) -> str:
    normalized = str(value).strip()
    lowered = normalized.lower()

    if key in {
        "review_needed",
        "rollback_ready",
        "adoption_ready",
        "rollback_target_available",
    }:
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