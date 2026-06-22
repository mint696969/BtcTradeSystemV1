# path: ./tools/test_phase4a_prediction_system_ps_q17d_tier0_source_quality_gate_coverage_contract.py
# desc: Unit tests for PS-Q17D tier0 source-quality gate coverage contract.

from __future__ import annotations

import json

from check_phase4a_prediction_system_ps_q17c_source_quality_coverage_diagnostic import CHECKER_VERSION as PS_Q17C_CHECKER_VERSION
from check_phase4a_prediction_system_ps_q17d_tier0_source_quality_gate_coverage_contract import CHECKER_VERSION, CONTRACT_ORDER, REQUIRED_TIER0_FIELDS, build_report, main


def _q17c_report() -> dict:
    return {
        "ok": True,
        "checker_version": PS_Q17C_CHECKER_VERSION,
        "diagnostic_only": True,
        "plan_only": True,
        "warroom_widget_design_premise": True,
        "warroom_widget_implementation_allowed": False,
        "confidence_increase_allowed": False,
        "d_hot_actual_read_allowed": False,
        "diagnostic_rows": [
            {
                "diagnostic_id": "tier0_source_quality_gate_coverage",
                "priority": "P0",
                "state": "open",
                "evidence": ["source_quality_warning_record_count=110"],
                "missing_contracts": [
                    "tier0_source_quality_gate.state",
                    "tier0_source_quality_gate.reason_codes",
                    "source_artifact_coverage.required_source_count",
                    "source_artifact_coverage.usable_source_count",
                ],
                "blocks_confidence_increase": True,
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
    assert report["contract_only"] is True
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


def test_ps_q17d_builds_tier0_gate_contract_from_q17c_diagnostic() -> None:
    report = build_report(supplied_q17c_report=_q17c_report())
    assert report["ok"] is True
    assert report["checker_version"] == CHECKER_VERSION
    assert report["source_q17c_report_valid"] is True
    assert report["source_diagnostic_id"] == "tier0_source_quality_gate_coverage"
    assert report["contract_count"] == 6
    assert report["p0_contract_count"] == 4
    assert report["p1_contract_count"] == 2
    contract_ids = [row["contract_id"] for row in report["contract_rows"]]
    for expected in CONTRACT_ORDER:
        assert expected in contract_ids
    assert report["recommended_first_validation"] == "tier0_gate_state_reason_contract"
    assert "tier0_source_quality_gate.state" in report["required_tier0_fields"]
    assert report["gate_state_enum"] == ["pass", "warn", "fail", "unknown"]
    _assert_safe(report)


def test_ps_q17d_blocks_invalid_or_nonblocking_q17c_report() -> None:
    invalid = build_report()
    assert invalid["ok"] is False
    assert "q17c_checker_version_mismatch" in invalid["source_q17c_validation_failures"]
    assert invalid["contract_rows"] == []
    _assert_safe(invalid)
    unsafe = _q17c_report()
    unsafe["would_send_to_broker"] = True
    report = build_report(supplied_q17c_report=unsafe)
    assert report["ok"] is False
    assert "q17c_boundary_not_false:would_send_to_broker" in report["source_q17c_validation_failures"]
    _assert_safe(report)
    nonblocking = _q17c_report()
    nonblocking["diagnostic_rows"][0]["blocks_confidence_increase"] = False
    blocked = build_report(supplied_q17c_report=nonblocking)
    assert blocked["ok"] is False
    assert "tier0_source_quality_gate_coverage_not_confidence_blocking" in blocked["source_q17c_validation_failures"]


def test_ps_q17d_observed_fixture_cli_and_main(capsys) -> None:
    assert main(["--use-observed-fixture"]) == 0
    printed = json.loads(capsys.readouterr().out)
    assert printed["ok"] is True
    assert printed["use_observed_fixture"] is True
    assert printed["p0_contract_count"] == 4
    assert "required_usable_source_count_contract" in printed["blocks_confidence_increase"]
    _assert_safe(printed)
    assert main([]) == 1
    blocked = json.loads(capsys.readouterr().out)
    assert blocked["ok"] is False
    _assert_safe(blocked)


def test_ps_q17d_keeps_contract_out_of_live_read_confidence_and_ui_scope() -> None:
    report = build_report(supplied_q17c_report=_q17c_report())
    assert report["warroom_widget_implementation_allowed"] is False
    assert report["confidence_increase_allowed"] is False
    assert report["d_hot_actual_read_allowed"] is False
    assert report["recommended_next_slice"].startswith("PS-Q17E")
    for row in report["contract_rows"]:
        assert row["read_only"] is True
        assert row["write_or_apply_allowed"] is False
        assert row["state"] == "required"
        assert row["next_validation"].endswith("_guard")
    assert len(REQUIRED_TIER0_FIELDS) >= 10
