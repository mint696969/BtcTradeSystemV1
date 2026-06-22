# path: ./tools/test_phase4a_prediction_system_ps_q16f_close_guard.py
# desc: Close guard for PS-Q16F scheduler enablement preflight / human decision checkpoint. Uses stubs only; no D-hot writes and no scheduler registration.

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

from _btcts_bootstrap import ensure_btcts_on_syspath

ensure_btcts_on_syspath()

import check_phase4a_prediction_system_ps_q16f_scheduler_enablement_preflight as preflight_mod  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[1]
EXPECTED_DIRTY = {
    "tools/check_phase4a_prediction_system_ps_q16f_scheduler_enablement_preflight.py",
    "docs/strategy/PREDICTION_SYSTEM_PS_Q16F_SCHEDULER_ENABLEMENT_PREFLIGHT_2026-06-22.md",
    "tools/test_phase4a_prediction_system_ps_q16f_scheduler_enablement_preflight_guard.py",
    "tools/test_phase4a_prediction_system_ps_q16f_close_guard.py",
}
REQUIRED_FILES = tuple(EXPECTED_DIRTY)
FOCUSED_GUARD = "tools/test_phase4a_prediction_system_ps_q16f_scheduler_enablement_preflight_guard.py"


def _dirty_paths() -> set[str]:
    proc = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True)
    out: set[str] = set()
    for line in proc.stdout.splitlines():
        if line.strip():
            out.add(line[3:].replace(chr(92), "/"))
    return out


def _fake_source_smoke(*, hot_latest_root_hint: str) -> dict[str, Any]:
    return {
        "ok": True,
        "adapter_state": "latest_prediction_source_ready",
        "actual_file_read_succeeded": True,
        "payload_decode_succeeded": True,
        "review_packet_ready": True,
        "blocker_count": 0,
        "warning_count": 2,
        "source_summary": {
            "prediction_run_id": "prediction_system.ps_q16f.close:BTC_JPY:bitFlyer:2026-06-22T11:36:23Z",
            "generated_at": "2026-06-22T11:36:23Z",
            "signal_strength_percent": 40,
            "signal_strength_band": "low_reference",
        },
    }


def _fake_status_panel(*, hot_latest_root_hint: str, allow_actual_read: bool, allow_guard_test_root: bool = False, **_: Any):
    class _Packet:
        def to_dict(self) -> dict[str, Any]:
            return {
                "panel_state": "producer_status_panel_loaded",
                "payload_decode_succeeded": True,
                "observed_age_sec": 10,
                "producer_runner_invoked": False,
                "scheduler_enabled_by_this_panel": False,
                "would_write_status_artifact": False,
                "would_write_latest_prediction_artifact": False,
                "warning_count": 1,
                "payload": {
                    "producer_state": "manual_refresh_exported_status_written",
                    "producer_enabled": False,
                    "scheduler_enabled": False,
                    "runtime_artifact_write_enabled": True,
                    "last_success_at": "2026-06-22T11:36:23Z",
                    "last_failure_at": None,
                    "last_success_generated_at": "2026-06-22T11:36:23Z",
                    "last_prediction_run_id": "prediction_system.ps_q16f.close:BTC_JPY:bitFlyer:2026-06-22T11:36:23Z",
                    "last_target_file_size_bytes": 123456,
                    "last_warning_count": 2,
                    "last_blocker_count": 0,
                    "consecutive_failure_count": 0,
                    "warnings": ["prediction_result_warnings_present:15"],
                    "blockers": [],
                    "disable_rollback_state": "manual_refresh_only_disable_by_not_running; scheduler_not_registered",
                },
            }
    return _Packet()


class _FixedDatetime:
    @classmethod
    def now(cls, tz: Any = None):
        from datetime import datetime, timezone
        value = datetime(2026, 6, 22, 11, 36, 33, tzinfo=timezone.utc)
        return value if tz is None else value.astimezone(tz)

    @classmethod
    def fromisoformat(cls, value: str):
        from datetime import datetime
        return datetime.fromisoformat(value)


def _with_stubs(*, dirty_status: list[str] | None = None):
    preflight_mod._git_status_short = lambda: list(dirty_status or [])
    preflight_mod.build_warroom_live_inference_smoke_payload = _fake_source_smoke
    preflight_mod.build_prediction_warroom_non_ui_scheduled_producer_status_panel_packet = _fake_status_panel
    preflight_mod.datetime = _FixedDatetime


