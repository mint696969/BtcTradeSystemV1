# path: ./tools/test_phase4a_prediction_system_ps_q23s_silent_launcher_no_window_subprocess_patch.py
# desc: Focused guard for PS-Q23S Q22X subprocess no-window patch.

from __future__ import annotations

import json
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import tools.run_phase4a_prediction_system_ps_q22x_silent_q22s_launcher as launcher  # noqa: E402

SPEC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q23S_SILENT_LAUNCHER_NO_WINDOW_SUBPROCESS_PATCH_2026-06-29.md"
LAUNCHER = REPO_ROOT / "tools/run_phase4a_prediction_system_ps_q22x_silent_q22s_launcher.py"
DIAG = REPO_ROOT / "tmp/work/window_popup_diagnosis/diagnose_popup_windows.ps1"


def test_spec_declares_no_window_subprocess_contract() -> None:
    text = SPEC.read_text(encoding="utf-8-sig")
    for marker in (
        "ps_q23s_silent_launcher_no_window_subprocess_patch=true",
        "scheduler_action_changed=false",
        "q22x_pythonw_action_retained=true",
        "subprocess_child_console_windows_suppressed=true",
        "uses_create_no_window=true",
        "uses_sw_hide_startupinfo=true",
        "broker_autotrade=false",
    ):
        assert marker in text, marker


def test_launcher_installs_windows_popen_no_window_patch() -> None:
    text = LAUNCHER.read_text(encoding="utf-8")
    assert "def _install_windows_no_window_subprocess_patch()" in text
    assert "subprocess.Popen" in text
    assert "CREATE_NO_WINDOW" in text
    assert "STARTF_USESHOWWINDOW" in text
    assert "wShowWindow" in text
    assert "no_window_subprocess_patch_installed" in text
    assert callable(launcher._install_windows_no_window_subprocess_patch)


def test_scheduler_action_switch_tokens_not_reintroduced() -> None:
    text = LAUNCHER.read_text(encoding="utf-8")
    for forbidden in (
        "Set-ScheduledTask",
        "Register-ScheduledTask",
        "New-ScheduledTaskTrigger",
        "Enable-ScheduledTask",
        "Disable-ScheduledTask",
        "send_order(",
        "place_order(",
    ):
        assert forbidden not in text, forbidden


def test_popup_diagnosis_pid_bug_fixed() -> None:
    text = DIAG.read_text(encoding="utf-8")
    assert "function Get-ParentChain($TargetPid)" in text
    assert "$current = $TargetPid" in text
    assert "function Get-ParentChain($Pid)" not in text


if __name__ == "__main__":
    test_spec_declares_no_window_subprocess_contract()
    test_launcher_installs_windows_popen_no_window_patch()
    test_scheduler_action_switch_tokens_not_reintroduced()
    test_popup_diagnosis_pid_bug_fixed()
    print(json.dumps({"ok": True}))
