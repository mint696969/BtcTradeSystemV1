# path: ./tools/test_phase4a_prediction_system_ps_q21s_single_d_hot_lock_creation_smoke.py
# desc: Focused guard for PS-Q21S gated single D-hot lock creation smoke tool.

from __future__ import annotations

import sys
from pathlib import Path
import tempfile

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.run_phase4a_prediction_system_ps_q21s_single_d_hot_lock_creation_smoke import (  # noqa: E402
    LOCK_RELATIVE_PATH,
    REQUIRED_OPERATOR_CONFIRMATION,
    SMOKE_VERSION,
    build_lock_payload,
    run_single_lock_file_creation_smoke,
)

TOOL = REPO_ROOT / "tools/run_phase4a_prediction_system_ps_q21s_single_d_hot_lock_creation_smoke.py"
SPEC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q21S_SINGLE_D_HOT_LOCK_CREATION_SMOKE_PREPARED_2026-06-26.md"

REQUIRED_MARKERS = (
    "ps_q21s_single_d_hot_lock_creation_smoke_prepared=true",
    "default_execution_is_dry_run_no_creation=true",
    "actual_d_hot_creation_requires_confirmation=CREATE_D_HOT_LOCK_FILE_ONCE_WITH_ROLLBACK_PLAN",
    "d_hot_lock_file_created_by_default=false",
    "lock_acquire_attempted=false",
    "scheduler_registration_allowed=false",
    "producer_loop_allowed=false",
    "recurring_enablement_allowed_now=false",
)

FALSE_BOUNDARIES = (
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


def test_spec_declares_gated_creation_smoke_and_default_no_creation() -> None:
    text = SPEC.read_text(encoding="utf-8-sig")
    for marker in REQUIRED_MARKERS:
        assert marker in text, marker
    for marker in FALSE_BOUNDARIES:
        assert marker in text, marker


def test_default_d_hot_path_is_dry_run_no_creation() -> None:
    result = run_single_lock_file_creation_smoke(execute_create=False)
    assert result["ok"] is True
    assert result["smoke_version"] == SMOKE_VERSION
    assert result["smoke_state"] == "single_d_hot_lock_creation_smoke_dry_run_no_creation"
    assert result["execute_create_requested"] is False
    assert result["d_hot_lock_file_created"] is False
    assert result["d_hot_lock_file_written"] is False
    assert result["lock_file_created"] is False
    assert result["lock_acquire_attempted"] is False
    assert result["lock_release_attempted"] is False
    assert result["scheduler_registered"] is False
    assert result["producer_runner_invoked"] is False
    assert result["latest_prediction_artifact_written"] is False
    assert result["status_artifact_written"] is False
    assert result["d_hot_lock_file_creation_allowed_now"] is False
    assert result["single_lock_file_write_allowed_now"] is False
    assert result["recurring_enablement_allowed_now"] is False


def test_guard_test_root_can_create_readback_and_remove_single_lock_file() -> None:
    with tempfile.TemporaryDirectory(prefix="ps_q21s_guard_") as tmp:
        result = run_single_lock_file_creation_smoke(
            target_root=Path(tmp),
            execute_create=True,
            confirmation=REQUIRED_OPERATOR_CONFIRMATION,
            allow_guard_test_root=True,
            remove_after_readback=True,
            now_utc="2026-06-26T09:00:00Z",
        )
        assert result["ok"] is True
        assert result["smoke_state"] == "single_lock_file_creation_smoke_created_and_read_back"
        assert result["is_d_hot_target"] is False
        assert result["lock_file_created"] is True
        assert result["lock_file_read_back"] is True
        assert result["lock_file_removed_after_readback"] is True
        assert Path(result["lock_artifact_path"]).exists() is False
        assert result["d_hot_lock_file_created"] is False
        assert result["d_hot_lock_file_written"] is False
        assert result["lock_acquire_attempted"] is False
        assert result["scheduler_registered"] is False
        assert result["producer_runner_invoked"] is False
        assert result["status_artifact_written"] is False
        assert result["would_send_to_broker"] is False


def test_execute_blocks_without_confirmation_or_guard_root() -> None:
    with tempfile.TemporaryDirectory(prefix="ps_q21s_block_") as tmp:
        result = run_single_lock_file_creation_smoke(target_root=Path(tmp), execute_create=True, confirmation="")
        assert result["ok"] is False
        assert result["smoke_state"] == "single_lock_creation_smoke_blocked_no_creation"
        assert "non_d_hot_target_requires_allow_guard_test_root" in result["blocked_reasons"]
        assert result["lock_file_created"] is False
        assert (Path(tmp) / LOCK_RELATIVE_PATH).exists() is False
        assert result["scheduler_registered"] is False
        assert result["recurring_enablement_allowed_now"] is False


def test_payload_has_required_owner_fields_and_safety_false() -> None:
    payload = build_lock_payload(run_id="test-run", now_utc="2026-06-26T09:00:00Z")
    for key in ("run_id", "pid", "host", "started_at_utc", "expires_at_utc", "reason"):
        assert key in payload
    assert payload["scheduler_registration_allowed"] is False
    assert payload["producer_loop_allowed"] is False
    assert payload["autotrade_trigger_allowed"] is False
    assert payload["broker_private_api_allowed"] is False


def test_tool_does_not_reference_runner_scheduler_broker_execution_paths() -> None:
    text = TOOL.read_text(encoding="utf-8")
    forbidden = (
        "subprocess.run(",
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
    assert "write_text" in text
    assert "REQUIRED_OPERATOR_CONFIRMATION" in text
    assert "run_preflight" in text
    assert "print(json.dumps" in text


if __name__ == "__main__":
    test_spec_declares_gated_creation_smoke_and_default_no_creation()
    test_default_d_hot_path_is_dry_run_no_creation()
    test_guard_test_root_can_create_readback_and_remove_single_lock_file()
    test_execute_blocks_without_confirmation_or_guard_root()
    test_payload_has_required_owner_fields_and_safety_false()
    test_tool_does_not_reference_runner_scheduler_broker_execution_paths()
    print('{"ok": true}')
