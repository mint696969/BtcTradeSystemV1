# path: ./tools/test_phase4a_prediction_system_ps_q18c_warroom_prediction_widget_source_read_probe_status_row_mount.py
# desc: Unit tests for PS-Q18C WarRoom source read probe status row mount.

from __future__ import annotations

import json

from check_phase4a_prediction_system_ps_q18c_warroom_prediction_widget_source_read_probe_status_row_mount import CHECKER_VERSION, SOURCE_READ_PROBE_STATUS_ROW_MOUNT_VERSION, build_report, main
from btcts.apps.operator_ui.components.prediction_warroom_prediction_widget_source_read_probe_status_panel import build_prediction_warroom_prediction_widget_source_read_probe_status_packet


def _assert_safe(report: dict) -> None:
    for key in ("read_only", "non_executing", "source_read_probe_status_row_mount_only", "warroom_status_rows_ready", "bounded_probe_report_display_only"):
        assert report[key] is True, key
    assert report["warroom_page_mutation_allowed"] is True
    for key in (
        "bounded_actual_source_read_probe_called_by_mount",
        "actual_source_read_invoked_by_mount",
        "actual_source_read_allowed_by_warroom_mount",
        "source_discovery_allowed",
        "d_hot_directory_scan_allowed",
        "d_hot_actual_read_allowed",
        "freshness_checked_against_d_hot",
        "warroom_widget_rendering_allowed",
        "real_prediction_widget_rendering_allowed",
        "warroom_ui_trigger_enabled",
        "refresh_invocation_allowed",
        "scheduler_enabled",
        "runtime_artifact_write_allowed",
        "status_artifact_write_allowed",
        "confidence_increase_allowed",
        "parameter_apply_allowed",
        "parameter_staging_write_allowed",
        "approval_or_authorization_allowed",
        "ledger_append_allowed",
        "autotrade_trigger_allowed",
        "broker_private_api_allowed",
        "would_write_runtime_artifact",
        "would_write_collector_state",
        "would_send_to_broker",
    ):
        assert report[key] is False, key


def test_ps_q18c_validates_status_row_mount_from_q18b_fixture() -> None:
    report = build_report(use_observed_fixture=True)
    assert report["ok"] is True
    assert report["checker_version"] == CHECKER_VERSION
    assert report["source_read_probe_status_row_mount_version"] == SOURCE_READ_PROBE_STATUS_ROW_MOUNT_VERSION
    assert report["source_q18b_report_valid"] is True
    assert report["status_packet_valid"] is True
    assert report["page_status_packet_valid"] is True
    assert report["status_row_count"] == 7
    assert report["page_status_row_count"] == 7
    assert report["page_validation_failures"] == []
    _assert_safe(report)


def test_ps_q18c_page_safe_status_packet_does_not_invoke_probe() -> None:
    packet = build_prediction_warroom_prediction_widget_source_read_probe_status_packet()
    assert packet["ok"] is True
    assert packet["status_row_count"] == 7
    assert packet["supplied_probe_report"] is False
    assert packet["observed_actual_file_read_succeeded"] is False
    assert packet["bounded_actual_source_read_probe_called_by_mount"] is False
    assert packet["actual_source_read_invoked_by_mount"] is False
    assert packet["actual_source_read_allowed_by_warroom_mount"] is False
    assert packet["d_hot_directory_scan_allowed"] is False


def test_ps_q18c_blocks_missing_q18b_source() -> None:
    blocked = build_report(page_text="")
    assert blocked["ok"] is False
    assert blocked["status_row_count"] == 0
    assert blocked["source_q18b_report_valid"] is False


def test_ps_q18c_observed_fixture_cli_and_main(capsys) -> None:
    assert main(["--use-observed-fixture"]) == 0
    printed = json.loads(capsys.readouterr().out)
    assert printed["ok"] is True
    assert printed["use_observed_fixture"] is True
    assert printed["stage"] == "warroom_prediction_widget_source_read_probe_status_row_mount_before_probe_invocation_d_hot_discovery_real_widget_rendering_and_refresh"
    assert printed["recommended_next_slice"].startswith("PS-Q18D")
    _assert_safe(printed)
    assert main([]) == 1
    blocked = json.loads(capsys.readouterr().out)
    assert blocked["ok"] is False
