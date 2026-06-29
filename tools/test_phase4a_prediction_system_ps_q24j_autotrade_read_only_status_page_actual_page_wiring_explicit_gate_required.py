# path: ./tools/test_phase4a_prediction_system_ps_q24j_autotrade_read_only_status_page_actual_page_wiring_explicit_gate_required.py
# desc: Focused pytest guard for PS-Q24J actual page wiring patch plan with explicit gate required.

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "btcts_next" / "src"
for candidate in (REPO_ROOT, SRC_ROOT):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

from tools.diagnose_phase4a_prediction_system_ps_q24j_autotrade_read_only_status_page_actual_page_wiring_explicit_gate_required import (  # noqa: E402
    DIAGNOSTIC_VERSION,
    run_autotrade_read_only_status_page_actual_page_wiring_explicit_gate_required,
)

SPEC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q24J_AUTOTRADE_READ_ONLY_STATUS_PAGE_ACTUAL_PAGE_WIRING_EXPLICIT_GATE_REQUIRED_2026-06-29.md"
MODULE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/autotrade_prediction_status_page_actual_page_wiring_patch_plan.py"
DIAG = REPO_ROOT / "tools/diagnose_phase4a_prediction_system_ps_q24j_autotrade_read_only_status_page_actual_page_wiring_explicit_gate_required.py"
AUTOTRADE_PAGE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/autotrade_page.py"


def test_spec_declares_q24j_actual_page_wiring_patch_plan_contract() -> None:
    text = SPEC.read_text(encoding="utf-8-sig")
    for marker in (
        "ps_q24j_autotrade_read_only_status_page_actual_page_wiring_explicit_gate_required=true",
        "base_reentry=PS_Q24I_AUTOTRADE_READ_ONLY_STATUS_PAGE_RENDERER_ACTUAL_PAGE_WIRING_GATE_READINESS_DONE",
        "q24i_page_change_gate_readiness_ready=true",
        "actual_page_wiring_patch_plan_packet_component_added=true",
        "autotrade_page_py_modified=false",
        "autotrade_prediction_status_page_wiring_applied=false",
        "actual_page_wiring_patch_plan_packet_read_only=true",
        "actual_page_wiring_patch_plan_packet_only=true",
        "explicit_page_change_gate_required=true",
        "page_change_gate_granted=false",
        "page_change_authorized=false",
        "page_patch_allowed_by_this_slice=false",
        "blocked_until_human_gate=true",
        "actual_page_wiring_patch_plan_packet_not_page_wiring=true",
        "actual_page_wiring_patch_plan_packet_not_runtime_wiring=true",
        "actual_page_wiring_patch_plan_packet_not_ui_rendering=true",
        "actual_page_wiring_patch_plan_packet_no_command_buttons=true",
        "actual_page_wiring_patch_plan_packet_no_forms=true",
        "actual_page_wiring_patch_plan_packet_no_session_state=true",
        "actual_page_wiring_patch_plan_packet_no_callbacks=true",
        "scheduler_action_changed=false",
        "runtime_artifact_write_changed=false",
        "shadow_decision_append=false",
        "mode_apply=false",
        "ledger_append=false",
        "broker_autotrade=false",
        "parameter_apply=false",
    ):
        assert marker in text, marker


