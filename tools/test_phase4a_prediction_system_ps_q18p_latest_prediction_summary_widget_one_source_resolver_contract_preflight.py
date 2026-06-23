# path: ./tools/test_phase4a_prediction_system_ps_q18p_latest_prediction_summary_widget_one_source_resolver_contract_preflight.py
# desc: Unit tests for PS-Q18P latest_prediction_summary_widget one-source resolver contract preflight.

from __future__ import annotations

import json

from check_phase4a_prediction_system_ps_q18p_latest_prediction_summary_widget_one_source_resolver_contract_preflight import CHECKER_VERSION, ONE_SOURCE_RESOLVER_CONTRACT_PREFLIGHT_CHECK_VERSION, build_report, main
from btcts.apps.operator_ui.components.prediction_warroom_latest_prediction_summary_widget_one_source_resolver_contract_preflight import ONE_SOURCE_RESOLVER_CONTRACT_ACK, build_latest_prediction_summary_widget_one_source_resolver_contract_preflight_packet


def _assert_safe(report: dict) -> None:
    for key in ("read_only", "non_executing", "latest_prediction_summary_widget_one_source_resolver_contract_preflight_only", "one_source_resolver_contract_preflight_ready", "resolver_contract_declared", "one_source_candidate_preserved", "source_candidate_count_fixed_to_one", "explicit_resolver_contract_ack_matched"):
        assert report[key] is True, key
    for key in (
        "warroom_page_mutation_allowed",
        "source_artifact_resolver_invoked",
        "source_artifact_resolution_allowed",
        "source_artifact_resolved",
        "source_artifact_path_materialized",
        "source_artifact_exists_checked",
        "source_artifact_schema_checked",
        "actual_source_read_allowed",
        "actual_source_read_invoked",
        "payload_reparse_allowed",
        "source_discovery_allowed",
        "d_hot_directory_scan_allowed",
        "d_hot_actual_read_allowed",
        "q18o_validation_invoked_by_mount",
        "q18n_validation_invoked_by_mount",
        "component_packet_builder_invoked_by_mount",
        "streamlit_render_invoked",
        "real_prediction_widget_rendering_allowed",
        "refresh_invocation_allowed",
        "runtime_artifact_write_allowed",
        "parameter_apply_allowed",
        "broker_private_api_allowed",
    ):
        assert report[key] is False, key


def test_ps_q18p_validates_resolver_contract_from_q18o_fixture() -> None:
    report = build_report(use_observed_fixture=True)
    assert report["ok"] is True
    assert report["checker_version"] == CHECKER_VERSION
    assert report["one_source_resolver_contract_preflight_check_version"] == ONE_SOURCE_RESOLVER_CONTRACT_PREFLIGHT_CHECK_VERSION
    assert report["one_source_resolver_contract_ack"] == ONE_SOURCE_RESOLVER_CONTRACT_ACK
    assert report["source_q18o_report_valid"] is True
    assert report["resolver_contract_packet_valid"] is True
    assert report["resolver_contract_row_count"] == 10
    assert report["source_candidate_count"] == 1
    assert report["resolver_contract_candidate_ready"] is True
    assert report["resolver_input_ref_kind"] == "artifact_ref_string_only"
    assert report["selected_candidate_generated_at"] == "2026-06-22T00:00:00Z"
    assert report["selected_candidate_source_artifact_ref"] == "fixture://ps_q18i/latest_prediction.json"
    assert report["selected_candidate_market_uid"] == "BTC-USD"
    _assert_safe(report)


def test_ps_q18p_packet_without_source_is_contract_only_but_candidate_not_ready() -> None:
    packet = build_latest_prediction_summary_widget_one_source_resolver_contract_preflight_packet()
    assert packet["ok"] is True
    assert packet["resolver_contract_row_count"] == 10
    assert packet["source_candidate_count"] == 1
    assert packet["one_source_resolver_contract_ack"] == ONE_SOURCE_RESOLVER_CONTRACT_ACK
    assert packet["supplied_design_checkpoint_report"] is False
    assert packet["resolver_contract_candidate_ready"] is False
    assert packet["resolver_input_ref_kind"] == "artifact_ref_string_only"
    assert packet["source_artifact_resolver_invoked"] is False
    assert packet["source_artifact_resolution_allowed"] is False
    assert packet["actual_source_read_invoked"] is False


def test_ps_q18p_blocks_missing_q18o_source() -> None:
    blocked = build_report()
    assert blocked["ok"] is False
    assert blocked["resolver_contract_row_count"] == 0
    assert blocked["source_q18o_report_valid"] is False
    assert blocked["source_artifact_resolver_invoked"] is False
    assert blocked["actual_source_read_invoked"] is False


def test_ps_q18p_observed_fixture_cli_and_main(capsys) -> None:
    assert main(["--use-observed-fixture"]) == 0
    printed = json.loads(capsys.readouterr().out)
    assert printed["ok"] is True
    assert printed["use_observed_fixture"] is True
    assert printed["stage"] == "latest_prediction_summary_widget_one_source_resolver_contract_preflight_before_resolution_path_materialization_read_render_refresh_and_writes"
    assert printed["recommended_next_slice"].startswith("PS-Q18Q")
    _assert_safe(printed)
    assert main([]) == 1
    blocked = json.loads(capsys.readouterr().out)
    assert blocked["ok"] is False
