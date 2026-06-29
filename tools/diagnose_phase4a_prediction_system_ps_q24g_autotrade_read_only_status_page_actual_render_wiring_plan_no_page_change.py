# path: ./tools/diagnose_phase4a_prediction_system_ps_q24g_autotrade_read_only_status_page_actual_render_wiring_plan_no_page_change.py
# desc: No-write diagnostic for AutoTrade read-only prediction status page actual-render wiring plan without page change.

from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import sys
from typing import Any, Mapping

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "btcts_next" / "src"
for candidate in (REPO_ROOT, SRC_ROOT):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

from btcts.apps.operator_ui.components.autotrade_prediction_status_page_actual_render_wiring_plan import (  # noqa: E402
    AUTOTRADE_PREDICTION_STATUS_PAGE_ACTUAL_RENDER_WIRING_PLAN_CONTRACT,
    build_autotrade_prediction_status_page_actual_render_wiring_plan_packet,
)
from btcts.autotrade.prediction_preview_status import AutoTradePredictionPreviewStatus  # noqa: E402
from tools.diagnose_phase4a_prediction_system_ps_q24f_autotrade_read_only_status_page_renderer_component_dry_run_no_page_wiring import (  # noqa: E402
    run_autotrade_read_only_status_page_renderer_component_dry_run_no_page_wiring,
)

DIAGNOSTIC_VERSION = "prediction_warroom.ps_q24g_autotrade_read_only_status_page_actual_render_wiring_plan_no_page_change.v1"
AUTOTRADE_PAGE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/autotrade_page.py"
PLAN_MODULE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/autotrade_prediction_status_page_actual_render_wiring_plan.py"
PLAN_MODULE_REF = "autotrade_prediction_status_page_actual_render_wiring_plan"
PLAN_BUILDER_REF = "build_autotrade_prediction_status_page_actual_render_wiring_plan_packet"


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _git(args: list[str]) -> str:
    proc = subprocess.run(["git", *args], cwd=REPO_ROOT, text=True, capture_output=True, check=False)
    return proc.stdout.strip()


def _sample_status() -> AutoTradePredictionPreviewStatus:
    return AutoTradePredictionPreviewStatus(
        status_id="ps_q24g_actual_render_wiring_plan_sample_status",
        generated_at="2026-06-29T00:00:00Z",
        status_state="ok",
        preview_id="ps_q24g_preview",
        readiness_id="ps_q24g_readiness",
        readiness_state="ready",
        intended_mode="READ_ONLY_PREVIEW",
        preview_action="WATCH",
        preview_bias="neutral",
        preview_confidence="medium",
        validation_state="ok",
        average_score=0.0,
        label_hit_rate=0.0,
        read_only=True,
        non_executing=True,
        would_append_shadow_decision=False,
        would_apply_mode=False,
        would_execute_prearmed_grant=False,
        would_write_runtime_artifact=False,
        would_send_to_broker=False,
        broker_execution_requested=False,
        mode_apply_requested=False,
        command_ledger_append_requested=False,
        approval_append_requested=False,
    )


def _all_false(payload: Mapping[str, Any], names: tuple[str, ...]) -> bool:
    return all(payload.get(name) is False for name in names)


