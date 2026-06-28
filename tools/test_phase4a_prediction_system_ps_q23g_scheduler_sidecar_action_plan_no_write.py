# path: ./tools/test_phase4a_prediction_system_ps_q23g_scheduler_sidecar_action_plan_no_write.py
# desc: Focused guard for PS-Q23G scheduler sidecar action plan no-write diagnostic.

from __future__ import annotations

import json
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.diagnose_phase4a_prediction_system_ps_q23g_scheduler_sidecar_action_plan_no_write import (  # noqa: E402
    DIAGNOSTIC_VERSION,
    SIDECAR_CONFIRMATION_FLAG,
    SIDECAR_ENABLE_FLAG,
    build_scheduler_sidecar_action_plan,
    candidate_silent_launcher_sidecar_args,
    expected_silent_launcher_args,
)
from tools.run_phase4a_prediction_system_ps_q21w_register_disabled_scheduler_once import TASK_NAME, TASK_PATH  # noqa: E402
from tools.run_phase4a_prediction_system_ps_q23b_gated_dual_write_sidecars_once import REQUIRED_CONFIRMATION as REQUIRED_DISTRIBUTED_SIDECAR_CONFIRMATION  # noqa: E402

SPEC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q23G_SCHEDULER_SIDECAR_ACTION_PLAN_NO_WRITE_2026-06-28.md"
TOOL = REPO_ROOT / "tools/diagnose_phase4a_prediction_system_ps_q23g_scheduler_sidecar_action_plan_no_write.py"


def _task(args: str | None = None, execute: str = r"C:\BtcTradeSystem\.venv\Scripts\pythonw.exe") -> dict:
    return {
        "ok": True,
        "task_exists": True,
        "task_name": TASK_NAME,
        "task_path": TASK_PATH,
        "state": "Ready",
        "action_execute": execute,
        "action_arguments": args or expected_silent_launcher_args(),
        "trigger_count": 1,
    }


def _q22v_ready() -> dict:
    return {"readiness_state": "post_enablement_tick_readiness_ready", "post_enablement_tick_ready": True}


def test_spec_declares_no_write_scheduler_plan_contract() -> None:
    text = SPEC.read_text(encoding="utf-8-sig")
    for marker in (
        "ps_q23g_scheduler_sidecar_action_plan_no_write=true",
        "reads_scheduler_task=true",
        "scheduler_action_replacement_executed=false",
        "scheduled_sidecar_write_enabled=false",
        "candidate_action_only=true",
        "broker_autotrade=false",
    ):
        assert marker in text, marker


def test_candidate_args_add_exact_sidecar_flags() -> None:
    expected = expected_silent_launcher_args()
    candidate = candidate_silent_launcher_sidecar_args()
    assert candidate.startswith(expected)
    assert SIDECAR_ENABLE_FLAG in candidate
    assert SIDECAR_CONFIRMATION_FLAG in candidate
    assert REQUIRED_DISTRIBUTED_SIDECAR_CONFIRMATION in candidate


def test_plan_ready_when_current_action_is_q22x_silent_launcher() -> None:
    result = build_scheduler_sidecar_action_plan(repo_status_short="", scheduler_task=_task(), q22v_readiness=_q22v_ready())
    assert result["diagnostic_version"] == DIAGNOSTIC_VERSION
    assert result["plan_ready_for_future_scheduler_action_replacement"] is True
    assert result["plan_state"] == "scheduler_sidecar_action_plan_ready_no_write"
    assert result["blockers"] == []
    assert result["candidate_action_adds_sidecar_flags"] is True
    assert result["scheduler_action_replacement_executed"] is False
    assert result["scheduled_sidecar_write_enabled"] is False
    assert result["latest_manifest_written"] is False
    assert result["run_sidecars_written"] is False
    assert result["would_send_to_broker"] is False


def test_plan_blocks_when_repo_dirty_or_scheduler_not_silent() -> None:
    result = build_scheduler_sidecar_action_plan(
        repo_status_short=" M some.py",
        scheduler_task=_task(args='"C:/BtcTradeSystem/tools/run_phase4a_prediction_system_ps_q22s_mountain2_actual_scheduled_latest_refresh_tick_once.py"'),
        q22v_readiness={"readiness_state": "blocked", "post_enablement_tick_ready": False},
    )
    assert result["plan_ready_for_future_scheduler_action_replacement"] is False
    assert "repo_clean_required_before_scheduler_sidecar_action_plan" in result["blockers"]
    assert "scheduler_action_arguments_must_be_current_q22x_silent_launcher_without_sidecar_flags" in result["blockers"]
    assert "q22v_post_enablement_readiness_required" in result["blockers"]
    assert result["scheduler_action_replacement_executed"] is False


def test_tool_contains_no_scheduler_mutation_or_broker_calls() -> None:
    text = TOOL.read_text(encoding="utf-8")
    for forbidden in (
        "Set-ScheduledTask",
        "Enable-ScheduledTask",
        "Disable-ScheduledTask",
        "Register-ScheduledTask",
        "New-ScheduledTaskTrigger",
        "Start-ScheduledTask",
        "send_order(",
        "place_order(",
        ".write_text(",
        ".write_bytes(",
        "os.replace",
    ):
        assert forbidden not in text, forbidden
    assert "candidate_action_arguments" in text
    assert '"scheduler_action_replacement_executed": False' in text
    assert '"scheduled_sidecar_write_enabled": False' in text
    assert '"latest_manifest_written": False' in text
    assert '"run_sidecars_written": False' in text


if __name__ == "__main__":
    test_spec_declares_no_write_scheduler_plan_contract()
    test_candidate_args_add_exact_sidecar_flags()
    test_plan_ready_when_current_action_is_q22x_silent_launcher()
    test_plan_blocks_when_repo_dirty_or_scheduler_not_silent()
    test_tool_contains_no_scheduler_mutation_or_broker_calls()
    print(json.dumps({"ok": True}))
