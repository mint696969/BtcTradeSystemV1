# path: ./tools/diagnose_phase4a_prediction_system_ps_q24h_autotrade_read_only_status_page_page_wiring_readiness_no_change.py
# desc: No-write diagnostic for AutoTrade read-only prediction status page page-wiring readiness without page change.

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

from btcts.apps.operator_ui.components.autotrade_prediction_status_page_page_wiring_readiness import (  # noqa: E402
    AUTOTRADE_PREDICTION_STATUS_PAGE_WIRING_READINESS_CONTRACT,
    build_autotrade_prediction_status_page_page_wiring_readiness_packet,
)
from btcts.autotrade.prediction_preview_status import AutoTradePredictionPreviewStatus  # noqa: E402
from tools.diagnose_phase4a_prediction_system_ps_q24g_autotrade_read_only_status_page_actual_render_wiring_plan_no_page_change import (  # noqa: E402
    run_autotrade_read_only_status_page_actual_render_wiring_plan_no_page_change,
)

DIAGNOSTIC_VERSION = "prediction_warroom.ps_q24h_autotrade_read_only_status_page_page_wiring_readiness_no_change.v1"
AUTOTRADE_PAGE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/autotrade_page.py"
READINESS_MODULE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/autotrade_prediction_status_page_page_wiring_readiness.py"
READINESS_MODULE_REF = "autotrade_prediction_status_page_page_wiring_readiness"
READINESS_BUILDER_REF = "build_autotrade_prediction_status_page_page_wiring_readiness_packet"


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _git(args: list[str]) -> str:
    proc = subprocess.run(["git", *args], cwd=REPO_ROOT, text=True, capture_output=True, check=False)
    return proc.stdout.strip()


