# path: ./tools/test_phase4a_prediction_system_ps_q18au_close_guard.py
# desc: Close guard for PS-Q18AU WarRoom observation cleanup quick status.

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
BTCTS_SRC = REPO_ROOT / "btcts_next" / "src"
if str(BTCTS_SRC) not in sys.path:
    sys.path.insert(0, str(BTCTS_SRC))

from btcts.apps.operator_ui.views.warroom_page import (  # noqa: E402
    _prediction_warroom_latest_prediction_observation_cleanup_summary_packet,
)

EXPECTED_DIRTY = {
    "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py",
    "docs/strategy/PREDICTION_SYSTEM_PS_Q18AU_WARROOM_OBSERVATION_CLEANUP_QUICK_STATUS_2026-06-24.md",
    "tools/test_phase4a_prediction_system_ps_q18au_close_guard.py",
    "tools/test_phase4a_prediction_system_ps_q18au_observation_cleanup_quick_status.py",
    "tools/test_phase4a_prediction_system_ps_q18au_observation_cleanup_quick_status_guard.py",
}


def _dirty_paths() -> set[str]:
    proc = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True)
    return {line[3:].replace(chr(92), "/") for line in proc.stdout.splitlines() if line.strip() and "/__pycache__/" not in line and not line.endswith(".pyc")}


def main_guard() -> int:
    failures: list[str] = []
    packet = _prediction_warroom_latest_prediction_observation_cleanup_summary_packet(
        q18aj_packet={"auto_refresh_enabled": True, "fragment_refresh_enabled": True, "broad_page_reload_disabled": True, "refresh_heartbeat_utc": "hb"},
        q18ak_packet={"freshness_state": "stale", "safe_fallback_reason_codes": ["source_generated_at_stale"]},
    )
    if packet.get("observation_cleanup_state") != "operator_quick_status_visible_display_only":
        failures.append("observation cleanup state mismatch")
    if packet.get("latest_prediction_observation_status") != "ready_for_operator_review":
        failures.append("latest prediction observation status mismatch")
    if packet.get("implementation_gate_review_result") != "blocked_not_ready_to_enable":
        failures.append("implementation gate must stay blocked")
    for key in ("real_rendering_enabled", "component_runtime_binding_allowed", "runtime_artifact_write_allowed", "status_artifact_write_allowed", "parameter_apply_allowed", "ledger_append_allowed", "autotrade_trigger_allowed", "broker_private_api_allowed", "would_send_to_broker"):
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
        "guard": "ps_q18au_close_guard",
        "phase": "phase3_warroom_observation_cleanup_quick_status_closed_display_only",
        "contract": {
            "ps_q18au_closed": not failures,
            "observation_cleanup_state": packet.get("observation_cleanup_state"),
            "latest_prediction_observation_status": packet.get("latest_prediction_observation_status"),
            "implementation_gate_review_result": packet.get("implementation_gate_review_result"),
            "real_rendering_enabled": False,
            "component_runtime_binding_allowed": False,
            "autotrade_trigger_allowed": False,
            "broker_private_api_allowed": False,
            "next_slice": "manual UI smoke for observation quick status or continued legacy preflight folding cleanup",
        },
        "dirty_paths": sorted(dirty),
        "unexpected_dirty": sorted(unexpected),
        "missing_dirty": sorted(missing),
        "failures": failures,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


def test_ps_q18au_close_guard() -> None:
    assert main_guard() == 0


if __name__ == "__main__":
    raise SystemExit(main_guard())
