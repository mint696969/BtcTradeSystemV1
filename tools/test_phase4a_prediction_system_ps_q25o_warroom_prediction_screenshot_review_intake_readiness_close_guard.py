# path: ./tools/test_phase4a_prediction_system_ps_q25o_warroom_prediction_screenshot_review_intake_readiness_close_guard.py
# desc: Close guard for PS-Q25O WarRoom prediction screenshot review intake readiness.

from __future__ import annotations

import json
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
EXPECTED_DIRTY = {
    "docs/strategy/PREDICTION_SYSTEM_PS_Q25O_WARROOM_PREDICTION_SCREENSHOT_REVIEW_INTAKE_READINESS_2026-06-30.md",
    "tools/diagnose_phase4a_prediction_system_ps_q25o_warroom_prediction_screenshot_review_intake_readiness.py",
    "tools/test_phase4a_prediction_system_ps_q25o_warroom_prediction_screenshot_review_intake_readiness.py",
    "tools/test_phase4a_prediction_system_ps_q25o_warroom_prediction_screenshot_review_intake_readiness_close_guard.py",
}


def _dirty() -> set[str]:
    proc = subprocess.run(["git", "status", "--short", "--untracked-files=all"], cwd=REPO_ROOT, text=True, capture_output=True, check=True)
    paths: set[str] = set()
    for line in proc.stdout.splitlines():
        path = line[3:].strip().replace(chr(92), "/")
        if path.startswith("tmp/work/") or path.startswith("tmp/gpt_room/") or "/__pycache__/" in path or path.endswith(".pyc"):
            continue
        paths.add(path)
    return paths


def main_guard() -> int:
    dirty = _dirty()
    result = {"ok": dirty == EXPECTED_DIRTY, "guard": "ps_q25o_warroom_prediction_screenshot_review_intake_readiness_close_guard", "dirty_paths": sorted(dirty), "missing_dirty": sorted(EXPECTED_DIRTY - dirty), "unexpected_dirty": sorted(dirty - EXPECTED_DIRTY), "contract": {"production_code_changed": False, "read_only_review_intake": True, "actual_screenshot_supplied": False, "actual_screenshot_review_performed": False, "actual_screenshot_review_required_before_visual_final": True, "q25j_density_tuning_review_target": True, "producer_cadence_changed": False, "scheduler_action_changed": False, "scheduler_enabled": False, "producer_enabled": False, "runtime_artifact_write_allowed": False, "status_artifact_write_allowed": False, "prediction_artifact_write_allowed": False, "view_artifact_write_allowed": False, "latest_manifest_written": False, "run_sidecars_written": False, "autotrade_trigger_allowed": False, "broker_private_api_allowed": False, "ledger_append": False, "mode_apply": False, "parameter_apply": False}}
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main_guard())
