# path: ./tools/test_phase4a_prediction_system_ps_q16a_close_guard.py
# desc: Close guard for PS-Q16A after non-UI scheduled producer contract/guard/visibility design passed.

from __future__ import annotations

import json
import subprocess
from pathlib import Path

from _btcts_bootstrap import ensure_btcts_on_syspath

ensure_btcts_on_syspath()

from btcts.apps.operator_ui.components.prediction_warroom_non_ui_scheduled_producer_contract import (  # noqa: E402
    PREDICTION_WARROOM_NON_UI_SCHEDULED_PRODUCER_CONTRACT_VERSION,
    build_prediction_warroom_non_ui_scheduled_producer_contract,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
EXPECTED_DIRTY = {
    "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_non_ui_scheduled_producer_contract.py",
    "btcts_next/src/btcts/apps/operator_ui/tests/test_prediction_warroom_non_ui_scheduled_producer_contract.py",
    "docs/strategy/PREDICTION_SYSTEM_PS_Q16A_NON_UI_SCHEDULED_PRODUCER_CONTRACT_2026-06-22.md",
    "tools/test_phase4a_prediction_system_ps_q16a_non_ui_scheduled_producer_contract_guard.py",
    "tools/test_phase4a_prediction_system_ps_q16a_close_guard.py",
}
REQUIRED_FILES = tuple(EXPECTED_DIRTY)
FOCUSED_GUARD = "tools/test_phase4a_prediction_system_ps_q16a_non_ui_scheduled_producer_contract_guard.py"
UNIT_TEST = "btcts_next/src/btcts/apps/operator_ui/tests/test_prediction_warroom_non_ui_scheduled_producer_contract.py"


def _dirty_paths() -> set[str]:
    proc = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True)
    out: set[str] = set()
    for line in proc.stdout.splitlines():
        if line.strip():
            out.add(line[3:].replace(chr(92), "/"))
    return out


def main() -> int:
    failures: list[str] = []
    for rel in REQUIRED_FILES:
        if not (REPO_ROOT / rel).exists():
            failures.append(f"missing required file: {rel}")
    packet = build_prediction_warroom_non_ui_scheduled_producer_contract().to_dict()
    if packet.get("contract_version") != PREDICTION_WARROOM_NON_UI_SCHEDULED_PRODUCER_CONTRACT_VERSION:
        failures.append("contract version mismatch")
    if packet.get("ready_for_next_disabled_runner_slice") is not True:
        failures.append("PS-Q16A should be ready for PS-Q16B disabled runner slice")
    for key in (
        "producer_enabled",
        "scheduler_enabled",
        "runtime_artifact_write_enabled",
        "warroom_ui_trigger_enabled",
        "ready_for_scheduler_enablement",
        "ready_for_runtime_artifact_write_automation_enablement",
        "would_write_runtime_artifact",
        "would_write_status_artifact",
        "would_mutate_live_parameters",
        "parameter_apply_allowed",
        "parameter_staging_write_allowed",
        "autotrade_trigger_allowed",
        "broker_private_api_allowed",
    ):
        if packet.get(key) is not False:
            failures.append(f"unsafe flag must remain false: {key}={packet.get(key)!r}")
    dirty = _dirty_paths()
    unexpected_dirty = dirty - EXPECTED_DIRTY
    if unexpected_dirty:
        failures.append(f"unexpected dirty paths: {sorted(unexpected_dirty)}")
    payload = {
        "ok": not failures,
        "guard": "ps_q16a_close_guard",
        "phase": "phase3_prediction_system_warroom_realtime_observation_contract_closed",
        "focused_guards_to_run_before_commit": [UNIT_TEST, FOCUSED_GUARD],
        "contract": {
            "ps_q16a_contract_closed": not failures,
            "next_slice": "PS-Q16B disabled-by-default non-UI producer runner scaffold and status artifact writer",
            "scheduler_enabled": False,
            "runtime_artifact_write_automation_enabled": False,
            "warroom_realtime_observation_priority": True,
            "autotrade_trigger_candidate_deferred": True,
        },
        "dirty_paths": sorted(dirty),
        "unexpected_dirty": sorted(unexpected_dirty),
        "failures": failures,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


def test_ps_q16a_close_guard() -> None:
    assert main() == 0


if __name__ == "__main__":
    raise SystemExit(main())
