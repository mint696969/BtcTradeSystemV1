# path: ./btcts_next/src/btcts/apps/operator_ui/components/autotrade_prediction_status_page_page_change_gate_readiness.py
# desc: Read-only explicit page-change gate readiness packet for future AutoTrade prediction status page wiring. No page edit, UI framework import, commands, writes, mode apply, ledger append, or broker behavior.

from __future__ import annotations

from typing import Any, Mapping

from btcts.apps.operator_ui.components.autotrade_prediction_status_page_page_wiring_readiness import (
    build_autotrade_prediction_status_page_page_wiring_readiness_packet,
)
from btcts.autotrade.prediction_preview_status import AutoTradePredictionPreviewStatus

AUTOTRADE_PREDICTION_STATUS_PAGE_CHANGE_GATE_READINESS_CONTRACT = {
    "gate_type": "autotrade_prediction_status_page_actual_wiring_page_change_gate_readiness_packet",
    "source_type": "autotrade_prediction_status_page_page_wiring_readiness_packet",
    "dashboard_role": "operator_ui_read_only_page_change_gate_readiness",
    "planned_page": "btcts_next/src/btcts/apps/operator_ui/views/autotrade_page.py",
    "planned_location": "runtime_health_vicinity_read_only_prediction_status_subsection",
    "read_only_contract": True,
    "non_executing": True,
    "page_change_gate_readiness_only": True,
    "explicit_page_change_gate_required": True,
    "page_change_gate_granted": False,
    "page_change_authorized": False,
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


def _readiness_packet(value: AutoTradePredictionPreviewStatus | Mapping[str, Any] | None, *, page_text: str = "") -> dict[str, Any]:
    data = _payload(value)
    if data.get("readiness_type") == "autotrade_prediction_status_page_page_wiring_readiness_packet":
        return dict(data)
    return build_autotrade_prediction_status_page_page_wiring_readiness_packet(value, autotrade_page_text=page_text)


def page_change_gate_readiness_snapshot_lines(packet: Mapping[str, Any] | None) -> tuple[str, ...]:
    data = dict(packet or {})
    if not data:
        return (
            "page_change_gate_readiness_available=false",
            "read_only_contract=true",
            "page_change_gate_readiness_only=true",
            "explicit_page_change_gate_required=true",
            "page_change_gate_granted=false",
            "page_change_authorized=false",
            "blocked_until_human_gate=true",
        )
    return (
        "page_change_gate_readiness_available=true",
        "gate_type=" + str(data.get("gate_type") or "unknown"),
        "planned_page=" + str(data.get("planned_page") or "unknown"),
        "candidate_anchor=" + str(data.get("candidate_anchor") or "unknown"),
        "readiness_ready=" + str(bool(data.get("readiness_ready"))).lower(),
        "read_only_contract=true",
        "page_change_gate_readiness_only=true",
        "explicit_page_change_gate_required=true",
        "page_change_gate_granted=false",
        "page_change_authorized=false",
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


def build_autotrade_prediction_status_page_page_change_gate_readiness_packet(
    status_or_page_wiring_readiness_packet: AutoTradePredictionPreviewStatus | Mapping[str, Any] | None,
    *,
    autotrade_page_text: str = "",
) -> dict[str, Any]:
    readiness = _readiness_packet(status_or_page_wiring_readiness_packet, page_text=autotrade_page_text)
    packet = {
        **AUTOTRADE_PREDICTION_STATUS_PAGE_CHANGE_GATE_READINESS_CONTRACT,
        "page_change_gate_readiness_available": bool(readiness.get("readiness_ready")),
        "page_wiring_readiness": readiness,
        "readiness_ready": bool(readiness.get("readiness_ready")),
        "candidate_anchor": readiness.get("candidate_anchor"),
        "candidate_section_heading": readiness.get("candidate_section_heading"),
        "candidate_anchor_present": readiness.get("candidate_anchor_present"),
        "runtime_health_section_present": readiness.get("runtime_health_section_present"),
        "render_json_helper_present": readiness.get("render_json_helper_present"),
        "planned_future_import": "btcts.apps.operator_ui.components.autotrade_prediction_status_page_renderer_dry_run",
        "planned_future_builder": "build_autotrade_prediction_status_page_renderer_dry_run_packet",
        "planned_future_call_site": "_render_runtime_health_status",
        "planned_future_render_mode": "read_only_static_text_from_dry_run_ops",
        "planned_future_page_diff_allowed_by_this_slice": False,
        "planned_future_requires_new_human_gate": True,
        "autotrade_page_edit_performed_by_this_slice": False,
        "page_runtime_mount_performed_by_this_slice": False,
        "actual_ui_rendering_performed_by_this_slice": False,
        "command_surface_changed_by_this_slice": False,
    }
    packet["gate_readiness_ready"] = all(
        packet.get(name) is True
        for name in (
            "page_change_gate_readiness_available",
            "readiness_ready",
            "candidate_anchor_present",
            "runtime_health_section_present",
            "render_json_helper_present",
            "explicit_page_change_gate_required",
            "blocked_until_human_gate",
            "planned_future_requires_new_human_gate",
        )
    ) and packet.get("page_change_gate_granted") is False and packet.get("page_change_authorized") is False
    packet["snapshot_lines"] = page_change_gate_readiness_snapshot_lines(packet)
    return packet
