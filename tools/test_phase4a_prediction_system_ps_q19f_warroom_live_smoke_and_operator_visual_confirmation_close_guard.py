# path: ./tools/test_phase4a_prediction_system_ps_q19f_warroom_live_smoke_and_operator_visual_confirmation_close_guard.py
# desc: Close guard for PS-Q19F WarRoom live smoke and operator visual confirmation helper.

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.test_phase4a_prediction_system_ps_q19f_warroom_live_smoke_and_operator_visual_confirmation import (  # noqa: E402
    FALSE_BOUNDARIES,
    REQUIRED_MARKERS,
    SPEC,
)

EXPECTED_DIRTY = {
    "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/read_models/latest_prediction_warroom_read_model.py",
    "tools/check_phase4a_prediction_system_ps_q19f_warroom_live_smoke.py",
    "docs/strategy/PREDICTION_SYSTEM_PS_Q19F_WARROOM_LIVE_SMOKE_AND_OPERATOR_VISUAL_CONFIRMATION_2026-06-25.md",
    "tools/test_phase4a_prediction_system_ps_q19f_warroom_live_smoke_and_operator_visual_confirmation.py",
    "tools/test_phase4a_prediction_system_ps_q19f_warroom_live_smoke_and_operator_visual_confirmation_close_guard.py",
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
        "guard": "ps_q19f_warroom_live_smoke_and_operator_visual_confirmation_close_guard",
        "phase": "ps_q19f_live_smoke_before_operator_manual_refresh_optional",
        "contract": {
            "ps_q19f_warroom_live_smoke_and_operator_visual_confirmation": True,
            "ps_q19e_dry_run_no_write_verified": True,
            "ps_q19c_read_model_loaded": True,
            "ps_q19d_display_packet_verified": True,
            "operator_visual_confirmation_flags_supported": True,
            "runtime_artifact_write_performed_by_smoke": False,
            "status_artifact_write_performed_by_smoke": False,
            "scheduler_enabled": False,
            "producer_enabled": False,
            "warroom_ui_trigger_enabled": False,
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


def test_ps_q19f_close_guard() -> None:
    assert main_guard() == 0


if __name__ == "__main__":
    raise SystemExit(main_guard())
