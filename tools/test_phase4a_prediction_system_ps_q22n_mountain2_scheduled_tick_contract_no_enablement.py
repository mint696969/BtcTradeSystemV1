# path: ./tools/test_phase4a_prediction_system_ps_q22n_mountain2_scheduled_tick_contract_no_enablement.py
# desc: Focused guard for PS-Q22N Mountain2 scheduled latest-refresh tick contract no enablement.

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.design_phase4a_prediction_system_ps_q22n_mountain2_scheduled_tick_contract_no_enablement import (  # noqa: E402
    CONTRACT_VERSION,
    FUTURE_TICK_NAME,
    build_scheduled_tick_contract,
)

SPEC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q22N_MOUNTAIN2_SCHEDULED_TICK_CONTRACT_NO_ENABLEMENT_2026-06-27.md"
TOOL = REPO_ROOT / "tools/design_phase4a_prediction_system_ps_q22n_mountain2_scheduled_tick_contract_no_enablement.py"


def _q22m(**overrides: object) -> dict:
    data = {
        "prep_state": "mountain2_recurring_trigger_prep_ready_no_enablement",
        "prep_ready_for_future_enablement_design": True,
        "prep_blockers": [],
        "scheduler_task": {"task_state": "Disabled", "task_trigger_count": 0},
        "scheduler_enabled": False,
        "trigger_added": False,
    }
    data.update(overrides)
    return data


def _q21o(**overrides: object) -> dict:
    data = {
        "lock_contract_state": "single_non_overlapping_run_lock_contract_ready_no_file_creation",
        "lock_contract_ready": True,
        "lock_contract_blockers": [],
        "lock_file_creation_allowed": False,
        "lock_acquire_allowed_now": False,
        "run_lock_contract": {"single_non_overlapping_runner_lock_required": True},
    }
    data.update(overrides)
    return data


def test_spec_declares_future_tick_contract_and_no_enablement() -> None:
    text = SPEC.read_text(encoding="utf-8-sig")
    for marker in (
        "ps_q22n_mountain2_scheduled_tick_contract_no_enablement=true",
        "read_only_contract_only=true",
        "no_scheduler_enablement=true",
        "no_trigger_addition=true",
        "no_recurring_or_periodic_execution=true",
        "no_latest_prediction_artifact_write=true",
        "future_tick_name=mountain2_scheduled_latest_refresh_tick_once",
        "scheduler_enabled=false",
        "trigger_added=false",
        "recurring_enablement_allowed_now=false",
        "would_send_to_broker=false",
    ):
        assert marker in text, marker


def test_ready_contract_does_not_execute_future_tick() -> None:
    result = build_scheduled_tick_contract(repo_status_short="", q22m_packet=_q22m(), q21o_packet=_q21o())
    assert result["contract_version"] == CONTRACT_VERSION
    assert result["contract_state"] == "mountain2_scheduled_tick_contract_ready_no_enablement"
    assert result["contract_ready_for_future_no_enable_runner_skeleton"] is True
    assert result["future_tick_contract"]["future_tick_name"] == FUTURE_TICK_NAME
    assert result["future_tick_contract"]["must_stop_for_operator_before_enablement"] is True
    assert result["future_scheduler_contract_not_executed"]["would_enable_scheduler"] is True
    assert result["scheduler_enabled"] is False
    assert result["trigger_added"] is False
    assert result["recurring_enablement_allowed_now"] is False
    assert result["periodic_execution_enabled"] is False
    assert result["latest_prediction_artifact_written"] is False
    assert result["status_artifact_written"] is False
    assert result["lock_acquire_attempted"] is False
    assert result["would_send_to_broker"] is False


def test_blocks_on_existing_task_enabled_or_lock_contract_missing() -> None:
    result = build_scheduled_tick_contract(
        repo_status_short="",
        q22m_packet=_q22m(scheduler_task={"task_state": "Ready", "task_trigger_count": 1}),
        q21o_packet=_q21o(run_lock_contract={}),
    )
    assert result["contract_ready_for_future_no_enable_runner_skeleton"] is False
    assert "existing_scheduler_task_must_be_disabled_before_tick_contract" in result["contract_blockers"]
    assert "existing_scheduler_task_must_have_zero_triggers_before_tick_contract" in result["contract_blockers"]
    assert "single_non_overlapping_lock_contract_required" in result["contract_blockers"]
    assert result["scheduler_enabled"] is False
    assert result["trigger_added"] is False


def test_tool_contains_no_direct_scheduler_or_runtime_write_commands() -> None:
    text = TOOL.read_text(encoding="utf-8")
    for token in (
        "Enable-ScheduledTask",
        "New-ScheduledTaskTrigger",
        "Start-ScheduledTask",
        "Register-ScheduledTask",
        "execute_one_shot_write=True",
        "allow_runtime_artifact_write=True",
        "execute_status_write_once=True",
        "_write_json_atomic",
        "send_order(",
        "place_order(",
    ):
        assert token not in text, token


if __name__ == "__main__":
    test_spec_declares_future_tick_contract_and_no_enablement()
    test_ready_contract_does_not_execute_future_tick()
    test_blocks_on_existing_task_enabled_or_lock_contract_missing()
    test_tool_contains_no_direct_scheduler_or_runtime_write_commands()
    print(json.dumps({"ok": True}))
