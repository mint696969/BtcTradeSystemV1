# path: ./tools/test_phase4a_prediction_system_ps_q22s_mountain2_actual_scheduled_latest_refresh_tick_once.py
# desc: Focused guard for PS-Q22S actual Mountain2 one-tick runner. Tests use temp roots/fake runners; no D-hot writes.

from __future__ import annotations

import json
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.diagnose_phase4a_prediction_system_ps_q22m_mountain2_recurring_trigger_prep_no_enablement import FUTURE_MOUNTAIN2_TOKEN_CANDIDATE  # noqa: E402
from tools.run_phase4a_prediction_system_ps_q22s_mountain2_actual_scheduled_latest_refresh_tick_once import (  # noqa: E402
    RUNNER_VERSION,
    LOCK_RELATIVE_PATH,
    run_mountain2_actual_scheduled_latest_refresh_tick_once,
)

SPEC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q22S_MOUNTAIN2_ACTUAL_TICK_RUNNER_NO_SCHEDULER_ENABLEMENT_2026-06-28.md"
TOOL = REPO_ROOT / "tools/run_phase4a_prediction_system_ps_q22s_mountain2_actual_scheduled_latest_refresh_tick_once.py"


def _ready() -> dict:
    return {
        "readiness_state": "mountain2_final_pre_danger_boundary_ready_no_enablement",
        "readiness_blockers": [],
        "runtime_readiness_blockers": [],
        "safe_to_stop_before_danger_boundary": True,
        "repo_status_short": "",
    }


def _setup_hot(tmp_path: Path) -> Path:
    root = tmp_path / "hot"
    status = root / "prediction" / "status" / "non_ui_scheduled_producer_status.json"
    latest = root / "prediction" / "latest_prediction_system_result.json"
    status.parent.mkdir(parents=True, exist_ok=True)
    latest.parent.mkdir(parents=True, exist_ok=True)
    latest.write_text(json.dumps({"forecast_batch": {"generated_at": "2026-06-28T00:00:00Z", "records": [1]}}), encoding="utf-8")
    status.write_text(json.dumps({
        "producer_version": "prediction_warroom.success_preserving_status_write_once.ps_q22e.v1",
        "producer_state": "manual_refresh_exported_status_written",
        "producer_enabled": False,
        "scheduler_enabled": False,
        "last_success_generated_at": "2026-06-28T00:00:00Z",
        "last_prediction_run_id": "run",
        "consecutive_failure_count": 0,
        "blockers": [],
        "safe_flags": {
            "producer_enabled_false": True,
            "scheduler_enabled_false": True,
            "scheduled_loop_enabled_false": True,
            "warroom_ui_trigger_false": True,
            "autotrade_trigger_allowed_false": True,
            "broker_private_api_allowed_false": True,
            "would_send_to_broker_false": True,
        },
    }), encoding="utf-8")
    return root


def _refresh_ok(**_: object) -> dict:
    return {"success": True, "latest_prediction_artifact_written": True, "status_artifact_written": True, "warning_reasons": [], "generated_at": "2026-06-28T00:01:00Z"}


def _q22e_ok(**kwargs: object) -> dict:
    design = kwargs.get("design_packet")
    assert isinstance(design, dict)
    assert design.get("design_state") == "success_preserving_producer_status_design_ready_no_write"
    assert design.get("design_blockers") == []
    return {"success": True, "latest_prediction_artifact_written": False, "status_artifact_written": True}


def test_spec_declares_actual_tick_but_no_scheduler_enablement() -> None:
    text = SPEC.read_text(encoding="utf-8-sig")
    for marker in (
        "ps_q22s_mountain2_actual_tick_runner_no_scheduler_enablement=true",
        "actual_tick_runner_implemented=true",
        "default_execution_is_dry_run_no_write=true",
        "uses_d_hot_non_overlap_lock=true",
        "runs_one_bounded_latest_refresh_per_tick=true",
        "restores_q22e_status_observation=true",
        "no_scheduler_action_replacement=true",
        "no_scheduler_enablement=true",
        "no_trigger_addition=true",
        "no_recurring_or_periodic_execution_enablement=true",
    ):
        assert marker in text, marker