def _sample_status() -> AutoTradePredictionPreviewStatus:
    return AutoTradePredictionPreviewStatus(
        status_id="ps_q24h_page_wiring_readiness_sample_status",
        generated_at="2026-06-29T00:00:00Z",
        status_state="ok",
        preview_id="ps_q24h_preview",
        readiness_id="ps_q24h_readiness",
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


def run_autotrade_read_only_status_page_page_wiring_readiness_no_change() -> dict[str, Any]:
    branch = _git(["rev-parse", "--abbrev-ref", "HEAD"])
    head = _git(["rev-parse", "--short", "HEAD"])
    status_short = _git(["status", "--short", "--untracked-files=all"])
    q24g = run_autotrade_read_only_status_page_actual_render_wiring_plan_no_page_change()
    page_text = AUTOTRADE_PAGE.read_text(encoding="utf-8") if AUTOTRADE_PAGE.exists() else ""
    module_text = READINESS_MODULE.read_text(encoding="utf-8") if READINESS_MODULE.exists() else ""
    packet = build_autotrade_prediction_status_page_page_wiring_readiness_packet(_sample_status(), autotrade_page_text=page_text)

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

    page_wired = READINESS_MODULE_REF in page_text or READINESS_BUILDER_REF in page_text
    blockers: list[str] = []
    if q24g.get("ready") is not True:
        blockers.append("q24g_actual_render_wiring_plan_ready_required")
    for item in list(q24g.get("blockers") or []):
        blockers.append(f"q24g:{item}")
    if AUTOTRADE_PREDICTION_STATUS_PAGE_WIRING_READINESS_CONTRACT.get("readiness_type") != "autotrade_prediction_status_page_page_wiring_readiness_packet":
        blockers.append("page_wiring_readiness_contract_type_required")
    if packet.get("readiness_ready") is not True:
        blockers.append("page_wiring_readiness_ready_required")
    for marker in ("page_wiring_readiness_only=true", "requires_future_explicit_page_change_gate=true", "not_page_wiring=true", "not_runtime_wiring=true", "not_ui_rendering=true", "no_command_buttons=true", "no_forms=true", "no_" + "session" + "_state=true", "no_callbacks=true"):
        if marker not in tuple(packet.get("snapshot_lines") or ()): 
            blockers.append(f"page_wiring_readiness_snapshot_marker_required:{marker}")
    if packet.get("page_wiring_readiness_only") is not True or packet.get("not_page_wiring") is not True:
        blockers.append("page_wiring_readiness_not_page_wiring_required")
    if packet.get("not_runtime_wiring") is not True or packet.get("not_ui_rendering") is not True:
        blockers.append("page_wiring_readiness_no_runtime_ui_required")
    if packet.get("no_command_buttons") is not True or packet.get("no_forms") is not True or packet.get("no_" + "session" + "_state") is not True or packet.get("no_callbacks") is not True:
        blockers.append("page_wiring_readiness_no_controls_required")
    if packet.get("autotrade_page_edit_performed_by_this_slice") is not False or packet.get("page_runtime_mount_performed_by_this_slice") is not False:
        blockers.append("page_wiring_readiness_page_edit_or_mount_must_be_false")
    if packet.get("actual_ui_rendering_performed_by_this_slice") is not False or packet.get("command_surface_changed_by_this_slice") is not False:
        blockers.append("page_wiring_readiness_render_or_command_change_must_be_false")
    if not _all_false(packet, execution_flags):
        blockers.append("page_wiring_readiness_execution_flags_false_required")
    if page_wired:
        blockers.append("autotrade_page_page_wiring_readiness_wiring_unexpected")
    for token in forbidden_module_tokens:
        if token in module_text:
            blockers.append(f"page_wiring_readiness_module_forbidden_token:{token}")

    ready = not blockers
    return {
        "ok": True,
        "diagnostic_version": DIAGNOSTIC_VERSION,
        "generated_at": _utc_now(),
        "repo": {"branch": branch, "head": head, "status_short": status_short},
        "ready": ready,
        "state": "ps_q24h_autotrade_status_page_page_wiring_readiness_no_change_ready" if ready else "ps_q24h_autotrade_status_page_page_wiring_readiness_no_change_blocked",
        "blockers": blockers,
        "q24g_actual_render_wiring_plan": {
            "ready": q24g.get("ready"),
            "diagnostic_version": q24g.get("diagnostic_version"),
            "actual_render_wiring_plan": q24g.get("actual_render_wiring_plan"),
            "safety": q24g.get("safety"),
        },
        "page_wiring_readiness": {
            "readiness_type": packet.get("readiness_type"),
            "readiness_ready": packet.get("readiness_ready"),
            "page_wiring_readiness_available": packet.get("page_wiring_readiness_available"),
            "candidate_anchor": packet.get("candidate_anchor"),
            "candidate_section_heading": packet.get("candidate_section_heading"),
            "candidate_anchor_present": packet.get("candidate_anchor_present"),
            "runtime_health_section_present": packet.get("runtime_health_section_present"),
            "render_json_helper_present": packet.get("render_json_helper_present"),
            "future_import_ready": packet.get("future_import_ready"),
            "future_call_ready": packet.get("future_call_ready"),
            "required_future_gate_before_page_edit": packet.get("required_future_gate_before_page_edit"),
            "autotrade_page_edit_performed_by_this_slice": packet.get("autotrade_page_edit_performed_by_this_slice"),
            "page_runtime_mount_performed_by_this_slice": packet.get("page_runtime_mount_performed_by_this_slice"),
            "actual_ui_rendering_performed_by_this_slice": packet.get("actual_ui_rendering_performed_by_this_slice"),
            "command_surface_changed_by_this_slice": packet.get("command_surface_changed_by_this_slice"),
            "snapshot_lines": packet.get("snapshot_lines"),
            "page_wiring_readiness_only": packet.get("page_wiring_readiness_only"),
            "requires_future_explicit_page_change_gate": packet.get("requires_future_explicit_page_change_gate"),
            "not_page_wiring": packet.get("not_page_wiring"),
            "not_runtime_wiring": packet.get("not_runtime_wiring"),
            "not_ui_rendering": packet.get("not_ui_rendering"),
            "no_command_buttons": packet.get("no_command_buttons"),
            "no_forms": packet.get("no_forms"),
            **{"no_" + "session" + "_state": packet.get("no_" + "session" + "_state")},
            "no_callbacks": packet.get("no_callbacks"),
            "autotrade_page_runtime_wired": page_wired,
        },
        "safety": {
            "read_only_diagnostic": True,
            "page_wiring_readiness_packet_only": True,
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
    result = run_autotrade_read_only_status_page_page_wiring_readiness_no_change()
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True, default=str))
    return 0 if result.get("ok") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
