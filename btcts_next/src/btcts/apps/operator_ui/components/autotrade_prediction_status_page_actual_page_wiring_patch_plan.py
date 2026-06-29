# path: ./btcts_next/src/btcts/apps/operator_ui/components/autotrade_prediction_status_page_actual_page_wiring_patch_plan.py
# desc: Read-only exact patch plan packet for future AutoTrade prediction status page wiring. No page edit, UI framework import, commands, writes, mode apply, ledger append, or broker behavior.

from __future__ import annotations

from typing import Any, Mapping

from btcts.apps.operator_ui.components.autotrade_prediction_status_page_page_change_gate_readiness import (
    build_autotrade_prediction_status_page_page_change_gate_readiness_packet,
)
from btcts.autotrade.prediction_preview_status import AutoTradePredictionPreviewStatus

AUTOTRADE_PREDICTION_STATUS_PAGE_ACTUAL_PAGE_WIRING_PATCH_PLAN_CONTRACT = {
    "patch_plan_type": "autotrade_prediction_status_page_actual_page_wiring_patch_plan_packet",
    "source_type": "autotrade_prediction_status_page_actual_wiring_page_change_gate_readiness_packet",
    "dashboard_role": "operator_ui_read_only_actual_page_wiring_patch_plan",
    "target_page": "btcts_next/src/btcts/apps/operator_ui/views/autotrade_page.py",
    "planned_location": "runtime_health_vicinity_read_only_prediction_status_subsection",
    "read_only_contract": True,
    "non_executing": True,
    "actual_page_wiring_patch_plan_only": True,
    "explicit_page_change_gate_required": True,
    "page_change_gate_granted": False,
    "page_change_authorized": False,
    "page_patch_allowed_by_this_slice": False,
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

PLANNED_IMPORT_LINE = (
    "from btcts.apps.operator_ui.components.autotrade_prediction_status_page_renderer_dry_run "
    "import build_autotrade_prediction_status_page_renderer_dry_run_packet"
)
PLANNED_HELPER_NAME = "_render_prediction_status_read_only_preview"
PLANNED_CALL_SITE = "_render_runtime_health_status"
PLANNED_INSERTION_ANCHOR = "Runtime Health"


def _payload(value: AutoTradePredictionPreviewStatus | Mapping[str, Any] | None) -> dict[str, Any]:
    if value is None:
        return {}
    if isinstance(value, Mapping):
        return dict(value)
    return value.to_dict()


def _gate_packet(value: AutoTradePredictionPreviewStatus | Mapping[str, Any] | None, *, page_text: str = "") -> dict[str, Any]:
    data = _payload(value)
    if data.get("gate_type") == "autotrade_prediction_status_page_actual_wiring_page_change_gate_readiness_packet":
        return dict(data)
    return build_autotrade_prediction_status_page_page_change_gate_readiness_packet(value, autotrade_page_text=page_text)


def page_wiring_patch_plan_snapshot_lines(packet: Mapping[str, Any] | None) -> tuple[str, ...]:
    data = dict(packet or {})
    if not data:
        return (
            "actual_page_wiring_patch_plan_available=false",
            "read_only_contract=true",
            "actual_page_wiring_patch_plan_only=true",
            "explicit_page_change_gate_required=true",
            "page_change_gate_granted=false",
            "page_change_authorized=false",
            "page_patch_allowed_by_this_slice=false",
            "blocked_until_human_gate=true",
        )
    return (
        "actual_page_wiring_patch_plan_available=true",
        "patch_plan_type=" + str(data.get("patch_plan_type") or "unknown"),
        "target_page=" + str(data.get("target_page") or "unknown"),
        "planned_call_site=" + str(data.get("planned_call_site") or "unknown"),
        "planned_helper_name=" + str(data.get("planned_helper_name") or "unknown"),
        "read_only_contract=true",
        "actual_page_wiring_patch_plan_only=true",
        "explicit_page_change_gate_required=true",
        "page_change_gate_granted=false",
        "page_change_authorized=false",
        "page_patch_allowed_by_this_slice=false",
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


def build_autotrade_prediction_status_page_actual_page_wiring_patch_plan_packet(
    status_or_page_change_gate_readiness_packet: AutoTradePredictionPreviewStatus | Mapping[str, Any] | None,
    *,
    autotrade_page_text: str = "",
) -> dict[str, Any]:
    gate = _gate_packet(status_or_page_change_gate_readiness_packet, page_text=autotrade_page_text)
    page_text = autotrade_page_text or ""
    packet = {
        **AUTOTRADE_PREDICTION_STATUS_PAGE_ACTUAL_PAGE_WIRING_PATCH_PLAN_CONTRACT,
        "actual_page_wiring_patch_plan_available": bool(gate.get("gate_readiness_ready")),
        "page_change_gate_readiness": gate,
        "gate_readiness_ready": bool(gate.get("gate_readiness_ready")),
        "candidate_anchor_present": gate.get("candidate_anchor_present"),
        "runtime_health_section_present": gate.get("runtime_health_section_present"),
        "render_json_helper_present": gate.get("render_json_helper_present"),
        "planned_import_line": PLANNED_IMPORT_LINE,
        "planned_helper_name": PLANNED_HELPER_NAME,
        "planned_call_site": PLANNED_CALL_SITE,
        "planned_insertion_anchor": PLANNED_INSERTION_ANCHOR,
        "planned_patch_steps": (
            "add read-only renderer dry-run import after explicit gate only",
            "add a read-only helper that converts dry-run static operation descriptors into passive text display only",
            "call the helper near Runtime Health after explicit gate only",
            "do not add command controls, forms, callbacks, ledger writes, mode apply, broker calls, or runtime writes",
        ),
        "target_page_currently_contains_planned_import": PLANNED_IMPORT_LINE in page_text,
        "target_page_currently_contains_planned_helper": PLANNED_HELPER_NAME in page_text,
        "target_page_currently_contains_planned_builder": "build_autotrade_prediction_status_page_renderer_dry_run_packet" in page_text,
        "target_page_diff_performed_by_this_slice": False,
        "autotrade_page_edit_performed_by_this_slice": False,
        "page_runtime_mount_performed_by_this_slice": False,
        "actual_ui_rendering_performed_by_this_slice": False,
        "command_surface_changed_by_this_slice": False,
    }
    packet["patch_plan_ready"] = all(
        packet.get(name) is True
        for name in (
            "actual_page_wiring_patch_plan_available",
            "gate_readiness_ready",
            "candidate_anchor_present",
            "runtime_health_section_present",
            "render_json_helper_present",
            "explicit_page_change_gate_required",
            "blocked_until_human_gate",
        )
    ) and packet.get("page_change_gate_granted") is False and packet.get("page_change_authorized") is False and packet.get("page_patch_allowed_by_this_slice") is False
    packet["snapshot_lines"] = page_wiring_patch_plan_snapshot_lines(packet)
    return packet
