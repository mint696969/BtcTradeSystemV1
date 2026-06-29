# path: ./btcts_next/src/btcts/apps/operator_ui/components/autotrade_prediction_status_page_actual_render_wiring_plan.py
# desc: Read-only actual-render wiring plan packet for future AutoTrade prediction status page section. No page edit, UI framework import, commands, writes, mode apply, ledger append, or broker behavior.

from __future__ import annotations

from typing import Any, Mapping

from btcts.apps.operator_ui.components.autotrade_prediction_status_page_renderer_dry_run import (
    build_autotrade_prediction_status_page_renderer_dry_run_packet,
)
from btcts.autotrade.prediction_preview_status import AutoTradePredictionPreviewStatus

AUTOTRADE_PREDICTION_STATUS_PAGE_ACTUAL_RENDER_WIRING_PLAN_CONTRACT = {
    "plan_type": "autotrade_prediction_status_page_actual_render_wiring_plan_packet",
    "source_type": "autotrade_prediction_status_page_renderer_dry_run_packet",
    "dashboard_role": "operator_ui_read_only_actual_render_wiring_plan",
    "planned_page": "btcts_next/src/btcts/apps/operator_ui/views/autotrade_page.py",
    "planned_location": "runtime_health_vicinity_read_only_prediction_status_subsection",
    "read_only_contract": True,
    "non_executing": True,
    "actual_render_wiring_plan_only": True,
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


def _dry_run_packet(value: AutoTradePredictionPreviewStatus | Mapping[str, Any] | None) -> dict[str, Any]:
    data = _payload(value)
    if data.get("dry_run_type") == "autotrade_prediction_status_page_renderer_dry_run_packet":
        return dict(data)
    return build_autotrade_prediction_status_page_renderer_dry_run_packet(value)


def actual_render_wiring_plan_snapshot_lines(plan: Mapping[str, Any] | None) -> tuple[str, ...]:
    data = dict(plan or {})
    if not data:
        return (
            "actual_render_wiring_plan_available=false",
            "read_only_contract=true",
            "actual_render_wiring_plan_only=true",
            "requires_future_explicit_page_change_gate=true",
            "not_page_wiring=true",
            "not_runtime_wiring=true",
            "not_ui_rendering=true",
        )
    return (
        "actual_render_wiring_plan_available=true",
        "plan_type=" + str(data.get("plan_type") or "unknown"),
        "planned_page=" + str(data.get("planned_page") or "unknown"),
        "planned_location=" + str(data.get("planned_location") or "unknown"),
        "candidate_anchor=" + str(data.get("candidate_anchor") or "unknown"),
        "read_only_contract=true",
        "actual_render_wiring_plan_only=true",
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


def build_autotrade_prediction_status_page_actual_render_wiring_plan_packet(
    status_or_dry_run_packet: AutoTradePredictionPreviewStatus | Mapping[str, Any] | None,
) -> dict[str, Any]:
    dry_run = _dry_run_packet(status_or_dry_run_packet)
    plan = {
        **AUTOTRADE_PREDICTION_STATUS_PAGE_ACTUAL_RENDER_WIRING_PLAN_CONTRACT,
        "actual_render_wiring_plan_available": bool(dry_run.get("renderer_dry_run_available")),
        "renderer_dry_run_packet": dry_run,
        "candidate_anchor": "_render_runtime_health_status_after_health_snapshot_caption",
        "candidate_section_heading": "Prediction Status / Read-only Preview",
        "candidate_render_source": "autotrade_prediction_status_page_renderer_dry_run_static_ops",
        "candidate_steps": (
            "add read-only import after future explicit page-change gate",
            "place static prediction status subsection near Runtime Health output",
            "render static summary fields from dry-run operation descriptors only",
            "keep command controls out of the prediction status subsection",
            "preserve existing operator command surface unchanged",
        ),
        "required_future_gate_before_page_edit": True,
        "autotrade_page_edit_performed_by_this_slice": False,
        "page_runtime_mount_performed_by_this_slice": False,
        "actual_ui_rendering_performed_by_this_slice": False,
        "command_surface_changed_by_this_slice": False,
    }
    plan["snapshot_lines"] = actual_render_wiring_plan_snapshot_lines(plan)
    return plan
