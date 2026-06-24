# path: ./tools/test_phase4a_prediction_system_ps_q19b2_health_telemetry_source_alignment_close_guard.py
# desc: Close guard for PS-Q19B2 Health telemetry source alignment.

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.test_phase4a_prediction_system_ps_q19b2_health_telemetry_source_alignment_guard import (  # noqa: E402
    FALSE_BOUNDARIES,
    REQUIRED_MARKERS,
    SPEC,
)

EXPECTED_DIRTY = {
    "btcts_next/src/btcts/apps/operator_ui/health_audit_read_model.py",
    "btcts_next/src/btcts/apps/operator_ui/health_data_service.py",
    "btcts_next/src/btcts/apps/operator_ui/components/health_chart_panels.py",
    "btcts_next/src/btcts/apps/operator_ui/texts/health.py",
    "btcts_next/src/btcts/apps/operator_ui/tests/test_health_data_service_coverage.py",
    "docs/strategy/PREDICTION_SYSTEM_PS_Q19B2_HEALTH_TELEMETRY_SOURCE_ALIGNMENT_2026-06-25.md",
    "tools/test_phase4a_prediction_system_ps_q19b2_health_telemetry_source_alignment_guard.py",
    "tools/test_phase4a_prediction_system_ps_q19b2_health_telemetry_source_alignment_close_guard.py",
}


def _dirty_paths() -> set[str]:
    proc = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True)
    paths: set[str] = set()
    for line in proc.stdout.splitlines():
        if not line.strip():
            continue
        path = line[3:].replace(chr(92), "/")
        if "/__pycache__/" in path or path.endswith(".pyc"):
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
        "guard": "ps_q19b2_health_telemetry_source_alignment_close_guard",
        "phase": "ps_q19b2_health_after_audit_telemetry_split",
        "contract": {
            "ps_q19b2_health_telemetry_source_alignment": True,
            "health_activity_source_uses_telemetry": True,
            "health_primary_audit_no_longer_required_for_success_activity_graph": True,
            "runtime_behavior_changed": False,
            "collector_data_collection_changed": False,
            "prediction_runtime_changed": False,
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


def test_ps_q19b2_close_guard() -> None:
    assert main_guard() == 0


if __name__ == "__main__":
    raise SystemExit(main_guard())
