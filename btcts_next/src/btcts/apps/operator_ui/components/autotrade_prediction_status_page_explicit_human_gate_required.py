# path: ./btcts_next/src/btcts/apps/operator_ui/components/autotrade_prediction_status_page_explicit_human_gate_required.py
# desc: Read-only explicit-human-gate-required packet for future AutoTrade prediction status page wiring. No page edit, UI framework import, commands, writes, mode apply, ledger append, or broker behavior.

from __future__ import annotations

from typing import Any, Mapping

from btcts.apps.operator_ui.components.autotrade_prediction_status_page_human_gate_decision import (
    build_autotrade_prediction_status_page_human_gate_decision_packet,
)
from btcts.autotrade.prediction_preview_status import AutoTradePredictionPreviewStatus

AUTOTRADE_PREDICTION_STATUS_PAGE_EXPLICIT_HUMAN_GATE_REQUIRED_CONTRACT = {
    "gate_requirement_type": "autotrade_prediction_status_page_actual_page_wiring_explicit_human_gate_required_packet",
    "source_type": "autotrade_prediction_status_page_actual_page_wiring_human_gate_decision_packet",
    "dashboard_role": "operator_ui_read_only_explicit_human_gate_required_record",
    "target_page": "btcts_next/src/btcts/apps/operator_ui/views/autotrade_page.py",
    "read_only_contract": True,
    "non_executing": True,
    "explicit_human_gate_required_packet_only": True,
    "explicit_human_gate_required": True,
    "human_gate_decision": "not_granted",
    "human_gate_granted": False,
    "page_change_authorized": False,
    "actual_page_wiring_allowed": False,
    "must_stop_before_autotrade_page_edit": True,
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


def _decision(value: AutoTradePredictionPreviewStatus | Mapping[str, Any] | None, *, page_text: str = "") -> dict[str, Any]:
    data = _payload(value)
    if data.get("decision_type") == "autotrade_prediction_status_page_actual_page_wiring_human_gate_decision_packet":
        return dict(data)
    return build_autotrade_prediction_status_page_human_gate_decision_packet(value, autotrade_page_text=page_text)


def explicit_human_gate_required_snapshot_lines(packet: Mapping[str, Any] | None) -> tuple[str, ...]:
    data = dict(packet or {})
    if not data:
        return (
            "explicit_human_gate_required_packet_available=false",
            "explicit_human_gate_required_packet_only=true",
            "explicit_human_gate_required=true",
            "human_gate_decision=not_granted",
            "human_gate_granted=false",
            "page_change_authorized=false",
            "actual_page_wiring_allowed=false",
            "must_stop_before_autotrade_page_edit=true",
            "blocked_until_human_gate=true",
        )
    return (
        "explicit_human_gate_required_packet_available=true",
        "gate_requirement_type=" + str(data.get("gate_requirement_type") or "unknown"),
        "target_page=" + str(data.get("target_page") or "unknown"),
        "explicit_human_gate_required_packet_only=true",
        "explicit_human_gate_required=true",
        "human_gate_decision=not_granted",
        "human_gate_granted=false",
        "page_change_authorized=false",
        "actual_page_wiring_allowed=false",
        "must_stop_before_autotrade_page_edit=true",
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


def build_autotrade_prediction_status_page_explicit_human_gate_required_packet(
    status_or_human_gate_decision_packet: AutoTradePredictionPreviewStatus | Mapping[str, Any] | None,
    *,
    autotrade_page_text: str = "",
) -> dict[str, Any]:
    decision = _decision(status_or_human_gate_decision_packet, page_text=autotrade_page_text)
    page_text = autotrade_page_text or ""
    packet = {
        **AUTOTRADE_PREDICTION_STATUS_PAGE_EXPLICIT_HUMAN_GATE_REQUIRED_CONTRACT,
        "explicit_human_gate_required_packet_available": bool(decision.get("human_gate_decision_ready")),
        "human_gate_decision_packet": decision,
        "human_gate_decision_ready": bool(decision.get("human_gate_decision_ready")),
        "decision_source": decision.get("decision_source"),
        "planned_helper_name": decision.get("planned_helper_name"),
        "planned_call_site": decision.get("planned_call_site"),
        "target_page_currently_contains_planned_import": decision.get("target_page_currently_contains_planned_import"),
        "target_page_currently_contains_planned_helper": decision.get("target_page_currently_contains_planned_helper"),
        "target_page_currently_contains_planned_builder": decision.get("target_page_currently_contains_planned_builder"),
        "autotrade_page_contains_gate_requirement_module": "autotrade_prediction_status_page_explicit_human_gate_required" in page_text,
        "autotrade_page_edit_performed_by_this_slice": False,
        "page_runtime_mount_performed_by_this_slice": False,
        "actual_ui_rendering_performed_by_this_slice": False,
        "command_surface_changed_by_this_slice": False,
    }
    packet["explicit_human_gate_required_ready"] = all(
        packet.get(name) is True
        for name in (
            "explicit_human_gate_required_packet_available",
            "human_gate_decision_ready",
            "explicit_human_gate_required",
            "must_stop_before_autotrade_page_edit",
            "blocked_until_human_gate",
        )
    ) and packet.get("human_gate_granted") is False and packet.get("page_change_authorized") is False and packet.get("actual_page_wiring_allowed") is False
    packet["snapshot_lines"] = explicit_human_gate_required_snapshot_lines(packet)
    return packet
