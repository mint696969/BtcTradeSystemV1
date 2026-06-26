# path: ./tools/test_phase4a_prediction_system_ps_q21h_bounded_manual_refresh_export_preflight_dry_run.py
# desc: Focused guard for PS-Q21H bounded manual refresh export preflight dry-run.

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.diagnose_phase4a_prediction_system_ps_q21h_bounded_manual_refresh_export_preflight_dry_run import (  # noqa: E402
    DIAGNOSTIC_VERSION,
    build_bounded_manual_refresh_export_preflight_dry_run,
)

TOOL = REPO_ROOT / "tools/diagnose_phase4a_prediction_system_ps_q21h_bounded_manual_refresh_export_preflight_dry_run.py"
SPEC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q21H_BOUNDED_MANUAL_REFRESH_EXPORT_PREFLIGHT_DRY_RUN_2026-06-26.md"

REQUIRED_MARKERS = (
    "ps_q21h_bounded_manual_refresh_export_preflight_dry_run=true",
    "actual_read_performed=true",
    "prediction_build_in_memory_attempted=true",
    "export_preflight_contract_attempted=true",
    "latest_payload_export_requested=false",
    "runtime_artifact_write_requested=false",
    "target_file_written=false",
    "read_only_diagnostic_only=true",
)

FALSE_BOUNDARIES = (
    "latest_prediction_artifact_export_allowed=false",
    "runtime_artifact_write_allowed=false",
    "status_artifact_write_allowed=false",
    "prediction_artifact_write_allowed=false",
    "scheduler_enablement_allowed=false",
    "producer_enablement_allowed=false",
    "warroom_ui_trigger_allowed=false",
    "approval_or_ledger_allowed=false",
    "autotrade_trigger_allowed=false",
    "broker_private_api_allowed=false",
    "would_send_to_broker=false",
)


def _fixture_bridge(*, ready: bool = True) -> dict:
    blockers = [] if ready else ["prediction_system_result_builder_runner_not_ready_for_export_preflight"]
    return {
        "bridge_state": "latest_payload_export_preflight_bridge_ready_for_future_non_ui_export_runner" if ready else "latest_payload_export_preflight_bridge_blocked",
        "hot_latest_root_hint": r"D:\btc_ts_hot",
        "ready_for_future_latest_payload_export_preflight": ready,
        "ready_for_future_non_ui_export_runner": ready,
        "prediction_run_id": "run-123",
        "generated_at": "2026-06-26T04:40:00Z",
        "market_uid": "bitflyer.fx.FX_BTC_JPY",
        "output_count": 110,
        "prediction_result_warning_count": 1,
        "blocked_reasons": blockers,
        "warning_reasons": ["prediction_result_warnings_present:1"],
        "builder_runner_packet": {
            "runner_state": "prediction_system_result_builder_runner_ready_for_future_latest_payload_export_preflight" if ready else "prediction_system_result_builder_runner_blocked",
            "prediction_system_result_built_by_this_runner": ready,
            "prediction_result_blocker_count": 0 if ready else 1,
            "blocked_reasons": blockers,
            "warning_reasons": [],
            "prediction_result_payload": {
                "run_identity": {"prediction_run_id": "run-123", "generated_at": "2026-06-26T04:40:00Z", "market_uid": "bitflyer.fx.FX_BTC_JPY"},
                "outputs": [{"horizon": 15}, {"horizon": 60}],
            } if ready else {},
        },
        "export_preflight_packet": {
            "contract_state": "latest_payload_export_preflight_ready_for_future_non_ui_export_runner" if ready else "latest_payload_export_preflight_blocked",
            "target_artifact_path_hint": r"D:\btc_ts_hot\prediction\latest_prediction_system_result.json",
            "observed_expected_artifact_exists": True,
            "blocked_reasons": [],
            "warning_reasons": [],
        } if ready else {},
    }


def test_spec_declares_preflight_dry_run_and_safety_boundaries() -> None:
    text = SPEC.read_text(encoding="utf-8-sig")
    for marker in REQUIRED_MARKERS:
        assert marker in text, marker
    for marker in FALSE_BOUNDARIES:
        assert marker in text, marker


def test_ready_bridge_reports_write_step_ready_but_no_write_performed() -> None:
    result = build_bounded_manual_refresh_export_preflight_dry_run(preflight_bridge_packet=_fixture_bridge(ready=True))
    assert result["ok"] is True
    assert result["diagnostic_version"] == DIAGNOSTIC_VERSION
    assert result["diagnosis_state"] == "bounded_manual_refresh_export_preflight_ready_no_write"
    assert result["prediction_build_in_memory_attempted"] is True
    assert result["prediction_build_in_memory_performed"] is True
    assert result["export_preflight_contract_attempted"] is True
    assert result["export_preflight_contract_performed"] is True
    assert result["prediction_result_payload_present"] is True
    assert result["prediction_run_id"] == "run-123"
    assert result["ready_for_future_non_ui_export_runner"] is True
    assert result["ready_for_bounded_manual_refresh_write_step"] is True
    assert result["target_file_written"] is False
    assert result["status_artifact_written"] is False
    assert result["latest_payload_export_requested"] is False
    assert result["runtime_artifact_write_requested"] is False
    assert result["latest_prediction_artifact_export_allowed"] is False
    assert result["runtime_artifact_write_allowed"] is False
    assert result["scheduler_enablement_allowed"] is False
    assert result["producer_enablement_allowed"] is False
    assert result["autotrade_trigger_allowed"] is False
    assert result["broker_private_api_allowed"] is False
    assert result["would_send_to_broker"] is False


def test_blocked_bridge_reports_blockers_without_write() -> None:
    result = build_bounded_manual_refresh_export_preflight_dry_run(preflight_bridge_packet=_fixture_bridge(ready=False))
    assert result["diagnosis_state"] == "bounded_manual_refresh_export_preflight_blocked_before_payload_build"
    assert result["prediction_build_in_memory_attempted"] is True
    assert result["prediction_build_in_memory_performed"] is False
    assert result["export_preflight_contract_attempted"] is True
    assert result["export_preflight_contract_performed"] is False
    assert result["ready_for_bounded_manual_refresh_write_step"] is False
    assert result["combined_blocker_count"] >= 1
    assert result["target_file_written"] is False
    assert result["prediction_artifact_write_allowed"] is False


def test_tool_does_not_request_export_write_status_write_or_enablement() -> None:
    text = TOOL.read_text(encoding="utf-8")
    forbidden = (
        "execute_export=True",
        "allow_latest_payload_export=True",
        "allow_runtime_artifact_write=True",
        "execute_manual_refresh=True",
        "allow_status_artifact_write=True",
        "execute_status_artifact_write=True",
        "write_text(",
        "open(\"w",
        "subprocess.run(",
        "send_order(",
        "place_order(",
    )
    for token in forbidden:
        assert token not in text, token
    assert "allow_prediction_build=True" in text
    assert "allow_export_preflight=True" in text
    assert "requested_latest_payload_export=False" in text
    assert "requested_runtime_write=False" in text
    assert "print(json.dumps" in text


if __name__ == "__main__":
    test_spec_declares_preflight_dry_run_and_safety_boundaries()
    test_ready_bridge_reports_write_step_ready_but_no_write_performed()
    test_blocked_bridge_reports_blockers_without_write()
    test_tool_does_not_request_export_write_status_write_or_enablement()
    print('{"ok": true}')
