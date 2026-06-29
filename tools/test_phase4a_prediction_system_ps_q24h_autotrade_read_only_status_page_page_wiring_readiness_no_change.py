# path: ./tools/test_phase4a_prediction_system_ps_q24h_autotrade_read_only_status_page_page_wiring_readiness_no_change.py
# desc: Focused pytest guard for PS-Q24H AutoTrade read-only status page page-wiring readiness without page change.

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

from tools.diagnose_phase4a_prediction_system_ps_q24h_autotrade_read_only_status_page_page_wiring_readiness_no_change import (  # noqa: E402
    DIAGNOSTIC_VERSION,
    run_autotrade_read_only_status_page_page_wiring_readiness_no_change,
)

SPEC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q24H_AUTOTRADE_READ_ONLY_STATUS_PAGE_PAGE_WIRING_READINESS_NO_CHANGE_2026-06-29.md"
MODULE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/autotrade_prediction_status_page_page_wiring_readiness.py"
DIAG = REPO_ROOT / "tools/diagnose_phase4a_prediction_system_ps_q24h_autotrade_read_only_status_page_page_wiring_readiness_no_change.py"
AUTOTRADE_PAGE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/autotrade_page.py"


def test_spec_declares_q24h_page_wiring_readiness_contract() -> None:
    text = SPEC.read_text(encoding="utf-8-sig")
    for marker in (
        "ps_q24h_autotrade_read_only_status_page_page_wiring_readiness_no_change=true",
        "base_reentry=PS_Q24G_AUTOTRADE_READ_ONLY_STATUS_PAGE_ACTUAL_RENDER_WIRING_PLAN_NO_PAGE_CHANGE_DONE",
        "q24g_actual_render_wiring_plan_ready=true",
        "page_wiring_readiness_packet_component_added=true",
        "autotrade_page_py_modified=false",
        "autotrade_prediction_status_page_wiring_applied=false",
        "page_wiring_readiness_packet_read_only=true",
        "page_wiring_readiness_packet_only=true",
        "page_wiring_readiness_requires_future_explicit_page_change_gate=true",
        "page_wiring_readiness_packet_not_page_wiring=true",
        "page_wiring_readiness_packet_not_runtime_wiring=true",
        "page_wiring_readiness_packet_not_ui_rendering=true",
        "page_wiring_readiness_packet_no_command_buttons=true",
        "page_wiring_readiness_packet_no_forms=true",
        "page_wiring_readiness_packet_no_session_state=true",
        "page_wiring_readiness_packet_no_callbacks=true",
        "scheduler_action_changed=false",
        "runtime_artifact_write_changed=false",
        "shadow_decision_append=false",
        "mode_apply=false",
        "ledger_append=false",
        "broker_autotrade=false",
        "parameter_apply=false",
    ):
        assert marker in text, marker


def test_live_q24h_page_wiring_readiness_no_change_ready() -> None:
    result = run_autotrade_read_only_status_page_page_wiring_readiness_no_change()
    assert result["ok"] is True
    assert result["diagnostic_version"] == DIAGNOSTIC_VERSION
    assert result["ready"] is True, result["blockers"]
    assert result["blockers"] == []
    assert result["q24g_actual_render_wiring_plan"]["ready"] is True
    packet = result["page_wiring_readiness"]
    assert packet["readiness_type"] == "autotrade_prediction_status_page_page_wiring_readiness_packet"
    assert packet["readiness_ready"] is True
    assert packet["page_wiring_readiness_available"] is True
    assert packet["candidate_anchor_present"] is True
    assert packet["runtime_health_section_present"] is True
    assert packet["render_json_helper_present"] is True
    assert packet["future_import_ready"] is True
    assert packet["future_call_ready"] is True
    assert packet["required_future_gate_before_page_edit"] is True
    assert packet["autotrade_page_edit_performed_by_this_slice"] is False
    assert packet["page_runtime_mount_performed_by_this_slice"] is False
    assert packet["actual_ui_rendering_performed_by_this_slice"] is False
    assert packet["command_surface_changed_by_this_slice"] is False
    assert "page_wiring_readiness_only=true" in packet["snapshot_lines"]
    assert "requires_future_explicit_page_change_gate=true" in packet["snapshot_lines"]
    assert "not_page_wiring=true" in packet["snapshot_lines"]
    assert "not_runtime_wiring=true" in packet["snapshot_lines"]
    assert "not_ui_rendering=true" in packet["snapshot_lines"]
    assert "no_command_buttons=true" in packet["snapshot_lines"]
    assert "no_forms=true" in packet["snapshot_lines"]
    assert "no_session_state=true" in packet["snapshot_lines"]
    assert "no_callbacks=true" in packet["snapshot_lines"]
    assert packet["page_wiring_readiness_only"] is True
    assert packet["requires_future_explicit_page_change_gate"] is True
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
    assert safety["page_wiring_readiness_packet_only"] is True
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


def test_autotrade_page_is_not_modified_or_wired_by_q24h_slice() -> None:
    proc = subprocess.run(["git", "status", "--short", "--untracked-files=all"], cwd=REPO_ROOT, text=True, capture_output=True, check=True)
    dirty = proc.stdout.replace(chr(92), "/")
    assert "btcts_next/src/btcts/apps/operator_ui/views/autotrade_page.py" not in dirty
    page_text = AUTOTRADE_PAGE.read_text(encoding="utf-8")
    assert "autotrade_prediction_status_page_page_wiring_readiness" not in page_text
    assert "build_autotrade_prediction_status_page_page_wiring_readiness_packet" not in page_text


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
    test_spec_declares_q24h_page_wiring_readiness_contract()
    test_live_q24h_page_wiring_readiness_no_change_ready()
    test_autotrade_page_is_not_modified_or_wired_by_q24h_slice()
    test_component_and_diagnostic_are_no_write_no_runtime_wiring_no_broker()
    print(json.dumps({"ok": True}, ensure_ascii=False))
