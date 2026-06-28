# path: ./tools/test_phase4a_prediction_system_ps_q23h_switch_scheduler_action_to_sidecar_once.py
# desc: Focused guard for PS-Q23H gated scheduler action switch to sidecar-enabled Q22X action.

from __future__ import annotations

import json
from pathlib import Path
import sys
from typing import Any, Mapping

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.diagnose_phase4a_prediction_system_ps_q23g_scheduler_sidecar_action_plan_no_write import (  # noqa: E402
    candidate_silent_launcher_sidecar_args,
    expected_silent_launcher_args,
)
from tools.run_phase4a_prediction_system_ps_q21w_register_disabled_scheduler_once import TASK_NAME, TASK_PATH  # noqa: E402
from tools.run_phase4a_prediction_system_ps_q23h_switch_scheduler_action_to_sidecar_once import (  # noqa: E402
    REQUIRED_CONFIRMATION,
    SWITCH_VERSION,
    run_switch_scheduler_action_to_sidecar_once,
)

SPEC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q23H_GATED_SCHEDULER_SIDECAR_ACTION_SWITCH_2026-06-28.md"
TOOL = REPO_ROOT / "tools/run_phase4a_prediction_system_ps_q23h_switch_scheduler_action_to_sidecar_once.py"


def _plan_ready() -> dict:
    return {
        "ok": True,
        "plan_ready_for_future_scheduler_action_replacement": True,
        "plan_state": "scheduler_sidecar_action_plan_ready_no_write",
        "blockers": [],
        "candidate_action_execute": r"C:\BtcTradeSystem\.venv\Scripts\pythonw.exe",
        "candidate_action_arguments": candidate_silent_launcher_sidecar_args(),
        "current_action_arguments": expected_silent_launcher_args(),
    }


def _plan_blocked() -> dict:
    return {"ok": True, "plan_ready_for_future_scheduler_action_replacement": False, "blockers": ["blocked"]}


def _ps_success(script: str) -> Mapping[str, Any]:
    assert "Set-ScheduledTask" in script
    assert "New-ScheduledTaskTrigger" not in script
    assert candidate_silent_launcher_sidecar_args() in script
    assert expected_silent_launcher_args() in script
    return {
        "ok": True,
        "task_exists": True,
        "task_name": TASK_NAME,
        "task_path": TASK_PATH,
        "state": "Ready",
        "action_execute": r"C:\BtcTradeSystem\.venv\Scripts\pythonw.exe",
        "action_arguments": candidate_silent_launcher_sidecar_args(),
        "trigger_count": 1,
    }


def test_spec_declares_gated_scheduler_switch_contract() -> None:
    text = SPEC.read_text(encoding="utf-8-sig")
    for marker in (
        "ps_q23h_gated_scheduler_sidecar_action_switch=true",
        "scheduler_action_replacement_runner_added=true",
        "default_execution_is_dry_run_no_write=true",
        "exact_confirmation_required=true",
        "scheduled_sidecar_write_enablement_requires_operator_token=true",
        "trigger_added=false",
        "broker_autotrade=false",
    ):
        assert marker in text, marker


def test_default_blocks_without_invoking_powershell() -> None:
    called = {"ps": False}
    def ps(_: str) -> Mapping[str, Any]:
        called["ps"] = True
        return _ps_success("")
    result = run_switch_scheduler_action_to_sidecar_once(ps_runner=ps, plan_provider=_plan_ready, repo_status_short="")
    assert result["switch_version"] == SWITCH_VERSION
    assert result["success"] is False
    assert result["execution_state"] == "scheduler_sidecar_action_switch_blocked_no_write"
    assert result["powershell_invoked"] is False
    assert result["scheduler_action_replacement_executed"] is False
    assert result["scheduled_sidecar_write_enabled"] is False
    assert called["ps"] is False


def test_exact_token_switches_action_and_preserves_trigger_count() -> None:
    result = run_switch_scheduler_action_to_sidecar_once(
        operator_acknowledged=True,
        execute_switch_once=True,
        confirmation=REQUIRED_CONFIRMATION,
        ps_runner=_ps_success,
        plan_provider=_plan_ready,
        repo_status_short="",
    )
    assert result["success"] is True
    assert result["execution_state"] == "scheduler_sidecar_action_switch_completed"
    assert result["powershell_invoked"] is True
    assert result["scheduler_action_replacement_executed"] is True
    assert result["scheduled_sidecar_write_enabled"] is True
    assert result["trigger_added"] is False
    assert result["periodic_trigger_added"] is False
    assert result["scheduler_task_created"] is False
    assert result["powershell_result"]["trigger_count"] == 1
    assert result["powershell_result"]["action_arguments"] == candidate_silent_launcher_sidecar_args()
    assert result["latest_prediction_artifact_written"] is False
    assert result["latest_manifest_written"] is False
    assert result["run_sidecars_written"] is False
    assert result["would_send_to_broker"] is False


def test_blocks_when_q23g_plan_not_ready() -> None:
    result = run_switch_scheduler_action_to_sidecar_once(
        operator_acknowledged=True,
        execute_switch_once=True,
        confirmation=REQUIRED_CONFIRMATION,
        ps_runner=_ps_success,
        plan_provider=_plan_blocked,
        repo_status_short="",
    )
    assert result["success"] is False
    assert result["powershell_invoked"] is False
    assert "q23g_scheduler_sidecar_action_plan_ready_required" in result["blocked_reasons"]
    assert result["scheduler_action_replacement_executed"] is False
    assert result["scheduled_sidecar_write_enabled"] is False


def test_tool_has_action_replacement_but_no_trigger_or_broker_code() -> None:
    text = TOOL.read_text(encoding="utf-8")
    assert "Set-ScheduledTask" in text
    assert "New-ScheduledTaskAction" in text
    for forbidden in (
        "New-ScheduledTaskTrigger",
        "Register-ScheduledTask",
        "Start-ScheduledTask",
        "send_order(",
        "place_order(",
        ".write_text(",
        ".write_bytes(",
        "os.replace",
    ):
        assert forbidden not in text, forbidden
    assert REQUIRED_CONFIRMATION in text


if __name__ == "__main__":
    test_spec_declares_gated_scheduler_switch_contract()
    test_default_blocks_without_invoking_powershell()
    test_exact_token_switches_action_and_preserves_trigger_count()
    test_blocks_when_q23g_plan_not_ready()
    test_tool_has_action_replacement_but_no_trigger_or_broker_code()
    print(json.dumps({"ok": True}))
