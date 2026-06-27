# path: ./tools/test_phase4a_prediction_system_ps_q22e_success_preserving_status_write_once.py
# desc: Focused guard for PS-Q22E success-preserving D-hot status-only write wrapper.

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.run_phase4a_prediction_system_ps_q22e_success_preserving_status_write_once import (  # noqa: E402
    REQUIRED_STATUS_WRITE_CONFIRMATION,
    WRITE_VERSION,
    run_success_preserving_status_write_once,
)

SPEC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q22E_SUCCESS_PRESERVING_STATUS_WRITE_WRAPPER_2026-06-27.md"
TOOL = REPO_ROOT / "tools/run_phase4a_prediction_system_ps_q22e_success_preserving_status_write_once.py"


def _design(**overrides: object) -> dict:
    payload = {
        "producer_state": "producer_shadow_status_success_preserved_no_write_design",
        "producer_enabled": False,
        "scheduler_enabled": False,
        "last_success_generated_at": "2026-06-27T04:31:32Z",
        "last_prediction_run_id": "prediction_system.ps_g_lite.v1:BTC_JPY:bitFlyer:2026-06-27T04:31:32Z",
        "last_target_file_size_bytes": 5422419,
        "warnings": ["w"],
        "blockers": [],
    }
    data = {
        "design_state": "success_preserving_producer_status_design_ready_no_write",
        "design_blockers": [],
        "preserves_last_success_generated_at": True,
        "preserves_last_prediction_run_id": True,
        "preserves_last_target_file_size_bytes": True,
        "proposed_status_payload_not_written": payload,
    }
    data.update(overrides)
    return data


def test_spec_declares_exact_token_and_status_only_boundary() -> None:
    text = SPEC.read_text(encoding="utf-8-sig")
    for marker in (
        "ps_q22e_success_preserving_status_write_wrapper=true",
        "default_execution_is_dry_run_no_write=true",
        "requires_exact_confirmation=WRITE_D_HOT_SUCCESS_PRESERVING_PRODUCER_STATUS_ONCE",
        "writes_latest_prediction_artifact=false",
        "producer_state_preserved_for_q21x=manual_refresh_exported_status_written",
        "would_send_to_broker=false",
    ):
        assert marker in text, marker


def test_default_blocks_without_writing() -> None:
    called = {"value": False}
    def fake(path: Path, payload: dict) -> int:
        called["value"] = True
        return 1
    result = run_success_preserving_status_write_once(design_packet=_design(), status_writer=fake, repo_clean=True)
    assert result["write_state"] == "success_preserving_status_write_blocked_no_write"
    assert result["status_artifact_written"] is False
    assert result["status_write_invoked"] is False
    assert "operator_acknowledgement_required" in result["blocked_reasons"]
    assert "execute_status_write_once_flag_required" in result["blocked_reasons"]
    assert "exact_status_write_confirmation_token_required" in result["blocked_reasons"]
    assert called["value"] is False


def test_blocks_when_q22d_design_not_ready() -> None:
    result = run_success_preserving_status_write_once(
        operator_acknowledged=True,
        execute_status_write_once=True,
        confirmation=REQUIRED_STATUS_WRITE_CONFIRMATION,
        design_packet=_design(design_state="success_preserving_producer_status_design_blocked", design_blockers=["x"]),
        status_writer=lambda path, payload: 1,
        repo_clean=True,
    )
    assert result["status_write_invoked"] is False
    assert "q22d_design_ready_required" in result["blocked_reasons"]
    assert "q22d_design_blockers_must_be_empty" in result["blocked_reasons"]


def test_exact_token_writes_q21x_compatible_status_via_fake_writer() -> None:
    calls = []
    def fake(path: Path, payload: dict) -> int:
        calls.append((path, payload))
        return 2048
    result = run_success_preserving_status_write_once(
        operator_acknowledged=True,
        execute_status_write_once=True,
        confirmation=REQUIRED_STATUS_WRITE_CONFIRMATION,
        design_packet=_design(),
        status_writer=fake,
        repo_clean=True,
        status_path=Path(r"D:\btc_ts_hot\prediction\status\non_ui_scheduled_producer_status.json"),
    )
    assert result["write_version"] == WRITE_VERSION
    assert result["success"] is True
    assert result["status_artifact_written"] is True
    assert result["status_write_invoked"] is True
    assert len(calls) == 1
    payload = calls[0][1]
    assert payload["producer_state"] == "manual_refresh_exported_status_written"
    assert payload["last_success_generated_at"] == "2026-06-27T04:31:32Z"
    assert payload["last_prediction_run_id"].startswith("prediction_system.ps_g_lite.v1")
    assert payload["producer_enabled"] is False
    assert payload["scheduler_enabled"] is False
    assert payload["blockers"] == []
    assert result["latest_prediction_artifact_written"] is False
    assert result["producer_loop_enabled"] is False
    assert result["would_send_to_broker"] is False


def test_tool_contains_single_write_helper_but_no_scheduler_or_broker_tokens() -> None:
    text = TOOL.read_text(encoding="utf-8")
    assert "WRITE_D_HOT_SUCCESS_PRESERVING_PRODUCER_STATUS_ONCE" in text
    assert "_write_json_atomic" in text
    for token in ("Enable-ScheduledTask", "New-ScheduledTaskTrigger", "Start-ScheduledTask", "send_order(", "place_order("):
        assert token not in text, token


if __name__ == "__main__":
    test_spec_declares_exact_token_and_status_only_boundary()
    test_default_blocks_without_writing()
    test_blocks_when_q22d_design_not_ready()
    test_exact_token_writes_q21x_compatible_status_via_fake_writer()
    test_tool_contains_single_write_helper_but_no_scheduler_or_broker_tokens()
    print(json.dumps({"ok": True}))
