# path: ./tools/test_phase4a_prediction_system_ps_q23f_q22s_optional_sidecar_hook.py
# desc: Focused guard for PS-Q23F optional Q22S distributed sidecar hook.

from __future__ import annotations

import json
from pathlib import Path
import sys
from typing import Any, Mapping

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.diagnose_phase4a_prediction_system_ps_q22m_mountain2_recurring_trigger_prep_no_enablement import FUTURE_MOUNTAIN2_TOKEN_CANDIDATE  # noqa: E402
from tools.run_phase4a_prediction_system_ps_q22s_mountain2_actual_scheduled_latest_refresh_tick_once import (  # noqa: E402
    REQUIRED_DISTRIBUTED_SIDECAR_CONFIRMATION,
    run_mountain2_actual_scheduled_latest_refresh_tick_once,
)

SPEC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q23F_Q22S_OPTIONAL_SIDECAR_HOOK_2026-06-28.md"
Q22S = REPO_ROOT / "tools/run_phase4a_prediction_system_ps_q22s_mountain2_actual_scheduled_latest_refresh_tick_once.py"


def _ready() -> dict:
    return {
        "readiness_state": "post_enablement_tick_readiness_ready",
        "post_enablement_tick_ready": True,
        "readiness_blockers": [],
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
    return {"success": True, "latest_prediction_artifact_written": False, "status_artifact_written": True}


def _sidecar_success(**kwargs: object) -> Mapping[str, Any]:
    hot_root = kwargs.get("hot_root")
    assert isinstance(hot_root, Path)
    assert not (hot_root / "prediction/runtime/non_ui_scheduler_producer.lock.json").exists()
    assert kwargs.get("operator_acknowledged") is True
    assert kwargs.get("execute_sidecar_write_once") is True
    assert kwargs.get("confirmation") == REQUIRED_DISTRIBUTED_SIDECAR_CONFIRMATION
    return {
        "ok": True,
        "success": True,
        "latest_manifest_written": True,
        "run_sidecars_written": True,
        "latest_prediction_artifact_written": False,
        "legacy_latest_modified": False,
        "status_artifact_written": False,
        "would_send_to_broker": False,
        "broker_private_api_allowed": False,
        "autotrade_trigger_allowed": False,
    }


def _sidecar_blocked(**_: object) -> Mapping[str, Any]:
    return {
        "ok": True,
        "success": False,
        "blocked_reasons": ["exact_distributed_sidecar_write_confirmation_required"],
        "latest_manifest_written": False,
        "run_sidecars_written": False,
        "latest_prediction_artifact_written": False,
        "legacy_latest_modified": False,
        "status_artifact_written": False,
        "would_send_to_broker": False,
        "broker_private_api_allowed": False,
        "autotrade_trigger_allowed": False,
    }


def _run(root: Path, **kwargs: object) -> dict:
    return run_mountain2_actual_scheduled_latest_refresh_tick_once(
        operator_acknowledged=True,
        execute_tick_once=True,
        confirmation=FUTURE_MOUNTAIN2_TOKEN_CANDIDATE,
        hot_root=root,
        readiness_provider=_ready,
        q21i_runner=_refresh_ok,
        q22e_runner=_q22e_ok,
        repo_status_short="",
        **kwargs,
    )


def test_spec_declares_optional_hook_contract() -> None:
    text = SPEC.read_text(encoding="utf-8-sig")
    for marker in (
        "ps_q23f_q22s_optional_sidecar_hook=true",
        "q22s_sidecar_hook_added=true",
        "sidecar_hook_default_disabled=true",
        "exact_sidecar_confirmation_required=true",
        "scheduler_action_changed=false",
        "scheduled_sidecar_write_enabled=false",
        "legacy_latest_refresh_semantics_preserved=true",
        "broker_autotrade=false",
    ):
        assert marker in text, marker


def test_default_q22s_does_not_invoke_sidecar_writer(tmp_path: Path) -> None:
    root = _setup_hot(tmp_path)
    called = {"sidecar": False}
    def sidecar(**_: object) -> Mapping[str, Any]:
        called["sidecar"] = True
        return _sidecar_success()
    result = _run(root, sidecar_writer=sidecar)
    assert result["success"] is True
    assert result["sidecar_dual_write_requested"] is False
    assert result["sidecar_dual_write_executed"] is False
    assert result["sidecar_dual_write_success"] is False
    assert result["latest_manifest_written"] is False
    assert result["run_sidecars_written"] is False
    assert called["sidecar"] is False


def test_enabled_hook_runs_after_lock_release_and_preserves_main_tick_success(tmp_path: Path) -> None:
    root = _setup_hot(tmp_path)
    result = _run(
        root,
        enable_distributed_sidecar_dual_write=True,
        distributed_sidecar_confirmation=REQUIRED_DISTRIBUTED_SIDECAR_CONFIRMATION,
        sidecar_writer=_sidecar_success,
    )
    assert result["success"] is True
    assert result["tick_state"] == "mountain2_actual_tick_completed_one_bounded_refresh"
    assert result["lock_released"] is True
    assert result["sidecar_dual_write_requested"] is True
    assert result["sidecar_dual_write_executed"] is True
    assert result["sidecar_dual_write_success"] is True
    assert result["latest_manifest_written"] is True
    assert result["run_sidecars_written"] is True
    assert result["sidecar_dual_write_result"]["status_artifact_written"] is False
    assert result["sidecar_dual_write_result"]["latest_prediction_artifact_written"] is False
    assert result["would_send_to_broker"] is False


def test_enabled_hook_with_bad_token_reports_warning_but_keeps_legacy_tick_success(tmp_path: Path) -> None:
    root = _setup_hot(tmp_path)
    result = _run(
        root,
        enable_distributed_sidecar_dual_write=True,
        distributed_sidecar_confirmation="WRONG",
        sidecar_writer=_sidecar_blocked,
    )
    assert result["success"] is True
    assert result["sidecar_dual_write_requested"] is True
    assert result["sidecar_dual_write_executed"] is True
    assert result["sidecar_dual_write_success"] is False
    assert result["sidecar_dual_write_warning"] is True
    assert "distributed_sidecar_dual_write_failed_or_blocked" in result["warning_reasons"]
    assert result["latest_prediction_artifact_written"] is True
    assert result["status_artifact_written"] is True
    assert result["latest_manifest_written"] is False
    assert result["run_sidecars_written"] is False


def test_q22s_tool_does_not_change_scheduler_action_or_broker_boundaries() -> None:
    text = Q22S.read_text(encoding="utf-8")
    for forbidden in (
        "Enable-ScheduledTask",
        "New-ScheduledTaskTrigger",
        "Register-ScheduledTask",
        "Start-ScheduledTask",
        "Set-ScheduledTask",
        "send_order(",
        "place_order(",
    ):
        assert forbidden not in text, forbidden
    assert "--enable-distributed-sidecar-dual-write" in text
    assert "REQUIRED_DISTRIBUTED_SIDECAR_CONFIRMATION" in text


if __name__ == "__main__":
    test_spec_declares_optional_hook_contract()
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        test_default_q22s_does_not_invoke_sidecar_writer(Path(tmp))
    with tempfile.TemporaryDirectory() as tmp:
        test_enabled_hook_runs_after_lock_release_and_preserves_main_tick_success(Path(tmp))
    with tempfile.TemporaryDirectory() as tmp:
        test_enabled_hook_with_bad_token_reports_warning_but_keeps_legacy_tick_success(Path(tmp))
    test_q22s_tool_does_not_change_scheduler_action_or_broker_boundaries()
    print(json.dumps({"ok": True}))
