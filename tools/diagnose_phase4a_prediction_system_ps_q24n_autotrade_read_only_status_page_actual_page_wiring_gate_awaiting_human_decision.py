# path: ./tools/diagnose_phase4a_prediction_system_ps_q24n_autotrade_read_only_status_page_actual_page_wiring_gate_awaiting_human_decision.py
# desc: No-write diagnostic for awaiting human gate decision before AutoTrade prediction status page wiring.

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

from btcts.apps.operator_ui.components.autotrade_prediction_status_page_gate_awaiting_human_decision import (  # noqa: E402
    AUTOTRADE_PREDICTION_STATUS_PAGE_GATE_AWAITING_HUMAN_DECISION_CONTRACT,
    build_autotrade_prediction_status_page_gate_awaiting_human_decision_packet,
)
from btcts.autotrade.prediction_preview_status import AutoTradePredictionPreviewStatus  # noqa: E402
from tools.diagnose_phase4a_prediction_system_ps_q24m_autotrade_read_only_status_page_actual_page_wiring_explicit_human_gate_decision_required import (  # noqa: E402
    run_autotrade_read_only_status_page_actual_page_wiring_explicit_human_gate_decision_required,
)

DIAGNOSTIC_VERSION = "prediction_warroom.ps_q24n_autotrade_read_only_status_page_actual_page_wiring_gate_awaiting_human_decision.v1"
AUTOTRADE_PAGE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/autotrade_page.py"
GATE_MODULE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/autotrade_prediction_status_page_gate_awaiting_human_decision.py"
GATE_MODULE_REF = "autotrade_prediction_status_page_gate_awaiting_human_decision"
GATE_BUILDER_REF = "build_autotrade_prediction_status_page_gate_awaiting_human_decision_packet"


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _git(args: list[str]) -> str:
    proc = subprocess.run(["git", *args], cwd=REPO_ROOT, text=True, capture_output=True, check=False)
    return proc.stdout.strip()


