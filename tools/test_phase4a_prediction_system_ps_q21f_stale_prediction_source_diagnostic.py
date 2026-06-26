# path: ./tools/test_phase4a_prediction_system_ps_q21f_stale_prediction_source_diagnostic.py
# desc: Focused guard for PS-Q21F stale prediction source diagnostic.

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.diagnose_phase4a_prediction_system_ps_q21f_stale_prediction_source import (  # noqa: E402
    DIAGNOSTIC_VERSION,
    build_stale_prediction_source_diagnostic,
)

TOOL = REPO_ROOT / "tools/diagnose_phase4a_prediction_system_ps_q21f_stale_prediction_source.py"
SPEC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q21F_STALE_PREDICTION_SOURCE_DIAGNOSTIC_2026-06-26.md"

REQUIRED_MARKERS = (
    "ps_q21f_stale_prediction_source_diagnostic=true",
    "panel_refresh_liveness_not_same_as_prediction_data_freshness=true",
    "latest_prediction_artifact_path=prediction/latest_prediction_system_result.json",
    "producer_status_artifact_path=prediction/status/non_ui_scheduled_producer_status.json",
    "read_only_diagnostic_only=true",
)

FALSE_BOUNDARIES = (
    "runtime_enablement_allowed=false",
    "scheduler_enablement_allowed=false",
    "producer_enablement_allowed=false",
    "runtime_artifact_write_allowed=false",
    "status_artifact_write_allowed=false",
    "prediction_artifact_write_allowed=false",
    "view_artifact_write_allowed=false",
    "autotrade_trigger_allowed=false",
    "broker_private_api_allowed=false",
    "would_send_to_broker=false",
)


def _latest_payload() -> dict:
    return {
        "generated_at": "2026-06-25T11:59:14Z",
        "predictions": [{"horizon": 15}, {"horizon": 60}],
    }


def _blocked_status() -> dict:
    return {
        "producer_version": "prediction_warroom_bounded_manual_refresh_runner.ps_q16d.v1",
        "producer_state": "manual_refresh_blocked_status_written",
        "producer_enabled": False,
        "scheduler_enabled": False,
        "runtime_artifact_write_enabled": False,
        "freshness_max_age_sec": 3600,
        "last_run_started_at": "2026-06-25T12:04:14Z",
        "last_run_finished_at": "2026-06-25T12:04:14Z",
        "last_success_at": None,
        "last_failure_at": "2026-06-25T12:04:14Z",
        "last_success_generated_at": None,
        "blockers": [
            "market_overview_trust_state_not_trusted",
            "market_overview_interpretation_bucket_not_allow_structural_use",
            "ps_q9z_probe_not_ready_for_future_prediction_source_mapping",
            "source_mapping_runner_not_ready_for_prediction_system_result_builder",
            "actual_export_runner_did_not_write_latest_prediction_artifact",
        ],
        "warnings": ["orderbook_snapshot_missing_exchange_ts_context_only"],
    }


def test_spec_declares_diagnostic_and_safety_boundaries() -> None:
    text = SPEC.read_text(encoding="utf-8-sig")
    for marker in REQUIRED_MARKERS:
        assert marker in text, marker
    for marker in FALSE_BOUNDARIES:
        assert marker in text, marker


def test_stale_prediction_source_diagnostic_identifies_blocked_manual_refresh() -> None:
    result = build_stale_prediction_source_diagnostic(
        latest_payload=_latest_payload(),
        status_payload=_blocked_status(),
        latest_path_exists=True,
        latest_mtime_utc="2026-06-25T12:00:00Z",
        now_utc="2026-06-26T03:45:57Z",
    )
    assert result["ok"] is True
    assert result["diagnostic_version"] == DIAGNOSTIC_VERSION
    assert result["diagnosis_state"] == "prediction_artifact_stale_because_last_manual_refresh_blocked"
    assert result["latest_prediction_generated_at"] == "2026-06-25T11:59:14Z"
    assert result["latest_prediction_age_sec"] > 3600
    assert result["prediction_artifact_stale"] is True
    assert result["producer_enabled"] is False
    assert result["scheduler_enabled"] is False
    assert result["last_manual_refresh_blocked"] is True
    assert result["actual_export_runner_did_not_write_latest_prediction_artifact"] is True
    assert result["source_mapping_blocked"] is True
    assert result["market_overview_trust_or_interpretation_blocked"] is True
    assert result["panel_refresh_liveness_not_same_as_prediction_data_freshness"] is True
    assert result["runtime_artifact_write_allowed"] is False
    assert result["prediction_artifact_write_allowed"] is False
    assert result["autotrade_trigger_allowed"] is False
    assert result["broker_private_api_allowed"] is False
    assert result["would_send_to_broker"] is False


def test_missing_latest_artifact_is_reported_without_enablement() -> None:
    result = build_stale_prediction_source_diagnostic(
        latest_payload={},
        status_payload={},
        latest_path_exists=False,
        now_utc="2026-06-26T03:45:57Z",
    )
    assert result["diagnosis_state"] == "latest_prediction_artifact_missing"
    assert result["latest_prediction_artifact_exists"] is False
    assert result["read_only_diagnostic_only"] is True
    assert result["scheduler_enablement_allowed"] is False
    assert result["producer_enablement_allowed"] is False
    assert result["runtime_artifact_write_allowed"] is False


def test_tool_is_stdout_only_and_has_no_runtime_writes_or_enablement() -> None:
    text = TOOL.read_text(encoding="utf-8")
    forbidden = (
        "write_text(",
        "open(\"w",
        "subprocess.run(",
        "scheduler_enabled: bool = True",
        "producer_enabled: bool = True",
        "runtime_artifact_write_allowed: bool = True",
        "prediction_artifact_write_allowed: bool = True",
        "status_artifact_write_allowed: bool = True",
        "send_order(",
        "place_order(",
    )
    for token in forbidden:
        assert token not in text, token
    assert "print(json.dumps" in text
    assert "read_only_diagnostic_only" in text
    assert "BTCTS_HOT_ROOT" in text
    assert "BTC_TS_HOT_ROOT" in text
    assert "BTC_TS_DATA_DIR" not in text


if __name__ == "__main__":
    test_spec_declares_diagnostic_and_safety_boundaries()
    test_stale_prediction_source_diagnostic_identifies_blocked_manual_refresh()
    test_missing_latest_artifact_is_reported_without_enablement()
    test_tool_is_stdout_only_and_has_no_runtime_writes_or_enablement()
    print('{"ok": true}')
