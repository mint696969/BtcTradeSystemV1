# path: ./tools/test_phase4a_prediction_system_ps_q18bd_close_guard.py
# desc: Close guard for PS-Q18BD WarRoom UI spec export and sync.

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.test_phase4a_prediction_system_ps_q18bd_warroom_ui_spec_export import (  # noqa: E402
    FALSE_BOUNDARIES,
    SPEC,
)

EXPECTED_DIRTY = {
    "docs/strategy/PREDICTION_SYSTEM_PS_Q18BD_WARROOM_UI_SPEC_EXPORT_2026-06-24.md",
    "tools/test_phase4a_prediction_system_ps_q18bd_close_guard.py",
    "tools/test_phase4a_prediction_system_ps_q18bd_warroom_ui_spec_export.py",
    "tools/test_phase4a_prediction_system_ps_q18bd_warroom_ui_spec_export_guard.py",
}


def _dirty_paths() -> set[str]:
    proc = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True)
    return {line[3:].replace(chr(92), "/") for line in proc.stdout.splitlines() if line.strip() and "/__pycache__/" not in line and not line.endswith(".pyc")}


def main_guard() -> int:
    failures: list[str] = []
    text = SPEC.read_text(encoding="utf-8-sig") if SPEC.exists() else ""
    for marker in FALSE_BOUNDARIES:
        if marker not in text:
            failures.append(f"missing safety marker: {marker}")
    for marker in (
        "warroom_ui_spec_exported=true",
        "WarRoom UI sorting and normal UI optimization=complete",
        "future contracts/components=preserved",
        "next recommended slice=PS-Q19A design gate",
    ):
        if marker not in text:
            failures.append(f"missing close marker: {marker}")
    dirty = _dirty_paths()
    unexpected = dirty - EXPECTED_DIRTY
    missing = EXPECTED_DIRTY - dirty
    if unexpected:
        failures.append(f"unexpected dirty paths: {sorted(unexpected)}")
    if missing:
        failures.append(f"missing expected dirty paths: {sorted(missing)}")
    result = {
        "ok": not failures,
        "guard": "ps_q18bd_close_guard",
        "phase": "phase3_warroom_ui_spec_export_closed",
        "contract": {
            "ps_q18bd_closed": not failures,
            "warroom_ui_spec_exported": True,
            "runtime_behavior_changed": False,
            "ui_code_changed": False,
            "component_modules_deleted": False,
            "future_contracts_documented": True,
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


def test_ps_q18bd_close_guard() -> None:
    assert main_guard() == 0


if __name__ == "__main__":
    raise SystemExit(main_guard())
