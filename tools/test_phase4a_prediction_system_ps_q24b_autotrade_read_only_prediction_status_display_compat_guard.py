# path: ./tools/test_phase4a_prediction_system_ps_q24b_autotrade_read_only_prediction_status_display_compat_guard.py
# desc: Focused pytest guard for PS-Q24B AutoTrade read-only prediction status display compatibility.

from __future__ import annotations

import json
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "btcts_next" / "src"
for candidate in (REPO_ROOT, SRC_ROOT):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

from tools.diagnose_phase4a_prediction_system_ps_q24b_autotrade_read_only_prediction_status_display_compat_guard import (  # noqa: E402
    DIAGNOSTIC_VERSION,
    run_autotrade_prediction_status_display_compat_guard,
)

SPEC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q24B_AUTOTRADE_READ_ONLY_PREDICTION_STATUS_DISPLAY_COMPAT_GUARD_2026-06-29.md"
DIAG = REPO_ROOT / "tools/diagnose_phase4a_prediction_system_ps_q24b_autotrade_read_only_prediction_status_display_compat_guard.py"


def test_spec_declares_q24b_display_compat_contract() -> None:
    text = SPEC.read_text(encoding="utf-8-sig")
    for marker in (
        "ps_q24b_autotrade_read_only_prediction_status_display_compat_guard=true",
        "base_reentry=PS_Q24A_AUTOTRADE_READ_ONLY_PREDICTION_CONSUMPTION_PLANNED",
        "q24a_read_only_consumption_planning_ready=true",
        "autotrade_prediction_preview_status_display_packet_ok=true",
        "status_display_state_ok=true",
        "status_display_snapshot_lines_include_safety=true",
        "no_ui_runtime_wiring=true",
        "no_streamlit_rendering=true",
        "no_command_buttons=true",
        "scheduler_action_changed=false",
        "runtime_artifact_write_changed=false",
        "shadow_decision_append=false",
        "mode_apply=false",
        "ledger_append=false",
        "broker_autotrade=false",
        "parameter_apply=false",
    ):
        assert marker in text, marker


def test_live_q24b_display_compat_ready() -> None:
    result = run_autotrade_prediction_status_display_compat_guard()
    assert result["ok"] is True
    assert result["diagnostic_version"] == DIAGNOSTIC_VERSION
    assert result["ready"] is True, result["blockers"]
    assert result["blockers"] == []
    q24a = result["q24a_read_only_consumption"]
    assert q24a["ready"] is True
    display = result["display_compat"]
    assert display["contract_section_type"] == "autotrade_prediction_preview_status_display_packet"
    assert display["contract_read_only"] is True
    assert display["display_state"] == "ok"
    assert display["status_available"] is True
    assert display["compact_line"].endswith("display_only")
    assert "no_command_buttons=true" in display["snapshot_lines"]
    assert "not_runtime_wiring=true" in display["snapshot_lines"]
    assert "not_ui_rendering=true" in display["snapshot_lines"]
    assert display["preview_action"] == "WATCH"
    assert display["preview_bias"] == "neutral"
    assert display["read_only_contract"] is True
    assert display["non_executing"] is True
    assert display["no_command_buttons"] is True
    assert display["not_runtime_wiring"] is True
    assert display["not_ui_rendering"] is True
    assert display["autotrade_page_runtime_wired"] is False
    safety = result["safety"]
    assert safety["read_only_diagnostic"] is True
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


def test_diagnostic_is_no_write_no_ui_command_no_broker() -> None:
    text = DIAG.read_text(encoding="utf-8")
    for forbidden in (
        "Set-ScheduledTask",
        "Enable-ScheduledTask",
        "Disable-ScheduledTask",
        "Register-ScheduledTask",
        "New-ScheduledTaskTrigger",
        "st.button",
        "st.checkbox",
        "append_decision_jsonl",
        "run_shadow_decision_from_snapshot",
        "submit_mode_change_command_request",
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
    test_spec_declares_q24b_display_compat_contract()
    test_live_q24b_display_compat_ready()
    test_diagnostic_is_no_write_no_ui_command_no_broker()
    print(json.dumps({"ok": True}, ensure_ascii=False))
