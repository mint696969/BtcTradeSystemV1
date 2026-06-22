# path: ./tools/test_phase4a_prediction_system_ps_q16d_close_guard.py
# desc: Close guard for PS-Q16D bounded manual refresh runner.

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any

from _btcts_bootstrap import ensure_btcts_on_syspath

ensure_btcts_on_syspath()

from btcts.apps.operator_ui.components.prediction_warroom_bounded_manual_refresh_runner import (  # noqa: E402
    PREDICTION_WARROOM_BOUNDED_MANUAL_REFRESH_RUNNER_VERSION,
    build_prediction_warroom_bounded_manual_refresh_runner,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
EXPECTED_DIRTY = {
    "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_bounded_manual_refresh_runner.py",
    "btcts_next/src/btcts/apps/operator_ui/tests/test_prediction_warroom_bounded_manual_refresh_runner.py",
    "docs/strategy/PREDICTION_SYSTEM_PS_Q16D_BOUNDED_MANUAL_REFRESH_RUNNER_2026-06-22.md",
    "tools/test_phase4a_prediction_system_ps_q16d_bounded_manual_refresh_runner_guard.py",
    "tools/test_phase4a_prediction_system_ps_q16d_close_guard.py",
}
REQUIRED_FILES = tuple(EXPECTED_DIRTY)
UNIT_TEST = "btcts_next/src/btcts/apps/operator_ui/tests/test_prediction_warroom_bounded_manual_refresh_runner.py"
FOCUSED_GUARD = "tools/test_phase4a_prediction_system_ps_q16d_bounded_manual_refresh_runner_guard.py"


def _dirty_paths() -> set[str]:
    proc = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True)
    out: set[str] = set()
    for line in proc.stdout.splitlines():
        if line.strip():
            out.add(line[3:].replace(chr(92), "/"))
    return out


def _fake_export(**kwargs: Any) -> dict[str, Any]:
    root = Path(str(kwargs["hot_latest_root_hint"]))
    target = root / "prediction" / "latest_prediction_system_result.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text('{"ok": true}\n', encoding="utf-8")
    return {
        "runner_state": "latest_payload_actual_export_runner_exported",
        "target_file_written": True,
        "target_artifact_path": str(target),
        "target_file_size_bytes": target.stat().st_size,
        "prediction_run_id": "prediction_system.ps_q16d.close:BTC_JPY:bitFlyer:2026-06-22T10:00:00Z",
        "generated_at": "2026-06-22T10:00:00Z",
        "exported_at": "2026-06-22T10:00:01Z",
        "blocked_reasons": [],
        "warning_reasons": [],
        "warroom_page_mutation_allowed": False,
        "warroom_panel_mutation_allowed": False,
        "ui_triggered_runner_execution": False,
        "approval_or_authorization_allowed": False,
        "ledger_append_allowed": False,
        "autotrade_trigger_allowed": False,
        "broker_private_api_allowed": False,
        "would_write_collector_state": False,
        "would_send_to_broker": False,
        "broker_execution_requested": False,
        "mode_apply_requested": False,
        "command_ledger_append_requested": False,
        "approval_append_requested": False,
        "authorization_grant_requested": False,
        "autotrade_trigger_enabled": False,
    }


