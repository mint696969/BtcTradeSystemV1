# path: ./tools/test_phase4a_prediction_system_ps_q21x_producer_loop_shadow_preflight_no_enablement.py
# desc: Focused guard for PS-Q21X producer-loop shadow preflight no enablement.

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.run_phase4a_prediction_system_ps_q21w_register_disabled_scheduler_once import (  # noqa: E402
    PS_Q21V_TOOL,
    TASK_NAME,
    TASK_PATH,
)
from tools.verify_phase4a_prediction_system_ps_q21u_scheduler_producer_registration_preflight import (  # noqa: E402
    REQUIRED_NEXT_PRODUCER_CONFIRMATION,
)
from tools.verify_phase4a_prediction_system_ps_q21x_producer_loop_shadow_preflight_no_enablement import (  # noqa: E402
    SHADOW_PREFLIGHT_VERSION,
    build_producer_loop_shadow_preflight,
)

TOOL = REPO_ROOT / "tools/verify_phase4a_prediction_system_ps_q21x_producer_loop_shadow_preflight_no_enablement.py"
SPEC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q21X_PRODUCER_LOOP_SHADOW_PREFLIGHT_NO_ENABLEMENT_2026-06-27.md"

REQUIRED_MARKERS = (
    "ps_q21x_producer_loop_shadow_preflight_no_enablement=true",
    "read_only_shadow_preflight_only=true",
    "preflight_state=observed_result",
    "producer_loop_shadow_once_requires_confirmation=ENABLE_DISABLED_PRODUCER_LOOP_SHADOW_ONCE_WITH_ROLLBACK_PLAN",
    "producer_runner_invocation_allowed_now=false",
    "producer_loop_enablement_allowed_now=false",
    "scheduler_enablement_allowed_now=false",
    "trigger_addition_allowed_now=false",
    "recurring_enablement_allowed_now=false",
    "producer_status_scheduler_not_registered_may_be_stale_manual_status_caveat=true",
    "scheduler_not_registered_in_d_hot_status_does_not_invalidate_ps_q21w_os_task_query=true",
)

FALSE_BOUNDARIES = (
    "producer_loop_enabled=false",
    "producer_runner_invoked=false",
    "scheduled_loop_enabled=false",
    "scheduler_enabled=false",
    "trigger_added=false",
    "runtime_artifact_write_allowed=false",
    "status_artifact_write_allowed=false",
    "prediction_artifact_write_allowed=false",
    "view_artifact_write_allowed=false",
    "warroom_ui_trigger_allowed=false",
    "approval_or_ledger_allowed=false",
    "parameter_apply_allowed=false",
    "parameter_staging_write_allowed=false",
    "autotrade_trigger_allowed=false",
    "broker_private_api_allowed=false",
    "would_send_to_broker=false",
    "would_write_collector_state=false",
)


def _visibility(**overrides: object) -> dict:
    data = {
        "ok": True,
        "visibility_state": "lock_scheduler_status_visible_non_stale_disabled_no_lock",
        "visibility_attention_reasons": [],
        "generated_at": "2026-06-26T15:01:38Z",
        "age_sec": 10,
        "latest_prediction_non_stale": True,
        "latest_status_success_observed": True,
        "disabled_boundary_preserved": True,
        "d_hot_lock_artifact_exists": False,
        "producer_state": "manual_refresh_exported_status_written",
        "producer_enabled": False,
        "scheduler_enabled": False,
        "status_warnings": ["prediction_result_warnings_present:19"],
        "status_blockers": [],
        "disable_rollback_state": "manual_refresh_only_disable_by_not_running; scheduler_not_registered",
    }
    data.update(overrides)
    return data


def _task(**overrides: object) -> dict:
    data = {
        "ok": True,
        "query_state": "disabled_scheduler_task_visible",
        "task_recognized_as_ps_q21w": True,
        "task_exists": True,
        "task_name": TASK_NAME,
        "task_path": TASK_PATH,
        "task_state": "Disabled",
        "trigger_count": 0,
        "action_target": str(PS_Q21V_TOOL),
        "producer_loop_enabled": False,
        "task_readback_failures": [],
    }
    data.update(overrides)
    return data


def test_spec_declares_shadow_preflight_no_enablement_boundary() -> None:
    text = SPEC.read_text(encoding="utf-8-sig")
    for marker in REQUIRED_MARKERS:
        assert marker in text, marker
    for marker in FALSE_BOUNDARIES:
        assert marker in text, marker


def test_shadow_preflight_ready_when_clean_fresh_no_lock_and_disabled_task_visible() -> None:
    result = build_producer_loop_shadow_preflight(
        visibility_packet=_visibility(),
        scheduler_query_packet=_task(),
        git_status_short="",
    )
    assert result["ok"] is True
    assert result["preflight_version"] == SHADOW_PREFLIGHT_VERSION
    assert result["preflight_state"] == "producer_loop_shadow_preflight_ready_for_one_shot_no_enablement"
    assert result["shadow_preflight_ready_for_one_shot"] is True
    assert result["shadow_preflight_blockers"] == []
    assert result["required_next_producer_confirmation"] == REQUIRED_NEXT_PRODUCER_CONFIRMATION
    assert result["task_recognized_as_ps_q21w"] is True
    assert result["task_state"] == "Disabled"
    assert result["task_trigger_count"] == 0
    assert result["producer_status_scheduler_not_registered_may_be_stale_manual_status_caveat"] is True
    assert result["scheduler_not_registered_in_d_hot_status_does_not_invalidate_ps_q21w_os_task_query"] is True
    assert result["producer_runner_invocation_allowed_now"] is False
    assert result["producer_loop_enablement_allowed_now"] is False
    assert result["scheduler_enablement_allowed_now"] is False
    assert result["trigger_addition_allowed_now"] is False
    assert result["recurring_enablement_allowed_now"] is False
    assert result["runtime_artifact_write_allowed"] is False
    assert result["would_send_to_broker"] is False


