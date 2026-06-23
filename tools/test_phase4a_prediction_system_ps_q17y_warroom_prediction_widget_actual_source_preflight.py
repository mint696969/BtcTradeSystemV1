# path: ./tools/test_phase4a_prediction_system_ps_q17y_warroom_prediction_widget_actual_source_preflight.py
# desc: Unit tests for PS-Q17Y WarRoom prediction widget actual-source preflight.

from __future__ import annotations

import json

from check_phase4a_prediction_system_ps_q17y_warroom_prediction_widget_actual_source_preflight import ACTUAL_SOURCE_PREFLIGHT_VERSION, CHECKER_VERSION, WIDGET_FAMILY_ORDER, build_report, main


def _assert_safe(report: dict) -> None:
    for key in ("read_only", "non_executing", "actual_source_preflight_only"):
        assert report[key] is True, key
    for key in (
        "source_artifact_resolution_allowed",
        "actual_source_bound",
        "source_artifact_resolved",
        "freshness_checked_against_d_hot",
        "readiness_row_visible_in_warroom",
        "real_prediction_widget_rendering_allowed",
        "warroom_widget_rendering_allowed",
        "warroom_page_mutation_allowed",
        "warroom_mount_patch_allowed",
        "actual_source_read_allowed",
        "d_hot_actual_read_allowed",
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


def test_ps_q17y_builds_actual_source_preflight_rows_from_q17p_and_q17x_fixtures() -> None:
    report = build_report(use_observed_fixture=True)
    assert report["ok"] is True
    assert report["checker_version"] == CHECKER_VERSION
    assert report["actual_source_preflight_version"] == ACTUAL_SOURCE_PREFLIGHT_VERSION
    assert report["source_q17p_report_valid"] is True
    assert report["source_q17x_report_valid"] is True
    assert report["preflight_row_count"] == 12
    assert [row["widget_family_id"] for row in report["preflight_rows"]] == list(WIDGET_FAMILY_ORDER)
    assert report["source_binding_contract_ready"] is True
    _assert_safe(report)


def test_ps_q17y_rows_keep_actual_read_binding_render_refresh_and_writes_disabled() -> None:
    report = build_report(use_observed_fixture=True)
    for row in report["preflight_rows"]:
        assert row["actual_source_binding_ready"] is True
        assert row["actual_source_bound"] is False
        assert row["source_artifact_resolved"] is False
        assert row["freshness_checked_against_d_hot"] is False
        assert row["real_widget_render_ready"] is False
        assert row["render_allowed"] is False
        assert row["actual_source_read_allowed"] is False
        assert row["d_hot_actual_read_allowed"] is False
        assert row["refresh_invocation_allowed"] is False
        assert row["runtime_artifact_write_allowed"] is False
        assert row["status_artifact_write_allowed"] is False
        assert row["parameter_apply_allowed"] is False
        assert row["ledger_append_allowed"] is False
        assert row["autotrade_trigger_allowed"] is False
        assert row["broker_private_api_allowed"] is False
    _assert_safe(report)


def test_ps_q17y_blocks_missing_sources() -> None:
    blocked = build_report()
    assert blocked["ok"] is False
    assert blocked["preflight_row_count"] == 0
    assert blocked["source_binding_contract_ready"] is False
    _assert_safe(blocked)


def test_ps_q17y_observed_fixture_cli_and_main(capsys) -> None:
    assert main(["--use-observed-fixture"]) == 0
    printed = json.loads(capsys.readouterr().out)
    assert printed["ok"] is True
    assert printed["use_observed_fixture"] is True
    assert printed["stage"] == "warroom_prediction_widget_actual_source_preflight_before_d_hot_read_and_real_widget_rendering"
    assert printed["recommended_next_slice"].startswith("PS-Q17Z")
    _assert_safe(printed)
    assert main([]) == 1
    blocked = json.loads(capsys.readouterr().out)
    assert blocked["ok"] is False
    _assert_safe(blocked)