def main() -> int:
    failures: list[str] = []
    for rel in REQUIRED_FILES:
        if not (REPO_ROOT / rel).exists():
            failures.append(f"missing required file: {rel}")

    default_packet = build_prediction_warroom_bounded_manual_refresh_runner().to_dict()
    if default_packet.get("runner_version") != PREDICTION_WARROOM_BOUNDED_MANUAL_REFRESH_RUNNER_VERSION:
        failures.append("runner version mismatch")
    if default_packet.get("actual_export_runner_invoked") is not False:
        failures.append("default runner must not invoke actual export runner")
    for key in (
        "latest_prediction_artifact_written",
        "status_artifact_written",
        "producer_enabled",
        "scheduler_enabled",
        "scheduled_loop_enabled",
        "warroom_ui_trigger_enabled",
        "ui_triggered_runner_execution",
        "parameter_apply_allowed",
        "parameter_staging_write_allowed",
        "approval_or_authorization_allowed",
        "ledger_append_allowed",
        "autotrade_trigger_allowed",
        "broker_private_api_allowed",
        "ready_for_scheduler_enablement",
        "ready_for_automation_enablement",
    ):
        if default_packet.get(key) is not False:
            failures.append(f"unsafe/default flag must remain false: {key}={default_packet.get(key)!r}")

    with TemporaryDirectory() as temp_dir:
        packet = build_prediction_warroom_bounded_manual_refresh_runner(
            hot_latest_root_hint=temp_dir,
            operator_acknowledged=True,
            execute_manual_refresh=True,
            allow_actual_read=True,
            allow_prediction_build=True,
            allow_export_preflight=True,
            allow_latest_payload_export=True,
            allow_runtime_artifact_write=True,
            allow_status_artifact_write=True,
            execute_status_artifact_write=True,
            allow_guard_test_root=True,
            actual_export_runner=_fake_export,
        ).to_dict()
        status_path = Path(str(packet.get("status_artifact_path")))
        if packet.get("runner_state") != "bounded_manual_refresh_exported_status_written":
            failures.append("explicit manual refresh should export and write status")
        if packet.get("actual_export_runner_invoked") is not True:
            failures.append("explicit manual refresh should invoke actual export")
        if packet.get("latest_prediction_artifact_written") is not True:
            failures.append("explicit manual refresh should write latest prediction artifact via child")
        if packet.get("status_artifact_written") is not True:
            failures.append("explicit manual refresh should write producer status")
        if packet.get("scheduler_enabled") is not False or packet.get("scheduled_loop_enabled") is not False:
            failures.append("scheduler/scheduled loop must remain false")
        if packet.get("warroom_ui_trigger_enabled") is not False:
            failures.append("WarRoom UI trigger must remain false")
        if not status_path.exists():
            failures.append("status artifact should exist after explicit guard-root run")
        else:
            data = json.loads(status_path.read_text(encoding="utf-8"))
            if data.get("producer_enabled") is not False:
                failures.append("status producer_enabled must be false")
            if data.get("scheduler_enabled") is not False:
                failures.append("status scheduler_enabled must be false")
            if data.get("last_prediction_run_id") != "prediction_system.ps_q16d.close:BTC_JPY:bitFlyer:2026-06-22T10:00:00Z":
                failures.append("status last_prediction_run_id mismatch")

    dirty = _dirty_paths()
    unexpected_dirty = dirty - EXPECTED_DIRTY
    if unexpected_dirty:
        failures.append(f"unexpected dirty paths: {sorted(unexpected_dirty)}")
    payload = {
        "ok": not failures,
        "guard": "ps_q16d_close_guard",
        "phase": "phase3_prediction_system_warroom_realtime_observation_bounded_manual_refresh_closed",
        "focused_guards_to_run_before_commit": [UNIT_TEST, FOCUSED_GUARD],
        "contract": {
            "ps_q16d_closed": not failures,
            "next_slice": "PS-Q16E operator-shell manual run wrapper/smoke against D-hot with clean-tree precheck",
            "bounded_manual_refresh_only": True,
            "actual_export_runner_invoked_only_after_all_explicit_flags": True,
            "scheduler_enabled": False,
            "scheduled_loop_enabled": False,
            "warroom_ui_trigger_enabled": False,
            "autotrade_trigger_candidate_deferred": True,
        },
        "dirty_paths": sorted(dirty),
        "unexpected_dirty": sorted(unexpected_dirty),
        "failures": failures,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


def test_ps_q16d_close_guard() -> None:
    assert main() == 0


if __name__ == "__main__":
    raise SystemExit(main())
