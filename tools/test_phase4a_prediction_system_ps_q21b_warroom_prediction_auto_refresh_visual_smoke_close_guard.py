# path: ./tools/test_phase4a_prediction_system_ps_q21b_warroom_prediction_auto_refresh_visual_smoke_close_guard.py
# desc: Close guard for PS-Q21B WarRoom prediction auto-refresh visual smoke helper.

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.test_phase4a_prediction_system_ps_q21b_warroom_prediction_auto_refresh_visual_smoke import (  # noqa: E402
    FALSE_BOUNDARIES,
    REQUIRED_MARKERS,
    SPEC,
)

EXPECTED_DIRTY = {
    "docs/strategy/PREDICTION_SYSTEM_PS_Q21B_WARROOM_PREDICTION_AUTO_REFRESH_VISUAL_SMOKE_2026-06-26.md",
    "tools/smoke_phase4a_prediction_system_ps_q21b_warroom_prediction_auto_refresh_visual_smoke.py",
    "tools/test_phase4a_prediction_system_ps_q21b_warroom_prediction_auto_refresh_visual_smoke.py",
    "tools/test_phase4a_prediction_system_ps_q21b_warroom_prediction_auto_refresh_visual_smoke_close_guard.py",
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
        "guard": "ps_q21b_warroom_prediction_auto_refresh_visual_smoke_close_guard",
        "contract": {
            "ps_q21b_warroom_prediction_auto_refresh_visual_smoke": True,
            "non_ui_packet_heartbeat_changed": True,
            "manual_ui_smoke_required": True,
            "refresh_target": "latest_prediction_warroom_read_model_display_panel",
            "refresh_interval_sec": 5,
            "broad_page_reload_disabled": True,
            "runtime_enablement_allowed": False,
            "loader_binding_runtime_allowed": False,
            "component_runtime_binding_allowed": False,
            "runtime_artifact_write_allowed": False,
            "status_artifact_write_allowed": False,
            "prediction_artifact_write_allowed": False,
            "view_artifact_write_allowed": False,
            "scheduler_enabled": False,
            "producer_enabled": False,
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


def test_ps_q21b_close_guard() -> None:
    assert main_guard() == 0


if __name__ == "__main__":
    raise SystemExit(main_guard())
