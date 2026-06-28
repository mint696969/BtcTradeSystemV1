# path: ./tools/test_phase4a_prediction_system_ps_q22w_recurring_failure_preserve_success.py
# desc: Focused guard for PS-Q22W recurring failure status preservation and Q22V retry readiness.

from __future__ import annotations

import json
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.diagnose_phase4a_prediction_system_ps_q22v_post_enablement_tick_readiness import build_post_enablement_readiness  # noqa: E402
from tools.run_phase4a_prediction_system_ps_q22s_mountain2_actual_scheduled_latest_refresh_tick_once import (  # noqa: E402
    _compact_runner_result,
    _readiness_green,
    _status_payload,
)

SPEC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q22W_RECURRING_FAILURE_PRESERVE_SUCCESS_2026-06-28.md"
Q22S_TOOL = REPO_ROOT / "tools/run_phase4a_prediction_system_ps_q22s_mountain2_actual_scheduled_latest_refresh_tick_once.py"
Q22V_TOOL = REPO_ROOT / "tools/diagnose_phase4a_prediction_system_ps_q22v_post_enablement_tick_readiness.py"


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


def _meta() -> dict:
    return {"exists": True, "size_bytes": 123, "mtime_utc": "2026-06-28T03:00:00Z"}


def test_spec_declares_failure_preservation_contract() -> None:
    text = SPEC.read_text(encoding="utf-8-sig")
    for marker in (
        "ps_q22w_recurring_failure_preserve_success=true",
        "q22s_failure_preserves_previous_success=true",
        "q22s_failure_records_q21i_summary=true",
        "q22v_accepts_retryable_q22s_failure_status=true",
        "scheduler_mutation_executed=false",
    ):
        assert marker in text, marker


def test_q22s_failure_payload_preserves_pre_tick_success_fields() -> None:
    pre_status = {
        "producer_version": "prediction_warroom.success_preserving_status_write_once.ps_q22e.v1",
        "producer_state": "manual_refresh_exported_status_written",
        "last_success_generated_at": "2026-06-28T02:55:20Z",
        "last_prediction_run_id": "prediction_system.ps_g_lite.v1:BTC_JPY:bitFlyer:2026-06-28T02:55:20Z",
        "last_target_file_size_bytes": 5247287,
        "safe_flags": {"would_send_to_broker_false": True},
    }
    payload = _status_payload(
        hot_root=Path("D:/btc_ts_hot"),
        run_id="tick-1",
        state="mountain2_tick_failed",
        blockers=["bounded_latest_refresh_failed_or_incomplete"],
        base_status=pre_status,
        extra={"q21i_result_summary": {"success": False, "blocked_reasons": ["x"]}},
    )
    assert payload["producer_state"] == "mountain2_tick_failed"
    assert payload["last_success_generated_at"] == "2026-06-28T02:55:20Z"
    assert payload["last_prediction_run_id"].startswith("prediction_system")
    assert payload["last_target_file_size_bytes"] == 5247287
    assert payload["failure_preserved_previous_success"] is True
    assert payload["q21i_result_summary"]["success"] is False


def test_compact_runner_result_contains_failure_context() -> None:
    compact = _compact_runner_result({"success": False, "blocked_reasons": ["a"], "warning_reasons": ["w"], "runner_state": "blocked", "latest_prediction_artifact_written": False})
    assert compact["success"] is False
    assert compact["blocked_reasons"] == ["a"]
    assert compact["warning_reasons"] == ["w"]
    assert compact["runner_state"] == "blocked"


def test_q22v_accepts_retryable_q22s_failure_with_preserved_success() -> None:
    latest = {"forecast_batch": {"generated_at": "2026-06-28T02:55:20Z"}}
    status = {
        "producer_version": "prediction_warroom.mountain2_actual_scheduled_latest_refresh_tick_once.ps_q22s.v1",
        "producer_state": "mountain2_tick_failed",
        "last_success_generated_at": "2026-06-28T02:55:20Z",
        "last_prediction_run_id": "prediction_system.ps_g_lite.v1:BTC_JPY:bitFlyer:2026-06-28T02:55:20Z",
        "consecutive_failure_count": 1,
        "last_tick_run_id": "mountain2.tick.ps_q22s:2026-06-28T03:00:11Z:abc",
        "failure_preserved_previous_success": True,
        "producer_enabled": False,
        "safe_flags": {
            "autotrade_trigger_allowed_false": True,
            "broker_private_api_allowed_false": True,
            "would_send_to_broker_false": True,
            "parameter_apply_allowed_false": True,
            "parameter_staging_write_allowed_false": True,
        },
    }
    packet = build_post_enablement_readiness(repo_status_short="", latest_payload=latest, latest_meta=_meta(), status_payload=status, status_meta=_meta(), scheduler_task=_task())
    assert packet["post_enablement_tick_ready"] is True
    assert packet["status_acceptance_mode"] == "retryable_q22s_failure_preserved_success"
    assert _readiness_green(packet) is True


def test_q22v_blocks_q22s_failure_without_preserved_success() -> None:
    latest = {"forecast_batch": {"generated_at": "2026-06-28T02:55:20Z"}}
    status = {
        "producer_version": "prediction_warroom.mountain2_actual_scheduled_latest_refresh_tick_once.ps_q22s.v1",
        "producer_state": "mountain2_tick_failed",
        "last_success_generated_at": None,
        "consecutive_failure_count": 2,
        "producer_enabled": False,
        "safe_flags": {
            "autotrade_trigger_allowed_false": True,
            "broker_private_api_allowed_false": True,
            "would_send_to_broker_false": True,
            "parameter_apply_allowed_false": True,
            "parameter_staging_write_allowed_false": True,
        },
    }
    packet = build_post_enablement_readiness(repo_status_short="", latest_payload=latest, latest_meta=_meta(), status_payload=status, status_meta=_meta(), scheduler_task=_task())
    assert packet["post_enablement_tick_ready"] is False
    assert "status_last_success_generated_at_must_match_latest" in packet["readiness_blockers"]


def test_code_contains_expected_markers() -> None:
    q22s = Q22S_TOOL.read_text(encoding="utf-8")
    q22v = Q22V_TOOL.read_text(encoding="utf-8")
    assert "failure_preserved_previous_success" in q22s
    assert "q21i_result_summary" in q22s
    assert "retryable_q22s_failure_preserved_success" in q22v


if __name__ == "__main__":
    test_spec_declares_failure_preservation_contract()
    test_q22s_failure_payload_preserves_pre_tick_success_fields()
    test_compact_runner_result_contains_failure_context()
    test_q22v_accepts_retryable_q22s_failure_with_preserved_success()
    test_q22v_blocks_q22s_failure_without_preserved_success()
    test_code_contains_expected_markers()
    print(json.dumps({"ok": True}))
