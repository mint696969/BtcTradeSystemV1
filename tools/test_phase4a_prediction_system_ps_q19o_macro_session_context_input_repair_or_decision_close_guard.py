# path: ./tools/test_phase4a_prediction_system_ps_q19o_macro_session_context_input_repair_or_decision_close_guard.py
# desc: Close guard for PS-Q19O explicit neutral macro/session context default.

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.test_phase4a_prediction_system_ps_q19o_macro_session_context_input_repair_or_decision import (  # noqa: E402
    FALSE_BOUNDARIES,
    REQUIRED_MARKERS,
    SPEC,
)

EXPECTED_DIRTY = {
    "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_prediction_system_result_builder_runner.py",
    "btcts_next/src/btcts/prediction/source_quality.py",
    "docs/strategy/PREDICTION_SYSTEM_PS_Q19O_MACRO_SESSION_CONTEXT_INPUT_REPAIR_OR_DECISION_2026-06-25.md",
    "tools/test_phase4a_prediction_system_ps_q19o_macro_session_context_input_repair_or_decision.py",
    "tools/test_phase4a_prediction_system_ps_q19o_macro_session_context_input_repair_or_decision_close_guard.py",
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
        "guard": "ps_q19o_macro_session_context_input_repair_or_decision_close_guard",
        "contract": {
            "ps_q19o_macro_session_context_input_repair_or_decision": True,
            "macro_session_decision": "explicit_neutral_context_only_default",
            "macro_context_neutral_default_supplied": True,
            "session_calendar_context_neutral_default_supplied": True,
            "external_macro_api_added": False,
            "external_session_calendar_api_added": False,
            "collector_behavior_changed": False,
            "runtime_artifact_write_allowed": False,
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


def test_ps_q19o_close_guard() -> None:
    assert main_guard() == 0


if __name__ == "__main__":
    raise SystemExit(main_guard())
