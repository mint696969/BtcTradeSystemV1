# path: ./tools/test_phase4a_prediction_system_ps_q21w_register_disabled_scheduler_once.py
# desc: Focused guard for PS-Q21W gated one-time disabled scheduler registration.

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.run_phase4a_prediction_system_ps_q21w_register_disabled_scheduler_once import (  # noqa: E402
    REGISTRATION_VERSION,
    REQUIRED_NEXT_PRODUCER_CONFIRMATION,
    REQUIRED_OPERATOR_CONFIRMATION,
    TASK_NAME,
    TASK_PATH,
    _task_action_args,
    query_disabled_scheduler_registration,
    run_disabled_scheduler_registration_once,
)

TOOL = REPO_ROOT / "tools/run_phase4a_prediction_system_ps_q21w_register_disabled_scheduler_once.py"
SPEC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q21W_REGISTER_DISABLED_SCHEDULER_ONCE_2026-06-26.md"

REQUIRED_MARKERS = (
    "ps_q21w_register_disabled_scheduler_once=true",
    "default_execution_is_dry_run_no_registration=true",
    "execute_registration_requires_confirmation=REGISTER_DISABLED_NON_UI_SCHEDULER_ONCE_WITH_ROLLBACK_PLAN",
    "registered_task_state_required=Disabled",
    "registered_task_trigger_count_required=0",
    "producer_loop_still_separate_approval=true",
    "scheduler_registered_by_default=false",
)

FALSE_BOUNDARIES = (
    "producer_loop_enabled=false",
    "producer_runner_invoked=false",
    "latest_prediction_artifact_written=false",
    "status_artifact_written=false",
    "warroom_ui_trigger_allowed=false",
    "autotrade_trigger_allowed=false",
    "broker_private_api_allowed=false",
    "would_send_to_broker=false",
    "would_write_collector_state=false",
)


def _preflight_ready() -> dict:
    return {
        "preflight_ready_for_separate_approval": True,
        "preflight_state": "scheduler_producer_registration_preflight_ready_for_separate_approval_no_registration",
        "preflight_blockers": [],
        "latest_prediction_non_stale": True,
        "latest_status_success_observed": True,
        "d_hot_lock_artifact_exists": False,
    }


def _fake_task_payload() -> dict:
    return {
        "ok": True,
        "task_exists": True,
        "task_name": TASK_NAME,
        "task_path": TASK_PATH,
        "state": "Disabled",
        "action_execute": sys.executable,
        "action_arguments": _task_action_args(),
        "trigger_count": 0,
    }


def test_spec_declares_gated_disabled_registration_only() -> None:
    text = SPEC.read_text(encoding="utf-8-sig")
    for marker in REQUIRED_MARKERS:
        assert marker in text, marker
    for marker in FALSE_BOUNDARIES:
        assert marker in text, marker


def test_default_is_dry_run_no_powershell_no_registration() -> None:
    called = {"value": False}

    def runner(_: str) -> dict:
        called["value"] = True
        raise AssertionError("PowerShell runner must not be called in default dry-run")

    result = run_disabled_scheduler_registration_once(ps_runner=runner)
    assert result["ok"] is True
    assert result["registration_state"] == "disabled_scheduler_registration_dry_run_no_registration"
    assert result["registration_version"] == REGISTRATION_VERSION
    assert called["value"] is False
    assert result["os_scheduler_registration_attempted"] is False
    assert result["scheduler_registered"] is False
    assert result["producer_loop_enabled"] is False
    assert result["producer_runner_invoked"] is False


def test_execute_blocks_without_confirmation_clean_tree_or_ready_preflight() -> None:
    result = run_disabled_scheduler_registration_once(
        execute_register=True,
        confirmation="wrong",
        git_status_short=" M something.py",
        preflight_packet={"preflight_ready_for_separate_approval": False, "d_hot_lock_artifact_exists": True},
        ps_runner=lambda _: _fake_task_payload(),
    )
    assert result["ok"] is False
    assert result["registration_state"] == "disabled_scheduler_registration_blocked_no_registration"
    assert "exact_operator_confirmation_required" in result["blocked_reasons"]
    assert "working_tree_must_be_clean_before_disabled_scheduler_registration" in result["blocked_reasons"]
    assert "ps_q21u_preflight_ready_required" in result["blocked_reasons"]
    assert "d_hot_lock_absent_required" in result["blocked_reasons"]
    assert result["os_scheduler_registration_attempted"] is False
    assert result["producer_loop_enabled"] is False


