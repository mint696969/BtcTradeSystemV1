# path: ./tools/test_phase4a_prediction_system_ps_q19e_non_ui_manual_or_scheduled_refresh_guarded.py
# desc: Focused guard for PS-Q19E guarded non-UI manual/scheduled refresh entrypoint.

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.run_prediction_warroom_bounded_manual_refresh_ps_q19e import (  # noqa: E402
    PS_Q19E_MANUAL_REFRESH_ACK,
    PS_Q19E_NON_UI_REFRESH_VERSION,
    build_ps_q19e_non_ui_refresh_request_packet,
)

SPEC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q19E_NON_UI_MANUAL_OR_SCHEDULED_REFRESH_GUARDED_2026-06-25.md"
TOOL = REPO_ROOT / "tools/run_prediction_warroom_bounded_manual_refresh_ps_q19e.py"

REQUIRED_MARKERS = (
    "ps_q19e_non_ui_manual_or_scheduled_refresh_guarded=true",
    "q16d_bounded_manual_refresh_runner_reused=true",
    "operator_tool_added=true",
    "default_dry_run_no_write=true",
    "explicit_ack_required=true",
    "manual_refresh_ack=PS_Q19E_RUN_BOUNDED_NON_UI_MANUAL_REFRESH",
    "scheduled_refresh_declared=true",
    "PS-Q19F_WARROOM_LIVE_SMOKE_AND_OPERATOR_VISUAL_CONFIRMATION",
)

FALSE_BOUNDARIES = (
    "scheduled_loop_enabled=false",
    "scheduler_enabled=false",
    "producer_enabled=false",
    "warroom_ui_trigger_enabled=false",
    "runtime_behavior_changed_by_patch=false",
    "collector_data_collection_changed=false",
    "ui_code_changed=false",
    "autotrade_trigger_allowed=false",
    "broker_private_api_allowed=false",
    "would_send_to_broker=false",
    "runtime_artifact_write_performed_by_patch=false",
    "status_artifact_write_performed_by_patch=false",
    "ui_triggered_runner_execution=false",
    "approval_or_authorization_allowed=false",
    "ledger_append_allowed=false",
    "parameter_apply_allowed=false",
    "parameter_staging_write_allowed=false",
)


def _fake_export_success(**kwargs: Any) -> dict[str, Any]:
    root = Path(str(kwargs["hot_latest_root_hint"]))
    target = root / "prediction" / "latest_prediction_system_result.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    payload = {"ok": True, "forecast_batch": {"generated_at": "2026-06-24T16:00:00Z", "records": []}}
    target.write_text(json.dumps(payload), encoding="utf-8")
    return {
        "runner_state": "latest_payload_actual_export_runner_exported",
        "target_file_written": True,
        "target_artifact_path": str(target),
        "target_file_size_bytes": target.stat().st_size,
        "prediction_run_id": "prediction_system.ps_q19e.test:BTC_JPY:bitFlyer:2026-06-24T16:00:00Z",
        "generated_at": "2026-06-24T16:00:00Z",
        "exported_at": "2026-06-24T16:00:01Z",
        "blocked_reasons": [],
        "warning_reasons": [],
        "approval_or_authorization_allowed": False,
        "ledger_append_allowed": False,
        "autotrade_trigger_allowed": False,
        "broker_private_api_allowed": False,
        "would_send_to_broker": False,
    }


def test_spec_declares_guarded_refresh_and_safety_boundaries() -> None:
    text = SPEC.read_text(encoding="utf-8-sig")
    for marker in REQUIRED_MARKERS:
        assert marker in text, marker
    for marker in FALSE_BOUNDARIES:
        assert marker in text, marker


def test_default_request_is_dry_run_no_write_and_does_not_invoke_export() -> None:
    called = {"value": False}

    def _should_not_call(**_: Any) -> dict[str, Any]:
        called["value"] = True
        raise AssertionError("export runner should not be called")

    packet = build_ps_q19e_non_ui_refresh_request_packet(actual_export_runner=_should_not_call)
    assert packet["ok"] is True
    assert packet["ps_q19e_version"] == PS_Q19E_NON_UI_REFRESH_VERSION
    assert packet["request_state"] == "dry_run_no_write"
    assert called["value"] is False
    assert packet["actual_export_runner_invoked"] is False
    assert packet["latest_prediction_artifact_written"] is False
    assert packet["status_artifact_written"] is False
    assert packet["default_dry_run_no_write"] is True
    assert packet["scheduler_enabled"] is False
    assert packet["scheduled_loop_enabled"] is False
    assert packet["warroom_ui_trigger_enabled"] is False
    assert packet["autotrade_trigger_allowed"] is False
    assert packet["broker_private_api_allowed"] is False