def main() -> int:
    failures: list[str] = []
    for rel in REQUIRED_FILES:
        if not (REPO_ROOT / rel).exists():
            failures.append(f"missing required file: {rel}")
    smoke_text = (REPO_ROOT / "tools/check_phase4a_prediction_system_ps_q16f_scheduler_enablement_preflight.py").read_text(encoding="utf-8-sig")
    for marker in (
        "CHECKER = \"ps_q16f_scheduler_enablement_preflight\"",
        "human_decision_checkpoint_open",
        "ready_for_scheduler_enablement\": False",
        "scheduler_registration_performed\": False",
        "scheduled_loop_enabled\": False",
        "build_warroom_live_inference_smoke_payload",
        "build_prediction_warroom_non_ui_scheduled_producer_status_panel_packet",
    ):
        if marker not in smoke_text:
            failures.append(f"missing preflight marker: {marker}")
    for forbidden in (
        "Register-ScheduledTask",
        "Set-ScheduledTask",
        "Start-ScheduledTask",
        "build_prediction_warroom_bounded_manual_refresh_runner(",
        "build_prediction_warroom_latest_payload_actual_export_runner(",
        "send_order(",
        "create_order(",
        "append_decision(",
        "append_command(",
    ):
        if forbidden in smoke_text:
            failures.append(f"forbidden preflight source token: {forbidden}")

    original_status = preflight_mod._git_status_short
    original_source_smoke = preflight_mod.build_warroom_live_inference_smoke_payload
    original_status_panel = preflight_mod.build_prediction_warroom_non_ui_scheduled_producer_status_panel_packet
    original_datetime = preflight_mod.datetime
    try:
        _with_stubs(dirty_status=[" M dirty.py"])
        dirty = preflight_mod.build_report(require_clean_tree=True)
        if dirty.get("ok") is not False:
            failures.append("dirty preflight should fail")
        if "working_tree_not_clean" not in dirty.get("blocked_reasons", []):
            failures.append("dirty preflight blocker missing")
        if dirty.get("scheduler_registration_performed") is not False or dirty.get("scheduled_loop_enabled") is not False:
            failures.append("dirty preflight must not enable scheduler")

        _with_stubs(dirty_status=[])
        report = preflight_mod.build_report(require_clean_tree=True)
        if report.get("ok") is not True:
            failures.append(f"stubbed preflight should pass: {report}")
        if report.get("preflight_passed") is not True:
            failures.append("preflight_passed should be true")
        if report.get("human_decision_checkpoint_open") is not True:
            failures.append("human decision checkpoint should open without approval record")
        if report.get("human_approved_for_next_slice") is not False:
            failures.append("human approval should be false by default")
        if report.get("ready_for_scheduler_enablement") is not False:
            failures.append("PS-Q16F must never enable scheduler")
        if report.get("ready_for_scheduler_implementation_slice") is not False:
            failures.append("next implementation slice should require explicit human record")
        if report.get("scheduler_enablement_command_generated") is not False:
            failures.append("scheduler enablement command must not be generated")
        if report.get("scheduler_registration_performed") is not False or report.get("scheduled_loop_enabled") is not False:
            failures.append("scheduler flags must remain false")
        latest = report.get("latest_prediction", {})
        status = report.get("producer_status", {})
        if latest.get("prediction_run_id") != status.get("last_prediction_run_id"):
            failures.append("run_id should match between latest source and producer status")
        if latest.get("generated_at") != status.get("last_success_generated_at"):
            failures.append("generated_at should match between latest source and producer status")
        if not report.get("safety") or not all(report.get("safety", {}).values()):
            failures.append(f"safety false flags should all be true: {report.get('safety')}")

        approved = preflight_mod.build_report(require_clean_tree=True, human_approval_record_present=True)
        if approved.get("ok") is not True:
            failures.append("approved stubbed preflight should still pass")
        if approved.get("human_decision_checkpoint_open") is not False:
            failures.append("checkpoint_open should close when approval record is present")
        if approved.get("human_approved_for_next_slice") is not True:
            failures.append("approval record should mark next slice readiness")
        if approved.get("ready_for_scheduler_implementation_slice") is not True:
            failures.append("approval record should open implementation slice readiness")
        if approved.get("ready_for_scheduler_enablement") is not False:
            failures.append("approval record still must not enable scheduler")
    finally:
        preflight_mod._git_status_short = original_status
        preflight_mod.build_warroom_live_inference_smoke_payload = original_source_smoke
        preflight_mod.build_prediction_warroom_non_ui_scheduled_producer_status_panel_packet = original_status_panel
        preflight_mod.datetime = original_datetime

    dirty_paths = _dirty_paths()
    unexpected_dirty = dirty_paths - EXPECTED_DIRTY
    if unexpected_dirty:
        failures.append(f"unexpected dirty paths: {sorted(unexpected_dirty)}")
    result = {
        "ok": not failures,
        "guard": "ps_q16f_close_guard",
        "phase": "phase3_prediction_system_scheduler_enablement_preflight_human_checkpoint_closed",
        "focused_guards_to_run_before_commit": [FOCUSED_GUARD],
        "contract": {
            "ps_q16f_closed": not failures,
            "preflight_only": True,
            "human_decision_checkpoint": True,
            "scheduler_enabled": False,
            "scheduled_loop_enabled": False,
            "warroom_ui_trigger_enabled": False,
            "runtime_artifact_write_automation_enabled": False,
            "autotrade_trigger_candidate_deferred": True,
            "next_slice": "PS-Q16G disabled scheduler implementation design packet/runbook only after explicit human decision",
        },
        "dirty_paths": sorted(dirty_paths),
        "unexpected_dirty": sorted(unexpected_dirty),
        "failures": failures,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


def test_ps_q16f_close_guard() -> None:
    assert main() == 0


if __name__ == "__main__":
    raise SystemExit(main())