def test_execute_with_confirmation_registers_disabled_no_trigger_task_with_fake_runner() -> None:
    scripts: list[str] = []

    def runner(script: str) -> dict:
        scripts.append(script)
        return _fake_task_payload()

    result = run_disabled_scheduler_registration_once(
        execute_register=True,
        confirmation=REQUIRED_OPERATOR_CONFIRMATION,
        git_status_short="",
        preflight_packet=_preflight_ready(),
        ps_runner=runner,
    )
    assert result["ok"] is True
    assert result["registration_state"] == "disabled_scheduler_registered_and_verified"
    assert result["os_scheduler_registration_attempted"] is True
    assert result["os_scheduler_registered"] is True
    assert result["scheduler_registered"] is True
    assert result["scheduler_registered_enabled"] is False
    assert result["scheduled_loop_enabled"] is False
    assert result["producer_loop_enabled"] is False
    assert "Register-ScheduledTask" in scripts[0]
    assert "Disable-ScheduledTask" in scripts[0]


def test_query_recognizes_disabled_task_with_fake_runner() -> None:
    result = query_disabled_scheduler_registration(ps_runner=lambda _: _fake_task_payload())
    assert result["ok"] is True
    assert result["query_state"] == "disabled_scheduler_task_visible"
    assert result["task_recognized_as_ps_q21w"] is True
    assert result["task_readback_failures"] == []
    assert result["producer_loop_enabled"] is False


def test_rollback_requires_confirmation_and_unregisters_only_matching_task() -> None:
    blocked = run_disabled_scheduler_registration_once(rollback=True, confirmation="wrong", ps_runner=lambda _: {"ok": True})
    assert blocked["ok"] is False
    assert blocked["rollback_unregister_attempted"] is False

    def runner(script: str) -> dict:
        assert "Unregister-ScheduledTask" in script
        return {"ok": True, "rollback_state": "unregistered_ps_q21w_disabled_scheduler_task_only", "task_exists_after": False}

    result = run_disabled_scheduler_registration_once(rollback=True, confirmation=REQUIRED_OPERATOR_CONFIRMATION, ps_runner=runner)
    assert result["ok"] is True
    assert result["rollback_unregister_attempted"] is True
    assert result["rollback_unregister_ok"] is True
    assert result["producer_loop_enabled"] is False


def test_tool_contains_scheduler_cmdlets_but_no_producer_or_broker_execution() -> None:
    text = TOOL.read_text(encoding="utf-8")
    assert "Register-ScheduledTask" in text
    assert "Disable-ScheduledTask" in text
    assert "Unregister-ScheduledTask" in text
    # The next producer-loop token is intentionally imported from PS-Q21U to avoid duplicated literal drift.
    assert "REQUIRED_NEXT_PRODUCER_CONFIRMATION" in text
    assert "ENABLE_DISABLED_PRODUCER_LOOP_SHADOW_ONCE_WITH_ROLLBACK_PLAN" in REQUIRED_NEXT_PRODUCER_CONFIRMATION
    forbidden = (
        "execute_export=True",
        "allow_runtime_artifact_write=True",
        "request_scheduler_enable=True",
        "producer_runner_invoked\": True",
        "latest_prediction_artifact_written\": True",
        "status_artifact_written\": True",
        "send_order(",
        "place_order(",
        "BTC_TS_DATA_DIR",
    )
    for token in forbidden:
        assert token not in text, token


if __name__ == "__main__":
    test_spec_declares_gated_disabled_registration_only()
    test_default_is_dry_run_no_powershell_no_registration()
    test_execute_blocks_without_confirmation_clean_tree_or_ready_preflight()
    test_execute_with_confirmation_registers_disabled_no_trigger_task_with_fake_runner()
    test_query_recognizes_disabled_task_with_fake_runner()
    test_rollback_requires_confirmation_and_unregisters_only_matching_task()
    test_tool_contains_scheduler_cmdlets_but_no_producer_or_broker_execution()
    print('{"ok": true}')
