# path: ./tools/test_phase4a_prediction_system_ps_q21y_freshness_recovery_preflight_no_write.py
# desc: Focused guard for PS-Q21Y freshness recovery preflight no-write command preparation.

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.run_phase4a_prediction_system_ps_q21i_one_shot_bounded_manual_latest_prediction_write import (  # noqa: E402
    REQUIRED_CONFIRMATION as Q21I_REQUIRED_CONFIRMATION,
)
from tools.verify_phase4a_prediction_system_ps_q21u_scheduler_producer_registration_preflight import (  # noqa: E402
    REQUIRED_NEXT_PRODUCER_CONFIRMATION,
)
from tools.verify_phase4a_prediction_system_ps_q21y_freshness_recovery_preflight_no_write import (  # noqa: E402
    EXPECTED_Q21X_STALE_BLOCKER,
    FRESHNESS_PREFLIGHT_VERSION,
    build_freshness_recovery_preflight,
)

TOOL = REPO_ROOT / "tools/verify_phase4a_prediction_system_ps_q21y_freshness_recovery_preflight_no_write.py"
SPEC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q21Y_FRESHNESS_RECOVERY_PREFLIGHT_NO_WRITE_2026-06-27.md"

REQUIRED_MARKERS = (
    "ps_q21y_freshness_recovery_preflight_no_write=true",
    "read_only_freshness_recovery_preflight_only=true",
    "manual_refresh_command_prepared_only=true",
    "manual_refresh_execute_allowed_now=false",
    "requires_existing_q21i_confirmation_token=WRITE_D_HOT_LATEST_PREDICTION_ONCE",
    "producer_loop_shadow_once_still_separate=true",
    "recurring_enablement_allowed_now=false",
)

FALSE_BOUNDARIES = (
    "manual_refresh_runner_invoked=false",
    "latest_prediction_artifact_written=false",
    "status_artifact_written=false",
    "runtime_artifact_write_allowed=false",
    "status_artifact_write_allowed=false",
    "prediction_artifact_write_allowed=false",
    "producer_loop_enabled=false",
    "producer_runner_invoked=false",
    "scheduler_enabled=false",
    "scheduler_enablement_allowed_now=false",
    "trigger_added=false",
    "trigger_addition_allowed_now=false",
    "recurring_enablement_allowed_now=false",
    "warroom_ui_trigger_allowed=false",
    "approval_or_ledger_allowed=false",
    "parameter_apply_allowed=false",
    "parameter_staging_write_allowed=false",
    "autotrade_trigger_allowed=false",
    "broker_private_api_allowed=false",
    "would_send_to_broker=false",
    "would_write_collector_state=false",
)


def _q21x(**overrides: object) -> dict:
    data = {
        "ok": True,
        "preflight_state": "producer_loop_shadow_preflight_blocked_no_enablement",
        "shadow_preflight_ready_for_one_shot": False,
        "shadow_preflight_blockers": [EXPECTED_Q21X_STALE_BLOCKER],
        "repo_clean": True,
        "generated_at": "2026-06-26T15:01:38Z",
        "age_sec": 38448,
        "latest_prediction_non_stale": False,
        "latest_status_success_observed": True,
        "d_hot_lock_artifact_exists": False,
        "task_exists": True,
        "task_name": "BTC_TS_PredictionWarRoom_NonUI_DisabledScheduler",
        "task_path": "\\BtcTradeSystem\\",
        "task_state": "Disabled",
        "task_trigger_count": 0,
        "task_recognized_as_ps_q21w": True,
        "producer_runner_invoked": False,
        "producer_loop_enabled": False,
        "scheduler_enablement_allowed_now": False,
        "trigger_addition_allowed_now": False,
        "status_warnings": ["prediction_result_warnings_present:19"],
        "status_blockers": [],
    }
    data.update(overrides)
    return data


def test_spec_declares_no_write_command_preparation_boundary() -> None:
    text = SPEC.read_text(encoding="utf-8-sig")
    for marker in REQUIRED_MARKERS:
        assert marker in text, marker
    for marker in FALSE_BOUNDARIES:
        assert marker in text, marker


