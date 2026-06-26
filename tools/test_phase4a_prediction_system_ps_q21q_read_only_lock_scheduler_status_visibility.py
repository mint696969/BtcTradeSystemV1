# path: ./tools/test_phase4a_prediction_system_ps_q21q_read_only_lock_scheduler_status_visibility.py
# desc: Focused guard for PS-Q21Q read-only lock/scheduler status visibility packet.

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.verify_phase4a_prediction_system_ps_q21q_read_only_lock_scheduler_status_visibility import (  # noqa: E402
    VISIBILITY_VERSION,
    build_lock_scheduler_status_visibility_packet,
)

TOOL = REPO_ROOT / "tools/verify_phase4a_prediction_system_ps_q21q_read_only_lock_scheduler_status_visibility.py"
SPEC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q21Q_READ_ONLY_LOCK_SCHEDULER_STATUS_VISIBILITY_2026-06-26.md"

REQUIRED_MARKERS = (
    "ps_q21q_read_only_lock_scheduler_status_visibility=true",
    "read_only_status_visibility_packet_only=true",
    "visibility_state=observed_result",
    "d_hot_lock_file_creation_allowed=false",
    "d_hot_lock_file_write_allowed=false",
    "scheduler_registration_allowed=false",
    "producer_loop_allowed=false",
    "recurring_enablement_allowed_now=false",
)

FALSE_BOUNDARIES = (
    "runtime_artifact_write_allowed=false",
    "status_artifact_write_allowed=false",
    "prediction_artifact_write_allowed=false",
    "view_artifact_write_allowed=false",
    "warroom_ui_trigger_allowed=false",
    "approval_or_ledger_allowed=false",
    "parameter_apply_allowed=false",
    "parameter_staging_write_allowed=false",
    "autotrade_trigger_allowed=false",
    "broker_private_api_allowed=false",
    "would_send_to_broker=false",
    "would_write_collector_state=false",
)


def _latest() -> dict:
    return {
        "run_identity": {"generated_at": "2026-06-26T07:34:29Z"},
        "forecast_batch": {"generated_at": "2026-06-26T07:34:29Z", "records": [{"x": 1}, {"x": 2}]},
    }


def _status() -> dict:
    return {
        "producer_state": "manual_refresh_exported_status_written",
        "producer_enabled": False,
        "scheduler_enabled": False,
        "runtime_artifact_write_enabled": True,
        "freshness_max_age_sec": 3600,
        "last_success_at": "2026-06-26T07:34:29Z",
        "last_success_generated_at": "2026-06-26T07:34:29Z",
        "last_failure_at": None,
        "last_blocker_count": 0,
        "last_warning_count": 1,
        "blockers": [],
        "warnings": ["prediction_result_warnings_present:19"],
        "safe_flags": {
            "producer_enabled_false": True,
            "scheduler_enabled_false": True,
            "scheduled_loop_enabled_false": True,
            "warroom_ui_trigger_false": True,
            "autotrade_trigger_allowed_false": True,
            "broker_private_api_allowed_false": True,
            "would_send_to_broker_false": True,
        },
    }


def _meta(size: int) -> dict:
    return {"exists": True, "size_bytes": size, "mtime_utc": "2026-06-26T07:34:29Z"}


def test_spec_declares_read_only_visibility_and_no_enablement() -> None:
    text = SPEC.read_text(encoding="utf-8-sig")
    for marker in REQUIRED_MARKERS:
        assert marker in text, marker
    for marker in FALSE_BOUNDARIES:
        assert marker in text, marker


def test_visibility_packet_non_stale_disabled_no_lock() -> None:
    result = build_lock_scheduler_status_visibility_packet(
        latest_payload=_latest(),
        status_payload=_status(),
        latest_meta=_meta(5256095),
        status_meta=_meta(2018),
        lock_meta={"exists": False, "size_bytes": None, "mtime_utc": ""},
        now_utc="2026-06-26T07:35:00Z",
    )
    assert result["ok"] is True
    assert result["visibility_version"] == VISIBILITY_VERSION
    assert result["visibility_state"] == "lock_scheduler_status_visible_non_stale_disabled_no_lock"
    assert result["visibility_ok_for_operator_display"] is True
    assert result["visibility_attention_reasons"] == []
    assert result["latest_prediction_non_stale"] is True
    assert result["latest_status_success_observed"] is True
    assert result["disabled_boundary_preserved"] is True
    assert result["d_hot_lock_artifact_exists"] is False
    assert result["scheduler_status_visible"] is True
    assert result["producer_status_visible"] is True
    assert result["lock_status_visible"] is True
    assert result["d_hot_lock_file_creation_allowed"] is False
    assert result["lock_acquire_allowed_now"] is False
    assert result["scheduler_registration_allowed"] is False
    assert result["producer_loop_allowed"] is False
    assert result["recurring_enablement_allowed_now"] is False
    assert result["runtime_artifact_write_allowed"] is False
    assert result["would_send_to_broker"] is False


def test_visibility_packet_stale_is_attention_not_enablement() -> None:
    result = build_lock_scheduler_status_visibility_packet(
        latest_payload=_latest(),
        status_payload=_status(),
        latest_meta=_meta(5256095),
        status_meta=_meta(2018),
        lock_meta={"exists": True, "size_bytes": 123, "mtime_utc": "2026-06-26T08:00:00Z"},
        now_utc="2026-06-26T09:00:00Z",
    )
    assert result["ok"] is True
    assert result["visibility_state"] == "lock_scheduler_status_visible_attention"
    assert "latest_prediction_stale_or_unknown" in result["visibility_attention_reasons"]
    assert "d_hot_runtime_lock_file_exists_attention" in result["visibility_attention_reasons"]
    assert result["latest_prediction_non_stale"] is False
    assert result["d_hot_lock_artifact_exists"] is True
    assert result["d_hot_lock_file_creation_allowed"] is False
    assert result["lock_acquire_allowed_now"] is False
    assert result["scheduler_registration_allowed"] is False
    assert result["producer_loop_allowed"] is False
    assert result["recurring_enablement_allowed_now"] is False


def test_tool_is_read_only_visibility_no_lock_write_or_runner_invocation() -> None:
    text = TOOL.read_text(encoding="utf-8")
    forbidden = (
        "write_text(",
        "open(\"w",
        "subprocess.run(",
        ".touch(",
        "Path.replace(",
        "os.replace(",
        "execute_export=True",
        "allow_runtime_artifact_write=True",
        "request_scheduler_enable=True",
        "request_warroom_ui_trigger=True",
        "scheduler_registered\": True",
        "producer_runner_invoked\": True",
        "latest_prediction_artifact_written\": True",
        "status_artifact_written\": True",
        "send_order(",
        "place_order(",
        "BTC_TS_DATA_DIR",
    )
    for token in forbidden:
        assert token not in text, token
    assert "BTCTS_HOT_ROOT" in text
    assert "BTC_TS_HOT_ROOT" in text
    assert "d_hot_lock_artifact_exists" in text
    assert "visibility_attention_reasons" in text
    assert "print(json.dumps" in text


if __name__ == "__main__":
    test_spec_declares_read_only_visibility_and_no_enablement()
    test_visibility_packet_non_stale_disabled_no_lock()
    test_visibility_packet_stale_is_attention_not_enablement()
    test_tool_is_read_only_visibility_no_lock_write_or_runner_invocation()
    print('{"ok": true}')