def test_shadow_preflight_accepts_q21w_nested_task_readback_shape() -> None:
    nested = {
        "ok": True,
        "query_state": "disabled_scheduler_task_visible",
        "task_recognized_as_ps_q21w": True,
        "task_readback_failures": [],
        "task_readback": {
            "ok": True,
            "task_exists": True,
            "task_name": TASK_NAME,
            "task_path": TASK_PATH,
            "state": "Disabled",
            "trigger_count": 0,
            "action_arguments": str(PS_Q21V_TOOL),
        },
        "producer_loop_enabled": False,
    }
    result = build_producer_loop_shadow_preflight(
        visibility_packet=_visibility(),
        scheduler_query_packet=nested,
        git_status_short="",
    )
    assert result["shadow_preflight_ready_for_one_shot"] is True
    assert result["task_exists"] is True
    assert result["task_name"] == TASK_NAME
    assert result["task_path"] == TASK_PATH
    assert result["task_state"] == "Disabled"
    assert result["task_trigger_count"] == 0
    assert "ps_q21w_disabled_scheduler_task_exists_required" not in result["shadow_preflight_blockers"]
    assert "task_name_mismatch" not in result["shadow_preflight_blockers"]
    assert "task_action_must_remain_ps_q21v_dry_run_tool" not in result["shadow_preflight_blockers"]


def test_shadow_preflight_blocks_without_recovering_on_stale_lock_dirty_or_bad_task() -> None:
    result = build_producer_loop_shadow_preflight(
        visibility_packet=_visibility(
            visibility_state="lock_scheduler_status_visible_attention",
            visibility_attention_reasons=["latest_prediction_stale_or_unknown", "d_hot_runtime_lock_file_exists_attention"],
            latest_prediction_non_stale=False,
            latest_status_success_observed=False,
            d_hot_lock_artifact_exists=True,
            scheduler_enabled=True,
        ),
        scheduler_query_packet=_task(task_state="Ready", trigger_count=1, task_recognized_as_ps_q21w=False),
        git_status_short=" M docs/example.md",
    )
    assert result["preflight_state"] == "producer_loop_shadow_preflight_blocked_no_enablement"
    assert result["shadow_preflight_ready_for_one_shot"] is False
    assert "working_tree_must_be_clean_before_shadow_once_preflight" in result["shadow_preflight_blockers"]
    assert "latest_prediction_non_stale_required_before_shadow_once" in result["shadow_preflight_blockers"]
    assert "latest_status_success_required_before_shadow_once" in result["shadow_preflight_blockers"]
    assert "d_hot_lock_absent_required_before_shadow_once" in result["shadow_preflight_blockers"]
    assert "d_hot_status_scheduler_disabled_required" in result["shadow_preflight_blockers"]
    assert "ps_q21w_task_recognized_required" in result["shadow_preflight_blockers"]
    assert "task_state_disabled_required" in result["shadow_preflight_blockers"]
    assert "task_trigger_count_zero_required" in result["shadow_preflight_blockers"]
    assert result["producer_runner_invoked"] is False
    assert result["latest_prediction_artifact_written"] is False
    assert result["status_artifact_written"] is False
    assert result["scheduler_enablement_allowed_now"] is False
    assert result["trigger_addition_allowed_now"] is False
    assert result["recurring_enablement_allowed_now"] is False


def test_tool_is_read_only_no_enablement_no_write_no_runner_invocation() -> None:
    text = TOOL.read_text(encoding="utf-8")
    forbidden = (
        "write_text(",
        "open(\"w",
        ".touch(",
        ".unlink(",
        "Path.replace(",
        "os.replace(",
        "execute_export=True",
        "allow_runtime_artifact_write=True",
        "request_scheduler_enable=True",
        "Register-ScheduledTask",
        "Enable-ScheduledTask",
        "New-ScheduledTaskTrigger",
        "Start-ScheduledTask",
        "producer_runner_invoked\": True",
        "latest_prediction_artifact_written\": True",
        "status_artifact_written\": True",
        "d_hot_lock_file_created\": True",
        "send_order(",
        "place_order(",
        "BTC_TS_DATA_DIR",
    )
    for token in forbidden:
        assert token not in text, token
    assert "run_visibility" in text
    assert "query_disabled_scheduler_registration" in text
    assert "ENABLE_DISABLED_PRODUCER_LOOP_SHADOW_ONCE_WITH_ROLLBACK_PLAN" in REQUIRED_NEXT_PRODUCER_CONFIRMATION
    assert "print(json.dumps" in text


if __name__ == "__main__":
    test_spec_declares_shadow_preflight_no_enablement_boundary()
    test_shadow_preflight_ready_when_clean_fresh_no_lock_and_disabled_task_visible()
    test_shadow_preflight_accepts_q21w_nested_task_readback_shape()
    test_shadow_preflight_blocks_without_recovering_on_stale_lock_dirty_or_bad_task()
    test_tool_is_read_only_no_enablement_no_write_no_runner_invocation()
    print('{"ok": true}')
