# path: ./tools/test_phase4a_prediction_system_ps_q21v_disabled_scheduler_registration_smoke.py
# desc: Focused guard for PS-Q21V disabled scheduler registration smoke preparation.

from __future__ import annotations

import sys
from pathlib import Path
import tempfile

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.run_phase4a_prediction_system_ps_q21v_disabled_scheduler_registration_smoke import (  # noqa: E402
    MOCK_REGISTRATION_RELATIVE_PATH,
    REQUIRED_OPERATOR_CONFIRMATION,
    SMOKE_VERSION,
    build_disabled_scheduler_registration_payload,
    run_disabled_scheduler_registration_smoke,
)

TOOL = REPO_ROOT / "tools/run_phase4a_prediction_system_ps_q21v_disabled_scheduler_registration_smoke.py"
SPEC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q21V_DISABLED_SCHEDULER_REGISTRATION_SMOKE_PREPARED_2026-06-26.md"

REQUIRED_MARKERS = (
    "ps_q21v_disabled_scheduler_registration_smoke_prepared=true",
    "default_execution_is_dry_run_no_registration=true",
    "real_d_hot_or_os_scheduler_registration_implemented_in_this_slice=false",
    "actual_registration_requires_confirmation=REGISTER_DISABLED_NON_UI_SCHEDULER_ONCE_WITH_ROLLBACK_PLAN",
    "scheduler_registered_by_default=false",
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


def test_spec_declares_prepared_default_no_registration() -> None:
    text = SPEC.read_text(encoding="utf-8-sig")
    for marker in REQUIRED_MARKERS:
        assert marker in text, marker
    for marker in FALSE_BOUNDARIES:
        assert marker in text, marker


def test_default_d_hot_path_is_dry_run_no_registration() -> None:
    result = run_disabled_scheduler_registration_smoke(execute_register=False)
    assert result["ok"] is True
    assert result["smoke_version"] == SMOKE_VERSION
    assert result["smoke_state"] == "disabled_scheduler_registration_smoke_dry_run_no_registration"
    assert result["execute_register_requested"] is False
    assert result["scheduler_registered"] is False
    assert result["os_scheduler_registration_attempted"] is False
    assert result["mock_registration_file_created"] is False
    assert result["producer_loop_enabled"] is False
    assert result["producer_runner_invoked"] is False
    assert result["latest_prediction_artifact_written"] is False
    assert result["status_artifact_written"] is False
    assert result["scheduler_registration_allowed_now"] is False
    assert result["recurring_enablement_allowed_now"] is False


def test_guard_test_root_can_create_readback_and_remove_mock_registration() -> None:
    with tempfile.TemporaryDirectory(prefix="ps_q21v_guard_") as tmp:
        result = run_disabled_scheduler_registration_smoke(
            target_root=Path(tmp),
            execute_register=True,
            confirmation=REQUIRED_OPERATOR_CONFIRMATION,
            allow_guard_test_root=True,
            remove_after_readback=True,
            now_utc="2026-06-26T10:44:40Z",
        )
        assert result["ok"] is True
        assert result["smoke_state"] == "disabled_scheduler_registration_mock_created_and_read_back"
        assert result["is_d_hot_target"] is False
        assert result["mock_registration_file_created"] is True
        assert result["mock_registration_file_read_back"] is True
        assert result["mock_registration_file_removed_after_readback"] is True
        assert (Path(tmp) / MOCK_REGISTRATION_RELATIVE_PATH).exists() is False
        assert result["os_scheduler_registered"] is False
        assert result["scheduler_registered"] is False
        assert result["producer_loop_enabled"] is False
        assert result["would_send_to_broker"] is False


def test_d_hot_execute_is_blocked_in_preparation_slice_even_with_confirmation() -> None:
    result = run_disabled_scheduler_registration_smoke(execute_register=True, confirmation=REQUIRED_OPERATOR_CONFIRMATION)
    assert result["ok"] is False
    assert result["smoke_state"] == "disabled_scheduler_registration_smoke_blocked_no_registration"
    assert "real_d_hot_or_os_scheduler_registration_not_implemented_in_ps_q21v_prepare_slice" in result["blocked_reasons"]
    assert result["scheduler_registered"] is False
    assert result["os_scheduler_registered"] is False
    assert result["producer_loop_enabled"] is False


def test_payload_has_disabled_scheduler_fields_and_safety_false() -> None:
    payload = build_disabled_scheduler_registration_payload(now_utc="2026-06-26T10:44:40Z")
    assert payload["registration_schema_version"] == SMOKE_VERSION
    assert payload["scheduler_registered_enabled"] is False
    assert payload["scheduler_started"] is False
    assert payload["scheduled_loop_enabled"] is False
    assert payload["producer_loop_enabled"] is False
    assert payload["producer_runner_invoked"] is False
    assert payload["status_artifact_write_allowed"] is False
    assert payload["prediction_artifact_write_allowed"] is False
    assert payload["autotrade_trigger_allowed"] is False
    assert payload["broker_private_api_allowed"] is False


def test_tool_does_not_reference_os_scheduler_or_runner_execution_paths() -> None:
    text = TOOL.read_text(encoding="utf-8")
    forbidden = (
        "subprocess.run(",
        "schtasks",
        "Register-ScheduledTask",
        "New-ScheduledTask",
        "execute_export=True",
        "allow_runtime_artifact_write=True",
        "request_scheduler_enable=True",
        "scheduler_registered\": True",
        "os_scheduler_registered\": True",
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
    assert "allow_guard_test_root" in text
    # The token is intentionally imported from PS-Q21U to avoid duplicated literal drift.
    assert "REQUIRED_OPERATOR_CONFIRMATION" in text
    assert "REGISTER_DISABLED_NON_UI_SCHEDULER_ONCE_WITH_ROLLBACK_PLAN" in REQUIRED_OPERATOR_CONFIRMATION
    assert "run_preflight" in text
    assert "print(json.dumps" in text


if __name__ == "__main__":
    test_spec_declares_prepared_default_no_registration()
    test_default_d_hot_path_is_dry_run_no_registration()
    test_guard_test_root_can_create_readback_and_remove_mock_registration()
    test_d_hot_execute_is_blocked_in_preparation_slice_even_with_confirmation()
    test_payload_has_disabled_scheduler_fields_and_safety_false()
    test_tool_does_not_reference_os_scheduler_or_runner_execution_paths()
    print('{"ok": true}')
