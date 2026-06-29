# path: ./tools/test_phase4a_prediction_system_ps_q24c_autotrade_read_only_status_page_planning_no_runtime_wiring.py
# desc: Focused pytest guard for PS-Q24C AutoTrade read-only status page planning without runtime wiring.

from __future__ import annotations

import json
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "btcts_next" / "src"
for candidate in (REPO_ROOT, SRC_ROOT):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

from tools.diagnose_phase4a_prediction_system_ps_q24c_autotrade_read_only_status_page_planning_no_runtime_wiring import (  # noqa: E402
    DIAGNOSTIC_VERSION,
    run_autotrade_read_only_status_page_planning_no_runtime_wiring,
)

SPEC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q24C_AUTOTRADE_READ_ONLY_STATUS_PAGE_PLANNING_NO_RUNTIME_WIRING_2026-06-29.md"
DIAG = REPO_ROOT / "tools/diagnose_phase4a_prediction_system_ps_q24c_autotrade_read_only_status_page_planning_no_runtime_wiring.py"
AUTOTRADE_PAGE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/autotrade_page.py"


def test_spec_declares_q24c_page_planning_contract() -> None:
    text = SPEC.read_text(encoding="utf-8-sig")
    for marker in (
        "ps_q24c_autotrade_read_only_status_page_planning_no_runtime_wiring=true",
        "base_reentry=PS_Q24B_AUTOTRADE_READ_ONLY_PREDICTION_STATUS_DISPLAY_COMPAT_GUARDED",
        "q24b_display_compat_ready=true",
        "autotrade_page_existing_command_surface_acknowledged=true",
        "autotrade_prediction_status_display_not_wired_to_page=true",
        "page_modification_changed=false",
        "ui_runtime_wiring_changed=false",
        "streamlit_rendering_added=false",
        "command_buttons_added=false",
        "scheduler_action_changed=false",
        "runtime_artifact_write_changed=false",
        "shadow_decision_append=false",
        "mode_apply=false",
        "ledger_append=false",
        "broker_autotrade=false",
        "parameter_apply=false",
    ):
        assert marker in text, marker


def test_live_q24c_page_planning_ready() -> None:
    result = run_autotrade_read_only_status_page_planning_no_runtime_wiring()
    assert result["ok"] is True
    assert result["diagnostic_version"] == DIAGNOSTIC_VERSION
    assert result["ready"] is True, result["blockers"]
    assert result["blockers"] == []
    q24b = result["q24b_display_compat"]
    assert q24b["ready"] is True
    plan = result["autotrade_page_plan"]
    assert plan["page_exists"] is True
    assert plan["prediction_status_display_wired"] is False
    assert plan["prediction_status_display_module_ref_present"] is False
    assert plan["prediction_status_display_builder_ref_present"] is False
    assert plan["existing_command_surface_acknowledged"] is True
    assert plan["existing_button_count"] >= 1
    assert plan["page_modification_changed"] is False
    assert plan["ui_runtime_wiring_changed"] is False
    assert plan["streamlit_rendering_added"] is False
    assert plan["command_buttons_added"] is False
    safety = result["safety"]
    assert safety["read_only_diagnostic"] is True
    assert safety["planning_only"] is True
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


def test_autotrade_page_is_not_modified_by_q24c_slice() -> None:
    proc = __import__("subprocess").run(["git", "status", "--short", "--untracked-files=all"], cwd=REPO_ROOT, text=True, capture_output=True, check=True)
    dirty = proc.stdout.replace(chr(92), "/")
    assert "btcts_next/src/btcts/apps/operator_ui/views/autotrade_page.py" not in dirty
    assert AUTOTRADE_PAGE.exists()


def test_diagnostic_is_no_write_no_runtime_wiring_no_broker() -> None:
    text = DIAG.read_text(encoding="utf-8")
    for forbidden in (
        "Set-ScheduledTask",
        "Enable-ScheduledTask",
        "Disable-ScheduledTask",
        "Register-ScheduledTask",
        "New-ScheduledTaskTrigger",
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
        assert forbidden not in text, forbidden


if __name__ == "__main__":
    test_spec_declares_q24c_page_planning_contract()
    test_live_q24c_page_planning_ready()
    test_autotrade_page_is_not_modified_by_q24c_slice()
    test_diagnostic_is_no_write_no_runtime_wiring_no_broker()
    print(json.dumps({"ok": True}, ensure_ascii=False))
