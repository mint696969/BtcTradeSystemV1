# path: ./tools/diagnose_phase4a_prediction_system_ps_q24f_autotrade_read_only_status_page_renderer_component_dry_run_no_page_wiring.py
# desc: No-write diagnostic for AutoTrade read-only prediction status page renderer dry-run packet without page wiring.

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

from btcts.apps.operator_ui.components.autotrade_prediction_status_page_renderer_dry_run import (  # noqa: E402
    AUTOTRADE_PREDICTION_STATUS_PAGE_RENDERER_DRY_RUN_CONTRACT,
    build_autotrade_prediction_status_page_renderer_dry_run_packet,
)
from btcts.autotrade.prediction_preview_status import AutoTradePredictionPreviewStatus  # noqa: E402
from tools.diagnose_phase4a_prediction_system_ps_q24e_autotrade_read_only_status_page_render_plan_no_commands import (  # noqa: E402
    run_autotrade_read_only_status_page_render_plan_no_commands,
)

DIAGNOSTIC_VERSION = "prediction_warroom.ps_q24f_autotrade_read_only_status_page_renderer_component_dry_run_no_page_wiring.v1"
AUTOTRADE_PAGE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/autotrade_page.py"
DRY_RUN_MODULE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/autotrade_prediction_status_page_renderer_dry_run.py"
DRY_RUN_MODULE_REF = "autotrade_prediction_status_page_renderer_dry_run"
DRY_RUN_BUILDER_REF = "build_autotrade_prediction_status_page_renderer_dry_run_packet"


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _git(args: list[str]) -> str:
    proc = subprocess.run(["git", *args], cwd=REPO_ROOT, text=True, capture_output=True, check=False)
    return proc.stdout.strip()


