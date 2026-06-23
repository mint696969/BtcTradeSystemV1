# path: ./tools/test_phase4a_prediction_system_ps_q18i_latest_prediction_summary_widget_real_payload_value_mapping_preflight.py
# desc: Unit tests for PS-Q18I latest_prediction_summary_widget real decoded-payload value mapping preflight.

from __future__ import annotations

import json

from check_phase4a_prediction_system_ps_q18i_latest_prediction_summary_widget_real_payload_value_mapping_preflight import CHECKER_VERSION, REAL_PAYLOAD_VALUE_MAPPING_PREFLIGHT_CHECK_VERSION, build_report, main, observed_decoded_payload_fixture
from btcts.apps.operator_ui.components.prediction_warroom_latest_prediction_summary_widget_real_payload_value_mapping_preflight import REQUIRED_REAL_PAYLOAD_VALUE_KEYS, build_latest_prediction_summary_widget_real_payload_value_mapping_preflight_packet


def _assert_safe(report: dict) -> None:
    for key in ("read_only", "non_executing", "latest_prediction_summary_widget_real_payload_value_mapping_preflight_only", "decoded_payload_supplied", "decoded_payload_values_mapped_to_props_candidate", "real_payload_values_bound_to_props_candidate"):
        assert report[key] is True, key
    assert report["props_value_binding_deferred"] is False
    for key in (
        "real_payload_values_bound_to_component",
        "component_props_binding_allowed",
        "component_props_bound_to_component",
        "component_runtime_binding_allowed",
        "streamlit_render_allowed",
        "streamlit_render_invoked",
        "render_invocation_allowed",
        "real_prediction_widget_rendering_allowed",
        "actual_source_read_invoked_by_mapping",
        "actual_source_read_allowed_by_mapping",
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


def test_ps_q18i_maps_real_payload_values_from_observed_fixture() -> None:
    report = build_report(use_observed_fixture=True)
    assert report["ok"] is True
    assert report["checker_version"] == CHECKER_VERSION
    assert report["real_payload_value_mapping_preflight_check_version"] == REAL_PAYLOAD_VALUE_MAPPING_PREFLIGHT_CHECK_VERSION
    assert report["source_q18e_report_valid"] is True
    assert report["mapping_packet_valid"] is True
    assert report["missing_required_payload_value_keys"] == []
    assert report["missing_required_component_props"] == []
    assert report["mapped_prediction_run_id"] == "ps_q18i_fixture_run"
    assert report["mapped_market_uid"] == "BTC-USD"
    assert report["mapped_source_generated_at"] == "2026-06-22T00:00:00Z"
    assert report["mapped_source_artifact_ref"] == "fixture://ps_q18i/latest_prediction.json"
    _assert_safe(report)


def test_ps_q18i_component_packet_mapping_blocks_missing_payload() -> None:
    packet = build_latest_prediction_summary_widget_real_payload_value_mapping_preflight_packet()
    assert packet["ok"] is False
    assert packet["decoded_payload_supplied"] is False
    assert set(REQUIRED_REAL_PAYLOAD_VALUE_KEYS).issuperset(packet["missing_required_payload_value_keys"])
    assert packet["real_payload_values_bound_to_props_candidate"] is False
    assert packet["component_props_binding_allowed"] is False
    assert packet["streamlit_render_invoked"] is False


def test_ps_q18i_blocks_missing_q18e_source() -> None:
    blocked = build_report(supplied_decoded_payload=observed_decoded_payload_fixture())
    assert blocked["ok"] is False
    assert blocked["source_q18e_report_valid"] is False
    assert blocked["decoded_payload_values_mapped_to_props_candidate"] is False
    assert blocked["actual_source_read_invoked_by_mapping"] is False


def test_ps_q18i_observed_fixture_cli_and_main(capsys) -> None:
    assert main(["--use-observed-fixture"]) == 0
    printed = json.loads(capsys.readouterr().out)
    assert printed["ok"] is True
    assert printed["use_observed_fixture"] is True
    assert printed["stage"] == "latest_prediction_summary_widget_real_payload_value_mapping_preflight_before_component_binding_real_rendering_refresh_and_writes"
    assert printed["recommended_next_slice"].startswith("PS-Q18J")
    _assert_safe(printed)
    assert main([]) == 1
    blocked = json.loads(capsys.readouterr().out)
    assert blocked["ok"] is False
