# path: ./tools/test_phase4a_prediction_system_ps_q22o_mountain2_scheduled_latest_refresh_tick_once.py
# desc: Focused guard for PS-Q22O no-enable Mountain2 scheduled latest-refresh tick skeleton.

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.diagnose_phase4a_prediction_system_ps_q22m_mountain2_recurring_trigger_prep_no_enablement import (  # noqa: E402
    FUTURE_MOUNTAIN2_TOKEN_CANDIDATE,
)
from tools.design_phase4a_prediction_system_ps_q22n_mountain2_scheduled_tick_contract_no_enablement import (  # noqa: E402
    CONTRACT_VERSION as Q22N_CONTRACT_VERSION,
    FUTURE_TICK_NAME,
)
from tools.run_phase4a_prediction_system_ps_q22o_mountain2_scheduled_latest_refresh_tick_once import (  # noqa: E402
    RUNNER_VERSION,
    build_mountain2_tick_runner_skeleton,
    run_mountain2_tick_runner_skeleton,
)

SPEC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q22O_MOUNTAIN2_TICK_RUNNER_SKELETON_NO_ENABLEMENT_2026-06-27.md"
TOOL = REPO_ROOT / "tools/run_phase4a_prediction_system_ps_q22o_mountain2_scheduled_latest_refresh_tick_once.py"


def _q22n(**overrides: object) -> dict:
    data = {
        "contract_version": Q22N_CONTRACT_VERSION,
        "contract_state": "mountain2_scheduled_tick_contract_ready_no_enablement",
        "contract_ready_for_future_no_enable_runner_skeleton": True,
        "contract_blockers": [],
        "contract_warnings": [],
        "scheduler_enabled": False,
        "trigger_added": False,
        "future_tick_contract": {
            "future_tick_name": FUTURE_TICK_NAME,
            "must_acquire_non_overlap_lock_before_latest_read_or_write": True,
            "must_run_one_bounded_latest_refresh_per_tick": True,
        },
    }
    data.update(overrides)
    return data


def test_spec_declares_no_enablement_skeleton() -> None:
    text = SPEC.read_text(encoding="utf-8-sig")
    for marker in (
        "ps_q22o_mountain2_tick_runner_skeleton_no_enablement=true",
        "default_dry_run_no_write=true",
        "execute_request_blocks_by_design=true",
        "no_scheduler_enablement=true",
        "no_trigger_addition=true",
        "no_recurring_or_periodic_execution=true",
        "no_latest_prediction_artifact_write=true",
        "no_status_artifact_write=true",
        "no_lock_acquire=true",
        "scheduler_enabled=false",
        "trigger_added=false",
        "would_send_to_broker=false",
    ):
        assert marker in text, marker


def test_default_skeleton_ready_does_not_execute_any_runtime_action() -> None:
    result = build_mountain2_tick_runner_skeleton(q22n_packet=_q22n())
    assert result["runner_version"] == RUNNER_VERSION
    assert result["runner_state"] == "mountain2_tick_runner_skeleton_ready_no_enablement"
    assert result["runner_ready_for_future_danger_boundary_review"] is True
    assert result["request_execute_tick_once"] is False
    assert result["future_runtime_steps_not_executed"]["would_write_latest_prediction"] is True
    assert result["scheduler_enabled"] is False
    assert result["trigger_added"] is False
    assert result["recurring_enablement_allowed_now"] is False
    assert result["periodic_execution_enabled"] is False
    assert result["latest_prediction_artifact_written"] is False
    assert result["status_artifact_written"] is False
    assert result["lock_acquire_attempted"] is False
    assert result["producer_runner_invoked"] is False
    assert result["would_send_to_broker"] is False


def test_execute_request_and_future_token_are_blocked_by_design() -> None:
    result = build_mountain2_tick_runner_skeleton(
        q22n_packet=_q22n(),
        operator_acknowledged=True,
        request_execute_tick_once=True,
        future_enablement_confirmation=FUTURE_MOUNTAIN2_TOKEN_CANDIDATE,
    )
    assert result["runner_state"] == "mountain2_tick_runner_execution_blocked_no_write"
    assert "ps_q22o_blocks_execute_tick_once_by_design" in result["blocked_reasons"]
    assert "future_enablement_token_detected_but_ps_q22o_must_not_use_it" in result["blocked_reasons"]
    assert result["latest_prediction_artifact_written"] is False
    assert result["lock_acquire_attempted"] is False
    assert result["scheduler_enabled"] is False
    assert result["trigger_added"] is False


def test_provider_path_does_not_require_runtime_write() -> None:
    result = run_mountain2_tick_runner_skeleton(q22n_provider=lambda: _q22n())
    assert result["runner_ready_for_future_danger_boundary_review"] is True
    assert result["actual_export_runner_invoked"] is False
    assert result["bounded_manual_refresh_invoked"] is False
    assert result["latest_prediction_artifact_written"] is False


def test_tool_contains_no_scheduler_runtime_write_or_broker_commands() -> None:
    text = TOOL.read_text(encoding="utf-8")
    for token in (
        "Enable-ScheduledTask",
        "New-ScheduledTaskTrigger",
        "Start-ScheduledTask",
        "Register-ScheduledTask",
        "run_one_shot_write",
        "run_bounded_manual_freshness_recovery_once",
        "execute_one_shot_write=True",
        "allow_runtime_artifact_write=True",
        "execute_status_write_once=True",
        "_write_json_atomic",
        ".write_text(",
        "Path.replace(",
        "os.replace(",
        "tmp.replace(",
        "target.replace(",
        "send_order(",
        "place_order(",
    ):
        assert token not in text, token


if __name__ == "__main__":
    test_spec_declares_no_enablement_skeleton()
    test_default_skeleton_ready_does_not_execute_any_runtime_action()
    test_execute_request_and_future_token_are_blocked_by_design()
    test_provider_path_does_not_require_runtime_write()
    test_tool_contains_no_scheduler_runtime_write_or_broker_commands()
    print(json.dumps({"ok": True}))
