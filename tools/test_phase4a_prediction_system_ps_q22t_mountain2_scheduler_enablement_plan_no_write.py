# path: ./tools/test_phase4a_prediction_system_ps_q22t_mountain2_scheduler_enablement_plan_no_write.py
# desc: Focused guard for PS-Q22T no-write scheduler enablement plan.

from __future__ import annotations

import json
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.diagnose_phase4a_prediction_system_ps_q22m_mountain2_recurring_trigger_prep_no_enablement import FUTURE_MOUNTAIN2_TOKEN_CANDIDATE  # noqa: E402
from tools.diagnose_phase4a_prediction_system_ps_q22t_mountain2_scheduler_enablement_plan_no_write import (  # noqa: E402
    PLAN_VERSION,
    build_plan,
)

SPEC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q22T_MOUNTAIN2_SCHEDULER_ENABLEMENT_PLAN_NO_WRITE_2026-06-28.md"
TOOL = REPO_ROOT / "tools/diagnose_phase4a_prediction_system_ps_q22t_mountain2_scheduler_enablement_plan_no_write.py"


def _q22q() -> dict:
    return {
        "readiness_state": "mountain2_final_pre_danger_boundary_ready_no_enablement",
        "readiness_blockers": [],
        "runtime_readiness_blockers": [],
    }


def _task() -> dict:
    return {
        "task_recognized_as_ps_q21w": True,
        "task_state": "Disabled",
        "task_trigger_count": 0,
        "task_action_arguments": "C:/BtcTradeSystem/tools/run_phase4a_prediction_system_ps_q21v_disabled_scheduler_registration_smoke.py",
    }


def test_spec_declares_no_write_plan_boundary() -> None:
    text = SPEC.read_text(encoding="utf-8-sig")
    for marker in (
        "ps_q22t_mountain2_scheduler_enablement_plan_no_write=true",
        "read_only_plan_only=true",
        "scheduler_action_replacement_executed=false",
        "periodic_trigger_addition_executed=false",
        "scheduler_enablement_executed=false",
        "recurring_or_periodic_execution_enabled=false",
        "rollback_executed=false",
    ):
        assert marker in text, marker


def test_ready_plan_is_no_write_and_names_danger_token() -> None:
    result = build_plan(repo_status_short="", q22q_packet=_q22q(), task=_task())
    assert result["plan_version"] == PLAN_VERSION
    assert result["plan_ready_for_explicit_operator_gate"] is True
    assert result["required_operator_confirmation_before_execution"] == FUTURE_MOUNTAIN2_TOKEN_CANDIDATE
    assert result["scheduler_action_replacement_executed"] is False
    assert result["scheduler_enabled"] is False
    assert result["trigger_added"] is False
    assert result["recurring_enablement_allowed_now"] is False
    assert result["future_task_action"]["arguments"].endswith(FUTURE_MOUNTAIN2_TOKEN_CANDIDATE)


def test_blocks_dirty_repo_or_nonzero_triggers() -> None:
    dirty = build_plan(repo_status_short=" M x", q22q_packet=_q22q(), task=_task())
    assert "repo_clean_required_before_scheduler_enablement_plan" in dirty["plan_blockers"]
    task = _task()
    task["task_trigger_count"] = 1
    trig = build_plan(repo_status_short="", q22q_packet=_q22q(), task=task)
    assert "scheduler_task_must_have_zero_triggers_before_enablement_plan" in trig["plan_blockers"]


def test_tool_contains_no_scheduler_execution_calls() -> None:
    text = TOOL.read_text(encoding="utf-8")
    # The no-write plan may name future dangerous cmdlets as strings. It must not
    # execute them or invoke PowerShell for mutation.
    for token in (
        "powershell.exe",
        "-Command",
        "subprocess.run([\"powershell.exe\"",
        "Set-ScheduledTask -",
        "Enable-ScheduledTask -",
        "New-ScheduledTaskTrigger -",
        "Start-ScheduledTask -",
        "Register-ScheduledTask -",
    ):
        assert token not in text, token


if __name__ == "__main__":
    test_spec_declares_no_write_plan_boundary()
    test_ready_plan_is_no_write_and_names_danger_token()
    test_blocks_dirty_repo_or_nonzero_triggers()
    test_tool_contains_no_scheduler_execution_calls()
    print(json.dumps({"ok": True}))
