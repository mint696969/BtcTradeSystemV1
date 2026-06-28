# path: ./tools/test_phase4a_prediction_system_ps_q22u_mountain2_scheduler_enablement_once.py
# desc: Focused guard for PS-Q22U scheduler enablement/rollback executor. Uses fake PowerShell runner only.

from __future__ import annotations

import json
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.diagnose_phase4a_prediction_system_ps_q22m_mountain2_recurring_trigger_prep_no_enablement import FUTURE_MOUNTAIN2_TOKEN_CANDIDATE  # noqa: E402
from tools.run_phase4a_prediction_system_ps_q22u_mountain2_scheduler_enablement_once import (  # noqa: E402
    ENABLE_VERSION,
    _q21v_action_args,
    _q22s_action_args,
    run_scheduler_enablement_once,
)

SPEC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q22U_MOUNTAIN2_SCHEDULER_ENABLEMENT_EXECUTOR_2026-06-28.md"
TOOL = REPO_ROOT / "tools/run_phase4a_prediction_system_ps_q22u_mountain2_scheduler_enablement_once.py"


def _plan() -> dict:
    return {"plan_ready_for_explicit_operator_gate": True, "plan_blockers": []}


def test_spec_declares_exact_token_and_rollback_boundary() -> None:
    text = SPEC.read_text(encoding="utf-8-sig")
    for marker in (
        "ps_q22u_mountain2_scheduler_enablement_executor=true",
        "default_execution_is_dry_run_no_write=true",
        "requires_exact_confirmation=ENABLE_RECURRING_PRODUCER_LOOP_WITH_TRIGGER_AND_ROLLBACK_PLAN",
        "has_rollback_mode=true",
        "scheduler_action_replacement_explicit_only=true",
        "periodic_trigger_addition_explicit_only=true",
        "scheduler_enablement_explicit_only=true",
        "broker_autotrade=false",
    ):
        assert marker in text, marker


def test_default_blocks_no_powershell_invocation() -> None:
    called = {"ps": False}
    def ps(_: str) -> dict:
        called["ps"] = True
        return {"ok": False}
    result = run_scheduler_enablement_once(ps_runner=ps, plan_provider=_plan, repo_status_short="")
    assert result["enable_version"] == ENABLE_VERSION
    assert result["success"] is False
    assert result["powershell_invoked"] is False
    assert result["scheduler_enabled"] is False
    assert called["ps"] is False


def test_enable_executes_expected_scheduler_boundary_with_fake_ps() -> None:
    seen = {"script": ""}
    def ps(script: str) -> dict:
        seen["script"] = script
        assert "Set-ScheduledTask" in script
        assert "New-ScheduledTaskTrigger" in script
        assert "Enable-ScheduledTask" in script
        return {
            "ok": True,
            "task_name": "BTC_TS_PredictionWarRoom_NonUI_DisabledScheduler",
            "task_path": "\\BtcTradeSystem\\",
            "state": "Ready",
            "action_arguments": _q22s_action_args(),
            "trigger_count": 1,
        }
    result = run_scheduler_enablement_once(
        operator_acknowledged=True,
        execute_enable_once=True,
        confirmation=FUTURE_MOUNTAIN2_TOKEN_CANDIDATE,
        ps_runner=ps,
        plan_provider=_plan,
        repo_status_short="",
    )
    assert result["success"] is True
    assert result["execution_state"] == "mountain2_scheduler_enabled"
    assert result["scheduler_action_replacement_executed"] is True
    assert result["scheduler_enabled"] is True
    assert result["trigger_added"] is True
    assert result["would_send_to_broker"] is False


def test_rollback_executes_disable_restore_q21v_with_fake_ps() -> None:
    def ps(script: str) -> dict:
        assert "Disable-ScheduledTask" in script
        assert "Unregister-ScheduledTask" in script
        assert "Register-ScheduledTask" in script
        return {
            "ok": True,
            "task_name": "BTC_TS_PredictionWarRoom_NonUI_DisabledScheduler",
            "task_path": "\\BtcTradeSystem\\",
            "state": "Disabled",
            "action_arguments": _q21v_action_args(),
            "trigger_count": 0,
        }
    result = run_scheduler_enablement_once(
        operator_acknowledged=True,
        rollback=True,
        confirmation=FUTURE_MOUNTAIN2_TOKEN_CANDIDATE,
        ps_runner=ps,
        plan_provider=_plan,
        repo_status_short="",
    )
    assert result["success"] is True
    assert result["execution_state"] == "mountain2_scheduler_rollback_completed"
    assert result["rollback_executed"] is True
    assert result["scheduler_enabled"] is False
    assert result["trigger_added"] is False


def test_tool_requires_exact_flags_before_mutation() -> None:
    text = TOOL.read_text(encoding="utf-8")
    assert "exact_scheduler_enablement_confirmation_required" in text
    assert "operator_acknowledgement_required" in text
    assert "execute_enable_once_flag_required" in text
    assert "would_send_to_broker" in text


if __name__ == "__main__":
    test_spec_declares_exact_token_and_rollback_boundary()
    test_default_blocks_no_powershell_invocation()
    test_enable_executes_expected_scheduler_boundary_with_fake_ps()
    test_rollback_executes_disable_restore_q21v_with_fake_ps()
    test_tool_requires_exact_flags_before_mutation()
    print(json.dumps({"ok": True}))
