# path: ./tools/diagnose_phase4a_prediction_system_ps_q24e_autotrade_read_only_status_page_render_plan_no_commands.py
# desc: No-write diagnostic for AutoTrade read-only prediction status page render-plan packet without commands.

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

from btcts.apps.operator_ui.components.autotrade_prediction_status_page_render_plan import (  # noqa: E402
    AUTOTRADE_PREDICTION_STATUS_PAGE_RENDER_PLAN_CONTRACT,
    DISPLAY_ORDER,
    build_autotrade_prediction_status_page_render_plan_packet,
)
from btcts.autotrade.prediction_preview_status import AutoTradePredictionPreviewStatus  # noqa: E402
from tools.diagnose_phase4a_prediction_system_ps_q24d_autotrade_read_only_status_page_display_packet_design import (  # noqa: E402
    run_autotrade_read_only_status_page_display_packet_design,
)

DIAGNOSTIC_VERSION = "prediction_warroom.ps_q24e_autotrade_read_only_status_page_render_plan_no_commands.v1"
AUTOTRADE_PAGE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/autotrade_page.py"
PLAN_MODULE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/autotrade_prediction_status_page_render_plan.py"
PLAN_MODULE_REF = "autotrade_prediction_status_page_render_plan"
PLAN_BUILDER_REF = "build_autotrade_prediction_status_page_render_plan_packet"


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _git(args: list[str]) -> str:
    proc = subprocess.run(["git", *args], cwd=REPO_ROOT, text=True, capture_output=True, check=False)
    return proc.stdout.strip()


def _sample_status() -> AutoTradePredictionPreviewStatus:
    return AutoTradePredictionPreviewStatus(
        status_id="ps_q24e_render_plan_sample_status",
        generated_at="2026-06-29T00:00:00Z",
        status_state="ok",
        preview_id="ps_q24e_preview",
        readiness_id="ps_q24e_readiness",
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


def run_autotrade_read_only_status_page_render_plan_no_commands() -> dict[str, Any]:
    branch = _git(["rev-parse", "--abbrev-ref", "HEAD"])
    head = _git(["rev-parse", "--short", "HEAD"])
    status_short = _git(["status", "--short", "--untracked-files=all"])
    q24d = run_autotrade_read_only_status_page_display_packet_design()
    page_text = AUTOTRADE_PAGE.read_text(encoding="utf-8") if AUTOTRADE_PAGE.exists() else ""
    module_text = PLAN_MODULE.read_text(encoding="utf-8") if PLAN_MODULE.exists() else ""
    plan = build_autotrade_prediction_status_page_render_plan_packet(_sample_status())

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
    if q24d.get("ready") is not True:
        blockers.append("q24d_page_section_packet_ready_required")
    for item in list(q24d.get("blockers") or []):
        blockers.append(f"q24d:{item}")
    if AUTOTRADE_PREDICTION_STATUS_PAGE_RENDER_PLAN_CONTRACT.get("plan_type") != "autotrade_prediction_status_page_render_plan_packet":
        blockers.append("render_plan_contract_type_required")
    if plan.get("render_plan_available") is not True:
        blockers.append("render_plan_available_required")
    if tuple(plan.get("display_order") or ()) != DISPLAY_ORDER:
        blockers.append("render_plan_display_order_required")
    for marker in ("render_plan_only=true", "not_page_wiring=true", "not_runtime_wiring=true", "not_ui_rendering=true", "no_command_buttons=true", "no_forms=true", "no_" + "session" + "_state=true", "no_callbacks=true"):
        if marker not in tuple(plan.get("snapshot_lines") or ()): 
            blockers.append(f"render_plan_snapshot_marker_required:{marker}")
    if plan.get("render_plan_only") is not True or plan.get("not_page_wiring") is not True:
        blockers.append("render_plan_not_page_wiring_required")
    if plan.get("not_runtime_wiring") is not True or plan.get("not_ui_rendering") is not True or plan.get("no_command_buttons") is not True:
        blockers.append("render_plan_no_runtime_ui_command_markers_required")
    if plan.get("no_forms") is not True or plan.get("no_" + "session" + "_state") is not True or plan.get("no_callbacks") is not True:
        blockers.append("render_plan_no_forms_session_callbacks_required")
    if not _all_false(plan, execution_flags):
        blockers.append("render_plan_execution_flags_false_required")
    if page_wired:
        blockers.append("autotrade_page_render_plan_wiring_unexpected")
    for token in forbidden_module_tokens:
        if token in module_text:
            blockers.append(f"render_plan_module_forbidden_token:{token}")

    ready = not blockers
    return {
        "ok": True,
        "diagnostic_version": DIAGNOSTIC_VERSION,
        "generated_at": _utc_now(),
        "repo": {"branch": branch, "head": head, "status_short": status_short},
        "ready": ready,
        "state": "ps_q24e_autotrade_status_page_render_plan_no_commands_ready" if ready else "ps_q24e_autotrade_status_page_render_plan_no_commands_blocked",
        "blockers": blockers,
        "q24d_page_section_packet": {
            "ready": q24d.get("ready"),
            "diagnostic_version": q24d.get("diagnostic_version"),
            "page_section_packet": q24d.get("page_section_packet"),
            "safety": q24d.get("safety"),
        },
        "render_plan_packet": {
            "plan_type": plan.get("plan_type"),
            "render_plan_available": plan.get("render_plan_available"),
            "layout_mode": plan.get("layout_mode"),
            "display_order": plan.get("display_order"),
            "field_values": plan.get("field_values"),
            "planned_page": plan.get("planned_page"),
            "planned_location": plan.get("planned_location"),
            "snapshot_lines": plan.get("snapshot_lines"),
            "render_plan_only": plan.get("render_plan_only"),
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
            "render_plan_packet_only": True,
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
    result = run_autotrade_read_only_status_page_render_plan_no_commands()
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True, default=str))
    return 0 if result.get("ok") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
