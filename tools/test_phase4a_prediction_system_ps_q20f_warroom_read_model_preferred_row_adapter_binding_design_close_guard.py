# path: ./tools/test_phase4a_prediction_system_ps_q20f_warroom_read_model_preferred_row_adapter_binding_design_close_guard.py
# desc: Close guard for PS-Q20F WarRoom read-model preferred-row adapter binding design.

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.test_phase4a_prediction_system_ps_q20f_warroom_read_model_preferred_row_adapter_binding_design import (  # noqa: E402
    FALSE_BOUNDARIES,
    REQUIRED_MARKERS,
    SPEC,
)

EXPECTED_DIRTY = {
    "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/read_models/preferred_row_adapter_binding_design.py",
    "docs/strategy/PREDICTION_SYSTEM_PS_Q20F_WARROOM_READ_MODEL_PREFERRED_ROW_ADAPTER_BINDING_DESIGN_2026-06-26.md",
    "tools/test_phase4a_prediction_system_ps_q20f_warroom_read_model_preferred_row_adapter_binding_design.py",
    "tools/test_phase4a_prediction_system_ps_q20f_warroom_read_model_preferred_row_adapter_binding_design_close_guard.py",
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
        "guard": "ps_q20f_warroom_read_model_preferred_row_adapter_binding_design_close_guard",
        "contract": {
            "ps_q20f_warroom_read_model_preferred_row_adapter_binding_design": True,
            "binding_design_only": True,
            "existing_warroom_read_model_changed": False,
            "existing_market_snapshot_replaced": False,
            "existing_market_state_service_changed": False,
            "existing_warroom_runtime_rewired": False,
            "component_runtime_binding_allowed": False,
            "ui_code_changed": False,
            "scheduler_enabled": False,
            "producer_enabled": False,
            "warroom_ui_trigger_enabled": False,
            "view_artifact_write_allowed": False,
            "would_write_warroom_view_artifact": False,
            "ps_q19r_scoring_policy_changed": False,
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


def test_ps_q20f_close_guard() -> None:
    assert main_guard() == 0


if __name__ == "__main__":
    raise SystemExit(main_guard())
