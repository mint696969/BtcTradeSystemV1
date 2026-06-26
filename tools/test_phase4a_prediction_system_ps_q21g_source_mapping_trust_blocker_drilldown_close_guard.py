# path: ./tools/test_phase4a_prediction_system_ps_q21g_source_mapping_trust_blocker_drilldown_close_guard.py
# desc: Close guard for PS-Q21G source mapping / market overview trust blocker drilldown.

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.test_phase4a_prediction_system_ps_q21g_source_mapping_trust_blocker_drilldown import (  # noqa: E402
    FALSE_BOUNDARIES,
    REQUIRED_MARKERS,
    SPEC,
)

EXPECTED_DIRTY = {
    "docs/strategy/PREDICTION_SYSTEM_PS_Q21G_SOURCE_MAPPING_TRUST_BLOCKER_DRILLDOWN_2026-06-26.md",
    "tools/diagnose_phase4a_prediction_system_ps_q21g_source_mapping_trust_blocker_drilldown.py",
    "tools/test_phase4a_prediction_system_ps_q21g_source_mapping_trust_blocker_drilldown.py",
    "tools/test_phase4a_prediction_system_ps_q21g_source_mapping_trust_blocker_drilldown_close_guard.py",
}


def _dirty_paths() -> set[str]:
    proc = subprocess.run(["git", "status", "--short", "--untracked-files=all"], cwd=REPO_ROOT, text=True, capture_output=True, check=True)
    paths: set[str] = set()
    for line in proc.stdout.splitlines():
        if not line.strip():
            continue
        path = line[3:].replace(chr(92), "/")
        if "/__pycache__/" in path or path.endswith(".pyc"):
            continue
        if path.startswith("tmp/work/") or path.startswith("tmp/gpt_room/"):
            continue
        paths.add(path)
    return paths


def main_guard() -> int:
    failures: list[str] = []
    text = SPEC.read_text(encoding="utf-8-sig") if SPEC.exists() else ""
    for marker in REQUIRED_MARKERS:
        if marker not in text:
            failures.append(f"missing required marker: {marker}")
    for marker in FALSE_BOUNDARIES:
        if marker not in text:
            failures.append(f"missing false boundary: {marker}")
    dirty = _dirty_paths()
    unexpected = dirty - EXPECTED_DIRTY
    missing = EXPECTED_DIRTY - dirty
    if unexpected:
        failures.append(f"unexpected dirty paths: {sorted(unexpected)}")
    if missing:
        failures.append(f"missing expected dirty paths: {sorted(missing)}")
    result = {
        "ok": not failures,
        "guard": "ps_q21g_source_mapping_trust_blocker_drilldown_close_guard",
        "contract": {
            "ps_q21g_source_mapping_trust_blocker_drilldown": True,
            "market_overview_trust_state_visible": True,
            "market_overview_interpretation_bucket_visible": True,
            "q9z_probe_readiness_visible": True,
            "q10a_mapping_readiness_visible": True,
            "read_only_diagnostic_only": True,
            "prediction_build_allowed": False,
            "latest_prediction_artifact_export_allowed": False,
            "runtime_enablement_allowed": False,
            "scheduler_enablement_allowed": False,
            "producer_enablement_allowed": False,
            "runtime_artifact_write_allowed": False,
            "status_artifact_write_allowed": False,
            "prediction_artifact_write_allowed": False,
            "view_artifact_write_allowed": False,
            "autotrade_trigger_allowed": False,
            "broker_private_api_allowed": False,
            "would_send_to_broker": False,
        },
        "dirty_paths": sorted(dirty),
        "unexpected_dirty": sorted(unexpected),
        "missing_dirty": sorted(missing),
        "failures": failures,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


def test_ps_q21g_close_guard() -> None:
    assert main_guard() == 0


if __name__ == "__main__":
    raise SystemExit(main_guard())
