# path: ./tools/test_phase4a_prediction_system_ps_q18d_latest_prediction_summary_widget_schema_probe.py
# desc: Unit tests for PS-Q18D latest_prediction_summary_widget schema-specific probe.

from __future__ import annotations

import json

from check_phase4a_prediction_system_ps_q18d_latest_prediction_summary_widget_schema_probe import CHECKER_VERSION, LATEST_PREDICTION_SUMMARY_WIDGET_SCHEMA_PROBE_CHECK_VERSION, build_report, main
from btcts.apps.operator_ui.components.prediction_warroom_latest_prediction_summary_widget_schema_probe import REQUIRED_SUMMARY_SCHEMA_KEYS, build_latest_prediction_summary_widget_schema_probe_packet


def _assert_safe(report: dict) -> None:
    for key in ("read_only", "non_executing", "latest_prediction_summary_widget_schema_probe_only", "schema_specific_probe_ready", "preview_key_contract_only"):
        assert report[key] is True, key
    for key in (
        "payload_reparse_allowed",
        "actual_source_read_invoked_by_schema_probe",
        "actual_source_read_allowed_by_schema_probe",
        "source_discovery_allowed",
        "d_hot_directory_scan_allowed",
        "d_hot_actual_read_allowed",
        "freshness_checked_against_d_hot",
        "warroom_page_mutation_allowed",
        "warroom_widget_rendering_allowed",
        "real_prediction_widget_rendering_allowed",
        "widget_props_binding_allowed",
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


def test_ps_q18d_validates_latest_summary_schema_from_q18b_fixture() -> None:
    report = build_report(use_observed_fixture=True)
    assert report["ok"] is True
    assert report["checker_version"] == CHECKER_VERSION
    assert report["latest_prediction_summary_widget_schema_probe_check_version"] == LATEST_PREDICTION_SUMMARY_WIDGET_SCHEMA_PROBE_CHECK_VERSION
    assert report["source_q18b_report_valid"] is True
    assert report["schema_packet_valid"] is True
    assert report["widget_family_id"] == "latest_prediction_summary_widget"
    assert report["source_packet_id"] == "latest_prediction_source_review_packet"
    assert report["schema_probe_row_count"] == len(REQUIRED_SUMMARY_SCHEMA_KEYS)
    assert report["missing_required_schema_keys"] == []
    _assert_safe(report)


def test_ps_q18d_blocks_missing_required_schema_key() -> None:
    probe_packet = {
        "ok": True,
        "probe_version": "prediction_warroom_prediction_widget_bounded_actual_source_read_probe.ps_q18b.v1",
        "source_packet_id": "latest_prediction_source_review_packet",
        "source_artifact_ref_field": "latest_prediction.source_artifact_ref",
        "payload_decode_succeeded": True,
        "schema_probe_ok": True,
        "payload_preview_keys": ["prediction_run_id", "generated_at", "market_uid"],
    }
    packet = build_latest_prediction_summary_widget_schema_probe_packet(supplied_probe_packet=probe_packet)
    assert packet["ok"] is False
    assert packet["missing_required_schema_keys"] == ["source_artifact_ref"]
    assert packet["actual_source_read_invoked_by_schema_probe"] is False


def test_ps_q18d_blocks_without_q18b_source() -> None:
    blocked = build_report()
    assert blocked["ok"] is False
    assert blocked["source_q18b_report_valid"] is False
    assert blocked["schema_probe_row_count"] == 0
    assert blocked["actual_source_read_invoked_by_schema_probe"] is False


def test_ps_q18d_observed_fixture_cli_and_main(capsys) -> None:
    assert main(["--use-observed-fixture"]) == 0
    printed = json.loads(capsys.readouterr().out)
    assert printed["ok"] is True
    assert printed["use_observed_fixture"] is True
    assert printed["stage"] == "latest_prediction_summary_widget_schema_probe_before_widget_props_binding_real_rendering_refresh_and_writes"
    assert printed["recommended_next_slice"].startswith("PS-Q18E")
    _assert_safe(printed)
    assert main([]) == 1
    blocked = json.loads(capsys.readouterr().out)
    assert blocked["ok"] is False