def test_default_blocks_no_write_no_runner_invocation(tmp_path: Path) -> None:
    called = {"refresh": False, "q22e": False}
    def refresh(**_: object) -> dict:
        called["refresh"] = True
        return _refresh_ok()
    def q22e(**_: object) -> dict:
        called["q22e"] = True
        return _q22e_ok()
    result = run_mountain2_actual_scheduled_latest_refresh_tick_once(hot_root=_setup_hot(tmp_path), readiness_provider=_ready, q21i_runner=refresh, q22e_runner=q22e)
    assert result["runner_version"] == RUNNER_VERSION
    assert result["tick_state"] == "mountain2_actual_tick_blocked_no_write"
    assert result["latest_prediction_artifact_written"] is False
    assert result["status_artifact_written"] is False
    assert result["lock_acquire_attempted"] is False
    assert called == {"refresh": False, "q22e": False}


def test_exact_token_executes_one_tick_with_lock_then_releases(tmp_path: Path) -> None:
    root = _setup_hot(tmp_path)
    result = run_mountain2_actual_scheduled_latest_refresh_tick_once(
        operator_acknowledged=True,
        execute_tick_once=True,
        confirmation=FUTURE_MOUNTAIN2_TOKEN_CANDIDATE,
        hot_root=root,
        readiness_provider=_ready,
        q21i_runner=_refresh_ok,
        q22e_runner=_q22e_ok,
        repo_status_short="",
    )
    assert result["success"] is True
    assert result["tick_state"] == "mountain2_actual_tick_completed_one_bounded_refresh"
    assert result["lock_acquire_attempted"] is True
    assert result["lock_acquired"] is True
    assert result["lock_released"] is True
    assert not (root / LOCK_RELATIVE_PATH).exists()
    assert result["latest_prediction_artifact_written"] is True
    assert result["status_artifact_written"] is True
    assert result["q22e_design"]["design_state"] == "success_preserving_producer_status_design_ready_no_write"
    assert result["scheduler_enabled"] is False
    assert result["trigger_added"] is False
    assert result["recurring_enablement_allowed_now"] is False
    assert result["would_send_to_broker"] is False
    assert result["sidecar_dual_write_requested"] is False
    assert result["sidecar_dual_write_executed"] is False
    assert result["latest_manifest_written"] is False
    assert result["run_sidecars_written"] is False


def test_active_lock_skips_and_writes_skip_status_without_refresh(tmp_path: Path) -> None:
    root = _setup_hot(tmp_path)
    lock = root / LOCK_RELATIVE_PATH
    lock.parent.mkdir(parents=True, exist_ok=True)
    lock.write_text(json.dumps({"run_id": "other", "started_at_utc": "2999-01-01T00:00:00Z", "expires_at_utc": "2999-01-01T00:10:00Z"}), encoding="utf-8")
    called = {"refresh": False}
    def refresh(**_: object) -> dict:
        called["refresh"] = True
        return _refresh_ok()
    result = run_mountain2_actual_scheduled_latest_refresh_tick_once(
        operator_acknowledged=True,
        execute_tick_once=True,
        confirmation=FUTURE_MOUNTAIN2_TOKEN_CANDIDATE,
        hot_root=root,
        readiness_provider=_ready,
        q21i_runner=refresh,
        q22e_runner=_q22e_ok,
        repo_status_short="",
    )
    assert result["tick_state"] == "mountain2_actual_tick_skipped_active_lock"
    assert result["lock_acquired"] is False
    assert result["latest_prediction_artifact_written"] is False
    assert result["status_artifact_written"] is True
    assert called["refresh"] is False


def test_tool_contains_no_scheduler_or_broker_enablement_tokens() -> None:
    text = TOOL.read_text(encoding="utf-8")
    for token in (
        "Enable-ScheduledTask",
        "New-ScheduledTaskTrigger",
        "Register-ScheduledTask",
        "Start-ScheduledTask",
        "send_order(",
        "place_order(",
        "request_approval_or_ledger_or_autotrade_or_broker=True",
    ):
        assert token not in text, token


if __name__ == "__main__":
    import tempfile
    with tempfile.TemporaryDirectory() as d:
        tmp = Path(d)
        test_spec_declares_actual_tick_but_no_scheduler_enablement()
        test_default_blocks_no_write_no_runner_invocation(tmp)
        test_exact_token_executes_one_tick_with_lock_then_releases(tmp)
        test_active_lock_skips_and_writes_skip_status_without_refresh(tmp)
        test_tool_contains_no_scheduler_or_broker_enablement_tokens()
    print(json.dumps({"ok": True}))
