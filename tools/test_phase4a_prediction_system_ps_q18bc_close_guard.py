# path: ./tools/test_phase4a_prediction_system_ps_q18bc_close_guard.py
# desc: Close guard for PS-Q18BC WarRoom header compact polish and cleanup thread close.

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "btcts_next" / "src"
for path in (REPO_ROOT, SRC_ROOT):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from tools.test_phase4a_prediction_system_ps_q18bc_warroom_header_compact_polish_cleanup_close import (  # noqa: E402
    FALSE_BOUNDARIES,
    build_ps_q18bc_cleanup_close_packet,
)

EXPECTED_DIRTY = {
    "btcts_next/src/btcts/apps/operator_ui/components/warroom_header.py",
    "docs/strategy/PREDICTION_SYSTEM_PS_Q18BC_WARROOM_HEADER_COMPACT_POLISH_CLEANUP_CLOSE_2026-06-24.md",
    "tools/test_phase4a_prediction_system_ps_q18bc_close_guard.py",
    "tools/test_phase4a_prediction_system_ps_q18bc_warroom_header_compact_polish_cleanup_close.py",
    "tools/test_phase4a_prediction_system_ps_q18bc_warroom_header_compact_polish_cleanup_close_guard.py",
}


def _dirty_paths() -> set[str]:
    proc = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True)
    return {line[3:].replace(chr(92), "/") for line in proc.stdout.splitlines() if line.strip() and "/__pycache__/" not in line and not line.endswith(".pyc")}


def main_guard() -> int:
    failures: list[str] = []
    packet = build_ps_q18bc_cleanup_close_packet()
    if packet.get("warroom_cleanup_optimization_complete") is not True:
        failures.append("WarRoom cleanup optimization must be complete")
    if packet.get("cleanup_thread_close_ready") is not True:
        failures.append("cleanup thread must be close-ready")
    if packet.get("caption_builder_functions_preserved") is not True:
        failures.append("caption builders must be preserved")
    if packet.get("component_modules_deleted_this_slice") is not False:
        failures.append("component modules must not be deleted in close slice")
    for key in FALSE_BOUNDARIES:
        if packet.get(key) is not False:
            failures.append(f"{key} must stay false")
    dirty = _dirty_paths()
    unexpected = dirty - EXPECTED_DIRTY
    missing = EXPECTED_DIRTY - dirty
    if unexpected:
        failures.append(f"unexpected dirty paths: {sorted(unexpected)}")
    if missing:
        failures.append(f"missing expected dirty paths: {sorted(missing)}")
    result = {
        "ok": not failures,
        "guard": "ps_q18bc_close_guard",
        "phase": "phase3_warroom_header_compact_polish_cleanup_thread_closed",
        "contract": {
            "ps_q18bc_closed": not failures,
            "warroom_cleanup_optimization_complete": packet.get("warroom_cleanup_optimization_complete"),
            "warroom_header_normal_ui_compact": packet.get("warroom_header_normal_ui_compact"),
            "caption_builder_functions_preserved": packet.get("caption_builder_functions_preserved"),
            "component_modules_deleted_this_slice": packet.get("component_modules_deleted_this_slice"),
            "real_prediction_widget_render_invoked": False,
            "autotrade_trigger_allowed": False,
            "broker_private_api_allowed": False,
        },
        "dirty_paths": sorted(dirty),
        "unexpected_dirty": sorted(unexpected),
        "missing_dirty": sorted(missing),
        "failures": failures,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


def test_ps_q18bc_close_guard() -> None:
    assert main_guard() == 0


if __name__ == "__main__":
    raise SystemExit(main_guard())
