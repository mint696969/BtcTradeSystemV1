# path: ./tools/test_phase4a_prediction_system_ps_q15b_source_readiness_producer_path_guard.py
# desc: Guard for PS-Q15B read-only latest prediction producer/export path diagnostic.

from __future__ import annotations

import json
import subprocess
from pathlib import Path

from _btcts_bootstrap import ensure_btcts_on_syspath

ensure_btcts_on_syspath()

from check_phase4a_prediction_system_ps_q15b_source_readiness_producer_path import (  # noqa: E402
    CHECKER,
    build_report,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
CHECKER_PATH = REPO_ROOT / "tools/check_phase4a_prediction_system_ps_q15b_source_readiness_producer_path.py"
GUARD = REPO_ROOT / "tools/test_phase4a_prediction_system_ps_q15b_source_readiness_producer_path_guard.py"
EXPECTED_DIRTY = {
    "tools/check_phase4a_prediction_system_ps_q15b_source_readiness_producer_path.py",
    "tools/test_phase4a_prediction_system_ps_q15b_source_readiness_producer_path_guard.py",
}
# NOTE: The checker intentionally contains static marker strings such as
# allow_runtime_artifact_write=True / execute_export=True to verify the prior
# PS-Q12D manual operator runner shape. Those strings are not execution.
# Runtime write/export execution is guarded below by safety booleans and by
# forbidding direct export runner function calls in this checker.
REQUIRED_MARKERS = (
    "ps_q15b_source_readiness_producer_path",
    "operator_shell_refresh_path_exists_but_is_not_scheduler",
    "current_latest_artifact_is_stale",
    "export_runner_executed",
    "runtime_artifact_write_performed",
    "warroom_ui_export_trigger_added",
    "do not run from WarRoom UI",
)
FORBIDDEN_MARKERS = (
    "build_prediction_warroom_latest_payload_actual_export_runner(",
    "build_prediction_warroom_latest_payload_export_runner(",
    "target.write_text(",
    "replace(target)",
    "append_decision(",
    "append_command(",
    "send_order(",
    "create_order(",
    '"export_runner_executed": True',
    '"runtime_artifact_write_performed": True',
    '"freshness_bypass_added": True',
    '"force_ready_added": True',
    '"warroom_ui_export_trigger_added": True',
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
    if CHECKER != "ps_q15b_source_readiness_producer_path":
        failures.append("checker id mismatch")
    report = build_report()
    safety = report.get("safety", {})
    for key in (
        "read_only_diagnostic",
    ):
        if safety.get(key) is not True:
            failures.append(f"safety {key} must be true")
    for key in (
        "export_runner_executed",
        "runtime_artifact_write_performed",
        "freshness_bypass_added",
        "force_ready_added",
        "warroom_ui_export_trigger_added",
        "ledger_append_allowed",
        "broker_private_api_allowed",
        "autotrade_trigger_allowed",
        "parameter_apply_allowed",
        "parameter_staging_write_allowed",
    ):
        if safety.get(key) is not False:
            failures.append(f"safety {key} must be false")
    source_report = report.get("source_marker_report", {})
    if not source_report.get("warroom_page", {}).get("export_runner_not_mounted"):
        failures.append("WarRoom page must not mount export runner")
    dirty = _dirty_paths()
    unexpected_dirty = dirty - EXPECTED_DIRTY
    if unexpected_dirty:
        failures.append(f"unexpected dirty paths: {sorted(unexpected_dirty)}")
    payload = {
        "ok": not failures,
        "guard": "ps_q15b_source_readiness_producer_path",
        "contract": {
            "read_only_diagnostic_present": not failures,
            "producer_path_classified": not failures,
            "warroom_export_runner_not_mounted": not failures,
            "no_runtime_write_or_execution": not failures,
            "expected_dirty_only": not unexpected_dirty,
        },
        "dirty_paths": sorted(dirty),
        "unexpected_dirty": sorted(unexpected_dirty),
        "failures": failures,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


def test_ps_q15b_source_readiness_producer_path_guard() -> None:
    assert main() == 0


if __name__ == "__main__":
    raise SystemExit(main())
