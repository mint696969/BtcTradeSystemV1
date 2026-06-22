# path: ./tools/test_phase4a_prediction_system_ps_q15a_source_readiness_root_cause_guard.py
# desc: Guard for PS-Q15A read-only source-readiness root-cause diagnostic.

from __future__ import annotations

import json
import subprocess
from pathlib import Path

from _btcts_bootstrap import ensure_btcts_on_syspath

ensure_btcts_on_syspath()

from check_phase4a_prediction_system_ps_q15a_source_readiness_root_cause import (  # noqa: E402
    CHECKER,
    _classify_root_causes,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
CHECKER_PATH = REPO_ROOT / "tools/check_phase4a_prediction_system_ps_q15a_source_readiness_root_cause.py"
GUARD = REPO_ROOT / "tools/test_phase4a_prediction_system_ps_q15a_source_readiness_root_cause_guard.py"
EXPECTED_DIRTY = {
    "tools/check_phase4a_prediction_system_ps_q15a_source_readiness_root_cause.py",
    "tools/test_phase4a_prediction_system_ps_q15a_source_readiness_root_cause_guard.py",
}

REQUIRED_CHECKER_MARKERS = (
    "ps_q15a_source_readiness_root_cause",
    "DEFAULT_REQUIRED_ARTIFACT_FRESHNESS_MAX_AGE_SEC",
    "build_prediction_warroom_latest_prediction_source_adapter",
    "latest_prediction_artifact_stale",
    "q9b_no_loaded_payload",
    "downstream_mapping_missing_after_loader_block",
    "handoff_blocked_because_review_packet_not_ready",
    "freshness_bypass_added",
    "force_ready_added",
    "runtime_artifact_write_allowed",
    "parameter_staging_write_allowed",
)
FORBIDDEN_MARKERS = (
    "append_decision(",
    "append_command(",
    "send_order(",
    "create_order(",
    "call_private_api(",
    "apply_live_parameters(",
    "mutate_live_parameters(",
    '"freshness_bypass_added": True',
    '"force_ready_added": True',
    '"runtime_artifact_write_allowed": True',
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
    if not CHECKER_PATH.exists():
        failures.append(f"missing checker: {CHECKER_PATH.relative_to(REPO_ROOT)}")
        text = ""
    else:
        text = _read(CHECKER_PATH)
    for marker in REQUIRED_CHECKER_MARKERS:
        if marker not in text:
            failures.append(f"missing checker marker: {marker}")
    for marker in FORBIDDEN_MARKERS:
        if marker in text:
            failures.append(f"forbidden marker present: {marker}")
    if CHECKER != "ps_q15a_source_readiness_root_cause":
        failures.append("checker id mismatch")
    causes = _classify_root_causes(
        {"path_exists": True, "freshness_status": "stale", "age_sec": 7200, "freshness_max_age_sec": 3600},
        {
            "actual_file_read_succeeded": False,
            "payload_decode_succeeded": False,
            "loaded_payload_count": 0,
            "review_packet_ready": False,
            "session_state_updated": False,
            "blocked_reasons": [
                "freshness_status_stale_before_actual_read",
                "prediction_result_payload_mapping_missing",
                "q10k_session_state_handoff_not_updated",
            ],
        },
    )
    categories = [item.get("category") for item in causes]
    for expected in (
        "latest_prediction_artifact_stale",
        "q9b_no_loaded_payload",
        "downstream_mapping_missing_after_loader_block",
        "handoff_blocked_because_review_packet_not_ready",
    ):
        if expected not in categories:
            failures.append(f"missing root-cause category: {expected}")
    dirty = _dirty_paths()
    unexpected_dirty = dirty - EXPECTED_DIRTY
    if unexpected_dirty:
        failures.append(f"unexpected dirty paths: {sorted(unexpected_dirty)}")
    payload = {
        "ok": not failures,
        "guard": "ps_q15a_source_readiness_root_cause",
        "contract": {
            "read_only_diagnostic_present": not failures,
            "staleness_primary_cause_classified": not failures,
            "downstream_fail_closed_chain_classified": not failures,
            "no_bypass_or_execution_surface": not failures,
            "expected_dirty_only": not unexpected_dirty,
        },
        "dirty_paths": sorted(dirty),
        "unexpected_dirty": sorted(unexpected_dirty),
        "failures": failures,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


def test_ps_q15a_source_readiness_root_cause_guard() -> None:
    assert main() == 0


if __name__ == "__main__":
    raise SystemExit(main())
