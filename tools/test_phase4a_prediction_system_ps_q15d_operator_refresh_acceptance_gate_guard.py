# path: ./tools/test_phase4a_prediction_system_ps_q15d_operator_refresh_acceptance_gate_guard.py
# desc: Guard for PS-Q15D read-only operator-refresh acceptance gate checker.

from __future__ import annotations

import json
import subprocess
from pathlib import Path

from _btcts_bootstrap import ensure_btcts_on_syspath

ensure_btcts_on_syspath()

from check_phase4a_prediction_system_ps_q15d_operator_refresh_acceptance_gate import (  # noqa: E402
    CHECKER,
    _acceptance_from_reports,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
CHECKER_PATH = REPO_ROOT / "tools/check_phase4a_prediction_system_ps_q15d_operator_refresh_acceptance_gate.py"
GUARD = REPO_ROOT / "tools/test_phase4a_prediction_system_ps_q15d_operator_refresh_acceptance_gate_guard.py"
EXPECTED_DIRTY = {
    "tools/check_phase4a_prediction_system_ps_q15d_operator_refresh_acceptance_gate.py",
    "tools/test_phase4a_prediction_system_ps_q15d_operator_refresh_acceptance_gate_guard.py",
}
REQUIRED_MARKERS = (
    "ps_q15d_operator_refresh_acceptance_gate",
    "build_q15a_report",
    "build_q15b_report",
    "build_warroom_live_inference_smoke_payload",
    "operator_refresh_accepted",
    "operator_refresh_not_accepted",
    "latest_prediction_artifact_not_fresh_after_operator_refresh",
    "q15a_still_reports_latest_prediction_artifact_stale",
    "q12c_smoke_not_ready_after_operator_refresh",
    "refresh_executed_by_this_checker",
    "runtime_artifact_write_performed_by_this_checker",
    "scheduler_created",
    "freshness_bypass_added",
    "force_ready_added",
    "parameter_staging_write_allowed",
)
FORBIDDEN_MARKERS = (
    "build_prediction_warroom_latest_payload_actual_export_runner(",
    "build_prediction_warroom_latest_payload_export_runner(",
    "run_ps_q12d_export_and_smoke.main(",
    "os.system(",
    "target.write_text(",
    "replace(target)",
    "append_decision(",
    "append_command(",
    "send_order(",
    "create_order(",
    '"refresh_executed_by_this_checker": True',
    '"export_runner_executed_by_this_checker": True',
    '"runtime_artifact_write_performed_by_this_checker": True',
    '"warroom_ui_export_trigger_added": True',
    '"scheduler_created": True',
    '"freshness_bypass_added": True',
    '"force_ready_added": True',
    '"parameter_apply_allowed": True',
    '"parameter_staging_write_allowed": True',
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def _dirty_paths() -> set[str]:
    proc = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True)
    out: set[str] = set()
    for line in proc.stdout.splitlines():
        if line.strip():
            out.add(line[3:].replace(chr(92), "/"))
    return out


def main() -> int:
    failures: list[str] = []
    text = _read(CHECKER_PATH) if CHECKER_PATH.exists() else ""
    if not CHECKER_PATH.exists():
        failures.append(f"missing checker: {CHECKER_PATH.relative_to(REPO_ROOT)}")
    for marker in REQUIRED_MARKERS:
        if marker not in text:
            failures.append(f"missing checker marker: {marker}")
    for marker in FORBIDDEN_MARKERS:
        if marker in text:
            failures.append(f"forbidden marker present: {marker}")
    if CHECKER != "ps_q15d_operator_refresh_acceptance_gate":
        failures.append("checker id mismatch")
    stale_gate = _acceptance_from_reports(
        {"primary_root_cause": "latest_prediction_artifact_stale", "file_metadata": {"age_sec": 7200, "freshness_status": "stale"}},
        {"primary_conclusion": "operator_shell_refresh_path_exists_but_is_not_scheduler", "artifact_metadata": {"age_sec": 7200}},
        {"ok": False, "adapter_state": "latest_prediction_source_blocked", "actual_file_read_succeeded": False, "payload_decode_succeeded": False, "loaded_payload_count": 0, "review_packet_ready": False, "session_state_updated": False},
    )
    if stale_gate.get("accepted") is not False:
        failures.append("stale gate must reject")
    ready_gate = _acceptance_from_reports(
        {"primary_root_cause": "no_blocking_root_cause_detected_by_ps_q15a", "file_metadata": {"age_sec": 10, "freshness_status": "fresh"}},
        {"primary_conclusion": "operator_shell_refresh_path_exists_but_is_not_scheduler", "artifact_metadata": {"age_sec": 10}},
        {"ok": True, "adapter_state": "latest_prediction_source_ready", "actual_file_read_succeeded": True, "payload_decode_succeeded": True, "loaded_payload_count": 1, "review_packet_ready": True, "session_state_updated": True},
    )
    if ready_gate.get("accepted") is not True:
        failures.append("fresh ready gate must accept")
    dirty = _dirty_paths()
    unexpected_dirty = dirty - EXPECTED_DIRTY
    if unexpected_dirty:
        failures.append(f"unexpected dirty paths: {sorted(unexpected_dirty)}")
    payload = {
        "ok": not failures,
        "guard": "ps_q15d_operator_refresh_acceptance_gate",
        "contract": {
            "read_only_acceptance_gate_present": not failures,
            "stale_inputs_rejected": stale_gate.get("accepted") is False,
            "fresh_ready_inputs_accepted": ready_gate.get("accepted") is True,
            "no_refresh_or_runtime_write_execution": not failures,
            "expected_dirty_only": not unexpected_dirty,
        },
        "dirty_paths": sorted(dirty),
        "unexpected_dirty": sorted(unexpected_dirty),
        "failures": failures,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


def test_ps_q15d_operator_refresh_acceptance_gate_guard() -> None:
    assert main() == 0


if __name__ == "__main__":
    raise SystemExit(main())
