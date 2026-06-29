# path: ./btcts_next/src/btcts/apps/operator_ui/components/autotrade_prediction_status_page_page_wiring_readiness.py
# desc: Read-only page-wiring readiness packet for future AutoTrade prediction status page section. No page edit, UI framework import, commands, writes, mode apply, ledger append, or broker behavior.

from __future__ import annotations

from typing import Any, Mapping

from btcts.apps.operator_ui.components.autotrade_prediction_status_page_actual_render_wiring_plan import (
    build_autotrade_prediction_status_page_actual_render_wiring_plan_packet,
)
from btcts.autotrade.prediction_preview_status import AutoTradePredictionPreviewStatus

AUTOTRADE_PREDICTION_STATUS_PAGE_WIRING_READINESS_CONTRACT = {
    "readiness_type": "autotrade_prediction_status_page_page_wiring_readiness_packet",
    "source_type": "autotrade_prediction_status_page_actual_render_wiring_plan_packet",
    "dashboard_role": "operator_ui_read_only_page_wiring_readiness",
    "planned_page": "btcts_next/src/btcts/apps/operator_ui/views/autotrade_page.py",
    "planned_location": "runtime_health_vicinity_read_only_prediction_status_subsection",
    "read_only_contract": True,
    "non_executing": True,
    "page_wiring_readiness_only": True,
    "requires_future_explicit_page_change_gate": True,
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


def _payload(value: AutoTradePredictionPreviewStatus | Mapping[str, Any] | None) -> dict[str, Any]:
    if value is None:
        return {}
    if isinstance(value, Mapping):
        return dict(value)
    return value.to_dict()


def _wiring_plan(value: AutoTradePredictionPreviewStatus | Mapping[str, Any] | None) -> dict[str, Any]:
    data = _payload(value)
    if data.get("plan_type") == "autotrade_prediction_status_page_actual_render_wiring_plan_packet":
        return dict(data)
    return build_autotrade_prediction_status_page_actual_render_wiring_plan_packet(value)


def _contains(text: str, marker: str) -> bool:
    return marker in text


def page_wiring_readiness_snapshot_lines(packet: Mapping[str, Any] | None) -> tuple[str, ...]:
    data = dict(packet or {})
    if not data:
        return (
            "page_wiring_readiness_available=false",
            "read_only_contract=true",
            "page_wiring_readiness_only=true",
            "requires_future_explicit_page_change_gate=true",
            "not_page_wiring=true",
            "not_runtime_wiring=true",
            "not_ui_rendering=true",
        )
    return (
        "page_wiring_readiness_available=true",
        "readiness_type=" + str(data.get("readiness_type") or "unknown"),
        "planned_page=" + str(data.get("planned_page") or "unknown"),
        "candidate_anchor=" + str(data.get("candidate_anchor") or "unknown"),
        "candidate_anchor_present=" + str(bool(data.get("candidate_anchor_present"))).lower(),
        "runtime_health_section_present=" + str(bool(data.get("runtime_health_section_present"))).lower(),
        "read_only_contract=true",
        "page_wiring_readiness_only=true",
        "requires_future_explicit_page_change_gate=true",
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


def build_autotrade_prediction_status_page_page_wiring_readiness_packet(
    status_or_wiring_plan_packet: AutoTradePredictionPreviewStatus | Mapping[str, Any] | None,
    *,
    autotrade_page_text: str = "",
) -> dict[str, Any]:
    plan = _wiring_plan(status_or_wiring_plan_packet)
    candidate_anchor = str(plan.get("candidate_anchor") or "")
    page_text = autotrade_page_text or ""
    packet = {
        **AUTOTRADE_PREDICTION_STATUS_PAGE_WIRING_READINESS_CONTRACT,
        "page_wiring_readiness_available": bool(plan.get("actual_render_wiring_plan_available")),
        "actual_render_wiring_plan": plan,
        "candidate_anchor": candidate_anchor,
        "candidate_section_heading": plan.get("candidate_section_heading"),
        "candidate_anchor_present": _contains(page_text, "def _render_runtime_health_status"),
        "runtime_health_section_present": _contains(page_text, "Runtime Health"),
        "render_json_helper_present": _contains(page_text, "def _render_json"),
        "future_import_ready": True,
        "future_call_ready": True,
        "required_future_gate_before_page_edit": True,
        "autotrade_page_edit_performed_by_this_slice": False,
        "page_runtime_mount_performed_by_this_slice": False,
        "actual_ui_rendering_performed_by_this_slice": False,
        "command_surface_changed_by_this_slice": False,
    }
    packet["readiness_ready"] = all(
        packet.get(name) is True
        for name in (
            "page_wiring_readiness_available",
            "candidate_anchor_present",
            "runtime_health_section_present",
            "render_json_helper_present",
            "future_import_ready",
            "future_call_ready",
            "required_future_gate_before_page_edit",
        )
    )
    packet["snapshot_lines"] = page_wiring_readiness_snapshot_lines(packet)
    return packet
