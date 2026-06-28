# path: ./tools/test_phase4a_prediction_system_ps_q22x_silent_scheduler_launcher.py
# desc: Focused guard for PS-Q22X silent launcher and scheduler action switch.

from __future__ import annotations

import json
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.diagnose_phase4a_prediction_system_ps_q22v_post_enablement_tick_readiness import build_post_enablement_readiness  # noqa: E402
from tools.run_phase4a_prediction_system_ps_q22x_switch_scheduler_action_to_silent_once import (  # noqa: E402
    Q22X_TOOL,
    _direct_q22s_action_args,
    _silent_q22x_action_args,
    run_switch_to_silent_scheduler_action_once,
)

SPEC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q22X_SILENT_SCHEDULER_LAUNCHER_2026-06-28.md"
LAUNCHER = REPO_ROOT / "tools/run_phase4a_prediction_system_ps_q22x_silent_q22s_launcher.py"
SWITCH = REPO_ROOT / "tools/run_phase4a_prediction_system_ps_q22x_switch_scheduler_action_to_silent_once.py"


def _ready_packet() -> dict:
    return {"ok": True, "post_enablement_tick_ready": True, "readiness_blockers": [], "repo_status_short": ""}


def _fake_ps_runner(script: str) -> dict:
    assert "New-ScheduledTaskAction" in script
    assert "Set-ScheduledTask" in script
    assert "New-ScheduledTaskTrigger" not in script
    assert "Register-ScheduledTask" not in script
    return {
        "ok": True,
        "task_exists": True,
        "task_name": "BTC_TS_PredictionWarRoom_NonUI_DisabledScheduler",
        "task_path": "\\BtcTradeSystem\\",
        "state": "Ready",
        "action_execute": "C:\\BtcTradeSystem\\.venv\\Scripts\\pythonw.exe",
        "action_arguments": _silent_q22x_action_args(),
        "trigger_count": 1,
    }


def test_spec_declares_silent_contract() -> None:
    text = SPEC.read_text(encoding="utf-8-sig")
    for marker in (
        "ps_q22x_silent_scheduler_launcher=true",
        "uses_pythonw_exe=true",
        "redirects_stdout_stderr_to_d_hot_log=true",
        "scheduler_action_replacement_explicit_only=true",
        "broker_autotrade=false",
    ):
        assert marker in text, marker


def test_launcher_redirects_stdout_stderr_and_calls_q22s() -> None:
    text = LAUNCHER.read_text(encoding="utf-8")
    assert "redirect_stdout" in text
    assert "redirect_stderr" in text
    assert "q22s_main" in text
    assert "prediction/logs/q22x_silent_scheduler_launcher" in text


def test_action_args_reference_silent_launcher_and_token() -> None:
    args = _silent_q22x_action_args()
    assert str(Q22X_TOOL) in args
    assert "--execute-tick-once" in args
    assert "ENABLE_RECURRING_PRODUCER_LOOP_WITH_TRIGGER_AND_ROLLBACK_PLAN" in args
    assert "run_phase4a_prediction_system_ps_q22s_mountain2_actual_scheduled_latest_refresh_tick_once.py" in _direct_q22s_action_args()


def test_switch_default_blocks_no_write() -> None:
    result = run_switch_to_silent_scheduler_action_once(repo_status_short="", readiness_provider=_ready_packet, pythonw_path=Path("C:/BtcTradeSystem/.venv/Scripts/pythonw.exe"), ps_runner=_fake_ps_runner)
    assert result["success"] is False
    assert result["powershell_invoked"] is False
    assert "operator_acknowledgement_required" in result["blocked_reasons"]
    assert "execute_switch_once_flag_required" in result["blocked_reasons"]


def test_switch_executes_only_action_replacement_with_explicit_token() -> None:
    result = run_switch_to_silent_scheduler_action_once(
        operator_acknowledged=True,
        execute_switch_once=True,
        confirmation="ENABLE_RECURRING_PRODUCER_LOOP_WITH_TRIGGER_AND_ROLLBACK_PLAN",
        repo_status_short="",
        readiness_provider=_ready_packet,
        pythonw_path=Path("C:/BtcTradeSystem/.venv/Scripts/pythonw.exe"),
        ps_runner=_fake_ps_runner,
    )
    assert result["success"] is True
    assert result["scheduler_action_replacement_executed"] is True
    assert result["trigger_added"] is False
    assert result["would_send_to_broker"] is False


def test_q22v_accepts_silent_launcher_action_as_q22s_compatible() -> None:
    latest = {"forecast_batch": {"generated_at": "2026-06-28T05:10:21Z"}}
    status = {
        "producer_version": "prediction_warroom.success_preserving_status_write_once.ps_q22e.v1",
        "producer_state": "manual_refresh_exported_status_written",
        "last_success_generated_at": "2026-06-28T05:10:21Z",
        "producer_enabled": False,
        "safe_flags": {
            "autotrade_trigger_allowed_false": True,
            "broker_private_api_allowed_false": True,
            "would_send_to_broker_false": True,
            "parameter_apply_allowed_false": True,
            "parameter_staging_write_allowed_false": True,
        },
    }
    task = {
        "ok": True,
        "task_exists": True,
        "task_name": "BTC_TS_PredictionWarRoom_NonUI_DisabledScheduler",
        "task_path": "\\BtcTradeSystem\\",
        "state": "Ready",
        "trigger_count": 1,
        "action_arguments": _silent_q22x_action_args(),
    }
    meta = {"exists": True, "size_bytes": 1, "mtime_utc": "2026-06-28T05:10:21Z"}
    packet = build_post_enablement_readiness(repo_status_short="", latest_payload=latest, latest_meta=meta, status_payload=status, status_meta=meta, scheduler_task=task)
    assert packet["post_enablement_tick_ready"] is True
    assert packet["scheduler_action_mode"] == "q22x_silent_launcher"


if __name__ == "__main__":
    test_spec_declares_silent_contract()
    test_launcher_redirects_stdout_stderr_and_calls_q22s()
    test_action_args_reference_silent_launcher_and_token()
    test_switch_default_blocks_no_write()
    test_switch_executes_only_action_replacement_with_explicit_token()
    test_q22v_accepts_silent_launcher_action_as_q22s_compatible()
    print(json.dumps({"ok": True}))
