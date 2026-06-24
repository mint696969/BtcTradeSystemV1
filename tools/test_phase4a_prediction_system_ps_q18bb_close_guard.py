# path: ./tools/test_phase4a_prediction_system_ps_q18bb_close_guard.py
# desc: Close guard for PS-Q18BB legacy component reference audit/archive-delete decision.

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.test_phase4a_prediction_system_ps_q18bb_legacy_component_reference_audit_archive_delete_decision import (  # noqa: E402
    FALSE_BOUNDARIES,
    build_ps_q18bb_legacy_component_reference_audit_packet,
)

EXPECTED_DIRTY = {
    "docs/strategy/PREDICTION_SYSTEM_PS_Q18BB_LEGACY_COMPONENT_REFERENCE_AUDIT_ARCHIVE_DELETE_DECISION_2026-06-24.md",
    "tools/test_phase4a_prediction_system_ps_q18bb_close_guard.py",
    "tools/test_phase4a_prediction_system_ps_q18bb_legacy_component_reference_audit_archive_delete_decision.py",
    "tools/test_phase4a_prediction_system_ps_q18bb_legacy_component_reference_audit_archive_delete_decision_guard.py",
}


def _dirty_paths() -> set[str]:
    proc = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True)
    return {line[3:].replace(chr(92), "/") for line in proc.stdout.splitlines() if line.strip() and "/__pycache__/" not in line and not line.endswith(".pyc")}


def main_guard() -> int:
    failures: list[str] = []
    packet = build_ps_q18bb_legacy_component_reference_audit_packet()
    if packet.get("warroom_page_legacy_import_refs") is not False:
        failures.append("warroom_page legacy refs must be zero")
    if packet.get("component_modules_deleted_this_slice") is not False:
        failures.append("component modules must not be deleted in PS-Q18BB")
    if packet.get("immediate_physical_delete_decision") != "defer":
        failures.append("physical delete must be deferred")
    if packet.get("future_extension_contracts_preserved") is not True:
        failures.append("future extension contracts must be preserved")
    if packet.get("prediction_widget_component_family_preserved") is not True:
        failures.append("prediction widget family must be preserved")
    if packet.get("next_safe_slice") != "PS-Q18BC WarRoom cleanup close and handoff":
        failures.append("next safe slice mismatch")
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
        "guard": "ps_q18bb_close_guard",
        "phase": "phase3_legacy_component_reference_audit_archive_delete_decision_closed",
        "contract": {
            "ps_q18bb_closed": not failures,
            "warroom_page_legacy_import_refs": packet.get("warroom_page_legacy_import_refs"),
            "component_modules_deleted_this_slice": packet.get("component_modules_deleted_this_slice"),
            "immediate_physical_delete_decision": packet.get("immediate_physical_delete_decision"),
            "future_extension_contracts_preserved": packet.get("future_extension_contracts_preserved"),
            "prediction_widget_component_family_preserved": packet.get("prediction_widget_component_family_preserved"),
            "real_prediction_widget_render_invoked": False,
            "autotrade_trigger_allowed": False,
            "broker_private_api_allowed": False,
            "next_slice": packet.get("next_safe_slice"),
        },
        "dirty_paths": sorted(dirty),
        "unexpected_dirty": sorted(unexpected),
        "missing_dirty": sorted(missing),
        "failures": failures,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


def test_ps_q18bb_close_guard() -> None:
    assert main_guard() == 0


if __name__ == "__main__":
    raise SystemExit(main_guard())
