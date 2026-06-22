# path: ./tools/test_phase4a_prediction_system_ps_q17h_close_guard.py
# desc: Close guard for PS-Q17H prediction-delta history contract.

from __future__ import annotations

import ast
import json
import subprocess
from pathlib import Path

from check_phase4a_prediction_system_ps_q17h_prediction_delta_history_contract import CHECKER_VERSION, CONTRACT_ORDER, DELTA_REASON_CODES, REQUIRED_DELTA_FIELDS, build_report, main

REPO_ROOT = Path(__file__).resolve().parents[1]
TOOL = REPO_ROOT / "tools/check_phase4a_prediction_system_ps_q17h_prediction_delta_history_contract.py"
UNIT = REPO_ROOT / "tools/test_phase4a_prediction_system_ps_q17h_prediction_delta_history_contract.py"
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q17H_PREDICTION_DELTA_HISTORY_CONTRACT_2026-06-22.md"
FOCUSED_GUARD = "tools/test_phase4a_prediction_system_ps_q17h_prediction_delta_history_contract_guard.py"
EXPECTED_DIRTY = {
    "tools/check_phase4a_prediction_system_ps_q17h_prediction_delta_history_contract.py",
    "tools/test_phase4a_prediction_system_ps_q17h_prediction_delta_history_contract.py",
    "docs/strategy/PREDICTION_SYSTEM_PS_Q17H_PREDICTION_DELTA_HISTORY_CONTRACT_2026-06-22.md",
    "tools/test_phase4a_prediction_system_ps_q17h_prediction_delta_history_contract_guard.py",
    "tools/test_phase4a_prediction_system_ps_q17h_close_guard.py",
}
EXPECTED_CONTRACTS = (
    "previous_latest_snapshot_reference_contract",
    "latest_snapshot_lineage_contract",
    "delta_computation_key_contract",
    "delta_reason_taxonomy_contract",
    "warroom_delta_widget_release_contract",
    "history_retention_and_freshness_contract",
)
EXPECTED_P0 = (
    "previous_latest_snapshot_reference_contract",
    "latest_snapshot_lineage_contract",
    "delta_computation_key_contract",
    "warroom_delta_widget_release_contract",
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def _dirty_paths() -> set[str]:
    proc = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True)
    return {line[3:].replace(chr(92), "/") for line in proc.stdout.splitlines() if line.strip()}


