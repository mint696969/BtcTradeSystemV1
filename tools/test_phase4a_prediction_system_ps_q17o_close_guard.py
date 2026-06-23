# path: ./tools/test_phase4a_prediction_system_ps_q17o_close_guard.py
# desc: Close guard for PS-Q17O parameter-candidate evidence adapter.

from __future__ import annotations

import ast
import json
import subprocess
from pathlib import Path

from check_phase4a_prediction_system_ps_q17o_parameter_candidate_evidence_adapter import ADAPTER_VERSION, CHECKER_VERSION, PARAMETER_PACKET_VERSION, REQUIRED_EVIDENCE_REFS, adapt_parameter_candidate, build_report, main

REPO_ROOT = Path(__file__).resolve().parents[1]
TOOL = REPO_ROOT / "tools/check_phase4a_prediction_system_ps_q17o_parameter_candidate_evidence_adapter.py"
UNIT = REPO_ROOT / "tools/test_phase4a_prediction_system_ps_q17o_parameter_candidate_evidence_adapter.py"
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q17O_PARAMETER_CANDIDATE_EVIDENCE_ADAPTER_2026-06-22.md"
FOCUSED_GUARD = "tools/test_phase4a_prediction_system_ps_q17o_parameter_candidate_evidence_adapter_guard.py"
EXPECTED_DIRTY = {
    "tools/check_phase4a_prediction_system_ps_q17o_parameter_candidate_evidence_adapter.py",
    "tools/test_phase4a_prediction_system_ps_q17o_parameter_candidate_evidence_adapter.py",
    "docs/strategy/PREDICTION_SYSTEM_PS_Q17O_PARAMETER_CANDIDATE_EVIDENCE_ADAPTER_2026-06-22.md",
    "tools/test_phase4a_prediction_system_ps_q17o_parameter_candidate_evidence_adapter_guard.py",
    "tools/test_phase4a_prediction_system_ps_q17o_close_guard.py",
}
REQUIRED_PACKET_KEYS = (
    "parameter_candidate",
    "parameter_candidate_release_gate",
    "contract_completeness",
    "warroom_parameter_candidate_widget",
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
        "adapter_only",
        "contract_only",
        "diagnostic_only",
        "warroom_widget_design_premise",
    ):
        if report.get(key) is not True:
            failures.append(f"{key} must be true")
    for key in (
        "warroom_widget_implementation_allowed",
        "parameter_candidate_actual_read_allowed",
        "parameter_candidate_widget_rendering_allowed",
        "parameter_candidate_reliability_claim_allowed",
        "confidence_increase_allowed",
        "parameter_tuning_allowed",
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
        "CHECKER = \"ps_q17o_parameter_candidate_evidence_adapter\"",
        "CHECKER_VERSION = \"check_phase4a_prediction_system_ps_q17o_parameter_candidate_evidence_adapter.v1\"",
        "ADAPTER_VERSION = \"parameter_candidate_evidence_adapter.v1\"",
        "PARAMETER_PACKET_VERSION = \"parameter_candidate_evidence_review_packet.v1\"",
        "PS_Q17N_SOURCE_CHECKER_VERSION",
        "REQUIRED_EVIDENCE_REFS",
        "adapt_parameter_candidate",
        "_safe_q17n_boundary",
        "_adapter_valid",
        "parameter_candidate",
        "parameter_candidate_release_gate",
        "warroom_parameter_candidate_widget",
        "evidence_complete",
        "parameter_staging_allowed",
        "parameter_apply_allowed",
        "confidence_increase_allowed",
        "parameter_tuning_allowed",
        "parameter_candidate_actual_read_allowed",
        "parameter_candidate_widget_rendering_allowed",
        "parameter_candidate_reliability_claim_allowed",
        "PS-Q17P WarRoom prediction widget integration design checkpoint",
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
    if "test_ps_q17o_adapts_supplied_parameter_candidate_to_review_packet" not in unit_text:
        failures.append("unit test must cover supplied parameter candidate adaptation")
    if "test_ps_q17o_blocks_invalid_source_contract_or_missing_candidate" not in unit_text:
        failures.append("unit test must cover invalid source/missing candidate blocking")

    if CHECKER_VERSION != "check_phase4a_prediction_system_ps_q17o_parameter_candidate_evidence_adapter.v1":
        failures.append("checker version mismatch")
    if ADAPTER_VERSION != "parameter_candidate_evidence_adapter.v1":
        failures.append("adapter version mismatch")
    if PARAMETER_PACKET_VERSION != "parameter_candidate_evidence_review_packet.v1":
        failures.append("parameter packet version mismatch")
    if tuple(REQUIRED_EVIDENCE_REFS) != ("source_quality_ref_id", "calibration_ref_id", "replay_feedback_ref_id"):
        failures.append("required evidence refs mismatch")

    report = build_report(use_observed_fixture=True)
    if report.get("ok") is not True:
        failures.append(f"observed fixture adapter should be ok: {report}")
    if report.get("stage") != "parameter_candidate_evidence_adapter_before_staging_apply_confidence_and_widget_release":
        failures.append("stage mismatch")
    if report.get("source_q17n_report_valid") is not True:
        failures.append("observed fixture source Q17N should validate")
    if report.get("adapter_valid") is not True:
        failures.append("adapter should validate")
    if report.get("adapter_validation_failures"):
        failures.append(f"adapter validation failures should be empty: {report.get('adapter_validation_failures')}")

    packet = report.get("adapted_packet", {})
    for key in REQUIRED_PACKET_KEYS:
        if key not in packet:
            failures.append(f"adapted packet missing: {key}")
    if packet.get("adapter_version") != "parameter_candidate_evidence_adapter.v1":
        failures.append("adapter version in packet mismatch")
    if packet.get("parameter_packet_version") != "parameter_candidate_evidence_review_packet.v1":
        failures.append("parameter packet version in packet mismatch")

    candidate_packet = packet.get("parameter_candidate", {})
    baseline = candidate_packet.get("baseline", {})
    candidate = candidate_packet.get("candidate", {})
    evidence = candidate_packet.get("evidence", {})
    rollback = candidate_packet.get("rollback", {})
    gate = packet.get("parameter_candidate_release_gate", {})
    completeness = packet.get("contract_completeness", {})
    widget = packet.get("warroom_parameter_candidate_widget", {})

    if candidate_packet.get("source_artifact_ref") != "fixture://parameter/candidate.json":
        failures.append("fixture source artifact ref mismatch")
    if candidate_packet.get("generated_at") != "2026-06-22T02:00:00Z":
        failures.append("fixture generated_at mismatch")
    if baseline.get("ref_id") != "baseline.ref.fixture" or baseline.get("parameter_set_id") != "params.v1":
        failures.append("baseline reference mismatch")
    if candidate.get("candidate_id") != "candidate.fixture.tighten_signal_floor":
        failures.append("candidate id mismatch")
    if candidate.get("changed_parameter_keys") != ["signal_strength_floor", "source_quality_min_count"]:
        failures.append("changed parameter keys mismatch")
    if evidence.get("source_quality_ref_id") != "source_quality.ps_q17e.fixture":
        failures.append("source quality ref mismatch")
    if evidence.get("calibration_ref_id") != "calibration.ps_q17g.fixture":
        failures.append("calibration ref mismatch")
    if evidence.get("replay_feedback_ref_id") != "replay.ps_q17k.fixture":
        failures.append("replay feedback ref mismatch")
    if rollback.get("rollback_threshold_ref_id") != "rollback.threshold.fixture":
        failures.append("rollback threshold ref mismatch")

    if gate.get("evidence_complete") is not True:
        failures.append("evidence_complete should be true for fixture")
    if gate.get("blocking_reason_codes") != ["adapter_stage_no_parameter_staging_or_apply"]:
        failures.append("release gate should retain adapter-stage blocker")
    for key in ("parameter_staging_allowed", "parameter_apply_allowed", "confidence_increase_allowed", "parameter_tuning_allowed"):
        if gate.get(key) is not False:
            failures.append(f"release gate must keep false: {key}")
    if widget.get("render_allowed") is not False:
        failures.append("WarRoom parameter candidate widget render must remain false")
    if widget.get("candidate_id") != "candidate.fixture.tighten_signal_floor":
        failures.append("WarRoom widget candidate id mismatch")
    if widget.get("baseline_ref_id") != "baseline.ref.fixture":
        failures.append("WarRoom widget baseline ref mismatch")
    for key in (
        "has_source_artifact_ref",
        "has_baseline_reference",
        "has_candidate_diff",
        "has_source_quality_ref",
        "has_calibration_ref",
        "has_replay_feedback_ref",
        "has_rollback_threshold",
        "has_release_gate",
    ):
        if completeness.get(key) is not True:
            failures.append(f"contract completeness should be true: {key}")
    _assert_false_boundaries(report, failures)

    direct_packet = adapt_parameter_candidate({
        "source_artifact_ref": "fixture://param",
        "generated_at": "2026-06-22T02:00:00Z",
        "baseline": {"ref_id": "baseline.ref", "parameter_set_id": "params.v1", "effective_at": "2026-06-01T00:00:00Z"},
        "candidate": {"candidate_id": "candidate.1", "changed_parameter_keys": ["signal_floor"], "diff_summary": "raise floor", "expected_effect_summary": "review only"},
        "evidence": {"source_quality_ref_id": "sq.ref", "calibration_ref_id": "cal.ref", "replay_feedback_ref_id": "replay.ref"},
        "rollback": {"rollback_threshold_ref_id": "rb.ref", "rollback_condition_summary": "rollback condition", "abort_condition_summary": "abort condition"},
    })
    direct_gate = direct_packet.get("parameter_candidate_release_gate", {})
    if direct_gate.get("evidence_complete") is not True:
        failures.append("direct adapter evidence_complete should be true")
    for key in ("parameter_staging_allowed", "parameter_apply_allowed", "confidence_increase_allowed", "parameter_tuning_allowed"):
        if direct_gate.get(key) is not False:
            failures.append(f"direct adapter gate should remain false: {key}")
    if direct_packet.get("warroom_parameter_candidate_widget", {}).get("render_allowed") is not False:
        failures.append("direct adapter render should remain false")

    blocked = build_report()
    if blocked.get("ok") is not False:
        failures.append("missing Q17N source/parameter candidate should block")
    if blocked.get("adapted_packet"):
        failures.append("blocked report must not emit adapted packet")
    _assert_false_boundaries(blocked, failures)
    if main(["--use-observed-fixture"]) != 0:
        failures.append("CLI observed fixture should return 0")
    if main([]) != 1:
        failures.append("CLI without source should return 1")

    for marker in (
        "checker=check_phase4a_prediction_system_ps_q17o_parameter_candidate_evidence_adapter.v1",
        "adapter_version=parameter_candidate_evidence_adapter.v1",
        "source_checker=check_phase4a_prediction_system_ps_q17n_parameter_candidate_evidence_contract.v1",
        "adapter_only=true",
        "contract_only=true",
        "diagnostic_only=true",
        "warroom_widget_implementation_allowed=false",
        "parameter_candidate_actual_read_allowed=false",
        "parameter_candidate_widget_rendering_allowed=false",
        "parameter_candidate_reliability_claim_allowed=false",
        "confidence_increase_allowed=false",
        "parameter_tuning_allowed=false",
        "d_hot_actual_read_allowed=false",
        "parameter_apply_allowed=false",
        "parameter_staging_write_allowed=false",
        "parameter_candidate.source_artifact_ref",
        "parameter_candidate.baseline.ref_id",
        "parameter_candidate.candidate.changed_parameter_keys",
        "parameter_candidate.evidence.source_quality_ref_id",
        "parameter_candidate.evidence.calibration_ref_id",
        "parameter_candidate.evidence.replay_feedback_ref_id",
        "parameter_candidate.rollback.rollback_threshold_ref_id",
        "parameter_candidate_release_gate.evidence_complete",
        "parameter_candidate_release_gate.parameter_staging_allowed=false",
        "parameter_candidate_release_gate.parameter_apply_allowed=false",
        "parameter_candidate_release_gate.confidence_increase_allowed=false",
        "parameter_candidate_release_gate.parameter_tuning_allowed=false",
        "warroom_parameter_candidate_widget.render_allowed=false",
        "evidence_complete=true does not allow staging or apply",
        "no_parameter_candidate_actual_read",
        "no_live_parameter_candidate_evaluation",
        "PS-Q17P: WarRoom prediction widget integration design checkpoint",
    ):
        if marker not in doc_text:
            failures.append(f"missing doc marker: {marker}")
    for forbidden in (
        "warroom_widget_implementation_allowed=true",
        "parameter_candidate_actual_read_allowed=true",
        "parameter_candidate_widget_rendering_allowed=true",
        "parameter_candidate_reliability_claim_allowed=true",
        "confidence_increase_allowed=true",
        "parameter_tuning_allowed=true",
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
        "guard": "ps_q17o_close_guard",
        "phase": "phase3_parameter_candidate_evidence_adapter_closed_before_staging_apply_confidence_and_widget_release",
        "focused_guards_to_run_before_commit": [FOCUSED_GUARD],
        "contract": {
            "ps_q17o_closed": not failures,
            "adapter_only": True,
            "source_q17n_required": True,
            "warroom_widget_design_premise": True,
            "warroom_widget_implementation_allowed": False,
            "parameter_candidate_actual_read_allowed": False,
            "parameter_candidate_widget_rendering_allowed": False,
            "parameter_candidate_reliability_claim_allowed": False,
            "confidence_increase_allowed": False,
            "parameter_tuning_allowed": False,
            "parameter_staging_write_allowed": False,
            "parameter_apply_allowed": False,
            "no_d_hot_actual_read": True,
            "no_runtime_write": True,
            "no_status_write": True,
            "no_ledger_append": True,
            "no_autotrade": True,
            "no_broker": True,
            "next_slice": "PS-Q17P WarRoom prediction widget integration design checkpoint or parameter-candidate evidence adapter actual-source preflight",
        },
        "dirty_paths": sorted(dirty),
        "unexpected_dirty": sorted(unexpected),
        "failures": failures,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


def test_ps_q17o_close_guard() -> None:
    assert main_guard() == 0


if __name__ == "__main__":
    raise SystemExit(main_guard())
