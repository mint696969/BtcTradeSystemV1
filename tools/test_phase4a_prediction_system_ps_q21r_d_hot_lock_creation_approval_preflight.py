# path: ./tools/test_phase4a_prediction_system_ps_q21r_d_hot_lock_creation_approval_preflight.py
# desc: Focused guard for PS-Q21R read-only D-hot lock creation approval/rollback preflight.

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.verify_phase4a_prediction_system_ps_q21r_d_hot_lock_creation_approval_preflight import (  # noqa: E402
    PREFLIGHT_VERSION,
    REQUIRED_OPERATOR_CONFIRMATION,
    build_d_hot_lock_creation_approval_preflight,
)

TOOL = REPO_ROOT / "tools/verify_phase4a_prediction_system_ps_q21r_d_hot_lock_creation_approval_preflight.py"
SPEC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q21R_D_HOT_LOCK_CREATION_APPROVAL_PREFLIGHT_2026-06-26.md"

REQUIRED_MARKERS = (
    "ps_q21r_d_hot_lock_creation_approval_preflight=true",
    "read_only_approval_preflight_only=true",
    "preflight_state=observed_result",
    "separate_operator_approval_required=true",
    "required_operator_confirmation=CREATE_D_HOT_LOCK_FILE_ONCE_WITH_ROLLBACK_PLAN",
    "d_hot_lock_file_creation_allowed_now=false",
    "d_hot_lock_file_write_allowed_now=false",
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


def _visibility(**overrides: object) -> dict:
    data = {
        "ok": True,
        "visibility_state": "lock_scheduler_status_visible_non_stale_disabled_no_lock",
        "visibility_attention_reasons": [],
        "generated_at": "2026-06-26T09:00:00Z",
        "age_sec": 1,
        "latest_prediction_non_stale": True,
        "latest_status_success_observed": True,
        "disabled_boundary_preserved": True,
        "d_hot_lock_artifact_exists": False,
        "producer_state": "manual_refresh_exported_status_written",
        "producer_enabled": False,
        "scheduler_enabled": False,
        "output_count": 110,
        "status_warnings": ["prediction_result_warnings_present:19"],
    }
    data.update(overrides)
    return data


def test_spec_declares_read_only_approval_preflight_and_no_creation() -> None:
    text = SPEC.read_text(encoding="utf-8-sig")
    for marker in REQUIRED_MARKERS:
        assert marker in text, marker
    for marker in FALSE_BOUNDARIES:
        assert marker in text, marker


def test_preflight_ready_for_separate_approval_but_not_allowed_now() -> None:
    result = build_d_hot_lock_creation_approval_preflight(visibility_packet=_visibility())
    assert result["ok"] is True
    assert result["preflight_version"] == PREFLIGHT_VERSION
    assert result["preflight_state"] == "d_hot_lock_creation_preflight_ready_for_separate_approval_no_creation"
    assert result["preflight_ready_for_separate_approval"] is True
    assert result["preflight_blockers"] == []
    assert result["separate_operator_approval_required"] is True
    assert result["required_operator_confirmation"] == REQUIRED_OPERATOR_CONFIRMATION
    assert result["approval_preflight_contract"]["rollback_plan_required"] is True
    assert result["approval_preflight_contract"]["scheduler_registration_still_separate_approval"] is True
    assert result["approval_preflight_contract"]["producer_loop_enablement_still_separate_approval"] is True
    assert result["rollback_plan"]["rollback_must_not_delete_prediction_or_status_artifacts"] is True
    assert result["d_hot_lock_file_creation_allowed_now"] is False
    assert result["d_hot_lock_file_write_allowed_now"] is False
    assert result["lock_acquire_allowed_now"] is False
    assert result["lock_release_allowed_now"] is False
    assert result["scheduler_registration_allowed"] is False
    assert result["producer_loop_allowed"] is False
    assert result["recurring_enablement_allowed_now"] is False
    assert result["runtime_artifact_write_allowed"] is False
    assert result["would_send_to_broker"] is False


def test_preflight_blocks_on_stale_or_existing_lock_without_recovery() -> None:
    result = build_d_hot_lock_creation_approval_preflight(
        visibility_packet=_visibility(
            visibility_state="lock_scheduler_status_visible_attention",
            visibility_attention_reasons=["latest_prediction_stale_or_unknown", "d_hot_runtime_lock_file_exists_attention"],
            latest_prediction_non_stale=False,
            d_hot_lock_artifact_exists=True,
        )
    )
    assert result["preflight_state"] == "d_hot_lock_creation_preflight_blocked_no_creation"
    assert result["preflight_ready_for_separate_approval"] is False
    assert "visibility_state_non_stale_disabled_no_lock_required" in result["preflight_blockers"]
    assert "latest_prediction_non_stale_required" in result["preflight_blockers"]
    assert "d_hot_lock_artifact_absent_required_before_creation_preflight" in result["preflight_blockers"]
    assert result["d_hot_lock_file_creation_allowed_now"] is False
    assert result["lock_acquire_allowed_now"] is False
    assert result["scheduler_registration_allowed"] is False
    assert result["producer_loop_allowed"] is False
    assert result["recurring_enablement_allowed_now"] is False


def test_tool_is_read_only_preflight_no_lock_write_or_runner_invocation() -> None:
    text = TOOL.read_text(encoding="utf-8")
    forbidden = (
        "write_text(",
        "open(\"w",
        "subprocess.run(",
        ".touch(",
        "Path.replace(",
        "os.replace(",
        ".unlink(",
        "execute_export=True",
        "allow_runtime_artifact_write=True",
        "request_scheduler_enable=True",
        "request_warroom_ui_trigger=True",
        "d_hot_lock_file_created\": True",
        "d_hot_lock_file_written\": True",
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
    assert "run_visibility" in text
    assert "required_operator_confirmation" in text
    assert "rollback_plan" in text
    assert "print(json.dumps" in text


if __name__ == "__main__":
    test_spec_declares_read_only_approval_preflight_and_no_creation()
    test_preflight_ready_for_separate_approval_but_not_allowed_now()
    test_preflight_blocks_on_stale_or_existing_lock_without_recovery()
    test_tool_is_read_only_preflight_no_lock_write_or_runner_invocation()
    print('{"ok": true}')
