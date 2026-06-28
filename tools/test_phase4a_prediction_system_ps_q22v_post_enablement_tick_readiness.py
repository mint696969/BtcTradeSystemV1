# path: ./tools/test_phase4a_prediction_system_ps_q22v_post_enablement_tick_readiness.py
# desc: Focused guard for PS-Q22V post-enable tick readiness and Q22S readiness acceptance.

from __future__ import annotations

import json
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.diagnose_phase4a_prediction_system_ps_q22v_post_enablement_tick_readiness import (  # noqa: E402
    Q22V_VERSION,
    build_post_enablement_readiness,
)
from tools.run_phase4a_prediction_system_ps_q22s_mountain2_actual_scheduled_latest_refresh_tick_once import _readiness_green  # noqa: E402

SPEC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q22V_POST_ENABLEMENT_TICK_READINESS_2026-06-28.md"
Q22S_TOOL = REPO_ROOT / "tools/run_phase4a_prediction_system_ps_q22s_mountain2_actual_scheduled_latest_refresh_tick_once.py"


def _latest() -> dict:
    return {"forecast_batch": {"generated_at": "2026-06-28T02:00:00Z"}}


def _status() -> dict:
    return {
        "producer_version": "prediction_warroom.success_preserving_status_write_once.ps_q22e.v1",
        "producer_state": "manual_refresh_exported_status_written",
        "last_success_generated_at": "2026-06-28T02:00:00Z",
        "producer_enabled": False,
        "safe_flags": {
            "autotrade_trigger_allowed_false": True,
            "broker_private_api_allowed_false": True,
            "would_send_to_broker_false": True,
            "parameter_apply_allowed_false": True,
            "parameter_staging_write_allowed_false": True,
        },
    }


def _meta() -> dict:
    return {"exists": True, "size_bytes": 10, "mtime_utc": "2026-06-28T02:00:00Z"}


def _task() -> dict:
    return {
        "ok": True,
        "task_exists": True,
        "task_name": "BTC_TS_PredictionWarRoom_NonUI_DisabledScheduler",
        "task_path": "\\BtcTradeSystem\\",
        "state": "Ready",
        "trigger_count": 1,
        "action_arguments": "C:/BtcTradeSystem/tools/run_phase4a_prediction_system_ps_q22s_mountain2_actual_scheduled_latest_refresh_tick_once.py --operator-acknowledged",
    }


def test_spec_declares_post_enablement_readiness() -> None:
    text = SPEC.read_text(encoding="utf-8-sig")
    for marker in (
        "ps_q22v_post_enablement_tick_readiness=true",
        "post_enablement_tick_readiness_for_q22s=true",
        "q22s_accepts_pre_danger_or_post_enablement_readiness=true",
        "read_only_diagnostic=true",
        "scheduler_mutation_executed=false",
    ):
        assert marker in text, marker


def test_post_enablement_ready_packet_is_accepted_by_q22s_readiness_gate() -> None:
    packet = build_post_enablement_readiness(repo_status_short="", latest_payload=_latest(), latest_meta=_meta(), status_payload=_status(), status_meta=_meta(), scheduler_task=_task())
    assert packet["readiness_version"] == Q22V_VERSION
    assert packet["post_enablement_tick_ready"] is True
    assert packet["readiness_blockers"] == []
    assert _readiness_green(packet) is True


def test_blocks_when_task_still_disabled_or_action_not_q22s() -> None:
    task = _task()
    task["state"] = "Disabled"
    blocked = build_post_enablement_readiness(repo_status_short="", latest_payload=_latest(), latest_meta=_meta(), status_payload=_status(), status_meta=_meta(), scheduler_task=task)
    assert "scheduler_task_must_be_ready_running_or_queued_after_enablement" in blocked["readiness_blockers"]
    task = _task()
    task["action_arguments"] = "run_phase4a_prediction_system_ps_q21v_disabled_scheduler_registration_smoke.py"
    blocked = build_post_enablement_readiness(repo_status_short="", latest_payload=_latest(), latest_meta=_meta(), status_payload=_status(), status_meta=_meta(), scheduler_task=task)
    assert "scheduler_task_action_must_be_q22s_after_enablement" in blocked["readiness_blockers"]


def test_q22s_tool_imports_q22v_and_accepts_post_enablement_key() -> None:
    text = Q22S_TOOL.read_text(encoding="utf-8")
    assert "run_post_enablement_readiness" in text
    assert "post_enablement_tick_ready" in text


if __name__ == "__main__":
    test_spec_declares_post_enablement_readiness()
    test_post_enablement_ready_packet_is_accepted_by_q22s_readiness_gate()
    test_blocks_when_task_still_disabled_or_action_not_q22s()
    test_q22s_tool_imports_q22v_and_accepts_post_enablement_key()
    print(json.dumps({"ok": True}))
