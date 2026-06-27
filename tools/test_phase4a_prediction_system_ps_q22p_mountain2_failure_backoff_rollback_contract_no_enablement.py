# path: ./tools/test_phase4a_prediction_system_ps_q22p_mountain2_failure_backoff_rollback_contract_no_enablement.py
# desc: Focused guard for PS-Q22P Mountain2 failure/backoff/rollback contract no enablement.

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.run_phase4a_prediction_system_ps_q22o_mountain2_scheduled_latest_refresh_tick_once import RUNNER_VERSION as Q22O_RUNNER_VERSION  # noqa: E402
from tools.design_phase4a_prediction_system_ps_q22p_mountain2_failure_backoff_rollback_contract_no_enablement import (  # noqa: E402
    CONTRACT_VERSION,
    HARD_DISABLE_FAILURES,
    SOFT_BACKOFF_FAILURES,
    build_failure_backoff_rollback_contract,
)

SPEC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q22P_MOUNTAIN2_FAILURE_BACKOFF_ROLLBACK_CONTRACT_NO_ENABLEMENT_2026-06-27.md"
TOOL = REPO_ROOT / "tools/design_phase4a_prediction_system_ps_q22p_mountain2_failure_backoff_rollback_contract_no_enablement.py"


def _q22o(**overrides: object) -> dict:
    data = {
        "runner_version": Q22O_RUNNER_VERSION,
        "runner_state": "mountain2_tick_runner_skeleton_ready_no_enablement",
        "runner_ready_for_future_danger_boundary_review": True,
        "blocked_reasons": [],
        "warning_reasons": [],
        "scheduler_enabled": False,
        "trigger_added": False,
        "latest_prediction_artifact_written": False,
        "status_artifact_written": False,
        "lock_acquire_attempted": False,
        "danger_boundary_next_stop": {"must_stop_before_scheduler_enablement": True},
    }
    data.update(overrides)
    return data


def test_spec_declares_failure_backoff_rollback_no_enablement() -> None:
    text = SPEC.read_text(encoding="utf-8-sig")
    for marker in (
        "ps_q22p_mountain2_failure_backoff_rollback_contract_no_enablement=true",
        "read_only_contract_only=true",
        "no_scheduler_enablement=true",
        "no_trigger_addition=true",
        "no_recurring_or_periodic_execution=true",
        "future_tick_must_write_status_on_failure=true",
        "future_tick_soft_backoff_after_failures=2",
        "future_tick_hard_disable_after_failures=3",
        "rollback_must_disable_scheduler_first=true",
        "scheduler_enabled=false",
        "trigger_added=false",
        "would_send_to_broker=false",
    ):
        assert marker in text, marker


def test_ready_contract_preserves_no_enablement_and_names_backoff() -> None:
    result = build_failure_backoff_rollback_contract(repo_status_short="", q22o_packet=_q22o())
    assert result["contract_version"] == CONTRACT_VERSION
    assert result["contract_state"] == "mountain2_failure_backoff_rollback_contract_ready_no_enablement"
    assert result["contract_ready_for_future_enablement_review"] is True
    assert result["failure_backoff_contract"]["soft_backoff_after_consecutive_failures"] == SOFT_BACKOFF_FAILURES
    assert result["failure_backoff_contract"]["hard_disable_after_consecutive_failures"] == HARD_DISABLE_FAILURES
    assert result["rollback_contract"]["disable_scheduler_first"] is True
    assert result["future_danger_boundary_not_crossed"]["scheduler_enabled"] is False
    assert result["scheduler_enabled"] is False
    assert result["trigger_added"] is False
    assert result["recurring_enablement_allowed_now"] is False
    assert result["latest_prediction_artifact_written"] is False
    assert result["status_artifact_written"] is False
    assert result["rollback_executed"] is False
    assert result["would_send_to_broker"] is False


def test_blocks_if_q22o_crossed_any_danger_boundary() -> None:
    result = build_failure_backoff_rollback_contract(
        repo_status_short="",
        q22o_packet=_q22o(scheduler_enabled=True, trigger_added=True, latest_prediction_artifact_written=True, lock_acquire_attempted=True),
    )
    assert result["contract_ready_for_future_enablement_review"] is False
    assert "q22o_must_preserve_no_scheduler_no_trigger" in result["contract_blockers"]
    assert "q22o_must_preserve_no_runtime_writes" in result["contract_blockers"]
    assert "q22o_must_not_acquire_lock" in result["contract_blockers"]
    assert result["scheduler_enabled"] is False
    assert result["trigger_added"] is False
    assert result["latest_prediction_artifact_written"] is False


def test_tool_contains_no_scheduler_runtime_write_or_rollback_commands() -> None:
    text = TOOL.read_text(encoding="utf-8")
    for token in (
        "Enable-ScheduledTask",
        "Disable-ScheduledTask",
        "New-ScheduledTaskTrigger",
        "Start-ScheduledTask",
        "Register-ScheduledTask",
        "Unregister-ScheduledTask",
        "run_one_shot_write",
        "run_bounded_manual_freshness_recovery_once",
        "execute_one_shot_write=True",
        "allow_runtime_artifact_write=True",
        "execute_status_write_once=True",
        "_write_json_atomic",
        ".write_text(",
        "Path.replace(",
        "os.replace(",
        "send_order(",
        "place_order(",
    ):
        assert token not in text, token


if __name__ == "__main__":
    test_spec_declares_failure_backoff_rollback_no_enablement()
    test_ready_contract_preserves_no_enablement_and_names_backoff()
    test_blocks_if_q22o_crossed_any_danger_boundary()
    test_tool_contains_no_scheduler_runtime_write_or_rollback_commands()
    print(json.dumps({"ok": True}))
