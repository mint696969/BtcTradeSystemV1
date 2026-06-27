# path: ./tools/test_phase4a_prediction_system_ps_q22a_producer_loop_shadow_once.py
# desc: Focused guard for PS-Q22A producer-loop shadow once wrapper. Default no-write; exact token required.

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.run_phase4a_prediction_system_ps_q22a_producer_loop_shadow_once import (  # noqa: E402
    SHADOW_ONCE_VERSION,
    run_producer_loop_shadow_once,
)
from tools.verify_phase4a_prediction_system_ps_q21u_scheduler_producer_registration_preflight import REQUIRED_NEXT_PRODUCER_CONFIRMATION  # noqa: E402

SPEC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q22A_PRODUCER_LOOP_SHADOW_ONCE_WRAPPER_2026-06-27.md"
TOOL = REPO_ROOT / "tools/run_phase4a_prediction_system_ps_q22a_producer_loop_shadow_once.py"


def _q21x(**overrides: object) -> dict:
    data = {
        "ok": True,
        "shadow_preflight_ready_for_one_shot": True,
        "shadow_preflight_blockers": [],
        "latest_prediction_non_stale": True,
        "latest_status_success_observed": True,
        "d_hot_lock_artifact_exists": False,
        "task_state": "Disabled",
        "task_trigger_count": 0,
        "producer_runner_invoked": False,
        "producer_loop_enabled": False,
        "would_send_to_broker": False,
    }
    data.update(overrides)
    return data


def _runner(**_: object) -> dict:
    return {
        "status_artifact_written": True,
        "status_artifact_path": r"D:\btc_ts_hot\prediction\status\non_ui_scheduled_producer_status.json",
        "runner_state": "producer_disabled_status_written",
        "producer_enabled": False,
        "scheduler_enabled": False,
        "would_send_to_broker": False,
    }


def test_spec_declares_exact_token_status_only_shadow_boundary() -> None:
    text = SPEC.read_text(encoding="utf-8-sig")
    for marker in (
        "ps_q22a_producer_loop_shadow_once_wrapper=true",
        "default_execution_is_dry_run_no_write=true",
        "execute_shadow_once_requires_confirmation=ENABLE_DISABLED_PRODUCER_LOOP_SHADOW_ONCE_WITH_ROLLBACK_PLAN",
        "writes_latest_prediction_artifact=false",
        "recurring_enablement_allowed_now=false",
        "would_send_to_broker=false",
    ):
        assert marker in text, marker


def test_default_blocks_without_invoking_runner() -> None:
    called = {"value": False}
    def fake(**_: object) -> dict:
        called["value"] = True
        return _runner()
    result = run_producer_loop_shadow_once(q21x_packet=_q21x(), producer_runner=fake, repo_clean=True)
    assert result["shadow_once_state"] == "producer_loop_shadow_once_blocked_no_write"
    assert result["producer_runner_invoked"] is False
    assert "operator_acknowledgement_required" in result["blocked_reasons"]
    assert "execute_shadow_once_flag_required" in result["blocked_reasons"]
    assert "exact_shadow_once_confirmation_token_required" in result["blocked_reasons"]
    assert called["value"] is False


def test_blocks_when_q21x_not_ready() -> None:
    result = run_producer_loop_shadow_once(
        operator_acknowledged=True,
        execute_shadow_once=True,
        confirmation=REQUIRED_NEXT_PRODUCER_CONFIRMATION,
        q21x_packet=_q21x(shadow_preflight_ready_for_one_shot=False, shadow_preflight_blockers=["x"], latest_status_success_observed=False),
        producer_runner=_runner,
        repo_clean=True,
    )
    assert result["producer_runner_invoked"] is False
    assert "q21x_shadow_preflight_ready_required" in result["blocked_reasons"]
    assert "q21x_shadow_preflight_blockers_must_be_empty" in result["blocked_reasons"]
    assert "latest_status_success_required_before_shadow_once" in result["blocked_reasons"]


def test_exact_token_invokes_existing_disabled_runner_once_status_only() -> None:
    calls = []
    def fake(**kwargs: object) -> dict:
        calls.append(kwargs)
        return _runner()
    result = run_producer_loop_shadow_once(
        operator_acknowledged=True,
        execute_shadow_once=True,
        confirmation=REQUIRED_NEXT_PRODUCER_CONFIRMATION,
        q21x_packet=_q21x(),
        producer_runner=fake,
        repo_clean=True,
    )
    assert result["shadow_once_version"] == SHADOW_ONCE_VERSION
    assert result["success"] is True
    assert result["producer_runner_invoked"] is True
    assert len(calls) == 1
    assert calls[0]["operator_acknowledged"] is True
    assert calls[0]["allow_status_artifact_write"] is True
    assert calls[0]["execute_status_artifact_write"] is True
    assert result["status_artifact_written"] is True
    assert result["latest_prediction_artifact_written"] is False
    assert result["scheduler_enabled"] is False
    assert result["trigger_added"] is False
    assert result["would_send_to_broker"] is False


def test_tool_has_no_scheduler_trigger_broker_tokens() -> None:
    text = TOOL.read_text(encoding="utf-8")
    for token in ("Enable-ScheduledTask", "New-ScheduledTaskTrigger", "Start-ScheduledTask", "send_order(", "place_order("):
        assert token not in text, token
    assert "build_prediction_warroom_non_ui_scheduled_producer_runner" in text
    assert "ENABLE_DISABLED_PRODUCER_LOOP_SHADOW_ONCE_WITH_ROLLBACK_PLAN" in text


if __name__ == "__main__":
    test_spec_declares_exact_token_status_only_shadow_boundary()
    test_default_blocks_without_invoking_runner()
    test_blocks_when_q21x_not_ready()
    test_exact_token_invokes_existing_disabled_runner_once_status_only()
    test_tool_has_no_scheduler_trigger_broker_tokens()
    print(json.dumps({"ok": True}))
