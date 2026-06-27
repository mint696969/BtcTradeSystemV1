# path: ./tools/test_phase4a_prediction_system_ps_q21z_bounded_manual_freshness_recovery_execute_existing_q21i_once.py
# desc: Focused guard for PS-Q21Z gated one-shot wrapper around existing PS-Q21I bounded manual freshness recovery.

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.run_phase4a_prediction_system_ps_q21i_one_shot_bounded_manual_latest_prediction_write import (  # noqa: E402
    REQUIRED_CONFIRMATION as Q21I_REQUIRED_CONFIRMATION,
)
from tools.run_phase4a_prediction_system_ps_q21z_bounded_manual_freshness_recovery_execute_existing_q21i_once import (  # noqa: E402
    RECOVERY_VERSION,
    run_bounded_manual_freshness_recovery_once,
)
from tools.verify_phase4a_prediction_system_ps_q21u_scheduler_producer_registration_preflight import (  # noqa: E402
    REQUIRED_NEXT_PRODUCER_CONFIRMATION,
)

TOOL = REPO_ROOT / "tools/run_phase4a_prediction_system_ps_q21z_bounded_manual_freshness_recovery_execute_existing_q21i_once.py"
SPEC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q21Z_BOUNDED_MANUAL_FRESHNESS_RECOVERY_EXECUTE_EXISTING_Q21I_ONCE_2026-06-27.md"

REQUIRED_MARKERS = (
    "ps_q21z_bounded_manual_freshness_recovery_execute_existing_q21i_once=true",
    "default_execution_is_dry_run_no_write=true",
    "execute_existing_q21i_once_requires_confirmation=WRITE_D_HOT_LATEST_PREDICTION_ONCE",
    "requires_operator_acknowledged_flag=true",
    "requires_execute_existing_q21i_once_flag=true",
    "requires_q21y_ready_for_operator_token=true",
    "producer_loop_shadow_once_still_separate=true",
    "recurring_enablement_allowed_now=false",
)