def _sample_status() -> AutoTradePredictionPreviewStatus:
    return AutoTradePredictionPreviewStatus(
        status_id="ps_q24n_gate_awaiting_human_decision_sample_status",
        generated_at="2026-06-29T00:00:00Z",
        status_state="ok",
        preview_id="ps_q24n_preview",
        readiness_id="ps_q24n_readiness",
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


def run_autotrade_read_only_status_page_actual_page_wiring_gate_awaiting_human_decision() -> dict[str, Any]:
    branch = _git(["rev-parse", "--abbrev-ref", "HEAD"])
    head = _git(["rev-parse", "--short", "HEAD"])
    status_short = _git(["status", "--short", "--untracked-files=all"])
    q24m = run_autotrade_read_only_status_page_actual_page_wiring_explicit_human_gate_decision_required()
    page_text = AUTOTRADE_PAGE.read_text(encoding="utf-8") if AUTOTRADE_PAGE.exists() else ""
    module_text = GATE_MODULE.read_text(encoding="utf-8") if GATE_MODULE.exists() else ""
    packet = build_autotrade_prediction_status_page_gate_awaiting_human_decision_packet(_sample_status(), autotrade_page_text=page_text)

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

    page_wired = GATE_MODULE_REF in page_text or GATE_BUILDER_REF in page_text
    blockers: list[str] = []
    if q24m.get("ready") is not True:
        blockers.append("q24m_explicit_human_gate_decision_required_ready_required")
    for item in list(q24m.get("blockers") or []):
        blockers.append(f"q24m:{item}")
    if AUTOTRADE_PREDICTION_STATUS_PAGE_GATE_AWAITING_HUMAN_DECISION_CONTRACT.get("awaiting_gate_type") != "autotrade_prediction_status_page_actual_page_wiring_gate_awaiting_human_decision_packet":
        blockers.append("gate_awaiting_human_decision_contract_type_required")
    if packet.get("gate_awaiting_human_decision_ready") is not True:
        blockers.append("gate_awaiting_human_decision_ready_required")
    for marker in ("gate_awaiting_human_decision_packet_only=true", "explicit_human_gate_required=true", "explicit_human_gate_decision_required=true", "gate_awaiting_human_decision=true", "human_gate_grant_record_present=false", "human_gate_decision=not_granted", "human_gate_granted=false", "page_change_authorized=false", "actual_page_wiring_allowed=false", "must_stop_before_autotrade_page_edit=true", "blocked_until_human_gate=true", "not_page_wiring=true", "not_runtime_wiring=true", "not_ui_rendering=true", "no_command_buttons=true", "no_forms=true", "no_" + "session" + "_state=true", "no_callbacks=true"):
        if marker not in tuple(packet.get("snapshot_lines") or ()): 
            blockers.append(f"gate_awaiting_human_decision_snapshot_marker_required:{marker}")
    if packet.get("gate_awaiting_human_decision") is not True or packet.get("explicit_human_gate_decision_required") is not True:
        blockers.append("awaiting_human_decision_stop_marker_required")
    if packet.get("human_gate_grant_record_present") is not False:
        blockers.append("human_gate_grant_record_must_be_absent")
    if packet.get("human_gate_decision") != "not_granted" or packet.get("human_gate_granted") is not False:
        blockers.append("human_gate_must_not_be_granted")
    if packet.get("page_change_authorized") is not False or packet.get("actual_page_wiring_allowed") is not False:
        blockers.append("page_wiring_must_not_be_authorized")
    if packet.get("must_stop_before_autotrade_page_edit") is not True or packet.get("blocked_until_human_gate") is not True:
        blockers.append("must_stop_before_page_edit_required")
    if packet.get("gate_awaiting_human_decision_packet_only") is not True or packet.get("not_page_wiring") is not True:
        blockers.append("gate_awaiting_human_decision_not_page_wiring_required")
    if packet.get("not_runtime_wiring") is not True or packet.get("not_ui_rendering") is not True:
        blockers.append("gate_awaiting_human_decision_no_runtime_ui_required")
    if packet.get("no_command_buttons") is not True or packet.get("no_forms") is not True or packet.get("no_" + "session" + "_state") is not True or packet.get("no_callbacks") is not True:
        blockers.append("gate_awaiting_human_decision_no_controls_required")
    if packet.get("autotrade_page_edit_performed_by_this_slice") is not False or packet.get("page_runtime_mount_performed_by_this_slice") is not False:
        blockers.append("gate_awaiting_human_decision_page_edit_or_mount_must_be_false")
    if packet.get("actual_ui_rendering_performed_by_this_slice") is not False or packet.get("command_surface_changed_by_this_slice") is not False:
        blockers.append("gate_awaiting_human_decision_render_or_command_change_must_be_false")
    if not _all_false(packet, execution_flags):
        blockers.append("gate_awaiting_human_decision_execution_flags_false_required")
    if page_wired:
        blockers.append("autotrade_page_gate_awaiting_human_decision_wiring_unexpected")
    for token in forbidden_module_tokens:
        if token in module_text:
            blockers.append(f"gate_awaiting_human_decision_module_forbidden_token:{token}")

    ready = not blockers
    return {
        "ok": True,
        "diagnostic_version": DIAGNOSTIC_VERSION,
        "generated_at": _utc_now(),
        "repo": {"branch": branch, "head": head, "status_short": status_short},
        "ready": ready,
        "state": "ps_q24n_autotrade_status_page_gate_awaiting_human_decision_ready" if ready else "ps_q24n_autotrade_status_page_gate_awaiting_human_decision_blocked",
        "blockers": blockers,
        "q24m_explicit_human_gate_decision_required": {
            "ready": q24m.get("ready"),
            "diagnostic_version": q24m.get("diagnostic_version"),
            "explicit_human_gate_decision_required": q24m.get("explicit_human_gate_decision_required"),
            "safety": q24m.get("safety"),
        },
        "gate_awaiting_human_decision": {
            "awaiting_gate_type": packet.get("awaiting_gate_type"),
            "gate_awaiting_human_decision_ready": packet.get("gate_awaiting_human_decision_ready"),
            "gate_awaiting_human_decision_packet_available": packet.get("gate_awaiting_human_decision_packet_available"),
            "explicit_human_gate_decision_required_ready": packet.get("explicit_human_gate_decision_required_ready"),
            "explicit_human_gate_required": packet.get("explicit_human_gate_required"),
            "explicit_human_gate_decision_required": packet.get("explicit_human_gate_decision_required"),
            "gate_awaiting_human_decision": packet.get("gate_awaiting_human_decision"),
            "human_gate_grant_record_present": packet.get("human_gate_grant_record_present"),
            "human_gate_decision": packet.get("human_gate_decision"),
            "human_gate_granted": packet.get("human_gate_granted"),
            "page_change_authorized": packet.get("page_change_authorized"),
            "actual_page_wiring_allowed": packet.get("actual_page_wiring_allowed"),
            "must_stop_before_autotrade_page_edit": packet.get("must_stop_before_autotrade_page_edit"),
            "blocked_until_human_gate": packet.get("blocked_until_human_gate"),
            "decision_source": packet.get("decision_source"),
            "planned_helper_name": packet.get("planned_helper_name"),
            "planned_call_site": packet.get("planned_call_site"),
            "target_page_currently_contains_planned_import": packet.get("target_page_currently_contains_planned_import"),
            "target_page_currently_contains_planned_helper": packet.get("target_page_currently_contains_planned_helper"),
            "target_page_currently_contains_planned_builder": packet.get("target_page_currently_contains_planned_builder"),
            "autotrade_page_contains_awaiting_gate_module": packet.get("autotrade_page_contains_awaiting_gate_module"),
            "autotrade_page_edit_performed_by_this_slice": packet.get("autotrade_page_edit_performed_by_this_slice"),
            "page_runtime_mount_performed_by_this_slice": packet.get("page_runtime_mount_performed_by_this_slice"),
            "actual_ui_rendering_performed_by_this_slice": packet.get("actual_ui_rendering_performed_by_this_slice"),
            "command_surface_changed_by_this_slice": packet.get("command_surface_changed_by_this_slice"),
            "snapshot_lines": packet.get("snapshot_lines"),
            "gate_awaiting_human_decision_packet_only": packet.get("gate_awaiting_human_decision_packet_only"),
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
            "gate_awaiting_human_decision_packet_only": True,
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
    result = run_autotrade_read_only_status_page_actual_page_wiring_gate_awaiting_human_decision()
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True, default=str))
    return 0 if result.get("ok") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
