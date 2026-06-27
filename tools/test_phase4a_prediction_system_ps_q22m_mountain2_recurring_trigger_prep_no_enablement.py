# path: ./tools/test_phase4a_prediction_system_ps_q22m_mountain2_recurring_trigger_prep_no_enablement.py
# desc: Focused guard for PS-Q22M Mountain2 recurring/trigger preparation no enablement.

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.diagnose_phase4a_prediction_system_ps_q22m_mountain2_recurring_trigger_prep_no_enablement import (  # noqa: E402
    FUTURE_MOUNTAIN2_TOKEN_CANDIDATE,
    PREP_VERSION,
    Q22E_STATUS_VERSION,
    build_mountain2_prep_packet,
)

SPEC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q22M_MOUNTAIN2_RECURRING_TRIGGER_PREP_NO_ENABLEMENT_2026-06-27.md"
TOOL = REPO_ROOT / "tools/diagnose_phase4a_prediction_system_ps_q22m_mountain2_recurring_trigger_prep_no_enablement.py"


def _latest() -> dict:
    return {"forecast_batch": {"generated_at": "2026-06-27T11:57:38Z", "record_count": 110}, "non_executing": True, "read_only": True}


def _status(**overrides: object) -> dict:
    data = {
        "producer_version": Q22E_STATUS_VERSION,
        "producer_state": "manual_refresh_exported_status_written",
        "last_success_generated_at": "2026-06-27T11:57:38Z",
        "last_prediction_run_id": "prediction_system.ps_g_lite.v1:BTC_JPY:bitFlyer:2026-06-27T11:57:38Z",
        "producer_enabled": False,
        "scheduler_enabled": False,
        "runtime_artifact_write_enabled": True,
    }
    data.update(overrides)
    return data


def _task(**overrides: object) -> dict:
    readback = {
        "task_exists": True,
        "task_name": "BTC_TS_PredictionWarRoom_NonUI_DisabledScheduler",
        "task_path": "\\BtcTradeSystem\\",
        "state": "Disabled",
        "trigger_count": 0,
        "action_arguments": r'"C:\BtcTradeSystem\tools\run_phase4a_prediction_system_ps_q21v_disabled_scheduler_registration_smoke.py"',
    }
    readback.update(overrides)
    return {"ok": True, "task_recognized_as_ps_q21w": True, "task_readback_failures": [], "task_readback": readback}


def _ready_packet(**overrides: object) -> dict:
    data = build_mountain2_prep_packet(
        repo_status_short="",
        collector_packet={"ok": True},
        latest_payload=_latest(),
        latest_meta={"exists": True, "size_bytes": 10, "mtime_utc": "2026-06-27T11:57:38Z"},
        status_payload=_status(),
        status_meta={"exists": True, "size_bytes": 10, "mtime_utc": "2026-06-27T12:02:05Z"},
        q21x_packet={"shadow_preflight_ready_for_one_shot": True, "shadow_preflight_blockers": [], "latest_prediction_non_stale": True},
        q21m_packet={"ready_for_disabled_dry_run_design_slice": True, "policy_design_state": "ready_for_disabled_dry_run_design_not_enablement"},
        q21n_packet={"dry_run_design_ready": True, "dry_run_design_state": "disabled_non_ui_scheduler_producer_dry_run_design_ready_no_registration"},
        scheduler_query_packet=_task(),
    )
    data.update(overrides)
    return data


def test_spec_declares_no_enablement_boundary() -> None:
    text = SPEC.read_text(encoding="utf-8-sig")
    for marker in (
        "ps_q22m_mountain2_recurring_trigger_prep_no_enablement=true",
        "no_scheduler_enablement=true",
        "no_trigger_addition=true",
        "no_recurring_or_periodic_execution=true",
        "no_latest_prediction_artifact_write=true",
        "future_mountain2_enablement_token_candidate=ENABLE_RECURRING_PRODUCER_LOOP_WITH_TRIGGER_AND_ROLLBACK_PLAN",
        "scheduler_enabled=false",
        "trigger_added=false",
        "recurring_enablement_allowed_now=false",
        "would_send_to_broker=false",
    ):
        assert marker in text, marker


def test_ready_packet_is_no_enablement_and_names_future_gate() -> None:
    result = _ready_packet()
    assert result["prep_version"] == PREP_VERSION
    assert result["prep_state"] == "mountain2_recurring_trigger_prep_ready_no_enablement"
    assert result["prep_ready_for_future_enablement_design"] is True
    assert result["prep_blockers"] == []
    assert result["mountain2_future_enablement_not_executed"]["future_token_candidate"] == FUTURE_MOUNTAIN2_TOKEN_CANDIDATE
    assert result["mountain2_future_enablement_not_executed"]["must_stop_for_operator_before_enablement"] is True
    assert result["scheduler_enabled"] is False
    assert result["trigger_added"] is False
    assert result["recurring_enablement_allowed_now"] is False
    assert result["latest_prediction_artifact_written"] is False
    assert result["producer_runner_invoked"] is False
    assert result["would_send_to_broker"] is False


def test_blocks_when_existing_task_has_trigger_or_enabled_state() -> None:
    result = build_mountain2_prep_packet(
        repo_status_short="",
        collector_packet={"ok": True},
        latest_payload=_latest(),
        latest_meta={"exists": True},
        status_payload=_status(),
        status_meta={"exists": True},
        q21x_packet={"shadow_preflight_ready_for_one_shot": True, "shadow_preflight_blockers": [], "latest_prediction_non_stale": True},
        q21m_packet={"ready_for_disabled_dry_run_design_slice": True},
        q21n_packet={"dry_run_design_ready": True},
        scheduler_query_packet=_task(state="Ready", trigger_count=1),
    )
    assert result["prep_ready_for_future_enablement_design"] is False
    assert "existing_scheduler_task_must_remain_disabled" in result["prep_blockers"]
    assert "existing_scheduler_task_must_have_zero_triggers" in result["prep_blockers"]
    assert result["scheduler_enabled"] is False
    assert result["trigger_added"] is False


def test_tool_contains_no_direct_scheduler_enablement_commands() -> None:
    text = TOOL.read_text(encoding="utf-8")
    for token in ("Enable-ScheduledTask", "New-ScheduledTaskTrigger", "Start-ScheduledTask", "Register-ScheduledTask", "send_order(", "place_order("):
        assert token not in text, token


if __name__ == "__main__":
    test_spec_declares_no_enablement_boundary()
    test_ready_packet_is_no_enablement_and_names_future_gate()
    test_blocks_when_existing_task_has_trigger_or_enabled_state()
    test_tool_contains_no_direct_scheduler_enablement_commands()
    print(json.dumps({"ok": True}))
