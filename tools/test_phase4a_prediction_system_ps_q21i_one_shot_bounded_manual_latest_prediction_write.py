# path: ./tools/test_phase4a_prediction_system_ps_q21i_one_shot_bounded_manual_latest_prediction_write.py
# desc: Focused guard for PS-Q21I explicitly gated one-shot bounded manual latest prediction write tool.

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.run_phase4a_prediction_system_ps_q21i_one_shot_bounded_manual_latest_prediction_write import (  # noqa: E402
    REQUIRED_CONFIRMATION,
    RUNNER_VERSION,
    build_blocked_packet,
    summarize_one_shot_write_packet,
)

TOOL = REPO_ROOT / "tools/run_phase4a_prediction_system_ps_q21i_one_shot_bounded_manual_latest_prediction_write.py"
SPEC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q21I_ONE_SHOT_BOUNDED_MANUAL_LATEST_PREDICTION_WRITE_2026-06-26.md"

REQUIRED_MARKERS = (
    "ps_q21i_one_shot_bounded_manual_latest_prediction_write=true",
    "requires_operator_acknowledged_flag=true",
    "requires_execute_one_shot_write_flag=true",
    "requires_confirmation_token=WRITE_D_HOT_LATEST_PREDICTION_ONCE",
    "requires_clean_working_tree=true",
    "one_shot_manual_write_only=true",
)

FALSE_BOUNDARIES = (
    "scheduler_enablement_allowed=false",
    "producer_enablement_allowed=false",
    "scheduled_loop_enabled=false",
    "warroom_ui_trigger_allowed=false",
    "ui_triggered_runner_execution=false",
    "approval_or_ledger_allowed=false",
    "parameter_apply_allowed=false",
    "parameter_staging_write_allowed=false",
    "autotrade_trigger_allowed=false",
    "broker_private_api_allowed=false",
    "would_send_to_broker=false",
    "would_write_collector_state=false",
)


def _meta(size: int) -> dict:
    return {"exists": True, "size_bytes": size, "mtime_utc": "2026-06-26T04:00:00Z"}


def test_spec_declares_write_gates_and_safety_boundaries() -> None:
    text = SPEC.read_text(encoding="utf-8-sig")
    for marker in REQUIRED_MARKERS:
        assert marker in text, marker
    for marker in FALSE_BOUNDARIES:
        assert marker in text, marker


def test_blocked_packet_requires_all_explicit_gates_without_writing() -> None:
    result = build_blocked_packet(
        reasons=["operator_acknowledgement_required", "execute_one_shot_write_required", "confirmation_token_required"],
        hot_root=Path(r"D:\btc_ts_hot"),
        requested_execute=False,
        git_status_before="",
    )
    assert result["ok"] is True
    assert result["runner_version"] == RUNNER_VERSION
    assert result["success"] is False
    assert result["latest_prediction_artifact_written"] is False
    assert result["status_artifact_written"] is False
    assert result["blocker_count"] == 3
    assert result["scheduler_enablement_allowed"] is False
    assert result["producer_enablement_allowed"] is False
    assert result["warroom_ui_trigger_allowed"] is False
    assert result["autotrade_trigger_allowed"] is False
    assert result["broker_private_api_allowed"] is False
    assert result["would_send_to_broker"] is False


def test_success_summary_preserves_scheduler_producer_broker_false() -> None:
    packet = {
        "runner_state": "bounded_manual_refresh_exported_status_written",
        "latest_prediction_artifact_written": True,
        "status_artifact_written": True,
        "latest_prediction_artifact_path": r"D:\btc_ts_hot\prediction\latest_prediction_system_result.json",
        "status_artifact_path": r"D:\btc_ts_hot\prediction\status\non_ui_scheduled_producer_status.json",
        "prediction_run_id": "run-123",
        "generated_at": "2026-06-26T04:50:00Z",
        "exported_at": "2026-06-26T04:50:02Z",
        "latest_prediction_artifact_size_bytes": 12345,
        "status_artifact_size_bytes": 2345,
        "blocker_count": 0,
        "blocked_reasons": [],
        "warning_count": 1,
        "warning_reasons": ["prediction_result_warnings_present:19"],
        "status_payload": {
            "producer_state": "manual_refresh_exported_status_written",
            "producer_enabled": False,
            "scheduler_enabled": False,
            "runtime_artifact_write_enabled": True,
            "safe_flags": {
                "scheduler_enabled_false": True,
                "producer_enabled_false": True,
                "warroom_ui_trigger_false": True,
                "autotrade_trigger_allowed_false": True,
                "broker_private_api_allowed_false": True,
            },
        },
    }
    result = summarize_one_shot_write_packet(
        packet=packet,
        before_latest_meta=_meta(100),
        before_status_meta=_meta(10),
        after_latest_meta=_meta(12345),
        after_status_meta=_meta(2345),
        git_status_before="",
        requested_execute=True,
    )
    assert result["success"] is True
    assert result["latest_prediction_artifact_written"] is True
    assert result["status_artifact_written"] is True
    assert result["prediction_run_id"] == "run-123"
    assert result["producer_enabled"] is False
    assert result["scheduler_enabled"] is False
    assert result["runtime_artifact_write_enabled"] is True
    assert result["scheduler_enablement_allowed"] is False
    assert result["producer_enablement_allowed"] is False
    assert result["warroom_ui_trigger_allowed"] is False
    assert result["approval_or_ledger_allowed"] is False
    assert result["autotrade_trigger_allowed"] is False
    assert result["broker_private_api_allowed"] is False
    assert result["would_send_to_broker"] is False


def test_tool_contains_required_gates_and_no_forbidden_enablement() -> None:
    text = TOOL.read_text(encoding="utf-8")
    assert REQUIRED_CONFIRMATION in text
    for token in (
        "operator_acknowledged=True",
        "execute_manual_refresh=True",
        "allow_actual_read=True",
        "allow_prediction_build=True",
        "allow_export_preflight=True",
        "allow_latest_payload_export=True",
        "allow_runtime_artifact_write=True",
        "allow_status_artifact_write=True",
        "execute_status_artifact_write=True",
        "request_scheduler_enable=False",
        "request_warroom_ui_trigger=False",
        "request_parameter_apply=False",
        "request_parameter_staging_write=False",
        "request_approval_or_ledger_or_autotrade_or_broker=False",
    ):
        assert token in text, token
    forbidden = (
        "request_scheduler_enable=True",
        "request_warroom_ui_trigger=True",
        "request_parameter_apply=True",
        "request_parameter_staging_write=True",
        "request_approval_or_ledger_or_autotrade_or_broker=True",
        "send_order(",
        "place_order(",
    )
    for token in forbidden:
        assert token not in text, token


if __name__ == "__main__":
    test_spec_declares_write_gates_and_safety_boundaries()
    test_blocked_packet_requires_all_explicit_gates_without_writing()
    test_success_summary_preserves_scheduler_producer_broker_false()
    test_tool_contains_required_gates_and_no_forbidden_enablement()
    print('{"ok": true}')
