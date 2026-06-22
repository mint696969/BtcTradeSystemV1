# path: ./tools/test_phase4a_prediction_system_ps_q17i_close_guard.py
# desc: Close guard for PS-Q17I prediction-delta history adapter.

from __future__ import annotations

import ast
import json
import subprocess
from pathlib import Path

from check_phase4a_prediction_system_ps_q17i_prediction_delta_history_adapter import ADAPTER_VERSION, CHECKER_VERSION, COMPARE_FIELDS, DELTA_PACKET_VERSION, JOIN_KEYS, adapt_snapshots, build_report, main

REPO_ROOT = Path(__file__).resolve().parents[1]
TOOL = REPO_ROOT / "tools/check_phase4a_prediction_system_ps_q17i_prediction_delta_history_adapter.py"
UNIT = REPO_ROOT / "tools/test_phase4a_prediction_system_ps_q17i_prediction_delta_history_adapter.py"
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q17I_PREDICTION_DELTA_HISTORY_ADAPTER_2026-06-22.md"
FOCUSED_GUARD = "tools/test_phase4a_prediction_system_ps_q17i_prediction_delta_history_adapter_guard.py"
EXPECTED_DIRTY = {
    "tools/check_phase4a_prediction_system_ps_q17i_prediction_delta_history_adapter.py",
    "tools/test_phase4a_prediction_system_ps_q17i_prediction_delta_history_adapter.py",
    "docs/strategy/PREDICTION_SYSTEM_PS_Q17I_PREDICTION_DELTA_HISTORY_ADAPTER_2026-06-22.md",
    "tools/test_phase4a_prediction_system_ps_q17i_prediction_delta_history_adapter_guard.py",
    "tools/test_phase4a_prediction_system_ps_q17i_close_guard.py",
}
REQUIRED_PACKET_KEYS = (
    "prediction_delta_history",
    "prediction_delta_release_gate",
    "contract_completeness",
    "warroom_delta_review_packet",
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
        "CHECKER = \"ps_q17i_prediction_delta_history_adapter\"",
        "CHECKER_VERSION = \"check_phase4a_prediction_system_ps_q17i_prediction_delta_history_adapter.v1\"",
        "ADAPTER_VERSION = \"prediction_delta_history_adapter.v1\"",
        "DELTA_PACKET_VERSION = \"prediction_delta_review_packet.v1\"",
        "PS_Q17H_SOURCE_CHECKER_VERSION",
        "JOIN_KEYS",
        "COMPARE_FIELDS",
        "adapt_snapshots",
        "_safe_q17h_boundary",
        "_adapter_valid",
        "prediction_delta_history",
        "prediction_delta_release_gate",
        "warroom_delta_review_packet",
        "contract_completeness",
        "widget_reliability_claim_allowed",
        "delta_widget_rendering_allowed",
        "history_actual_read_allowed",
        "PS-Q17J replay-outcome calibration contract",
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
    if "test_ps_q17i_adapts_supplied_snapshots_to_delta_packet" not in unit_text:
        failures.append("unit test must cover supplied snapshot adaptation")
    if "test_ps_q17i_blocks_invalid_source_contract_or_missing_snapshots" not in unit_text:
        failures.append("unit test must cover invalid source/missing snapshots blocking")
    if CHECKER_VERSION != "check_phase4a_prediction_system_ps_q17i_prediction_delta_history_adapter.v1":
        failures.append("checker version mismatch")
    if ADAPTER_VERSION != "prediction_delta_history_adapter.v1":
        failures.append("adapter version mismatch")
    if DELTA_PACKET_VERSION != "prediction_delta_review_packet.v1":
        failures.append("delta packet version mismatch")
    if tuple(JOIN_KEYS) != ("market_uid", "family", "horizon_key", "record_id"):
        failures.append("join keys mismatch")
    if tuple(COMPARE_FIELDS) != ("estimated_signal_strength_percent", "source_quality_gate_state", "scenario_trace_state"):
        failures.append("compare fields mismatch")
    report = build_report(use_observed_fixture=True)
    if report.get("ok") is not True:
        failures.append(f"observed fixture adapter should be ok: {report}")
    if report.get("stage") != "prediction_delta_history_adapter_before_realtime_widget_rendering":
        failures.append("stage mismatch")
    if report.get("source_q17h_report_valid") is not True:
        failures.append("observed fixture source Q17H should validate")
    if report.get("adapter_valid") is not True:
        failures.append("adapter should validate")
    if report.get("adapter_validation_failures"):
        failures.append(f"adapter validation failures should be empty: {report.get('adapter_validation_failures')}")
    packet = report.get("adapted_packet", {})
    for key in REQUIRED_PACKET_KEYS:
        if key not in packet:
            failures.append(f"adapted packet missing: {key}")
    history = packet.get("prediction_delta_history", {})
    release = packet.get("prediction_delta_release_gate", {})
    completeness = packet.get("contract_completeness", {})
    warroom = packet.get("warroom_delta_review_packet", {})
    if packet.get("adapter_version") != "prediction_delta_history_adapter.v1":
        failures.append("adapter version in packet mismatch")
    if packet.get("delta_packet_version") != "prediction_delta_review_packet.v1":
        failures.append("delta packet version in packet mismatch")
    if history.get("previous_snapshot", {}).get("run_id") != "fixture.previous.run":
        failures.append("fixture previous run id mismatch")
    if history.get("latest_snapshot", {}).get("run_id") != "fixture.latest.run":
        failures.append("fixture latest run id mismatch")
    if int(history.get("changed_row_count", 0)) != 2:
        failures.append("fixture should include two changed rows")
    for reason in ("changed_signal_strength", "changed_scenario_trace"):
        if reason not in history.get("delta_reason_codes", []):
            failures.append(f"fixture missing delta reason: {reason}")
    if release.get("history_available") is not True:
        failures.append("fixture history should be available from supplied snapshots")
    if release.get("blocking_reason_codes") != ["adapter_stage_no_delta_widget_release"]:
        failures.append("release gate should retain adapter-stage blocker")
    for key in ("widget_reliability_claim_allowed", "delta_widget_rendering_allowed"):
        if release.get(key) is not False:
            failures.append(f"release gate must keep false: {key}")
    if warroom.get("render_allowed") is not False:
        failures.append("WarRoom delta render must remain false")
    if int(warroom.get("changed_row_count", 0)) != 2:
        failures.append("WarRoom review packet changed row count mismatch")
    for key in ("has_previous_snapshot", "has_latest_snapshot", "has_delta_keys", "has_release_gate"):
        if completeness.get(key) is not True:
            failures.append(f"contract completeness should be true: {key}")
    _assert_false_boundaries(report, failures)
    direct_packet = adapt_snapshots({
        "previous_snapshot": {"run_id": "prev", "generated_at": "2026-06-22T00:00:00Z", "source_artifact_ref": "fixture://prev", "records": [{"record_id": "r", "market_uid": "BTC_JPY:bitFlyer", "family": "trend", "horizon_key": "short", "estimated_signal_strength_percent": 1, "source_quality_gate_state": "fail", "scenario_trace_state": "a"}]},
        "latest_snapshot": {"run_id": "latest", "generated_at": "2026-06-22T00:01:00Z", "source_artifact_ref": "fixture://latest", "records": [{"record_id": "r", "market_uid": "BTC_JPY:bitFlyer", "family": "trend", "horizon_key": "short", "estimated_signal_strength_percent": 2, "source_quality_gate_state": "warn", "scenario_trace_state": "b"}]},
    })
    if direct_packet.get("prediction_delta_release_gate", {}).get("widget_reliability_claim_allowed") is not False:
        failures.append("direct adapter widget reliability should remain false")
    if direct_packet.get("prediction_delta_release_gate", {}).get("delta_widget_rendering_allowed") is not False:
        failures.append("direct adapter delta widget rendering should remain false")
    if direct_packet.get("warroom_delta_review_packet", {}).get("render_allowed") is not False:
        failures.append("direct adapter render should remain false")
    blocked = build_report()
    if blocked.get("ok") is not False:
        failures.append("missing Q17H source/snapshots should block")
    if blocked.get("adapted_packet"):
        failures.append("blocked report must not emit adapted packet")
    _assert_false_boundaries(blocked, failures)
    if main(["--use-observed-fixture"]) != 0:
        failures.append("CLI observed fixture should return 0")
    if main([]) != 1:
        failures.append("CLI without source should return 1")
    for marker in (
        "checker=check_phase4a_prediction_system_ps_q17i_prediction_delta_history_adapter.v1",
        "adapter_version=prediction_delta_history_adapter.v1",
        "source_checker=check_phase4a_prediction_system_ps_q17h_prediction_delta_history_contract.v1",
        "adapter_only=true",
        "contract_only=true",
        "diagnostic_only=true",
        "warroom_widget_implementation_allowed=false",
        "delta_widget_rendering_allowed=false",
        "history_actual_read_allowed=false",
        "d_hot_actual_read_allowed=false",
        "prediction_delta_history.previous_snapshot.run_id",
        "prediction_delta_history.previous_snapshot.generated_at",
        "prediction_delta_history.latest_snapshot.run_id",
        "prediction_delta_history.changed_rows[].delta_key.market_uid",
        "prediction_delta_history.changed_rows[].changed_fields",
        "prediction_delta_history.delta_reason_codes",
        "prediction_delta_release_gate.history_available",
        "prediction_delta_release_gate.widget_reliability_claim_allowed=false",
        "prediction_delta_release_gate.delta_widget_rendering_allowed=false",
        "warroom_delta_review_packet.render_allowed=false",
        "no_history_actual_read",
        "no_live_delta_computation",
        "PS-Q17J: replay-outcome calibration contract",
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
        "guard": "ps_q17i_close_guard",
        "phase": "phase3_prediction_delta_history_adapter_closed_before_realtime_widget_rendering",
        "focused_guards_to_run_before_commit": [FOCUSED_GUARD],
        "contract": {
            "ps_q17i_closed": not failures,
            "adapter_only": True,
            "source_q17h_required": True,
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
            "next_slice": "PS-Q17J replay-outcome calibration contract or prediction-delta adapter integration design",
        },
        "dirty_paths": sorted(dirty),
        "unexpected_dirty": sorted(unexpected),
        "failures": failures,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


def test_ps_q17i_close_guard() -> None:
    assert main_guard() == 0


if __name__ == "__main__":
    raise SystemExit(main_guard())
