# path: ./tools/test_phase4a_prediction_system_ps_q16b_close_guard.py
# desc: Close guard for PS-Q16B disabled non-UI producer runner scaffold and status artifact writer.

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from tempfile import TemporaryDirectory

from _btcts_bootstrap import ensure_btcts_on_syspath

ensure_btcts_on_syspath()

from btcts.apps.operator_ui.components.prediction_warroom_non_ui_scheduled_producer_runner import (  # noqa: E402
    PREDICTION_WARROOM_NON_UI_SCHEDULED_PRODUCER_RUNNER_VERSION,
    build_prediction_warroom_non_ui_scheduled_producer_runner,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
EXPECTED_DIRTY = {
    "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_non_ui_scheduled_producer_runner.py",
    "btcts_next/src/btcts/apps/operator_ui/tests/test_prediction_warroom_non_ui_scheduled_producer_runner.py",
    "docs/strategy/PREDICTION_SYSTEM_PS_Q16B_DISABLED_NON_UI_PRODUCER_RUNNER_2026-06-22.md",
    "tools/test_phase4a_prediction_system_ps_q16b_disabled_non_ui_producer_runner_guard.py",
    "tools/test_phase4a_prediction_system_ps_q16b_close_guard.py",
}
REQUIRED_FILES = tuple(EXPECTED_DIRTY)
UNIT_TEST = "btcts_next/src/btcts/apps/operator_ui/tests/test_prediction_warroom_non_ui_scheduled_producer_runner.py"
FOCUSED_GUARD = "tools/test_phase4a_prediction_system_ps_q16b_disabled_non_ui_producer_runner_guard.py"


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
    packet = build_prediction_warroom_non_ui_scheduled_producer_runner().to_dict()
    if packet.get("runner_version") != PREDICTION_WARROOM_NON_UI_SCHEDULED_PRODUCER_RUNNER_VERSION:
        failures.append("runner version mismatch")
    if packet.get("ready_for_warroom_status_observation") is not True:
        failures.append("runner should be ready for WarRoom status observation")
    if packet.get("ready_for_manual_bounded_refresh_slice") is not True:
        failures.append("default runner should be contract-ready for the next manual bounded refresh slice")
    for key in (
        "producer_enabled",
        "scheduler_enabled",
        "runtime_artifact_write_enabled",
        "latest_prediction_artifact_write_enabled",
        "status_artifact_written",
        "actual_export_runner_invoked",
        "prediction_build_requested",
        "warroom_ui_trigger_enabled",
        "parameter_apply_allowed",
        "parameter_staging_write_allowed",
        "autotrade_trigger_allowed",
        "broker_private_api_allowed",
        "ready_for_scheduler_enablement",
        "ready_for_latest_prediction_artifact_write_automation",
    ):
        if packet.get(key) is not False:
            failures.append(f"unsafe/default flag must remain false: {key}={packet.get(key)!r}")
    with TemporaryDirectory() as temp_dir:
        written = build_prediction_warroom_non_ui_scheduled_producer_runner(
            hot_latest_root_hint=temp_dir,
            operator_acknowledged=True,
            allow_status_artifact_write=True,
            execute_status_artifact_write=True,
            allow_guard_test_root=True,
        ).to_dict()
        status_path = Path(str(written.get("status_artifact_path")))
        if written.get("runner_state") != "producer_disabled_status_written":
            failures.append("explicit status write should reach producer_disabled_status_written")
        if not status_path.exists():
            failures.append("explicit status write should create status artifact")
        else:
            data = json.loads(status_path.read_text(encoding="utf-8"))
            if data.get("producer_enabled") is not False:
                failures.append("status artifact producer_enabled must be false")
            if data.get("scheduler_enabled") is not False:
                failures.append("status artifact scheduler_enabled must be false")
            if data.get("runtime_artifact_write_enabled") is not False:
                failures.append("status artifact runtime_artifact_write_enabled must be false")
            if data.get("disable_rollback_state") != "disabled_by_default_no_scheduler_no_latest_prediction_write":
                failures.append("status artifact disable rollback state mismatch")
    dirty = _dirty_paths()
    unexpected_dirty = dirty - EXPECTED_DIRTY
    if unexpected_dirty:
        failures.append(f"unexpected dirty paths: {sorted(unexpected_dirty)}")
    payload = {
        "ok": not failures,
        "guard": "ps_q16b_close_guard",
        "phase": "phase3_prediction_system_warroom_realtime_observation_status_writer_closed",
        "focused_guards_to_run_before_commit": [UNIT_TEST, FOCUSED_GUARD],
        "contract": {
            "ps_q16b_closed": not failures,
            "next_slice": "PS-Q16C WarRoom read-only producer status loader/panel",
            "disabled_by_default": True,
            "status_artifact_writer_explicit_only": True,
            "scheduler_enabled": False,
            "latest_prediction_artifact_write_enabled": False,
            "autotrade_trigger_candidate_deferred": True,
        },
        "dirty_paths": sorted(dirty),
        "unexpected_dirty": sorted(unexpected_dirty),
        "failures": failures,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


def test_ps_q16b_close_guard() -> None:
    assert main() == 0


if __name__ == "__main__":
    raise SystemExit(main())