def run_autotrade_read_only_status_page_actual_render_wiring_plan_no_page_change() -> dict[str, Any]:
    branch = _git(["rev-parse", "--abbrev-ref", "HEAD"])
    head = _git(["rev-parse", "--short", "HEAD"])
    status_short = _git(["status", "--short", "--untracked-files=all"])
    q24f = run_autotrade_read_only_status_page_renderer_component_dry_run_no_page_wiring()
    page_text = AUTOTRADE_PAGE.read_text(encoding="utf-8") if AUTOTRADE_PAGE.exists() else ""
    module_text = PLAN_MODULE.read_text(encoding="utf-8") if PLAN_MODULE.exists() else ""
    plan = build_autotrade_prediction_status_page_actual_render_wiring_plan_packet(_sample_status())

    execution_flags = (
        "would_append_shadow_decision",
        "would_apply_mode",
        "would_execute_prearmed_grant",
        "would_write_runtime_artifact",
        "would_send_to_broker",
        "broker_execution_requested",
        "mode_apply_requested",
        "command_ledger_append_requested",
        "approval_append_requested",
    )
    forbidden_module_tokens = (
        "stream" + "lit",
        "st." + "button",
        "st." + "checkbox",
        "st." + "form",
        "session_" + "state",
        "append_" + "decision_jsonl",
        "run_shadow_" + "decision_from_snapshot",
        "submit_mode_" + "change_command_request",
        "validate_and_" + "append_command",
        "place_" + "order(",
        "send_" + "order(",
        "create_" + "order(",
        "write_" + "text(",
        "." + "write(",
        "op" + "en(",
    )

    page_wired = PLAN_MODULE_REF in page_text or PLAN_BUILDER_REF in page_text
    blockers: list[str] = []
    if q24f.get("ready") is not True:
        blockers.append("q24f_renderer_dry_run_ready_required")
    for item in list(q24f.get("blockers") or []):
        blockers.append(f"q24f:{item}")
    if AUTOTRADE_PREDICTION_STATUS_PAGE_ACTUAL_RENDER_WIRING_PLAN_CONTRACT.get("plan_type") != "autotrade_prediction_status_page_actual_render_wiring_plan_packet":
        blockers.append("actual_render_wiring_plan_contract_type_required")
    if plan.get("actual_render_wiring_plan_available") is not True:
        blockers.append("actual_render_wiring_plan_available_required")
    if plan.get("required_future_gate_before_page_edit") is not True:
        blockers.append("future_page_change_gate_required")
    for marker in ("actual_render_wiring_plan_only=true", "requires_future_explicit_page_change_gate=true", "not_page_wiring=true", "not_runtime_wiring=true", "not_ui_rendering=true", "no_command_buttons=true", "no_forms=true", "no_" + "session" + "_state=true", "no_callbacks=true"):
        if marker not in tuple(plan.get("snapshot_lines") or ()): 
            blockers.append(f"actual_render_wiring_plan_snapshot_marker_required:{marker}")
    if plan.get("actual_render_wiring_plan_only") is not True or plan.get("not_page_wiring") is not True:
        blockers.append("actual_render_wiring_plan_not_page_wiring_required")
    if plan.get("not_runtime_wiring") is not True or plan.get("not_ui_rendering") is not True:
        blockers.append("actual_render_wiring_plan_no_runtime_ui_required")
    if plan.get("no_command_buttons") is not True or plan.get("no_forms") is not True or plan.get("no_" + "session" + "_state") is not True or plan.get("no_callbacks") is not True:
        blockers.append("actual_render_wiring_plan_no_controls_required")
    if plan.get("autotrade_page_edit_performed_by_this_slice") is not False or plan.get("page_runtime_mount_performed_by_this_slice") is not False:
        blockers.append("actual_render_wiring_plan_page_edit_or_mount_must_be_false")
    if plan.get("actual_ui_rendering_performed_by_this_slice") is not False or plan.get("command_surface_changed_by_this_slice") is not False:
        blockers.append("actual_render_wiring_plan_render_or_command_change_must_be_false")
    if not _all_false(plan, execution_flags):
        blockers.append("actual_render_wiring_plan_execution_flags_false_required")
    if page_wired:
        blockers.append("autotrade_page_actual_render_wiring_plan_wiring_unexpected")
    for token in forbidden_module_tokens:
        if token in module_text:
            blockers.append(f"actual_render_wiring_plan_module_forbidden_token:{token}")

    ready = not blockers
    return {
        "ok": True,
        "diagnostic_version": DIAGNOSTIC_VERSION,
        "generated_at": _utc_now(),
        "repo": {"branch": branch, "head": head, "status_short": status_short},
        "ready": ready,
        "state": "ps_q24g_autotrade_status_page_actual_render_wiring_plan_no_page_change_ready" if ready else "ps_q24g_autotrade_status_page_actual_render_wiring_plan_no_page_change_blocked",
        "blockers": blockers,
        "q24f_renderer_dry_run": {
            "ready": q24f.get("ready"),
            "diagnostic_version": q24f.get("diagnostic_version"),
            "renderer_dry_run_packet": q24f.get("renderer_dry_run_packet"),
            "safety": q24f.get("safety"),
        },
        "actual_render_wiring_plan": {
            "plan_type": plan.get("plan_type"),
            "actual_render_wiring_plan_available": plan.get("actual_render_wiring_plan_available"),
            "candidate_anchor": plan.get("candidate_anchor"),
            "candidate_section_heading": plan.get("candidate_section_heading"),
            "candidate_steps": plan.get("candidate_steps"),
            "required_future_gate_before_page_edit": plan.get("required_future_gate_before_page_edit"),
            "autotrade_page_edit_performed_by_this_slice": plan.get("autotrade_page_edit_performed_by_this_slice"),
            "page_runtime_mount_performed_by_this_slice": plan.get("page_runtime_mount_performed_by_this_slice"),
            "actual_ui_rendering_performed_by_this_slice": plan.get("actual_ui_rendering_performed_by_this_slice"),
            "command_surface_changed_by_this_slice": plan.get("command_surface_changed_by_this_slice"),
            "planned_page": plan.get("planned_page"),
            "planned_location": plan.get("planned_location"),
            "snapshot_lines": plan.get("snapshot_lines"),
            "actual_render_wiring_plan_only": plan.get("actual_render_wiring_plan_only"),
            "requires_future_explicit_page_change_gate": plan.get("requires_future_explicit_page_change_gate"),
            "not_page_wiring": plan.get("not_page_wiring"),
            "not_runtime_wiring": plan.get("not_runtime_wiring"),
            "not_ui_rendering": plan.get("not_ui_rendering"),
            "no_command_buttons": plan.get("no_command_buttons"),
            "no_forms": plan.get("no_forms"),
            **{"no_" + "session" + "_state": plan.get("no_" + "session" + "_state")},
            "no_callbacks": plan.get("no_callbacks"),
            "autotrade_page_runtime_wired": page_wired,
        },
        "safety": {
            "read_only_diagnostic": True,
            "actual_render_wiring_plan_packet_only": True,
            "autotrade_page_modified": False,
            "ui_runtime_wiring_changed": False,
            "ui_command_buttons_enabled": False,
            "ui_rendering_added": False,
            "runtime_artifact_write_enabled": False,
            "scheduler_action_changed": False,
            "shadow_decision_append_allowed": False,
            "mode_apply_allowed": False,
            "command_or_approval_ledger_allowed": False,
            "parameter_apply_allowed": False,
            "broker_private_api_allowed": False,
            "autotrade_trigger_allowed": False,
            "would_send_to_broker": False,
        },
    }


def main() -> int:
    result = run_autotrade_read_only_status_page_actual_render_wiring_plan_no_page_change()
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True, default=str))
    return 0 if result.get("ok") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
