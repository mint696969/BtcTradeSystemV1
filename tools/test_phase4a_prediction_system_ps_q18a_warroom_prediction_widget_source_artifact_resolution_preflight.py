# path: ./tools/test_phase4a_prediction_system_ps_q18a_warroom_prediction_widget_source_artifact_resolution_preflight.py
# desc: Unit tests for PS-Q18A WarRoom prediction widget source artifact resolution preflight.

from __future__ import annotations

import json

from check_phase4a_prediction_system_ps_q18a_warroom_prediction_widget_source_artifact_resolution_preflight import CHECKER_VERSION, SOURCE_ARTIFACT_RESOLUTION_PREFLIGHT_VERSION, build_report, main


def _assert_safe(report: dict) -> None:
    for key in ("read_only", "non_executing", "source_artifact_resolution_preflight_only", "source_artifact_resolution_preflight_ready"):
        assert report[key] is True, key
    for key in (
        "source_artifact_resolution_allowed",
        "source_artifact_resolved",
        "source_artifact_path_materialized",
        "source_artifact_exists_checked",
        "source_artifact_schema_checked",
        "actual_source_bound",
        "actual_source_read_allowed",
        "d_hot_actual_read_allowed",
        "freshness_checked_against_d_hot",
        "real_prediction_widget_rendering_allowed",
        "warroom_widget_rendering_allowed",
        "warroom_page_mutation_allowed",
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


def test_ps_q18a_validates_artifact_resolution_preflight_from_q17z_fixture() -> None:
    report = build_report(use_observed_fixture=True)
    assert report["ok"] is True
    assert report["checker_version"] == CHECKER_VERSION
    assert report["source_artifact_resolution_preflight_version"] == SOURCE_ARTIFACT_RESOLUTION_PREFLIGHT_VERSION
    assert report["source_q17z_report_valid"] is True
    assert report["panel_packet_valid"] is True
    assert report["artifact_resolution_row_count"] == 12
    assert report["unique_artifact_resolution_key_count"] == 9
    assert report["unique_source_packet_count"] == 9
    assert report["panel_validation_failures"] == []
    _assert_safe(report)


def test_ps_q18a_keeps_materialization_read_render_refresh_and_writes_disabled() -> None:
    report = build_report(use_observed_fixture=True)
    assert report["source_artifact_resolution_preflight_ready"] is True
    assert report["source_artifact_resolution_allowed"] is False
    assert report["source_artifact_resolved"] is False
    assert report["source_artifact_path_materialized"] is False
    assert report["source_artifact_exists_checked"] is False
    assert report["source_artifact_schema_checked"] is False
    assert report["actual_source_read_allowed"] is False
    assert report["d_hot_actual_read_allowed"] is False
    assert report["real_prediction_widget_rendering_allowed"] is False
    assert report["refresh_invocation_allowed"] is False
    assert report["runtime_artifact_write_allowed"] is False
    assert report["parameter_apply_allowed"] is False
    _assert_safe(report)


def test_ps_q18a_blocks_missing_q17z_source() -> None:
    blocked = build_report()
    assert blocked["ok"] is False
    assert blocked["artifact_resolution_row_count"] == 0
    assert blocked["source_q17z_report_valid"] is False
    assert blocked["source_artifact_resolution_preflight_ready"] is False


def test_ps_q18a_observed_fixture_cli_and_main(capsys) -> None:
    assert main(["--use-observed-fixture"]) == 0
    printed = json.loads(capsys.readouterr().out)
    assert printed["ok"] is True
    assert printed["use_observed_fixture"] is True
    assert printed["stage"] == "warroom_prediction_widget_source_artifact_resolution_preflight_before_source_materialization_d_hot_read_and_real_widget_rendering"
    assert printed["recommended_next_slice"].startswith("PS-Q18B")
    _assert_safe(printed)
    assert main([]) == 1
    blocked = json.loads(capsys.readouterr().out)
    assert blocked["ok"] is False
