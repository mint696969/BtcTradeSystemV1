# path: ./tools/test_phase4a_prediction_system_ps_q25n_warroom_prediction_display_cadence_gate_closeout_readiness_close_guard.py
# desc: Close guard for PS-Q25N WarRoom prediction display/cadence-gate closeout readiness.

from __future__ import annotations

import json
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
EXPECTED_DIRTY = {
    "docs/strategy/PREDICTION_SYSTEM_PS_Q25N_WARROOM_PREDICTION_DISPLAY_CADENCE_GATE_CLOSEOUT_READINESS_2026-06-30.md",
    "tools/diagnose_phase4a_prediction_system_ps_q25n_warroom_prediction_display_cadence_gate_closeout_readiness.py",
    "tools/test_phase4a_prediction_system_ps_q25n_warroom_prediction_display_cadence_gate_closeout_readiness.py",
    "tools/test_phase4a_prediction_system_ps_q25n_warroom_prediction_display_cadence_gate_closeout_readiness_close_guard.py",
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
    result = {"ok": dirty == EXPECTED_DIRTY, "guard": "ps_q25n_warroom_prediction_display_cadence_gate_closeout_readiness_close_guard", "dirty_paths": sorted(dirty), "missing_dirty": sorted(EXPECTED_DIRTY - dirty), "unexpected_dirty": sorted(dirty - EXPECTED_DIRTY), "contract": {"production_code_changed": False, "read_only_closeout": True, "display_lane_closeout_ready": True, "cadence_lane_stopped_at_human_gate": True, "actual_screenshot_review_performed": False, "actual_screenshot_review_required_before_visual_final": True, "producer_cadence_changed": False, "scheduler_action_changed": False, "scheduler_enabled": False, "producer_enabled": False, "runtime_artifact_write_allowed": False, "status_artifact_write_allowed": False, "prediction_artifact_write_allowed": False, "view_artifact_write_allowed": False, "latest_manifest_written": False, "run_sidecars_written": False, "autotrade_trigger_allowed": False, "broker_private_api_allowed": False, "ledger_append": False, "mode_apply": False, "parameter_apply": False}}
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main_guard())
