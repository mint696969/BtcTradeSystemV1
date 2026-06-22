# path: ./tools/test_phase4a_prediction_system_ps_q17k_close_guard.py
# desc: Close guard for PS-Q17K replay-outcome calibration adapter.

from __future__ import annotations

import ast
import json
import subprocess
from pathlib import Path

from check_phase4a_prediction_system_ps_q17k_replay_outcome_calibration_adapter import ADAPTER_VERSION, CHECKER_VERSION, JOIN_KEYS, OUTCOME_METRIC_FIELDS, REPLAY_PACKET_VERSION, adapt_replay_feedback, build_report, main

REPO_ROOT = Path(__file__).resolve().parents[1]
TOOL = REPO_ROOT / "tools/check_phase4a_prediction_system_ps_q17k_replay_outcome_calibration_adapter.py"
UNIT = REPO_ROOT / "tools/test_phase4a_prediction_system_ps_q17k_replay_outcome_calibration_adapter.py"
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q17K_REPLAY_OUTCOME_CALIBRATION_ADAPTER_2026-06-22.md"
FOCUSED_GUARD = "tools/test_phase4a_prediction_system_ps_q17k_replay_outcome_calibration_adapter_guard.py"
EXPECTED_DIRTY = {
    "tools/check_phase4a_prediction_system_ps_q17k_replay_outcome_calibration_adapter.py",
    "tools/test_phase4a_prediction_system_ps_q17k_replay_outcome_calibration_adapter.py",
    "docs/strategy/PREDICTION_SYSTEM_PS_Q17K_REPLAY_OUTCOME_CALIBRATION_ADAPTER_2026-06-22.md",
    "tools/test_phase4a_prediction_system_ps_q17k_replay_outcome_calibration_adapter_guard.py",
    "tools/test_phase4a_prediction_system_ps_q17k_close_guard.py",
}
REQUIRED_PACKET_KEYS = (
    "replay_outcome_calibration",
    "replay_calibration_release_gate",
    "contract_completeness",
    "warroom_replay_outcome_widget",
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
        "replay_history_actual_read_allowed",
        "replay_outcome_widget_rendering_allowed",
        "confidence_increase_allowed",
        "signal_reliability_claim_allowed",
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
        "CHECKER = \"ps_q17k_replay_outcome_calibration_adapter\"",
        "CHECKER_VERSION = \"check_phase4a_prediction_system_ps_q17k_replay_outcome_calibration_adapter.v1\"",
        "ADAPTER_VERSION = \"replay_outcome_calibration_adapter.v1\"",
        "REPLAY_PACKET_VERSION = \"replay_outcome_calibration_review_packet.v1\"",
        "PS_Q17J_SOURCE_CHECKER_VERSION",
        "JOIN_KEYS",
        "OUTCOME_METRIC_FIELDS",
        "adapt_replay_feedback",
        "_safe_q17j_boundary",
        "_adapter_valid",
        "replay_outcome_calibration",
        "replay_calibration_release_gate",
        "contract_completeness",
        "warroom_replay_outcome_widget",
        "confidence_reliability_claim_allowed",
        "signal_reliability_claim_allowed",
        "parameter_tuning_allowed",
        "replay_history_actual_read_allowed",
        "replay_outcome_widget_rendering_allowed",
        "PS-Q17L scenario-trace semantic mapping contract",
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
    if "test_ps_q17k_adapts_supplied_replay_feedback_to_review_packet" not in unit_text:
        failures.append("unit test must cover supplied replay feedback adaptation")
    if "test_ps_q17k_blocks_invalid_source_contract_or_missing_feedback" not in unit_text:
        failures.append("unit test must cover invalid source/missing feedback blocking")
    if CHECKER_VERSION != "check_phase4a_prediction_system_ps_q17k_replay_outcome_calibration_adapter.v1":
        failures.append("checker version mismatch")
    if ADAPTER_VERSION != "replay_outcome_calibration_adapter.v1":
        failures.append("adapter version mismatch")
    if REPLAY_PACKET_VERSION != "replay_outcome_calibration_review_packet.v1":
        failures.append("replay packet version mismatch")
    if tuple(JOIN_KEYS) != ("market_uid", "family", "horizon_key", "record_id"):
        failures.append("join keys mismatch")
    if tuple(OUTCOME_METRIC_FIELDS) != ("predicted_direction_hit", "actual_return_bps", "magnitude_error_bps"):
        failures.append("outcome metric fields mismatch")
    report = build_report(use_observed_fixture=True)
    if report.get("ok") is not True:
        failures.append(f"observed fixture adapter should be ok: {report}")
    if report.get("stage") != "replay_outcome_calibration_adapter_before_confidence_parameter_and_widget_release":
        failures.append("stage mismatch")
    if report.get("source_q17j_report_valid") is not True:
        failures.append("observed fixture source Q17J should validate")
    if report.get("adapter_valid") is not True:
        failures.append("adapter should validate")
    if report.get("adapter_validation_failures"):
        failures.append(f"adapter validation failures should be empty: {report.get('adapter_validation_failures')}")
    packet = report.get("adapted_packet", {})
    for key in REQUIRED_PACKET_KEYS:
        if key not in packet:
            failures.append(f"adapted packet missing: {key}")
    replay = packet.get("replay_outcome_calibration", {})
    gate = packet.get("replay_calibration_release_gate", {})
    completeness = packet.get("contract_completeness", {})
    warroom = packet.get("warroom_replay_outcome_widget", {})
    if packet.get("adapter_version") != "replay_outcome_calibration_adapter.v1":
        failures.append("adapter version in packet mismatch")
    if packet.get("replay_packet_version") != "replay_outcome_calibration_review_packet.v1":
        failures.append("replay packet version in packet mismatch")
    if replay.get("replay_feedback", {}).get("run_id") != "fixture.replay.run":
        failures.append("fixture replay run id mismatch")
    if int(replay.get("sample_count", 0)) != 2:
        failures.append("fixture should include two replay samples")
    summary = replay.get("summary_metrics", {})
    if summary.get("predicted_direction_hit_rate") != 0.5:
        failures.append("fixture hit rate should be 0.5")
    if summary.get("mean_magnitude_error_bps") != 14.5:
        failures.append("fixture mean magnitude error should be 14.5")
    if gate.get("replay_feedback_present") is not True:
        failures.append("fixture replay feedback should be present")
    if gate.get("blocking_reason_codes") != ["adapter_stage_no_confidence_or_parameter_release"]:
        failures.append("release gate should retain adapter-stage blocker")
    for key in ("confidence_reliability_claim_allowed", "signal_reliability_claim_allowed", "parameter_tuning_allowed"):
        if gate.get(key) is not False:
            failures.append(f"release gate must keep false: {key}")
    if warroom.get("render_allowed") is not False:
        failures.append("WarRoom replay widget render must remain false")
    if int(warroom.get("sample_count", 0)) != 2:
        failures.append("WarRoom replay widget sample count mismatch")
    for key in ("has_replay_feedback", "has_outcome_window", "has_join_keys", "has_outcome_metrics", "has_release_gate"):
        if completeness.get(key) is not True:
            failures.append(f"contract completeness should be true: {key}")
    _assert_false_boundaries(report, failures)
    direct_packet = adapt_replay_feedback({
        "replay_feedback": {"run_id": "rf", "generated_at": "2026-06-22T01:00:00Z", "source_artifact_ref": "fixture://rf"},
        "outcome_window": {"start_at": "2026-06-01T00:00:00Z", "end_at": "2026-06-22T00:00:00Z", "market_uid": "BTC_JPY:bitFlyer", "horizon_keys": ["short"]},
        "rows": [
            {"record_id": "r", "market_uid": "BTC_JPY:bitFlyer", "family": "trend", "horizon_key": "short", "predicted_direction_hit": True, "actual_return_bps": 10.0, "magnitude_error_bps": 2.0}
        ],
    })
    direct_gate = direct_packet.get("replay_calibration_release_gate", {})
    for key in ("confidence_reliability_claim_allowed", "signal_reliability_claim_allowed", "parameter_tuning_allowed"):
        if direct_gate.get(key) is not False:
            failures.append(f"direct adapter gate should remain false: {key}")
    if direct_packet.get("warroom_replay_outcome_widget", {}).get("render_allowed") is not False:
        failures.append("direct adapter render should remain false")
    blocked = build_report()
    if blocked.get("ok") is not False:
        failures.append("missing Q17J source/replay feedback should block")
    if blocked.get("adapted_packet"):
        failures.append("blocked report must not emit adapted packet")
    _assert_false_boundaries(blocked, failures)
    if main(["--use-observed-fixture"]) != 0:
        failures.append("CLI observed fixture should return 0")
    if main([]) != 1:
        failures.append("CLI without source should return 1")
    for marker in (
        "checker=check_phase4a_prediction_system_ps_q17k_replay_outcome_calibration_adapter.v1",
        "adapter_version=replay_outcome_calibration_adapter.v1",
        "source_checker=check_phase4a_prediction_system_ps_q17j_replay_outcome_calibration_contract.v1",
        "adapter_only=true",
        "contract_only=true",
        "diagnostic_only=true",
        "warroom_widget_implementation_allowed=false",
        "replay_history_actual_read_allowed=false",
        "replay_outcome_widget_rendering_allowed=false",
        "confidence_increase_allowed=false",
        "signal_reliability_claim_allowed=false",
        "parameter_tuning_allowed=false",
        "d_hot_actual_read_allowed=false",
        "replay_outcome_calibration.replay_feedback.run_id",
        "replay_outcome_calibration.outcome_window.market_uid",
        "replay_outcome_calibration.outcome_rows[].forecast_to_outcome_key.market_uid",
        "replay_outcome_calibration.outcome_rows[].outcome_metrics.predicted_direction_hit",
        "replay_calibration_release_gate.replay_feedback_present",
        "replay_calibration_release_gate.confidence_reliability_claim_allowed=false",
        "replay_calibration_release_gate.signal_reliability_claim_allowed=false",
        "replay_calibration_release_gate.parameter_tuning_allowed=false",
        "warroom_replay_outcome_widget.render_allowed=false",
        "no_replay_history_actual_read",
        "no_live_outcome_computation",
        "PS-Q17L: scenario-trace semantic mapping contract",
    ):
        if marker not in doc_text:
            failures.append(f"missing doc marker: {marker}")
    for forbidden in (
        "warroom_widget_implementation_allowed=true",
        "replay_history_actual_read_allowed=true",
        "replay_outcome_widget_rendering_allowed=true",
        "confidence_increase_allowed=true",
        "signal_reliability_claim_allowed=true",
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
        "guard": "ps_q17k_close_guard",
        "phase": "phase3_replay_outcome_calibration_adapter_closed_before_confidence_parameter_and_widget_release",
        "focused_guards_to_run_before_commit": [FOCUSED_GUARD],
        "contract": {
            "ps_q17k_closed": not failures,
            "adapter_only": True,
            "source_q17j_required": True,
            "warroom_widget_design_premise": True,
            "warroom_widget_implementation_allowed": False,
            "replay_history_actual_read_allowed": False,
            "replay_outcome_widget_rendering_allowed": False,
            "confidence_increase_allowed": False,
            "signal_reliability_claim_allowed": False,
            "parameter_tuning_allowed": False,
            "no_d_hot_actual_read": True,
            "no_runtime_write": True,
            "no_status_write": True,
            "no_parameter_apply": True,
            "no_parameter_staging_write": True,
            "no_ledger_append": True,
            "no_autotrade": True,
            "no_broker": True,
            "next_slice": "PS-Q17L scenario-trace semantic mapping contract or parameter-candidate evidence contract",
        },
        "dirty_paths": sorted(dirty),
        "unexpected_dirty": sorted(unexpected),
        "failures": failures,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


def test_ps_q17k_close_guard() -> None:
    assert main_guard() == 0


if __name__ == "__main__":
    raise SystemExit(main_guard())
