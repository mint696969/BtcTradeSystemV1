# path: ./tools/test_phase4a_prediction_system_ps_q18b_warroom_prediction_widget_bounded_actual_source_read_probe.py
# desc: Unit tests for PS-Q18B bounded actual-source read probe.

from __future__ import annotations

import json

from check_phase4a_prediction_system_ps_q18b_warroom_prediction_widget_bounded_actual_source_read_probe import CHECKER_VERSION, BOUNDED_ACTUAL_SOURCE_READ_PROBE_CHECK_VERSION, build_report, main
from btcts.apps.operator_ui.components.prediction_warroom_prediction_widget_bounded_actual_source_read_probe import ALLOW_ACK, build_prediction_warroom_prediction_widget_bounded_actual_source_read_probe_packet


def _assert_safe(report: dict) -> None:
    for key in ("read_only", "non_executing", "bounded_actual_source_read_probe_only", "single_file_probe_only"):
        assert report[key] is True, key
    for key in (
        "source_discovery_allowed",
        "d_hot_directory_scan_allowed",
        "d_hot_actual_read_allowed",
        "freshness_checked_against_d_hot",
        "warroom_page_mutation_allowed",
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


def test_ps_q18b_probe_reads_one_explicit_fixture_json_only(tmp_path) -> None:
    fixture = tmp_path / "latest_prediction_fixture.json"
    fixture.write_text(json.dumps({"prediction_run_id": "run1", "generated_at": "2026-06-22T00:00:00Z"}), encoding="utf-8")
    probe = build_prediction_warroom_prediction_widget_bounded_actual_source_read_probe_packet(
        source_packet_id="latest_prediction_source_review_packet",
        source_artifact_ref_field="latest_prediction.source_artifact_ref",
        explicit_source_path=str(fixture),
        allow_actual_read=True,
        explicit_ack=ALLOW_ACK,
    )
    assert probe["ok"] is True
    assert probe["actual_file_read_attempted"] is True
    assert probe["actual_file_read_succeeded"] is True
    assert probe["payload_decode_succeeded"] is True
    report = build_report(supplied_probe_packet=probe, use_observed_fixture=True)
    assert report["ok"] is True
    assert report["checker_version"] == CHECKER_VERSION
    assert report["bounded_actual_source_read_probe_check_version"] == BOUNDED_ACTUAL_SOURCE_READ_PROBE_CHECK_VERSION
    assert report["actual_source_read_allowed"] is True
    assert report["payload_preview_key_count"] >= 1
    _assert_safe(report)


def test_ps_q18b_blocks_without_ack_or_allow(tmp_path) -> None:
    fixture = tmp_path / "blocked.json"
    fixture.write_text("{}", encoding="utf-8")
    blocked = build_prediction_warroom_prediction_widget_bounded_actual_source_read_probe_packet(
        source_packet_id="latest_prediction_source_review_packet",
        source_artifact_ref_field="latest_prediction.source_artifact_ref",
        explicit_source_path=str(fixture),
        allow_actual_read=False,
        explicit_ack="",
    )
    assert blocked["ok"] is False
    assert blocked["actual_file_read_attempted"] is False
    assert "allow_actual_read_false" in blocked["blocker_reasons"]
    assert "explicit_ack_missing_or_mismatch" in blocked["blocker_reasons"]


def test_ps_q18b_observed_fixture_report_is_safe() -> None:
    report = build_report(use_observed_fixture=True)
    assert report["ok"] is True
    assert report["source_q18a_report_valid"] is True
    assert report["probe_packet_valid"] is True
    assert report["actual_file_read_attempted"] is True
    assert report["payload_decode_succeeded"] is True
    _assert_safe(report)


def test_ps_q18b_observed_fixture_cli_and_main(capsys) -> None:
    assert main(["--use-observed-fixture"]) == 0
    printed = json.loads(capsys.readouterr().out)
    assert printed["ok"] is True
    assert printed["use_observed_fixture"] is True
    assert printed["stage"] == "warroom_prediction_widget_bounded_actual_source_read_probe_before_warroom_binding_real_widget_rendering_and_refresh"
    assert printed["recommended_next_slice"].startswith("PS-Q18C")
    _assert_safe(printed)
    assert main([]) == 1
    blocked = json.loads(capsys.readouterr().out)
    assert blocked["ok"] is False
