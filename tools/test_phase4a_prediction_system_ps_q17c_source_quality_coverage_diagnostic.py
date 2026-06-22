# path: ./tools/test_phase4a_prediction_system_ps_q17c_source_quality_coverage_diagnostic.py
# desc: Unit tests for PS-Q17C source-quality coverage diagnostic.

from __future__ import annotations

import json

from check_phase4a_prediction_system_ps_q17b_inference_quality_gap_plan import CHECKER_VERSION as PS_Q17B_CHECKER_VERSION
from check_phase4a_prediction_system_ps_q17c_source_quality_coverage_diagnostic import CHECKER_VERSION, DIAGNOSTIC_ORDER, REQUIRED_SOURCE_QUALITY_FIELDS, build_report, main


def _q17b_report() -> dict:
    return {
        "ok": True,
        "checker_version": PS_Q17B_CHECKER_VERSION,
        "plan_only": True,
        "warroom_widget_design_premise": True,
        "warroom_widget_implementation_allowed": False,
        "plan_rows": [
            {
                "gap_id": "source_quality_cap_and_coverage",
                "priority": "P0",
                "state": "open",
                "reasons": ["source_quality_warning_record_count=110", "source_quality_warnings_present_in_records"],
                "blocks_before_warroom_widget_implementation": True,
                "read_only": True,
                "write_or_apply_allowed": False,
            }
        ],
        "parameter_apply_allowed": False,
        "parameter_staging_write_allowed": False,
        "approval_or_authorization_allowed": False,
        "ledger_append_allowed": False,
        "autotrade_trigger_allowed": False,
        "broker_private_api_allowed": False,
        "would_write_runtime_artifact": False,
        "would_write_collector_state": False,
        "would_send_to_broker": False,
        "warroom_ui_trigger_enabled": False,
        "refresh_invocation_allowed": False,
        "scheduler_enabled": False,
    }


def _assert_safe(report: dict) -> None:
    assert report["read_only"] is True
    assert report["non_executing"] is True
    assert report["diagnostic_only"] is True
    assert report["plan_only"] is True
    assert report["warroom_widget_design_premise"] is True
    for key in (
        "warroom_widget_implementation_allowed",
        "confidence_increase_allowed",
        "runtime_artifact_write_allowed",
        "status_artifact_write_allowed",
        "d_hot_actual_read_allowed",
        "parameter_apply_allowed",
        "parameter_staging_write_allowed",
        "approval_or_authorization_allowed",
        "ledger_append_allowed",
        "autotrade_trigger_allowed",
        "broker_private_api_allowed",
        "would_write_runtime_artifact",
        "would_write_collector_state",
        "would_send_to_broker",
        "warroom_ui_trigger_enabled",
        "refresh_invocation_allowed",
        "scheduler_enabled",
    ):
        assert report[key] is False, key


def test_ps_q17c_decomposes_source_quality_p0_gap() -> None:
    report = build_report(supplied_q17b_report=_q17b_report())
    assert report["ok"] is True
    assert report["checker_version"] == CHECKER_VERSION
    assert report["source_q17b_report_valid"] is True
    assert report["source_quality_gap_id"] == "source_quality_cap_and_coverage"
    assert report["diagnostic_count"] == 6
    assert report["p0_diagnostic_count"] >= 4
    diagnostic_ids = [row["diagnostic_id"] for row in report["diagnostic_rows"]]
    for expected in DIAGNOSTIC_ORDER:
        assert expected in diagnostic_ids
    assert "tier0_source_quality_gate.state" in report["required_source_quality_fields"]
    assert "tier0_source_quality_gate_not_passed" in report["observed_warning_taxonomy"]
    assert report["recommended_first_validation"] == "tier0_source_quality_gate_coverage"
    _assert_safe(report)


def test_ps_q17c_blocks_invalid_or_nonblocking_q17b_report() -> None:
    invalid = build_report()
    assert invalid["ok"] is False
    assert "q17b_checker_version_mismatch" in invalid["source_q17b_validation_failures"]
    assert invalid["diagnostic_rows"] == []
    _assert_safe(invalid)
    unsafe = _q17b_report()
    unsafe["would_send_to_broker"] = True
    report = build_report(supplied_q17b_report=unsafe)
    assert report["ok"] is False
    assert "q17b_boundary_not_false:would_send_to_broker" in report["source_q17b_validation_failures"]
    _assert_safe(report)
    nonblocking = _q17b_report()
    nonblocking["plan_rows"][0]["blocks_before_warroom_widget_implementation"] = False
    blocked = build_report(supplied_q17b_report=nonblocking)
    assert blocked["ok"] is False
    assert "source_quality_gap_not_blocking_widgets" in blocked["source_q17b_validation_failures"]


def test_ps_q17c_observed_fixture_cli_and_main(capsys) -> None:
    assert main(["--use-observed-fixture"]) == 0
    printed = json.loads(capsys.readouterr().out)
    assert printed["ok"] is True
    assert printed["use_observed_fixture"] is True
    assert printed["p0_diagnostic_count"] >= 4
    assert "source_artifact_coverage.by_family" in printed["required_source_quality_fields"]
    _assert_safe(printed)
    assert main([]) == 1
    blocked = json.loads(capsys.readouterr().out)
    assert blocked["ok"] is False
    _assert_safe(blocked)


def test_ps_q17c_keeps_diagnostic_out_of_execution_and_ui_scope() -> None:
    report = build_report(supplied_q17b_report=_q17b_report())
    assert report["warroom_widget_implementation_allowed"] is False
    assert report["confidence_increase_allowed"] is False
    assert report["d_hot_actual_read_allowed"] is False
    assert report["recommended_next_slice"].startswith("PS-Q17D")
    for row in report["diagnostic_rows"]:
        assert row["read_only"] is True
        assert row["write_or_apply_allowed"] is False
        assert row["state"] == "open"
        assert row["next_validation"].endswith("_guard")
    assert len(REQUIRED_SOURCE_QUALITY_FIELDS) >= 8
