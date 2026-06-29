# path: ./btcts_next/src/btcts/apps/operator_ui/components/autotrade_prediction_status_page_render_plan.py
# desc: Read-only render-plan packet for future AutoTrade prediction status page section. No UI framework import, page wiring, commands, writes, mode apply, ledger append, or broker behavior.

from __future__ import annotations

from typing import Any, Mapping

from btcts.apps.operator_ui.components.autotrade_prediction_status_page_display_section import (
    build_autotrade_prediction_status_page_display_section_packet,
)
from btcts.autotrade.prediction_preview_status import AutoTradePredictionPreviewStatus

AUTOTRADE_PREDICTION_STATUS_PAGE_RENDER_PLAN_CONTRACT = {
    "plan_type": "autotrade_prediction_status_page_render_plan_packet",
    "source_type": "autotrade_prediction_status_page_display_section_packet",
    "dashboard_role": "operator_ui_read_only_render_plan_design",
    "planned_page": "btcts_next/src/btcts/apps/operator_ui/views/autotrade_page.py",
    "planned_location": "runtime_health_vicinity_read_only_prediction_status_subsection",
    "read_only_contract": True,
    "non_executing": True,
    "render_plan_only": True,
    "not_page_wiring": True,
    "not_runtime_wiring": True,
    "not_ui_rendering": True,
    "no_command_buttons": True,
    "no_forms": True,
    **{"no_" + "session" + "_state": True},
    "no_callbacks": True,
    "would_append_shadow_decision": False,
    "would_apply_mode": False,
    "would_execute_prearmed_grant": False,
    "would_write_runtime_artifact": False,
    "would_send_to_broker": False,
    "broker_execution_requested": False,
    "mode_apply_requested": False,
    "command_ledger_append_requested": False,
    "approval_append_requested": False,
}

DISPLAY_ORDER = (
    "section_state",
    "readiness_state",
    "preview_action",
    "preview_bias",
    "preview_confidence",
    "generated_at",
    "status_id",
    "preview_id",
    "blocker_count",
    "warning_count",
)


def _payload(value: AutoTradePredictionPreviewStatus | Mapping[str, Any] | None) -> dict[str, Any]:
    if value is None:
        return {}
    if isinstance(value, Mapping):
        return dict(value)
    return value.to_dict()


def _section_packet(value: AutoTradePredictionPreviewStatus | Mapping[str, Any] | None) -> dict[str, Any]:
    data = _payload(value)
    if data.get("section_type") == "autotrade_prediction_status_page_display_section_packet":
        return dict(data)
    return build_autotrade_prediction_status_page_display_section_packet(value)


def _count(value: Any) -> int:
    if value is None:
        return 0
    if isinstance(value, str):
        return 1 if value else 0
    try:
        return len(tuple(value))
    except TypeError:
        return 1


def _field_values(section: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "section_state": section.get("section_state"),
        "readiness_state": section.get("readiness_state"),
        "preview_action": section.get("preview_action"),
        "preview_bias": section.get("preview_bias"),
        "preview_confidence": section.get("preview_confidence"),
        "generated_at": section.get("generated_at"),
        "status_id": section.get("status_id"),
        "preview_id": section.get("preview_id"),
        "blocker_count": _count(section.get("blockers")),
        "warning_count": _count(section.get("warnings")),
    }


def prediction_status_page_render_plan_snapshot_lines(plan: Mapping[str, Any] | None) -> tuple[str, ...]:
    data = dict(plan or {})
    if not data:
        return (
            "render_plan_available=false",
            "read_only_contract=true",
            "render_plan_only=true",
            "not_page_wiring=true",
            "not_runtime_wiring=true",
            "not_ui_rendering=true",
            "no_command_buttons=true",
        )
    return (
        "render_plan_available=true",
        "plan_type=" + str(data.get("plan_type") or "unknown"),
        "planned_page=" + str(data.get("planned_page") or "unknown"),
        "planned_location=" + str(data.get("planned_location") or "unknown"),
        "layout_mode=" + str(data.get("layout_mode") or "unknown"),
        "field_count=" + str(len(tuple(data.get("display_order") or ()))),
        "read_only_contract=true",
        "render_plan_only=true",
        "not_page_wiring=true",
        "not_runtime_wiring=true",
        "not_ui_rendering=true",
        "no_command_buttons=true",
        "no_forms=true",
        "no_" + "session" + "_state=true",
        "no_callbacks=true",
        "would_append_shadow_decision=false",
        "would_apply_mode=false",
        "would_write_runtime_artifact=false",
        "would_send_to_broker=false",
    )


def build_autotrade_prediction_status_page_render_plan_packet(
    status_or_section_packet: AutoTradePredictionPreviewStatus | Mapping[str, Any] | None,
) -> dict[str, Any]:
    section = _section_packet(status_or_section_packet)
    field_values = _field_values(section)
    plan = {
        **AUTOTRADE_PREDICTION_STATUS_PAGE_RENDER_PLAN_CONTRACT,
        "render_plan_available": bool(section.get("section_available")),
        "layout_mode": "read_only_status_summary_then_details",
        "display_order": DISPLAY_ORDER,
        "field_values": field_values,
        "section_packet": section,
        "compact_line": section.get("compact_line"),
        "safety_lines": tuple(line for line in section.get("snapshot_lines") or () if "=" in str(line)),
        "render_notes": (
            "show compact_line as caption-like text",
            "show DISPLAY_ORDER values as read-only metrics or static text",
            "show blockers and warnings as static text only",
            "do not add command controls",
            "do not append ledgers or mutate mode",
        ),
    }
    plan["snapshot_lines"] = prediction_status_page_render_plan_snapshot_lines(plan)
    return plan
