# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_prediction_warroom_non_ui_scheduled_producer_contract.py
# desc: Verify PS-Q16A non-UI scheduled producer contract is design-only, disabled-by-default, visible, rollback-capable, and accuracy-review-only.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.apps.operator_ui.components.prediction_warroom_non_ui_scheduled_producer_contract import (  # noqa: E402
    FRESHNESS_MAX_AGE_SEC,
    PRODUCER_STATUS_ARTIFACT_RELATIVE_PATH,
    RECOMMENDED_CADENCE_SEC,
    REQUIRED_STATUS_FIELDS,
    SAFE_FLAG_KEYS,
    build_prediction_warroom_non_ui_scheduled_producer_contract,
)


def _ready_adapter() -> dict:
    return {
        "adapter_state": "latest_prediction_source_ready",
        "review_packet_ready": True,
        "warning_count": 2,
        "blocker_count": 0,
        "source_summary": {
            "generated_at": "2026-06-22T09:37:06Z",
            "prediction_run_id": "prediction_system.ps_g_lite.v1:BTC_JPY:bitFlyer:2026-06-22T09:37:06Z",
            "market_uid": "bitflyer.fx.FX_BTC_JPY",
            "signal_strength_percent": 49,
            "signal_strength_band": "weak",
        },
    }


def _status_artifact() -> dict:
    return {
        "producer_version": "prediction_non_ui_scheduled_producer.future_disabled.v1",
        "producer_state": "disabled_not_running",
        "producer_enabled": False,
        "scheduler_enabled": False,
        "runtime_artifact_write_enabled": False,
        "latest_prediction_artifact_relative_path": "prediction/latest_prediction_system_result.json",
        "status_artifact_relative_path": PRODUCER_STATUS_ARTIFACT_RELATIVE_PATH,
        "freshness_max_age_sec": FRESHNESS_MAX_AGE_SEC,
        "recommended_cadence_sec": RECOMMENDED_CADENCE_SEC,
        "last_run_started_at": None,
        "last_run_finished_at": None,
        "last_success_at": None,
        "last_failure_at": None,
        "last_success_generated_at": None,
        "last_prediction_run_id": None,
        "last_target_file_size_bytes": None,
        "last_warning_count": 0,
        "last_blocker_count": 0,
        "consecutive_failure_count": 0,
        "safe_flags": {key: True for key in SAFE_FLAG_KEYS},
        "warnings": [],
        "blockers": [],
        "disable_rollback_state": "disabled_by_default",
    }


def test_default_contract_is_disabled_by_default_and_design_only() -> None:
    packet = build_prediction_warroom_non_ui_scheduled_producer_contract().to_dict()
    assert packet["contract_state"] == "non_ui_scheduled_producer_contract_ready_for_disabled_runner_slice"
    assert packet["ready_for_next_disabled_runner_slice"] is True
    assert packet["ready_for_scheduler_enablement"] is False
    assert packet["ready_for_runtime_artifact_write_automation_enablement"] is False
    assert packet["producer_enabled"] is False
    assert packet["scheduler_enabled"] is False
    assert packet["runtime_artifact_write_enabled"] is False
    assert packet["warroom_ui_trigger_enabled"] is False
    assert packet["contract_only"] is True
    assert packet["guard_only"] is True
    assert packet["visibility_design_required"] is True
    assert packet["would_write_runtime_artifact"] is False
    assert packet["would_write_status_artifact"] is False
    assert packet["would_mutate_live_parameters"] is False
    assert packet["parameter_apply_allowed"] is False
    assert packet["parameter_staging_write_allowed"] is False
    assert packet["autotrade_trigger_allowed"] is False
    assert packet["broker_private_api_allowed"] is False
    assert packet["warning_reasons"] == [
        "latest_prediction_source_adapter_not_supplied_for_design_context",
        "producer_status_artifact_not_supplied_yet_expected_before_warroom_status_display",
    ]


def test_contract_carries_realtime_observation_status_schema_and_accuracy_review_only() -> None:
    packet = build_prediction_warroom_non_ui_scheduled_producer_contract(
        latest_prediction_source_adapter_packet=_ready_adapter(),
        producer_status_artifact=_status_artifact(),
    ).to_dict()
    assert packet["latest_prediction_review_ready"] is True
    assert packet["latest_prediction_generated_at"] == "2026-06-22T09:37:06Z"
    assert packet["latest_prediction_warning_count"] == 2
    assert packet["producer_status_artifact_supplied"] is True
    assert packet["producer_status_missing_fields"] == []
    assert packet["producer_status_required_field_count"] == len(REQUIRED_STATUS_FIELDS)
    cadence = packet["cadence_policy"]
    assert cadence["freshness_max_age_sec"] == 3600
    assert cadence["recommended_cadence_sec"] == 300
    visibility = packet["status_visibility_contract"]
    assert visibility["status_artifact_relative_path"] == PRODUCER_STATUS_ARTIFACT_RELATIVE_PATH
    assert visibility["failure_visibility_required"] is True
    assert visibility["warnings_visible"] is True
    assert visibility["blockers_visible"] is True
    assert visibility["safe_flags_visible"] is True
    accuracy = packet["accuracy_adjustment_review_contract"]
    assert accuracy["review_state"] == "proposal_only_no_apply_no_staging_write"
    assert accuracy["apply_allowed"] is False
    assert accuracy["staging_write_allowed"] is False
    assert accuracy["live_parameter_mutation_allowed"] is False
    assert accuracy["human_review_required_before_any_future_apply"] is True
    rollback = packet["disable_rollback_contract"]
    assert rollback["default_enabled"] is False
    assert rollback["rollback_does_not_force_ready"] is True


def test_enablement_requests_are_blocked_in_ps_q16a() -> None:
    packet = build_prediction_warroom_non_ui_scheduled_producer_contract(
        request_scheduler_enable=True,
        request_runtime_artifact_write_enable=True,
        request_producer_enable=True,
        request_warroom_ui_trigger=True,
        request_parameter_apply=True,
        request_parameter_staging_write=True,
        request_approval_or_ledger_or_autotrade_or_broker=True,
    ).to_dict()
    assert packet["contract_state"] == "non_ui_scheduled_producer_contract_blocked"
    assert packet["ready_for_next_disabled_runner_slice"] is False
    assert packet["ready_for_scheduler_enablement"] is False
    assert packet["ready_for_runtime_artifact_write_automation_enablement"] is False
    assert set(packet["requested_enablement_flags"]) == {
        "request_scheduler_enable",
        "request_runtime_artifact_write_enable",
        "request_producer_enable",
        "request_warroom_ui_trigger",
        "request_parameter_apply",
        "request_parameter_staging_write",
        "request_approval_or_ledger_or_autotrade_or_broker",
    }
    assert any(reason.startswith("forbidden_enablement_in_ps_q16a:") for reason in packet["blocked_reasons"])


if __name__ == "__main__":
    test_default_contract_is_disabled_by_default_and_design_only()
    test_contract_carries_realtime_observation_status_schema_and_accuracy_review_only()
    test_enablement_requests_are_blocked_in_ps_q16a()
    print("ok")
