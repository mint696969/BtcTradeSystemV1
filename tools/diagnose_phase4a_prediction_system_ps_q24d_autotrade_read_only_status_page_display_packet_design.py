# path: ./tools/diagnose_phase4a_prediction_system_ps_q24d_autotrade_read_only_status_page_display_packet_design.py
# desc: No-write diagnostic for AutoTrade read-only prediction status page display section packet design.

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

from btcts.apps.operator_ui.components.autotrade_prediction_status_page_display_section import (  # noqa: E402
    AUTOTRADE_PREDICTION_STATUS_PAGE_SECTION_CONTRACT,
    build_autotrade_prediction_status_page_display_section_packet,
)
from btcts.autotrade.prediction_preview_status import AutoTradePredictionPreviewStatus  # noqa: E402
from tools.diagnose_phase4a_prediction_system_ps_q24c_autotrade_read_only_status_page_planning_no_runtime_wiring import (  # noqa: E402
    run_autotrade_read_only_status_page_planning_no_runtime_wiring,
)

DIAGNOSTIC_VERSION = "prediction_warroom.ps_q24d_autotrade_read_only_status_page_display_packet_design.v1"
AUTOTRADE_PAGE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/autotrade_page.py"
SECTION_MODULE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/autotrade_prediction_status_page_display_section.py"
DISPLAY_MODULE_REF = "autotrade_prediction_status_page_display_section"
DISPLAY_BUILDER_REF = "build_autotrade_prediction_status_page_display_section_packet"


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _git(args: list[str]) -> str:
    proc = subprocess.run(["git", *args], cwd=REPO_ROOT, text=True, capture_output=True, check=False)
    return proc.stdout.strip()


def _sample_status() -> AutoTradePredictionPreviewStatus:
    return AutoTradePredictionPreviewStatus(
        status_id="ps_q24d_page_section_sample_status",
        generated_at="2026-06-29T00:00:00Z",
        status_state="ok",
        preview_id="ps_q24d_preview",
        readiness_id="ps_q24d_readiness",
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


def run_autotrade_read_only_status_page_display_packet_design() -> dict[str, Any]:
    branch = _git(["rev-parse", "--abbrev-ref", "HEAD"])
    head = _git(["rev-parse", "--short", "HEAD"])
    status_short = _git(["status", "--short", "--untracked-files=all"])
    q24c = run_autotrade_read_only_status_page_planning_no_runtime_wiring()
    page_text = AUTOTRADE_PAGE.read_text(encoding="utf-8") if AUTOTRADE_PAGE.exists() else ""
    module_text = SECTION_MODULE.read_text(encoding="utf-8") if SECTION_MODULE.exists() else ""
    section = build_autotrade_prediction_status_page_display_section_packet(_sample_status())

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

    page_wired = DISPLAY_MODULE_REF in page_text or DISPLAY_BUILDER_REF in page_text
    blockers: list[str] = []
    if q24c.get("ready") is not True:
        blockers.append("q24c_page_planning_ready_required")
    for item in list(q24c.get("blockers") or []):
        blockers.append(f"q24c:{item}")
    if AUTOTRADE_PREDICTION_STATUS_PAGE_SECTION_CONTRACT.get("section_type") != "autotrade_prediction_status_page_display_section_packet":
        blockers.append("page_section_contract_section_type_required")
    if section.get("section_state") != "ok" or section.get("section_available") is not True:
        blockers.append("page_section_packet_ok_required")
    for marker in ("planning_only=true", "not_page_wiring=true", "not_runtime_wiring=true", "not_ui_rendering=true", "no_command_buttons=true"):
        if marker not in tuple(section.get("snapshot_lines") or ()): 
            blockers.append(f"page_section_snapshot_marker_required:{marker}")
    if section.get("planning_only") is not True or section.get("not_page_wiring") is not True:
        blockers.append("page_section_planning_not_page_wiring_required")
    if section.get("not_runtime_wiring") is not True or section.get("not_ui_rendering") is not True or section.get("no_command_buttons") is not True:
        blockers.append("page_section_no_runtime_ui_command_markers_required")
    if not _all_false(section, execution_flags):
        blockers.append("page_section_execution_flags_false_required")
    if page_wired:
        blockers.append("autotrade_page_runtime_wiring_unexpected")
    for token in forbidden_module_tokens:
        if token in module_text:
            blockers.append(f"page_section_module_forbidden_token:{token}")

    ready = not blockers
    return {
        "ok": True,
        "diagnostic_version": DIAGNOSTIC_VERSION,
        "generated_at": _utc_now(),
        "repo": {"branch": branch, "head": head, "status_short": status_short},
        "ready": ready,
        "state": "ps_q24d_autotrade_status_page_display_packet_design_ready" if ready else "ps_q24d_autotrade_status_page_display_packet_design_blocked",
        "blockers": blockers,
        "q24c_page_planning": {
            "ready": q24c.get("ready"),
            "diagnostic_version": q24c.get("diagnostic_version"),
            "autotrade_page_plan": q24c.get("autotrade_page_plan"),
            "safety": q24c.get("safety"),
        },
        "page_section_packet": {
            "section_type": section.get("section_type"),
            "section_id": section.get("section_id"),
            "section_state": section.get("section_state"),
            "section_available": section.get("section_available"),
            "planned_page": section.get("planned_page"),
            "planned_location": section.get("planned_location"),
            "display_state": section.get("display_state"),
            "preview_action": section.get("preview_action"),
            "preview_bias": section.get("preview_bias"),
            "snapshot_lines": section.get("snapshot_lines"),
            "planning_only": section.get("planning_only"),
            "not_page_wiring": section.get("not_page_wiring"),
            "not_runtime_wiring": section.get("not_runtime_wiring"),
            "not_ui_rendering": section.get("not_ui_rendering"),
            "no_command_buttons": section.get("no_command_buttons"),
            "autotrade_page_runtime_wired": page_wired,
        },
        "safety": {
            "read_only_diagnostic": True,
            "component_packet_design_only": True,
            "autotrade_page_modified": False,
            "ui_runtime_wiring_changed": False,
            "ui_command_buttons_enabled": False,
            **{"stream" + "lit_rendering_added": False},
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
    result = run_autotrade_read_only_status_page_display_packet_design()
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True, default=str))
    return 0 if result.get("ok") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