def _sample_status() -> AutoTradePredictionPreviewStatus:
    return AutoTradePredictionPreviewStatus(
        status_id="ps_q24f_renderer_dry_run_sample_status",
        generated_at="2026-06-29T00:00:00Z",
        status_state="ok",
        preview_id="ps_q24f_preview",
        readiness_id="ps_q24f_readiness",
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


def run_autotrade_read_only_status_page_renderer_component_dry_run_no_page_wiring() -> dict[str, Any]:
    branch = _git(["rev-parse", "--abbrev-ref", "HEAD"])
    head = _git(["rev-parse", "--short", "HEAD"])
    status_short = _git(["status", "--short", "--untracked-files=all"])
    q24e = run_autotrade_read_only_status_page_render_plan_no_commands()
    page_text = AUTOTRADE_PAGE.read_text(encoding="utf-8") if AUTOTRADE_PAGE.exists() else ""
    module_text = DRY_RUN_MODULE.read_text(encoding="utf-8") if DRY_RUN_MODULE.exists() else ""
    dry_run = build_autotrade_prediction_status_page_renderer_dry_run_packet(_sample_status())

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

    page_wired = DRY_RUN_MODULE_REF in page_text or DRY_RUN_BUILDER_REF in page_text
    blockers: list[str] = []
    if q24e.get("ready") is not True:
        blockers.append("q24e_render_plan_ready_required")
    for item in list(q24e.get("blockers") or []):
        blockers.append(f"q24e:{item}")
    if AUTOTRADE_PREDICTION_STATUS_PAGE_RENDERER_DRY_RUN_CONTRACT.get("dry_run_type") != "autotrade_prediction_status_page_renderer_dry_run_packet":
        blockers.append("renderer_dry_run_contract_type_required")
    if dry_run.get("renderer_dry_run_available") is not True:
        blockers.append("renderer_dry_run_available_required")
    if dry_run.get("ops_count", 0) < 5:
        blockers.append("renderer_dry_run_static_ops_required")
    for marker in ("renderer_dry_run_only=true", "static_ops_only=true", "not_page_wiring=true", "not_runtime_wiring=true", "not_ui_rendering=true", "no_command_buttons=true", "no_forms=true", "no_" + "session" + "_state=true", "no_callbacks=true"):
        if marker not in tuple(dry_run.get("snapshot_lines") or ()): 
            blockers.append(f"renderer_dry_run_snapshot_marker_required:{marker}")
    if dry_run.get("renderer_dry_run_only") is not True or dry_run.get("static_ops_only") is not True:
        blockers.append("renderer_dry_run_static_only_required")
    if dry_run.get("not_page_wiring") is not True or dry_run.get("not_runtime_wiring") is not True or dry_run.get("not_ui_rendering") is not True:
        blockers.append("renderer_dry_run_no_wiring_required")
    if dry_run.get("no_command_buttons") is not True or dry_run.get("no_forms") is not True or dry_run.get("no_" + "session" + "_state") is not True or dry_run.get("no_callbacks") is not True:
        blockers.append("renderer_dry_run_no_controls_required")
    if dry_run.get("all_ops_static") is not True or dry_run.get("all_ops_non_mutating") is not True or dry_run.get("all_ops_non_broker") is not True:
        blockers.append("renderer_dry_run_ops_static_non_mutating_required")
    if not _all_false(dry_run, execution_flags):
        blockers.append("renderer_dry_run_execution_flags_false_required")
    if page_wired:
        blockers.append("autotrade_page_renderer_dry_run_wiring_unexpected")
    for token in forbidden_module_tokens:
        if token in module_text:
            blockers.append(f"renderer_dry_run_module_forbidden_token:{token}")

    ready = not blockers
    return {
        "ok": True,
        "diagnostic_version": DIAGNOSTIC_VERSION,
        "generated_at": _utc_now(),
        "repo": {"branch": branch, "head": head, "status_short": status_short},
        "ready": ready,
        "state": "ps_q24f_autotrade_status_page_renderer_component_dry_run_no_page_wiring_ready" if ready else "ps_q24f_autotrade_status_page_renderer_component_dry_run_no_page_wiring_blocked",
        "blockers": blockers,
        "q24e_render_plan": {
            "ready": q24e.get("ready"),
            "diagnostic_version": q24e.get("diagnostic_version"),
            "render_plan_packet": q24e.get("render_plan_packet"),
            "safety": q24e.get("safety"),
        },
        "renderer_dry_run_packet": {
            "dry_run_type": dry_run.get("dry_run_type"),
            "renderer_dry_run_available": dry_run.get("renderer_dry_run_available"),
            "layout_mode": dry_run.get("layout_mode"),
            "ops_count": dry_run.get("ops_count"),
            "all_ops_static": dry_run.get("all_ops_static"),
            "all_ops_non_mutating": dry_run.get("all_ops_non_mutating"),
            "all_ops_non_broker": dry_run.get("all_ops_non_broker"),
            "planned_page": dry_run.get("planned_page"),
            "planned_location": dry_run.get("planned_location"),
            "snapshot_lines": dry_run.get("snapshot_lines"),
            "renderer_dry_run_only": dry_run.get("renderer_dry_run_only"),
            "static_ops_only": dry_run.get("static_ops_only"),
            "not_page_wiring": dry_run.get("not_page_wiring"),
            "not_runtime_wiring": dry_run.get("not_runtime_wiring"),
            "not_ui_rendering": dry_run.get("not_ui_rendering"),
            "no_command_buttons": dry_run.get("no_command_buttons"),
            "no_forms": dry_run.get("no_forms"),
            **{"no_" + "session" + "_state": dry_run.get("no_" + "session" + "_state")},
            "no_callbacks": dry_run.get("no_callbacks"),
            "autotrade_page_runtime_wired": page_wired,
        },
        "safety": {
            "read_only_diagnostic": True,
            "renderer_dry_run_packet_only": True,
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
    result = run_autotrade_read_only_status_page_renderer_component_dry_run_no_page_wiring()
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True, default=str))
    return 0 if result.get("ok") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
