# path: ./btcts_next/src/btcts/apps/operator_ui/components/autotrade_prediction_status_page_human_gate_decision.py
# desc: Read-only human-gate decision packet for future AutoTrade prediction status page wiring. No page edit, UI framework import, commands, writes, mode apply, ledger append, or broker behavior.

from __future__ import annotations

from typing import Any, Mapping

from btcts.apps.operator_ui.components.autotrade_prediction_status_page_actual_page_wiring_patch_plan import (
    build_autotrade_prediction_status_page_actual_page_wiring_patch_plan_packet,
)
from btcts.autotrade.prediction_preview_status import AutoTradePredictionPreviewStatus

AUTOTRADE_PREDICTION_STATUS_PAGE_HUMAN_GATE_DECISION_CONTRACT = {
    "decision_type": "autotrade_prediction_status_page_actual_page_wiring_human_gate_decision_packet",
    "source_type": "autotrade_prediction_status_page_actual_page_wiring_patch_plan_packet",
    "dashboard_role": "operator_ui_read_only_human_gate_decision_record",
    "target_page": "btcts_next/src/btcts/apps/operator_ui/views/autotrade_page.py",
    "read_only_contract": True,
    "non_executing": True,
    "human_gate_decision_packet_only": True,
    "explicit_page_change_gate_required": True,
    "human_gate_decision": "not_granted",
    "human_gate_granted": False,
    "page_change_authorized": False,
    "actual_page_wiring_allowed": False,
    "blocked_until_human_gate": True,
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


def _patch_plan(value: AutoTradePredictionPreviewStatus | Mapping[str, Any] | None, *, page_text: str = "") -> dict[str, Any]:
    data = _payload(value)
    if data.get("patch_plan_type") == "autotrade_prediction_status_page_actual_page_wiring_patch_plan_packet":
        return dict(data)
    return build_autotrade_prediction_status_page_actual_page_wiring_patch_plan_packet(value, autotrade_page_text=page_text)


def human_gate_decision_snapshot_lines(packet: Mapping[str, Any] | None) -> tuple[str, ...]:
    data = dict(packet or {})
    if not data:
        return (
            "human_gate_decision_packet_available=false",
            "human_gate_decision_packet_only=true",
            "explicit_page_change_gate_required=true",
            "human_gate_decision=not_granted",
            "human_gate_granted=false",
            "page_change_authorized=false",
            "actual_page_wiring_allowed=false",
            "blocked_until_human_gate=true",
        )
    return (
        "human_gate_decision_packet_available=true",
        "decision_type=" + str(data.get("decision_type") or "unknown"),
        "target_page=" + str(data.get("target_page") or "unknown"),
        "human_gate_decision_packet_only=true",
        "explicit_page_change_gate_required=true",
        "human_gate_decision=not_granted",
        "human_gate_granted=false",
        "page_change_authorized=false",
        "actual_page_wiring_allowed=false",
        "blocked_until_human_gate=true",
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


def build_autotrade_prediction_status_page_human_gate_decision_packet(
    status_or_patch_plan_packet: AutoTradePredictionPreviewStatus | Mapping[str, Any] | None,
    *,
    autotrade_page_text: str = "",
) -> dict[str, Any]:
    patch_plan = _patch_plan(status_or_patch_plan_packet, page_text=autotrade_page_text)
    page_text = autotrade_page_text or ""
    packet = {
        **AUTOTRADE_PREDICTION_STATUS_PAGE_HUMAN_GATE_DECISION_CONTRACT,
        "human_gate_decision_packet_available": bool(patch_plan.get("patch_plan_ready")),
        "actual_page_wiring_patch_plan": patch_plan,
        "patch_plan_ready": bool(patch_plan.get("patch_plan_ready")),
        "planned_helper_name": patch_plan.get("planned_helper_name"),
        "planned_call_site": patch_plan.get("planned_call_site"),
        "target_page_currently_contains_planned_import": patch_plan.get("target_page_currently_contains_planned_import"),
        "target_page_currently_contains_planned_helper": patch_plan.get("target_page_currently_contains_planned_helper"),
        "target_page_currently_contains_planned_builder": patch_plan.get("target_page_currently_contains_planned_builder"),
        "decision_source": "no_explicit_human_page_change_gate_granted_in_current_slice",
        "autotrade_page_contains_decision_module": "autotrade_prediction_status_page_human_gate_decision" in page_text,
        "autotrade_page_edit_performed_by_this_slice": False,
        "page_runtime_mount_performed_by_this_slice": False,
        "actual_ui_rendering_performed_by_this_slice": False,
        "command_surface_changed_by_this_slice": False,
    }
    packet["human_gate_decision_ready"] = all(
        packet.get(name) is True
        for name in (
            "human_gate_decision_packet_available",
            "patch_plan_ready",
            "explicit_page_change_gate_required",
            "blocked_until_human_gate",
        )
    ) and packet.get("human_gate_granted") is False and packet.get("page_change_authorized") is False and packet.get("actual_page_wiring_allowed") is False
    packet["snapshot_lines"] = human_gate_decision_snapshot_lines(packet)
    return packet