def test_live_q24j_actual_page_wiring_patch_plan_ready_gate_closed() -> None:
    result = run_autotrade_read_only_status_page_actual_page_wiring_explicit_gate_required()
    assert result["ok"] is True
    assert result["diagnostic_version"] == DIAGNOSTIC_VERSION
    assert result["ready"] is True, result["blockers"]
    assert result["blockers"] == []
    assert result["q24i_page_change_gate_readiness"]["ready"] is True
    packet = result["actual_page_wiring_patch_plan"]
    assert packet["patch_plan_type"] == "autotrade_prediction_status_page_actual_page_wiring_patch_plan_packet"
    assert packet["patch_plan_ready"] is True
    assert packet["actual_page_wiring_patch_plan_available"] is True
    assert packet["planned_helper_name"] == "_render_prediction_status_read_only_preview"
    assert packet["planned_call_site"] == "_render_runtime_health_status"
    assert packet["explicit_page_change_gate_required"] is True
    assert packet["page_change_gate_granted"] is False
    assert packet["page_change_authorized"] is False
    assert packet["page_patch_allowed_by_this_slice"] is False
    assert packet["blocked_until_human_gate"] is True
    assert packet["target_page_currently_contains_planned_import"] is False
    assert packet["target_page_currently_contains_planned_helper"] is False
    assert packet["target_page_currently_contains_planned_builder"] is False
    assert packet["target_page_diff_performed_by_this_slice"] is False
    assert packet["autotrade_page_edit_performed_by_this_slice"] is False
    assert packet["page_runtime_mount_performed_by_this_slice"] is False
    assert packet["actual_ui_rendering_performed_by_this_slice"] is False
    assert packet["command_surface_changed_by_this_slice"] is False
    assert "actual_page_wiring_patch_plan_only=true" in packet["snapshot_lines"]
    assert "explicit_page_change_gate_required=true" in packet["snapshot_lines"]
    assert "page_change_gate_granted=false" in packet["snapshot_lines"]
    assert "page_change_authorized=false" in packet["snapshot_lines"]
    assert "page_patch_allowed_by_this_slice=false" in packet["snapshot_lines"]
    assert "blocked_until_human_gate=true" in packet["snapshot_lines"]
    assert "not_page_wiring=true" in packet["snapshot_lines"]
    assert "not_runtime_wiring=true" in packet["snapshot_lines"]
    assert "not_ui_rendering=true" in packet["snapshot_lines"]
    assert "no_command_buttons=true" in packet["snapshot_lines"]
    assert "no_forms=true" in packet["snapshot_lines"]
    assert "no_session_state=true" in packet["snapshot_lines"]
    assert "no_callbacks=true" in packet["snapshot_lines"]
    assert packet["actual_page_wiring_patch_plan_only"] is True
    assert packet["not_page_wiring"] is True
    assert packet["not_runtime_wiring"] is True
    assert packet["not_ui_rendering"] is True
    assert packet["no_command_buttons"] is True
    assert packet["no_forms"] is True
    assert packet["no_session_state"] is True
    assert packet["no_callbacks"] is True
    assert packet["autotrade_page_runtime_wired"] is False
    safety = result["safety"]
    assert safety["read_only_diagnostic"] is True
    assert safety["actual_page_wiring_patch_plan_packet_only"] is True
    assert safety["autotrade_page_modified"] is False
    assert safety["ui_runtime_wiring_changed"] is False
    assert safety["ui_command_buttons_enabled"] is False
    assert safety["ui_rendering_added"] is False
    assert safety["runtime_artifact_write_enabled"] is False
    assert safety["scheduler_action_changed"] is False
    assert safety["shadow_decision_append_allowed"] is False
    assert safety["mode_apply_allowed"] is False
    assert safety["command_or_approval_ledger_allowed"] is False
    assert safety["parameter_apply_allowed"] is False
    assert safety["broker_private_api_allowed"] is False
    assert safety["autotrade_trigger_allowed"] is False
    assert safety["would_send_to_broker"] is False


def test_autotrade_page_is_not_modified_or_wired_by_q24j_slice() -> None:
    proc = subprocess.run(["git", "status", "--short", "--untracked-files=all"], cwd=REPO_ROOT, text=True, capture_output=True, check=True)
    dirty = proc.stdout.replace(chr(92), "/")
    assert "btcts_next/src/btcts/apps/operator_ui/views/autotrade_page.py" not in dirty
    page_text = AUTOTRADE_PAGE.read_text(encoding="utf-8")
    assert "autotrade_prediction_status_page_actual_page_wiring_patch_plan" not in page_text
    assert "build_autotrade_prediction_status_page_actual_page_wiring_patch_plan_packet" not in page_text
    assert "_render_prediction_status_read_only_preview" not in page_text


def test_component_and_diagnostic_are_no_write_no_runtime_wiring_no_broker() -> None:
    for path in (MODULE, DIAG):
        text = path.read_text(encoding="utf-8")
        for forbidden in (
            "Set-ScheduledTask",
            "Enable-ScheduledTask",
            "Disable-ScheduledTask",
            "Register-ScheduledTask",
            "New-ScheduledTaskTrigger",
            "streamlit",
            "st.button",
            "st.checkbox",
            "st.form",
            "session_state",
            "append_decision_jsonl",
            "run_shadow_decision_from_snapshot",
            "submit_mode_change_command_request",
            "validate_and_append_command",
            "send_order(",
            "place_order(",
            "create_order(",
            ".write_text(",
            ".write_bytes(",
            "os.replace",
            "shutil.copy2",
        ):
            assert forbidden not in text, f"{path}: {forbidden}"


if __name__ == "__main__":
    test_spec_declares_q24j_actual_page_wiring_patch_plan_contract()
    test_live_q24j_actual_page_wiring_patch_plan_ready_gate_closed()
    test_autotrade_page_is_not_modified_or_wired_by_q24j_slice()
    test_component_and_diagnostic_are_no_write_no_runtime_wiring_no_broker()
    print(json.dumps({"ok": True}, ensure_ascii=False))