FALSE_BOUNDARIES = (
    "producer_loop_enabled=false",
    "producer_runner_invoked=false",
    "scheduled_loop_enabled=false",
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


def _q21y(**overrides: object) -> dict:
    data = {
        "ok": True,
        "preflight_state": "freshness_recovery_preflight_ready_for_operator_token_no_write",
        "freshness_recovery_ready_for_operator_token": True,
        "freshness_recovery_blockers": [],
        "repo_clean": True,
        "latest_prediction_non_stale": False,
        "latest_status_success_observed": True,
        "d_hot_lock_artifact_exists": False,
    }
    data.update(overrides)
    return data


def _successful_q21i(**overrides: object) -> dict:
    data = {
        "ok": True,
        "success": True,
        "runner_state": "bounded_manual_refresh_exported_status_written",
        "latest_prediction_artifact_written": True,
        "status_artifact_written": True,
        "prediction_run_id": "prediction_system.ps_g_lite.v1:BTC_JPY:bitFlyer:2026-06-27T00:00:00Z",
        "generated_at": "2026-06-27T00:00:00Z",
        "latest_prediction_artifact_path": r"D:\btc_ts_hot\prediction\latest_prediction_system_result.json",
        "status_artifact_path": r"D:\btc_ts_hot\prediction\status\non_ui_scheduled_producer_status.json",
        "scheduler_enablement_allowed": False,
        "producer_enablement_allowed": False,
        "warroom_ui_trigger_allowed": False,
        "autotrade_trigger_allowed": False,
        "broker_private_api_allowed": False,
        "would_send_to_broker": False,
    }
    data.update(overrides)
    return data


def test_spec_declares_gated_existing_q21i_execution_boundary() -> None:
    text = SPEC.read_text(encoding="utf-8-sig")
    for marker in REQUIRED_MARKERS:
        assert marker in text, marker
    for marker in FALSE_BOUNDARIES:
        assert marker in text, marker


def test_default_is_dry_run_no_q21i_invocation_or_write() -> None:
    called = {"value": False}

    def fake_q21i(**_: object) -> dict:
        called["value"] = True
        raise AssertionError("Q21I must not be called by default")

    result = run_bounded_manual_freshness_recovery_once(q21y_packet=_q21y(), q21i_runner=fake_q21i)
    assert result["ok"] is True
    assert result["recovery_version"] == RECOVERY_VERSION
    assert result["recovery_state"] == "bounded_manual_freshness_recovery_blocked_no_write"
    assert "operator_acknowledgement_required" in result["blocked_reasons"]
    assert "execute_existing_q21i_once_flag_required" in result["blocked_reasons"]
    assert "exact_q21i_confirmation_token_required" in result["blocked_reasons"]
    assert result["q21i_runner_invoked"] is False
    assert result["latest_prediction_artifact_written"] is False
    assert result["status_artifact_written"] is False
    assert called["value"] is False


def test_execute_blocks_without_q21y_ready_or_confirmation() -> None:
    result = run_bounded_manual_freshness_recovery_once(
        operator_acknowledged=True,
        execute_existing_q21i_once=True,
        confirmation="wrong",
        q21y_packet=_q21y(freshness_recovery_ready_for_operator_token=False, freshness_recovery_blockers=["repo_clean_required_before_manual_freshness_recovery"], repo_clean=False),
        q21i_runner=lambda **_: _successful_q21i(),
    )
    assert result["success"] is False
    assert "exact_q21i_confirmation_token_required" in result["blocked_reasons"]
    assert "q21y_ready_for_operator_token_required" in result["blocked_reasons"]
    assert "q21y_blockers_must_be_empty" in result["blocked_reasons"]
    assert "repo_clean_required_before_existing_q21i_execution" in result["blocked_reasons"]
    assert result["q21i_runner_invoked"] is False
    assert result["producer_loop_enabled"] is False
    assert result["would_send_to_broker"] is False


def test_execute_with_exact_token_invokes_existing_q21i_once_via_fake_runner() -> None:
    calls: list[dict[str, object]] = []

    def fake_q21i(**kwargs: object) -> dict:
        calls.append(dict(kwargs))
        return _successful_q21i()

    result = run_bounded_manual_freshness_recovery_once(
        operator_acknowledged=True,
        execute_existing_q21i_once=True,
        confirmation=Q21I_REQUIRED_CONFIRMATION,
        q21y_packet=_q21y(),
        q21i_runner=fake_q21i,
    )
    assert result["success"] is True
    assert result["recovery_state"] == "bounded_manual_freshness_recovery_executed_existing_q21i_once"
    assert result["q21i_runner_invoked"] is True
    assert len(calls) == 1
    assert calls[0]["operator_acknowledged"] is True
    assert calls[0]["execute_one_shot_write"] is True
    assert calls[0]["confirmation"] == Q21I_REQUIRED_CONFIRMATION
    assert result["latest_prediction_artifact_written"] is True
    assert result["status_artifact_written"] is True
    assert result["required_next_producer_confirmation"] == REQUIRED_NEXT_PRODUCER_CONFIRMATION
    assert result["producer_loop_shadow_once_still_separate"] is True
    assert result["producer_loop_enabled"] is False
    assert result["producer_runner_invoked"] is False
    assert result["recurring_enablement_allowed_now"] is False
    assert result["broker_private_api_allowed"] is False
    assert result["would_send_to_broker"] is False


def test_tool_gates_q21i_and_contains_no_scheduler_or_broker_enablement() -> None:
    text = TOOL.read_text(encoding="utf-8")
    assert "Q21I_REQUIRED_CONFIRMATION" in text
    assert "execute_existing_q21i_once" in text
    assert "run_one_shot_write" in text
    forbidden = (
        "request_scheduler_enable=True",
        "Register-ScheduledTask",
        "Enable-ScheduledTask",
        "New-ScheduledTaskTrigger",
        "Start-ScheduledTask",
        "send_order(",
        "place_order(",
        "request_approval_or_ledger_or_autotrade_or_broker=True",
    )
    for token in forbidden:
        assert token not in text, token


if __name__ == "__main__":
    test_spec_declares_gated_existing_q21i_execution_boundary()
    test_default_is_dry_run_no_q21i_invocation_or_write()
    test_execute_blocks_without_q21y_ready_or_confirmation()
    test_execute_with_exact_token_invokes_existing_q21i_once_via_fake_runner()
    test_tool_gates_q21i_and_contains_no_scheduler_or_broker_enablement()
    print('{"ok": true}')