def test_explicit_ack_executes_one_bounded_manual_refresh_under_existing_q16d_guard(tmp_path: Path) -> None:
    packet = build_ps_q19e_non_ui_refresh_request_packet(
        hot_latest_root_hint=str(tmp_path),
        execute_manual_refresh=True,
        ack=PS_Q19E_MANUAL_REFRESH_ACK,
        allow_guard_test_root=True,
        actual_export_runner=_fake_export_success,
    )
    assert packet["ok"] is True
    assert packet["request_state"] == "bounded_manual_refresh_executed"
    assert packet["manual_execution_authorized"] is True
    assert packet["actual_export_runner_invoked"] is True
    assert packet["latest_prediction_artifact_written"] is True
    assert packet["status_artifact_written"] is True
    assert Path(packet["latest_prediction_artifact_path"]).exists()
    assert Path(packet["status_artifact_path"]).exists()
    assert packet["scheduler_enabled"] is False
    assert packet["scheduled_loop_enabled"] is False
    assert packet["producer_enabled"] is False
    assert packet["warroom_ui_trigger_enabled"] is False
    assert packet["autotrade_trigger_allowed"] is False
    assert packet["broker_private_api_allowed"] is False
    assert packet["would_send_to_broker"] is False


def test_execute_without_ack_blocks_and_does_not_invoke_export(tmp_path: Path) -> None:
    called = {"value": False}

    def _should_not_call(**_: Any) -> dict[str, Any]:
        called["value"] = True
        return {}

    packet = build_ps_q19e_non_ui_refresh_request_packet(
        hot_latest_root_hint=str(tmp_path),
        execute_manual_refresh=True,
        ack="WRONG_ACK",
        allow_guard_test_root=True,
        actual_export_runner=_should_not_call,
    )
    assert packet["ok"] is False
    assert packet["request_state"] == "manual_refresh_blocked"
    assert packet["manual_execution_authorized"] is False
    assert called["value"] is False
    assert packet["actual_export_runner_invoked"] is False
    assert packet["latest_prediction_artifact_written"] is False
    assert packet["status_artifact_written"] is False
    assert "operator_acknowledgement_required" in packet["blocked_reasons"]


def test_scheduled_refresh_request_is_represented_but_disabled(tmp_path: Path) -> None:
    packet = build_ps_q19e_non_ui_refresh_request_packet(
        hot_latest_root_hint=str(tmp_path),
        request_scheduled_refresh=True,
        allow_guard_test_root=True,
        actual_export_runner=_fake_export_success,
    )
    assert packet["ok"] is True
    assert packet["request_state"] == "scheduled_refresh_requested_but_disabled"
    assert packet["request_scheduled_refresh"] is True
    assert packet["scheduled_refresh_declared"] is True
    assert packet["scheduler_enabled"] is False
    assert packet["scheduled_loop_enabled"] is False
    assert packet["actual_export_runner_invoked"] is False
    assert "scheduled_refresh_loop_not_enabled_in_ps_q19e" in packet["blocked_reasons"]
    assert "scheduler_enable_not_allowed_in_ps_q16d" in packet["blocked_reasons"]


def test_tool_keeps_ack_literal_and_default_dry_run_contract() -> None:
    text = TOOL.read_text(encoding="utf-8")
    assert "PS_Q19E_RUN_BOUNDED_NON_UI_MANUAL_REFRESH" in text
    assert "default_dry_run_no_write" in text
    assert "request_scheduled_refresh" in text
    assert "scheduled_loop_enabled" in text


if __name__ == "__main__":
    test_spec_declares_guarded_refresh_and_safety_boundaries()
    test_default_request_is_dry_run_no_write_and_does_not_invoke_export()
    from tempfile import TemporaryDirectory

    with TemporaryDirectory() as temp_dir:
        test_explicit_ack_executes_one_bounded_manual_refresh_under_existing_q16d_guard(Path(temp_dir))
    with TemporaryDirectory() as temp_dir:
        test_execute_without_ack_blocks_and_does_not_invoke_export(Path(temp_dir))
    with TemporaryDirectory() as temp_dir:
        test_scheduled_refresh_request_is_represented_but_disabled(Path(temp_dir))
    test_tool_keeps_ack_literal_and_default_dry_run_contract()
    print(json.dumps({"ok": True}, ensure_ascii=False))