def _assert_false_boundaries(report: dict, failures: list[str]) -> None:
    for key in (
        "read_only",
        "non_executing",
        "contract_only",
        "diagnostic_only",
        "plan_only",
        "warroom_widget_design_premise",
    ):
        if report.get(key) is not True:
            failures.append(f"{key} must be true")
    for key in (
        "warroom_widget_implementation_allowed",
        "delta_widget_rendering_allowed",
        "history_actual_read_allowed",
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
        if report.get(key) is not False:
            failures.append(f"{key} must stay false")


def main_guard() -> int:
    failures: list[str] = []
    for path in (TOOL, UNIT, DOC):
        if not path.exists():
            failures.append(f"missing file: {path.relative_to(REPO_ROOT)}")
            continue
        if path.suffix == ".py":
            try:
                ast.parse(_read(path), filename=str(path))
            except SyntaxError as exc:
                failures.append(f"syntax failed: {path.relative_to(REPO_ROOT)}: {exc}")
    tool_text = _read(TOOL) if TOOL.exists() else ""
    unit_text = _read(UNIT) if UNIT.exists() else ""
    doc_text = _read(DOC) if DOC.exists() else ""
    for marker in (
        "CHECKER = \"ps_q17h_prediction_delta_history_contract\"",
        "CHECKER_VERSION = \"check_phase4a_prediction_system_ps_q17h_prediction_delta_history_contract.v1\"",
        "PS_Q17B_SOURCE_CHECKER_VERSION",
        "SOURCE_GAP_ID = \"prediction_delta_history\"",
        "CONTRACT_ORDER",
        "REQUIRED_DELTA_FIELDS",
        "DELTA_REASON_CODES",
        "previous_latest_snapshot_reference_contract",
        "latest_snapshot_lineage_contract",
        "delta_computation_key_contract",
        "delta_reason_taxonomy_contract",
        "warroom_delta_widget_release_contract",
        "history_retention_and_freshness_contract",
        "blocks_realtime_delta_widget",
        "history_required_before_delta_claim",
        "delta_widget_rendering_allowed",
        "history_actual_read_allowed",
        "PS-Q17I prediction-delta history adapter",
    ):
        if marker not in tool_text:
            failures.append(f"missing tool marker: {marker}")
    for forbidden in (
        "from pathlib import Path",
        "read_text(",
        "write_text(",
        "write_bytes(",
        "open(",
        "mkdir(",
        "unlink(",
        "replace(",
        "data_read",
        "data_slice",
        "allow_actual_read=True",
        "build_report(hot_root=",
        "append_decision(",
        "append_command(",
        "send_order(",
        "create_order(",
    ):
        if forbidden in tool_text:
            failures.append(f"forbidden tool token: {forbidden}")
    if "test_ps_q17h_builds_delta_history_contract_from_q17b_gap" not in unit_text:
        failures.append("unit test must cover Q17B delta gap to contract")
    if "test_ps_q17h_blocks_invalid_or_nonblocking_q17b_report" not in unit_text:
        failures.append("unit test must cover invalid/nonblocking Q17B blocking")
    if CHECKER_VERSION != "check_phase4a_prediction_system_ps_q17h_prediction_delta_history_contract.v1":
        failures.append("checker version mismatch")
    if tuple(CONTRACT_ORDER) != EXPECTED_CONTRACTS:
        failures.append("contract order mismatch")
    for reason in (
        "previous_payload_missing_delta_widget_gap",
        "snapshot_lineage_mismatch",
        "market_or_horizon_key_mismatch",
        "changed_signal_strength",
        "changed_source_quality_state",
        "changed_scenario_trace",
    ):
        if reason not in DELTA_REASON_CODES:
            failures.append(f"delta reason code missing: {reason}")
    for field in (
        "prediction_delta_history.previous_snapshot.run_id",
        "prediction_delta_history.previous_snapshot.generated_at",
        "prediction_delta_history.previous_snapshot.source_artifact_ref",
        "prediction_delta_history.latest_snapshot.run_id",
        "prediction_delta_history.latest_snapshot.generated_at",
        "prediction_delta_history.latest_snapshot.source_artifact_ref",
        "prediction_delta_history.delta_key.market_uid",
        "prediction_delta_history.delta_key.family",
        "prediction_delta_history.delta_key.horizon_key",
        "prediction_delta_history.changed_fields",
        "prediction_delta_history.delta_reason_codes",
        "prediction_delta_release_gate.history_available",
        "prediction_delta_release_gate.widget_reliability_claim_allowed",
    ):
        if field not in REQUIRED_DELTA_FIELDS:
            failures.append(f"required delta field missing: {field}")
    report = build_report(use_observed_fixture=True)
    if report.get("ok") is not True:
        failures.append(f"observed fixture contract should be ok: {report}")
    if report.get("stage") != "prediction_delta_history_contract_before_realtime_widget_rendering":
        failures.append("stage mismatch")
    if report.get("source_q17b_report_valid") is not True:
        failures.append("observed fixture source Q17B should validate")
    if report.get("source_gap_id") != "prediction_delta_history":
        failures.append("source gap id mismatch")
    if report.get("contract_count") != 6:
        failures.append("expected six contracts")
    if report.get("p0_contract_count") != 4:
        failures.append("expected four P0 contracts")
    if report.get("p1_contract_count") != 2:
        failures.append("expected two P1 contracts")
    if report.get("recommended_first_validation") != "previous_latest_snapshot_reference_contract":
        failures.append("recommended first validation mismatch")
    if report.get("history_required_before_delta_claim") is not True:
        failures.append("history required before delta claim must be true")
    contract_ids = [row.get("contract_id") for row in report.get("contract_rows", [])]
    priorities = {row.get("contract_id"): row.get("priority") for row in report.get("contract_rows", [])}
    for contract_id in EXPECTED_CONTRACTS:
        if contract_id not in contract_ids:
            failures.append(f"missing contract row: {contract_id}")
        if contract_id not in report.get("blocks_realtime_delta_widget", []):
            failures.append(f"expected realtime delta widget blocker: {contract_id}")
    for contract_id in EXPECTED_P0:
        if priorities.get(contract_id) != "P0":
            failures.append(f"expected P0 contract: {contract_id}")
    for row in report.get("contract_rows", []):
        if row.get("state") != "required":
            failures.append(f"contract row should stay required: {row}")
        if row.get("read_only") is not True or row.get("write_or_apply_allowed") is not False:
            failures.append(f"contract row boundary mismatch: {row}")
        if not str(row.get("next_validation", "")).endswith("_guard"):
            failures.append(f"next validation should be guard: {row}")
    _assert_false_boundaries(report, failures)
    blocked = build_report()
    if blocked.get("ok") is not False:
        failures.append("missing Q17B source should block")
    if blocked.get("contract_rows"):
        failures.append("blocked report must not emit contract rows")
    _assert_false_boundaries(blocked, failures)
    if main(["--use-observed-fixture"]) != 0:
        failures.append("CLI observed fixture should return 0")
    if main([]) != 1:
        failures.append("CLI without source should return 1")
    for marker in (
        "checker=check_phase4a_prediction_system_ps_q17h_prediction_delta_history_contract.v1",
        "source_checker=check_phase4a_prediction_system_ps_q17b_inference_quality_gap_plan.v1",
        "source_gap_id=prediction_delta_history",
        "contract_only=true",
        "diagnostic_only=true",
        "plan_only=true",
        "warroom_widget_implementation_allowed=false",
        "delta_widget_rendering_allowed=false",
        "history_actual_read_allowed=false",
        "d_hot_actual_read_allowed=false",
        "P0 previous_latest_snapshot_reference_contract",
        "P0 latest_snapshot_lineage_contract",
        "P0 delta_computation_key_contract",
        "P0 warroom_delta_widget_release_contract",
        "P1 delta_reason_taxonomy_contract",
        "P1 history_retention_and_freshness_contract",
        "prediction_delta_history.previous_snapshot.run_id",
        "prediction_delta_history.previous_snapshot.generated_at",
        "prediction_delta_history.latest_snapshot.run_id",
        "prediction_delta_history.delta_key.market_uid",
        "prediction_delta_history.delta_key.horizon_key",
        "prediction_delta_history.changed_fields",
        "prediction_delta_history.delta_reason_codes",
        "prediction_delta_release_gate.history_available",
        "prediction_delta_release_gate.widget_reliability_claim_allowed",
        "history_available must be true before realtime delta widget reliability claims",
        "widget_reliability_claim_allowed remains false until previous/latest lineage and delta keys are verified",
        "no_history_actual_read",
        "PS-Q17I: prediction-delta history adapter",
    ):
        if marker not in doc_text:
            failures.append(f"missing doc marker: {marker}")
    for forbidden in (
        "warroom_widget_implementation_allowed=true",
        "delta_widget_rendering_allowed=true",
        "history_actual_read_allowed=true",
        "d_hot_actual_read_allowed=true",
        "parameter_apply_allowed=true",
        "parameter_staging_write_allowed=true",
        "ledger_append_allowed=true",
        "autotrade_trigger_allowed=true",
        "broker_private_api_allowed=true",
        "warroom_ui_trigger_enabled=true",
        "refresh_invocation_allowed=true",
        "scheduler_enabled=true",
    ):
        if forbidden in doc_text:
            failures.append(f"forbidden doc marker present: {forbidden}")
    dirty = _dirty_paths()
    unexpected = dirty - EXPECTED_DIRTY
    if unexpected:
        failures.append(f"unexpected dirty paths: {sorted(unexpected)}")
    result = {
        "ok": not failures,
        "guard": "ps_q17h_close_guard",
        "phase": "phase3_prediction_delta_history_contract_closed_before_realtime_widget_rendering",
        "focused_guards_to_run_before_commit": [FOCUSED_GUARD],
        "contract": {
            "ps_q17h_closed": not failures,
            "contract_only": True,
            "source_q17b_required": True,
            "warroom_widget_design_premise": True,
            "warroom_widget_implementation_allowed": False,
            "delta_widget_rendering_allowed": False,
            "history_actual_read_allowed": False,
            "no_d_hot_actual_read": True,
            "no_runtime_write": True,
            "no_status_write": True,
            "no_parameter_apply": True,
            "no_parameter_staging_write": True,
            "no_ledger_append": True,
            "no_autotrade": True,
            "no_broker": True,
            "next_slice": "PS-Q17I prediction-delta history adapter or replay-outcome calibration contract",
        },
        "dirty_paths": sorted(dirty),
        "unexpected_dirty": sorted(unexpected),
        "failures": failures,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


def test_ps_q17h_close_guard() -> None:
    assert main_guard() == 0


if __name__ == "__main__":
    raise SystemExit(main_guard())
