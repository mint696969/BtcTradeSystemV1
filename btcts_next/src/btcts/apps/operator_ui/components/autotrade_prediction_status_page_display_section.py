# path: ./btcts_next/src/btcts/apps/operator_ui/components/autotrade_prediction_status_page_display_section.py
# desc: Read-only page-section packet for future AutoTrade prediction status placement. No Streamlit rendering, page wiring, commands, writes, mode apply, ledger append, or broker behavior.

from __future__ import annotations

from typing import Any, Mapping

from btcts.apps.operator_ui.components.autotrade_prediction_preview_status_display import (
    build_autotrade_prediction_preview_status_display_packet,
)
from btcts.autotrade.prediction_preview_status import AutoTradePredictionPreviewStatus

AUTOTRADE_PREDICTION_STATUS_PAGE_SECTION_CONTRACT = {
    "section_type": "autotrade_prediction_status_page_display_section_packet",
    "source_type": "autotrade_prediction_preview_status_display_packet",
    "dashboard_role": "operator_ui_read_only_page_section_design",
    "planned_page": "btcts_next/src/btcts/apps/operator_ui/views/autotrade_page.py",
    "planned_location": "runtime_health_vicinity_read_only_prediction_status_subsection",
    "read_only_contract": True,
    "non_executing": True,
    "planning_only": True,
    "component_reusable": True,
    "not_page_wiring": True,
    "not_runtime_wiring": True,
    "not_ui_rendering": True,
    "no_command_buttons": True,
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


def _payload(status: AutoTradePredictionPreviewStatus | Mapping[str, Any] | None) -> dict[str, Any]:
    if status is None:
        return {}
    if isinstance(status, Mapping):
        return dict(status)
    return status.to_dict()


def _display_packet(status_or_packet: AutoTradePredictionPreviewStatus | Mapping[str, Any] | None) -> dict[str, Any]:
    data = _payload(status_or_packet)
    if data.get("section_type") == "autotrade_prediction_preview_status_display_packet":
        return dict(data)
    return build_autotrade_prediction_preview_status_display_packet(status_or_packet)


def _section_state(display: Mapping[str, Any]) -> str:
    if display.get("status_available") is not True:
        return "unavailable"
    state = str(display.get("display_state") or "").strip()
    if state in {"ok", "review", "blocked"}:
        return state
    return "unavailable"


def _tuple_text(value: Any) -> tuple[str, ...]:
    if value is None:
        return ()
    if isinstance(value, str):
        return (value,) if value else ()
    try:
        return tuple(str(item) for item in value if str(item))
    except TypeError:
        text = str(value)
        return (text,) if text else ()


def prediction_status_page_section_snapshot_lines(section: Mapping[str, Any] | None) -> tuple[str, ...]:
    data = dict(section or {})
    if not data:
        return (
            "section_available=false",
            "section_state=unavailable",
            "read_only_contract=true",
            "planning_only=true",
            "not_page_wiring=true",
            "not_runtime_wiring=true",
            "not_ui_rendering=true",
            "no_command_buttons=true",
        )
    return (
        "section_available=" + ("true" if data.get("section_available") else "false"),
        "section_state=" + str(data.get("section_state") or "unavailable"),
        "planned_page=" + str(data.get("planned_page") or "unknown"),
        "planned_location=" + str(data.get("planned_location") or "unknown"),
        "display_state=" + str(data.get("display_state") or "unavailable"),
        "preview_action=" + str(data.get("preview_action") or "unknown"),
        "preview_bias=" + str(data.get("preview_bias") or "unknown"),
        "read_only_contract=true",
        "planning_only=true",
        "not_page_wiring=true",
        "not_runtime_wiring=true",
        "not_ui_rendering=true",
        "no_command_buttons=true",
        "would_append_shadow_decision=false",
        "would_apply_mode=false",
        "would_write_runtime_artifact=false",
        "would_send_to_broker=false",
    )


def build_autotrade_prediction_status_page_display_section_packet(
    status_or_display_packet: AutoTradePredictionPreviewStatus | Mapping[str, Any] | None,
    *,
    section_id: str = "autotrade_prediction_status_read_only_section",
) -> dict[str, Any]:
    display = _display_packet(status_or_display_packet)
    blockers = _tuple_text(display.get("blockers"))
    warnings = _tuple_text(display.get("warnings"))
    section = {
        **AUTOTRADE_PREDICTION_STATUS_PAGE_SECTION_CONTRACT,
        "section_id": section_id,
        "section_available": bool(display.get("status_available")),
        "section_state": _section_state(display),
        "display_packet": display,
        "display_state": display.get("display_state"),
        "status_available": display.get("status_available"),
        "status_id": display.get("status_id"),
        "generated_at": display.get("generated_at"),
        "preview_id": display.get("preview_id"),
        "readiness_id": display.get("readiness_id"),
        "readiness_state": display.get("readiness_state"),
        "intended_mode": display.get("intended_mode"),
        "preview_action": display.get("preview_action"),
        "preview_bias": display.get("preview_bias"),
        "preview_confidence": display.get("preview_confidence"),
        "blockers": blockers,
        "warnings": warnings,
        "compact_line": "page_section=" + _section_state(display) + " / " + str(display.get("compact_line") or "prediction_preview_status unavailable / display_only"),
    }
    section["snapshot_lines"] = prediction_status_page_section_snapshot_lines(section)
    return section
