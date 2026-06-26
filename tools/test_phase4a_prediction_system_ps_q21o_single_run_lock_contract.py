# path: ./tools/test_phase4a_prediction_system_ps_q21o_single_run_lock_contract.py
# desc: Focused guard for PS-Q21O single non-overlapping run-lock contract.

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.design_phase4a_prediction_system_ps_q21o_single_run_lock_contract import (  # noqa: E402
    LOCK_CONTRACT_VERSION,
    build_single_run_lock_contract,
)

TOOL = REPO_ROOT / "tools/design_phase4a_prediction_system_ps_q21o_single_run_lock_contract.py"
SPEC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q21O_SINGLE_RUN_LOCK_CONTRACT_NO_FILE_CREATION_2026-06-26.md"

REQUIRED_MARKERS = (
    "ps_q21o_single_run_lock_contract=true",
    "read_only_lock_contract_only=true",
    "lock_contract_ready=observed_result",
    "lock_file_creation_allowed=false",
    "lock_file_write_allowed=false",
    "lock_acquire_allowed_now=false",
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
        "recommended_cadence_sec": 300,
        "last_success_generated_at": "2026-06-26T07:34:29Z",
        "last_failure_at": None,
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


def test_spec_declares_lock_contract_and_no_file_creation() -> None:
    text = SPEC.read_text(encoding="utf-8-sig")
    for marker in REQUIRED_MARKERS:
        assert marker in text, marker
    for marker in FALSE_BOUNDARIES:
        assert marker in text, marker


def test_run_lock_contract_ready_without_lock_creation_or_runner_invocation() -> None:
    result = build_single_run_lock_contract(
        latest_payload=_latest(),
        status_payload=_status(),
        latest_meta=_meta(5256095),
        status_meta=_meta(2018),
        lock_meta={"exists": False, "size_bytes": None, "mtime_utc": ""},
        now_utc="2026-06-26T07:35:00Z",
    )
    assert result["ok"] is True
    assert result["lock_contract_version"] == LOCK_CONTRACT_VERSION
    assert result["lock_contract_state"] == "single_non_overlapping_run_lock_contract_ready_no_file_creation"
    assert result["lock_contract_ready"] is True
    assert result["latest_prediction_non_stale"] is True
    assert result["latest_status_success_observed"] is True
    assert result["disabled_boundary_preserved"] is True
    contract = result["run_lock_contract"]
    assert contract["single_non_overlapping_runner_lock_required"] is True
    assert contract["enablement_allowed_without_lock"] is False
    assert contract["lock_contract_only"] is True
    execution = result["lock_execution_result"]
    assert execution["lock_file_created"] is False
    assert execution["lock_file_written"] is False
    assert execution["lock_acquire_attempted"] is False
    assert execution["lock_acquired"] is False
    assert execution["lock_release_attempted"] is False
    assert execution["lock_released"] is False
    assert execution["scheduler_registered"] is False
    assert execution["producer_runner_invoked"] is False
    assert execution["latest_prediction_artifact_written"] is False
    assert execution["status_artifact_written"] is False
    assert result["lock_file_creation_allowed"] is False
    assert result["lock_file_write_allowed"] is False
    assert result["lock_acquire_allowed_now"] is False
    assert result["scheduler_registration_allowed"] is False
    assert result["producer_loop_allowed"] is False
    assert result["recurring_enablement_allowed_now"] is False
    assert result["runtime_artifact_write_allowed"] is False
    assert result["broker_private_api_allowed"] is False
    assert result["would_send_to_broker"] is False


def test_stale_or_enabled_boundary_blocks_lock_contract_ready() -> None:
    status = dict(_status())
    status["producer_enabled"] = True
    result = build_single_run_lock_contract(
        latest_payload=_latest(),
        status_payload=status,
        latest_meta=_meta(5256095),
        status_meta=_meta(2018),
        lock_meta={"exists": False},
        now_utc="2026-06-26T09:00:00Z",
    )
    assert result["lock_contract_state"] == "single_non_overlapping_run_lock_contract_blocked"
    assert result["lock_contract_ready"] is False
    assert "latest_prediction_non_stale_required_before_run_lock_contract" in result["lock_contract_blockers"]
    assert "disabled_boundary_required_before_run_lock_contract" in result["lock_contract_blockers"]
    assert result["lock_file_creation_allowed"] is False
    assert result["recurring_enablement_allowed_now"] is False


def test_tool_is_read_only_lock_contract_no_file_creation_or_enablement() -> None:
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
        "lock_file_created\": True",
        "lock_acquired\": True",
        "scheduler_registered\": True",
        "producer_runner_invoked\": True",
        "send_order(",
        "place_order(",
        "BTC_TS_DATA_DIR",
    )
    for token in forbidden:
        assert token not in text, token
    assert "BTCTS_HOT_ROOT" in text
    assert "BTC_TS_HOT_ROOT" in text
    assert "lock_relative_path_design" in text
    assert "lock_execution_result" in text
    assert "print(json.dumps" in text


if __name__ == "__main__":
    test_spec_declares_lock_contract_and_no_file_creation()
    test_run_lock_contract_ready_without_lock_creation_or_runner_invocation()
    test_stale_or_enabled_boundary_blocks_lock_contract_ready()
    test_tool_is_read_only_lock_contract_no_file_creation_or_enablement()
    print('{"ok": true}')
