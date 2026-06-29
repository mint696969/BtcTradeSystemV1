# path: ./tools/test_phase4a_prediction_system_ps_q24d_autotrade_read_only_status_page_display_packet_design.py
# desc: Focused pytest guard for PS-Q24D AutoTrade read-only status page display packet design.

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

from tools.diagnose_phase4a_prediction_system_ps_q24d_autotrade_read_only_status_page_display_packet_design import (  # noqa: E402
    DIAGNOSTIC_VERSION,
    run_autotrade_read_only_status_page_display_packet_design,
)

SPEC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q24D_AUTOTRADE_READ_ONLY_STATUS_PAGE_DISPLAY_PACKET_DESIGN_2026-06-29.md"
MODULE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/autotrade_prediction_status_page_display_section.py"
DIAG = REPO_ROOT / "tools/diagnose_phase4a_prediction_system_ps_q24d_autotrade_read_only_status_page_display_packet_design.py"
AUTOTRADE_PAGE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/autotrade_page.py"


def test_spec_declares_q24d_page_section_packet_contract() -> None:
    text = SPEC.read_text(encoding="utf-8-sig")
    for marker in (
        "ps_q24d_autotrade_read_only_status_page_display_packet_design=true",
        "base_reentry=PS_Q24C_AUTOTRADE_READ_ONLY_STATUS_PAGE_PLANNING_NO_RUNTIME_WIRING_DONE",
        "q24c_page_planning_ready=true",
        "page_display_section_packet_component_added=true",
        "autotrade_page_py_modified=false",
        "autotrade_prediction_status_display_wired_to_page=false",
        "page_section_packet_read_only=true",
        "page_section_packet_planning_only=true",
        "page_section_packet_not_page_wiring=true",
        "page_section_packet_not_runtime_wiring=true",
        "page_section_packet_not_ui_rendering=true",
        "page_section_packet_no_command_buttons=true",
        "scheduler_action_changed=false",
        "runtime_artifact_write_changed=false",
        "shadow_decision_append=false",
        "mode_apply=false",
        "ledger_append=false",
        "broker_autotrade=false",
        "parameter_apply=false",
    ):
        assert marker in text, marker


def test_live_q24d_page_section_packet_design_ready() -> None:
    result = run_autotrade_read_only_status_page_display_packet_design()
    assert result["ok"] is True
    assert result["diagnostic_version"] == DIAGNOSTIC_VERSION
    assert result["ready"] is True, result["blockers"]
    assert result["blockers"] == []
    assert result["q24c_page_planning"]["ready"] is True
    packet = result["page_section_packet"]
    assert packet["section_type"] == "autotrade_prediction_status_page_display_section_packet"
    assert packet["section_state"] == "ok"
    assert packet["section_available"] is True
    assert packet["planned_page"] == "btcts_next/src/btcts/apps/operator_ui/views/autotrade_page.py"
    assert packet["display_state"] == "ok"
    assert packet["preview_action"] == "WATCH"
    assert packet["preview_bias"] == "neutral"
    assert "planning_only=true" in packet["snapshot_lines"]
    assert "not_page_wiring=true" in packet["snapshot_lines"]
    assert "not_runtime_wiring=true" in packet["snapshot_lines"]
    assert "not_ui_rendering=true" in packet["snapshot_lines"]
    assert "no_command_buttons=true" in packet["snapshot_lines"]
    assert packet["planning_only"] is True
    assert packet["not_page_wiring"] is True
    assert packet["not_runtime_wiring"] is True
    assert packet["not_ui_rendering"] is True
    assert packet["no_command_buttons"] is True
    assert packet["autotrade_page_runtime_wired"] is False
    safety = result["safety"]
    assert safety["read_only_diagnostic"] is True
    assert safety["component_packet_design_only"] is True
    assert safety["autotrade_page_modified"] is False
    assert safety["ui_runtime_wiring_changed"] is False
    assert safety["ui_command_buttons_enabled"] is False
    assert safety["streamlit_rendering_added"] is False
    assert safety["runtime_artifact_write_enabled"] is False
    assert safety["scheduler_action_changed"] is False
    assert safety["shadow_decision_append_allowed"] is False
    assert safety["mode_apply_allowed"] is False
    assert safety["command_or_approval_ledger_allowed"] is False
    assert safety["parameter_apply_allowed"] is False
    assert safety["broker_private_api_allowed"] is False
    assert safety["autotrade_trigger_allowed"] is False
    assert safety["would_send_to_broker"] is False


def test_autotrade_page_is_not_modified_or_wired_by_q24d_slice() -> None:
    proc = subprocess.run(["git", "status", "--short", "--untracked-files=all"], cwd=REPO_ROOT, text=True, capture_output=True, check=True)
    dirty = proc.stdout.replace(chr(92), "/")
    assert "btcts_next/src/btcts/apps/operator_ui/views/autotrade_page.py" not in dirty
    page_text = AUTOTRADE_PAGE.read_text(encoding="utf-8")
    assert "autotrade_prediction_status_page_display_section" not in page_text
    assert "build_autotrade_prediction_status_page_display_section_packet" not in page_text


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
    test_spec_declares_q24d_page_section_packet_contract()
    test_live_q24d_page_section_packet_design_ready()
    test_autotrade_page_is_not_modified_or_wired_by_q24d_slice()
    test_component_and_diagnostic_are_no_write_no_runtime_wiring_no_broker()
    print(json.dumps({"ok": True}, ensure_ascii=False))
