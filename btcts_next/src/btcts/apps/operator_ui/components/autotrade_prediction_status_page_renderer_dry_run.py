# path: ./btcts_next/src/btcts/apps/operator_ui/components/autotrade_prediction_status_page_renderer_dry_run.py
# desc: Read-only renderer dry-run packet for future AutoTrade prediction status page section. No UI framework import, page wiring, commands, writes, mode apply, ledger append, or broker behavior.

from __future__ import annotations

from typing import Any, Mapping

from btcts.apps.operator_ui.components.autotrade_prediction_status_page_render_plan import (
    build_autotrade_prediction_status_page_render_plan_packet,
)
from btcts.autotrade.prediction_preview_status import AutoTradePredictionPreviewStatus

AUTOTRADE_PREDICTION_STATUS_PAGE_RENDERER_DRY_RUN_CONTRACT = {
    "dry_run_type": "autotrade_prediction_status_page_renderer_dry_run_packet",
    "source_type": "autotrade_prediction_status_page_render_plan_packet",
    "dashboard_role": "operator_ui_read_only_renderer_dry_run",
    "planned_page": "btcts_next/src/btcts/apps/operator_ui/views/autotrade_page.py",
    "planned_location": "runtime_health_vicinity_read_only_prediction_status_subsection",
    "read_only_contract": True,
    "non_executing": True,
    "renderer_dry_run_only": True,
    "static_ops_only": True,
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


def _plan_packet(value: AutoTradePredictionPreviewStatus | Mapping[str, Any] | None) -> dict[str, Any]:
    data = _payload(value)
    if data.get("plan_type") == "autotrade_prediction_status_page_render_plan_packet":
        return dict(data)
    return build_autotrade_prediction_status_page_render_plan_packet(value)


def _static_op(name: str, value: Any, *, role: str) -> dict[str, Any]:
    return {
        "op_type": "static_text",
        "name": name,
        "value": value,
        "role": role,
        "interactive": False,
        "command_control": False,
        "would_mutate_state": False,
        "would_write": False,
        "would_send_to_broker": False,
    }


def _ops_from_plan(plan: Mapping[str, Any]) -> tuple[dict[str, Any], ...]:
    field_values = plan.get("field_values") if isinstance(plan.get("field_values"), Mapping) else {}
    display_order = tuple(str(item) for item in plan.get("display_order") or ())
    ops: list[dict[str, Any]] = [
        _static_op("compact_line", plan.get("compact_line"), role="summary"),
        _static_op("layout_mode", plan.get("layout_mode"), role="metadata"),
    ]
    for item in display_order:
        ops.append(_static_op(item, field_values.get(item), role="field"))
    for idx, note in enumerate(tuple(plan.get("render_notes") or ())):
        ops.append(_static_op(f"render_note_{idx}", note, role="note"))
    return tuple(ops)


def prediction_status_page_renderer_dry_run_snapshot_lines(dry_run: Mapping[str, Any] | None) -> tuple[str, ...]:
    data = dict(dry_run or {})
    if not data:
        return (
            "renderer_dry_run_available=false",
            "read_only_contract=true",
            "renderer_dry_run_only=true",
            "static_ops_only=true",
            "not_page_wiring=true",
            "not_runtime_wiring=true",
            "not_ui_rendering=true",
            "no_command_buttons=true",
        )
    return (
        "renderer_dry_run_available=true",
        "dry_run_type=" + str(data.get("dry_run_type") or "unknown"),
        "planned_page=" + str(data.get("planned_page") or "unknown"),
        "planned_location=" + str(data.get("planned_location") or "unknown"),
        "ops_count=" + str(data.get("ops_count") or 0),
        "read_only_contract=true",
        "renderer_dry_run_only=true",
        "static_ops_only=true",
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


def build_autotrade_prediction_status_page_renderer_dry_run_packet(
    status_or_render_plan_packet: AutoTradePredictionPreviewStatus | Mapping[str, Any] | None,
) -> dict[str, Any]:
    plan = _plan_packet(status_or_render_plan_packet)
    ops = _ops_from_plan(plan)
    dry_run = {
        **AUTOTRADE_PREDICTION_STATUS_PAGE_RENDERER_DRY_RUN_CONTRACT,
        "renderer_dry_run_available": bool(plan.get("render_plan_available")),
        "render_plan_packet": plan,
        "layout_mode": plan.get("layout_mode"),
        "display_order": plan.get("display_order"),
        "ops": ops,
        "ops_count": len(ops),
        "all_ops_static": all(op.get("op_type") == "static_text" and op.get("interactive") is False for op in ops),
        "all_ops_non_mutating": all(op.get("would_mutate_state") is False and op.get("would_write") is False for op in ops),
        "all_ops_non_broker": all(op.get("would_send_to_broker") is False for op in ops),
    }
    dry_run["snapshot_lines"] = prediction_status_page_renderer_dry_run_snapshot_lines(dry_run)
    return dry_run