def test_preflight_ready_when_q21x_blocked_only_by_stale_prediction() -> None:
    result = build_freshness_recovery_preflight(q21x_packet=_q21x())
    assert result["ok"] is True
    assert result["preflight_version"] == FRESHNESS_PREFLIGHT_VERSION
    assert result["preflight_state"] == "freshness_recovery_preflight_ready_for_operator_token_no_write"
    assert result["freshness_recovery_ready_for_operator_token"] is True
    assert result["freshness_recovery_blockers"] == []
    assert result["manual_refresh_confirmation_required"] == Q21I_REQUIRED_CONFIRMATION
    assert result["producer_loop_shadow_once_requires_confirmation"] == REQUIRED_NEXT_PRODUCER_CONFIRMATION
    assert result["prepared_command_is_not_executed_by_q21y"] is True
    assert "--confirmation" in result["prepared_command"]
    assert Q21I_REQUIRED_CONFIRMATION in result["prepared_command"]
    assert result["manual_refresh_runner_invoked"] is False
    assert result["latest_prediction_artifact_written"] is False
    assert result["status_artifact_written"] is False
    assert result["recurring_enablement_allowed_now"] is False
    assert result["would_send_to_broker"] is False


def test_preflight_blocks_on_unexpected_q21x_blockers_or_non_stale_state() -> None:
    result = build_freshness_recovery_preflight(
        q21x_packet=_q21x(
            latest_prediction_non_stale=True,
            shadow_preflight_blockers=[EXPECTED_Q21X_STALE_BLOCKER, "d_hot_lock_absent_required_before_shadow_once"],
            d_hot_lock_artifact_exists=True,
            task_state="Ready",
        )
    )
    assert result["preflight_state"] == "freshness_recovery_preflight_blocked_no_write"
    assert result["freshness_recovery_ready_for_operator_token"] is False
    assert "latest_prediction_already_non_stale_manual_recovery_not_needed" in result["freshness_recovery_blockers"]
    assert "q21x_must_be_blocked_only_by_latest_prediction_stale" in result["freshness_recovery_blockers"]
    assert "d_hot_lock_absent_required_before_manual_freshness_recovery" in result["freshness_recovery_blockers"]
    assert "ps_q21w_task_state_disabled_required" in result["freshness_recovery_blockers"]
    assert result["manual_refresh_execute_allowed_now"] is False
    assert result["latest_prediction_artifact_written"] is False
    assert result["status_artifact_written"] is False


def test_tool_is_read_only_no_write_and_does_not_invoke_q21i_runner() -> None:
    text = TOOL.read_text(encoding="utf-8")
    forbidden = (
        "run_one_shot_write(",
        "execute_one_shot_write=True",
        "operator_acknowledged=True",
        "allow_runtime_artifact_write=True",
        "allow_status_artifact_write=True",
        "write_text(",
        "open(\"w",
        ".touch(",
        ".unlink(",
        "Path.replace(",
        "os.replace(",
        "request_scheduler_enable=True",
        "Register-ScheduledTask",
        "Enable-ScheduledTask",
        "New-ScheduledTaskTrigger",
        "Start-ScheduledTask",
        "send_order(",
        "place_order(",
        "BTC_TS_DATA_DIR",
    )
    for token in forbidden:
        assert token not in text, token
    assert "run_shadow_preflight" in text
    assert "Q21I_REQUIRED_CONFIRMATION" in text
    assert "prepared_command" in text
    assert "print(json.dumps" in text


if __name__ == "__main__":
    test_spec_declares_no_write_command_preparation_boundary()
    test_preflight_ready_when_q21x_blocked_only_by_stale_prediction()
    test_preflight_blocks_on_unexpected_q21x_blockers_or_non_stale_state()
    test_tool_is_read_only_no_write_and_does_not_invoke_q21i_runner()
    print('{"ok": true}')
