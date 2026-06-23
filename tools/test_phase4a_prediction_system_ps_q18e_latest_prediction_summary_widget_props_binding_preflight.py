# path: ./tools/test_phase4a_prediction_system_ps_q18e_latest_prediction_summary_widget_props_binding_preflight.py
# desc: Unit tests for PS-Q18E latest_prediction_summary_widget props binding preflight.

from __future__ import annotations

import json

from check_phase4a_prediction_system_ps_q18e_latest_prediction_summary_widget_props_binding_preflight import CHECKER_VERSION, LATEST_PREDICTION_SUMMARY_WIDGET_PROPS_BINDING_PREFLIGHT_CHECK_VERSION, build_report, main
from btcts.apps.operator_ui.components.prediction_widgets._shared import REQUIRED_COMPONENT_PROPS
from btcts.apps.operator_ui.components.prediction_warroom_latest_prediction_summary_widget_props_binding_preflight import build_latest_prediction_summary_widget_props_binding_preflight_packet


def _assert_safe(report: dict) -> None:
    for key in ("read_only", "non_executing", "latest_prediction_summary_widget_props_binding_preflight_only", "props_candidate_ready", "props_contract_complete", "props_value_binding_deferred"):
        assert report[key] is True, key
    for key in (
        "real_payload_values_bound",
        "widget_props_binding_allowed",
        "widget_props_bound_to_component",
        "render_invocation_allowed",
        "real_prediction_widget_rendering_allowed",
        "actual_source_read_invoked_by_props_preflight",
        "actual_source_read_allowed_by_props_preflight",
        "payload_reparse_allowed",
        "source_discovery_allowed",
        "d_hot_directory_scan_allowed",
        "d_hot_actual_read_allowed",
        "freshness_checked_against_d_hot",
        "warroom_page_mutation_allowed",
        "warroom_widget_rendering_allowed",
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


def test_ps_q18e_validates_props_preflight_from_q18d_fixture() -> None:
    report = build_report(use_observed_fixture=True)
    assert report["ok"] is True
    assert report["checker_version"] == CHECKER_VERSION
    assert report["latest_prediction_summary_widget_props_binding_preflight_check_version"] == LATEST_PREDICTION_SUMMARY_WIDGET_PROPS_BINDING_PREFLIGHT_CHECK_VERSION
    assert report["source_q18d_report_valid"] is True
    assert report["props_packet_valid"] is True
    assert report["widget_family_id"] == "latest_prediction_summary_widget"
    assert report["source_packet_id"] == "latest_prediction_source_review_packet"
    assert report["missing_required_component_props"] == []
    assert report["schema_probe_row_count"] == 4
    assert report["missing_required_schema_keys"] == []
    _assert_safe(report)


def test_ps_q18e_candidate_has_all_required_component_props() -> None:
    schema_packet = {
        "ok": True,
        "probe_version": "prediction_warroom_latest_prediction_summary_widget_schema_probe.ps_q18d.v1",
        "widget_family_id": "latest_prediction_summary_widget",
        "source_packet_id": "latest_prediction_source_review_packet",
        "schema_specific_probe_ready": True,
        "schema_probe_row_count": 4,
        "missing_required_schema_keys": [],
    }
    packet = build_latest_prediction_summary_widget_props_binding_preflight_packet(supplied_schema_probe_packet=schema_packet)
    assert packet["ok"] is True
    candidate = packet["props_candidate"]
    for field in REQUIRED_COMPONENT_PROPS:
        assert field in candidate
    assert candidate["source_generated_at"] == "schema_verified_value_not_bound"
    assert candidate["source_artifact_ref"] == "schema_verified_value_not_bound"
    assert packet["widget_props_binding_allowed"] is False
    assert packet["render_invocation_allowed"] is False


def test_ps_q18e_blocks_without_schema_source() -> None:
    blocked = build_report()
    assert blocked["ok"] is False
    assert blocked["source_q18d_report_valid"] is False
    assert blocked["props_candidate_ready"] is False
    assert blocked["widget_props_bound_to_component"] is False


def test_ps_q18e_observed_fixture_cli_and_main(capsys) -> None:
    assert main(["--use-observed-fixture"]) == 0
    printed = json.loads(capsys.readouterr().out)
    assert printed["ok"] is True
    assert printed["use_observed_fixture"] is True
    assert printed["stage"] == "latest_prediction_summary_widget_props_binding_preflight_before_component_binding_real_rendering_refresh_and_writes"
    assert printed["recommended_next_slice"].startswith("PS-Q18F")
    _assert_safe(printed)
    assert main([]) == 1
    blocked = json.loads(capsys.readouterr().out)
    assert blocked["ok"] is False
