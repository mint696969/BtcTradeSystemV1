# path: ./btcts_next/src/btcts/apps/operator_ui/components/review_hint_presenter.py
# desc: Shared read-only presenter helpers for Position/Execution review hint display context.

from __future__ import annotations

from typing import Any


def _summary(context: dict[str, Any] | None, key: str) -> dict[str, Any]:
    if not context:
        return {}
    value = context.get(key)
    return dict(value) if isinstance(value, dict) else {}


def _text(value: Any, fallback: str = "unknown") -> str:
    text = str(value or "").strip()
    return text if text else fallback


def _bool_token(value: Any) -> str:
    return "true" if bool(value) else "false"


def review_hint_compact_reading_line(context: dict[str, Any] | None) -> str:
    if not context or not bool(context.get("available")):
        return "review_hint_reading unavailable"

    position = _summary(context, "position_summary")
    execution = _summary(context, "execution_summary")

    position_hint = _text(position.get("latest_management_hint"), "position_unknown")
    execution_hint = _text(execution.get("latest_timing_hint"), "execution_unknown")
    position_count = int(position.get("snapshot_count") or 0)
    execution_count = int(execution.get("snapshot_count") or 0)

    return (
        "review_hint_reading="
        f"position:{position_hint}({position_count}) / "
        f"execution:{execution_hint}({execution_count}) / review_only"
    )


def review_hint_snapshot_lines(context: dict[str, Any] | None) -> tuple[str, ...]:
    if not context or not bool(context.get("available")):
        return ()

    position = _summary(context, "position_summary")
    execution = _summary(context, "execution_summary")
    lines: list[str] = [
        "context_type=" + _text(
            context.get("context_type"),
            "prediction_review_hint_summary_context",
        ),
        "source_kind=" + _text(context.get("source_kind"), "replay_report"),
        "available=" + _bool_token(context.get("available")),
        "read_only_contract=" + _bool_token(context.get("read_only_contract")),
        "not_runtime_wiring=" + _bool_token(context.get("not_runtime_wiring")),
        "not_ui_rendering=" + _bool_token(context.get("not_ui_rendering")),
    ]

    if position:
        lines.extend(
            [
                "position_snapshot_count=" + _text(position.get("snapshot_count"), "0"),
                "position_prediction_type=" + _text(position.get("latest_prediction_type")),
                "position_source_kind=" + _text(position.get("latest_source_kind")),
                "position_management_hint=" + _text(position.get("latest_management_hint")),
                "position_exposure_risk_hint=" + _text(position.get("latest_exposure_risk_hint")),
                "position_read_only_contract=" + _bool_token(position.get("latest_read_only_contract")),
                "position_not_runtime_wiring=" + _bool_token(position.get("latest_not_runtime_wiring")),
                "position_not_ui_wiring=" + _bool_token(position.get("latest_not_ui_wiring")),
            ]
        )

    if execution:
        lines.extend(
            [
                "execution_snapshot_count=" + _text(execution.get("snapshot_count"), "0"),
                "execution_prediction_type=" + _text(execution.get("latest_prediction_type")),
                "execution_source_kind=" + _text(execution.get("latest_source_kind")),
                "execution_timing_hint=" + _text(execution.get("latest_timing_hint")),
                "execution_urgency_hint=" + _text(execution.get("latest_urgency_hint")),
                "execution_feasibility_hint=" + _text(execution.get("latest_feasibility_hint")),
                "execution_side_effect_free=" + _bool_token(execution.get("latest_execution_side_effect_free")),
                "execution_broker_link_free=" + _bool_token(execution.get("latest_broker_link_free")),
                "execution_account_side_effect_free=" + _bool_token(execution.get("latest_account_side_effect_free")),
                "execution_read_only_contract=" + _bool_token(execution.get("latest_read_only_contract")),
                "execution_not_runtime_wiring=" + _bool_token(execution.get("latest_not_runtime_wiring")),
                "execution_not_ui_wiring=" + _bool_token(execution.get("latest_not_ui_wiring")),
            ]
        )

    return tuple(lines)


def review_hint_display_sections(context: dict[str, Any] | None) -> dict[str, Any]:
    return {
        "section_type": "prediction_review_hint_display_context",
        "compact_line": review_hint_compact_reading_line(context),
        "snapshot_lines": review_hint_snapshot_lines(context),
        "read_only_contract": True,
        "not_runtime_wiring": True,
        "not_ui_rendering": True,
        "widget_reusable": True,
    }
