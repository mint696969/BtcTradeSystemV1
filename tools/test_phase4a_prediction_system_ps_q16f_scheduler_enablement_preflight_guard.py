# path: ./tools/test_phase4a_prediction_system_ps_q16f_scheduler_enablement_preflight_guard.py
# desc: Focused guard for PS-Q16F scheduler enablement preflight / human decision checkpoint. Uses stubs; does not write D-hot or register scheduler.

from __future__ import annotations

import ast
import json
import subprocess
from pathlib import Path
from typing import Any

from _btcts_bootstrap import ensure_btcts_on_syspath

ensure_btcts_on_syspath()

import check_phase4a_prediction_system_ps_q16f_scheduler_enablement_preflight as preflight_mod  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[1]
PREFLIGHT = REPO_ROOT / "tools/check_phase4a_prediction_system_ps_q16f_scheduler_enablement_preflight.py"
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q16F_SCHEDULER_ENABLEMENT_PREFLIGHT_2026-06-22.md"
EXPECTED_DIRTY = {
    "tools/check_phase4a_prediction_system_ps_q16f_scheduler_enablement_preflight.py",
    "docs/strategy/PREDICTION_SYSTEM_PS_Q16F_SCHEDULER_ENABLEMENT_PREFLIGHT_2026-06-22.md",
    "tools/test_phase4a_prediction_system_ps_q16f_close_guard.py",
    "tools/test_phase4a_prediction_system_ps_q16f_scheduler_enablement_preflight_guard.py",
}
REQUIRED_DOC_MARKERS = (
    "PS-Q16F checks whether the PS-Q16E manual refresh path has proven enough evidence",
    "preflight_only=true",
    "human_decision_checkpoint=true",
    "scheduler_enablement_command_generated=false",
    "scheduler_registration_performed=false",
    "python .\\tools\\check_phase4a_prediction_system_ps_q16f_scheduler_enablement_preflight.py",
    "ready_for_scheduler_enablement=false",
    "PS-Q16G: disabled scheduler implementation design packet or runbook only",
)
FORBIDDEN_SOURCE_TOKENS = (
    "schtasks",
    "TaskScheduler",
    "Register-ScheduledTask",
    "Set-ScheduledTask",
    "Start-ScheduledTask",
    "build_prediction_warroom_bounded_manual_refresh_runner(",
    "build_prediction_warroom_latest_payload_actual_export_runner(",
    "run_ps_q12d_export_and_smoke",
    "send_order(",
    "create_order(",
    "append_decision(",
    "append_command(",
    "write_text(",
    "write_bytes(",
    "replace(target)",
)
FORBIDDEN_DOC_MARKERS = (
    "scheduler_registration=true",
    "scheduled_loop=true",
    "WarRoom UI trigger=true",
    "automation_enablement=true",
    "latest_prediction_refresh=true",
    "parameter_apply=true",
    "parameter_staging_write=true",
    "approval_or_ledger_or_autotrade_or_broker=true",
    "freshness_bypass_added=true",
    "force_ready_added=true",
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def _guard_search_text(text: str) -> str:
    start = text.find("FORBIDDEN_SOURCE_TOKENS = (")
    end = text.find("FORBIDDEN_DOC_MARKERS = (", start)
    if start >= 0 and end > start:
        text = text[:start] + text[end:]
    return text


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
            "prediction_run_id": "prediction_system.ps_q16f.guard:BTC_JPY:bitFlyer:2026-06-22T11:36:23Z",
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
                    "last_prediction_run_id": "prediction_system.ps_q16f.guard:BTC_JPY:bitFlyer:2026-06-22T11:36:23Z",
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


def main() -> int:
    failures: list[str] = []
    for path in (PREFLIGHT, DOC):
        if not path.exists():
            failures.append(f"missing file: {path.relative_to(REPO_ROOT)}")
            continue
        text = _read(path)
        if path.suffix == ".py":
            try:
                ast.parse(text, filename=str(path))
            except SyntaxError as exc:
                failures.append(f"syntax failed: {path.relative_to(REPO_ROOT)}: {exc}")
    source_text = _read(PREFLIGHT) if PREFLIGHT.exists() else ""
    source_search = _guard_search_text(source_text)
    for token in FORBIDDEN_SOURCE_TOKENS:
        if token in source_search:
            failures.append(f"forbidden source token: {token}")
    if "build_warroom_live_inference_smoke_payload" not in source_text:
        failures.append("preflight must verify latest prediction source smoke")
    if "build_prediction_warroom_non_ui_scheduled_producer_status_panel_packet" not in source_text:
        failures.append("preflight must verify producer status panel visibility")
    if "ready_for_scheduler_enablement":
        pass
    doc_text = _read(DOC) if DOC.exists() else ""
    for marker in REQUIRED_DOC_MARKERS:
        if marker not in doc_text:
            failures.append(f"missing doc marker: {marker}")
    for marker in FORBIDDEN_DOC_MARKERS:
        if marker in doc_text:
            failures.append(f"forbidden doc marker present: {marker}")

    original_status = preflight_mod._git_status_short
    original_source_smoke = preflight_mod.build_warroom_live_inference_smoke_payload
    original_status_panel = preflight_mod.build_prediction_warroom_non_ui_scheduled_producer_status_panel_packet
    original_datetime = preflight_mod.datetime

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

    try:
        preflight_mod._git_status_short = lambda: [" M dirty.py"]
        dirty = preflight_mod.build_report(require_clean_tree=True)
        if dirty.get("ok") is not False or "working_tree_not_clean" not in dirty.get("blocked_reasons", []):
            failures.append("dirty tree must block PS-Q16F preflight")
        preflight_mod._git_status_short = lambda: []
        preflight_mod.build_warroom_live_inference_smoke_payload = _fake_source_smoke
        preflight_mod.build_prediction_warroom_non_ui_scheduled_producer_status_panel_packet = _fake_status_panel
        preflight_mod.datetime = _FixedDatetime
        report = preflight_mod.build_report(require_clean_tree=True)
        if report.get("ok") is not True:
            failures.append(f"stubbed preflight should pass: {report}")
        if report.get("human_decision_checkpoint_open") is not True:
            failures.append("passing preflight should open human decision checkpoint")
        if report.get("ready_for_scheduler_enablement") is not False:
            failures.append("PS-Q16F must not report ready_for_scheduler_enablement true")
        if report.get("scheduler_registration_performed") is not False:
            failures.append("PS-Q16F must not register scheduler")
        if report.get("scheduled_loop_enabled") is not False:
            failures.append("PS-Q16F must not enable scheduled loop")
        safety = report.get("safety", {})
        if not safety or not all(safety.values()):
            failures.append(f"safety false flags must all be true: {safety}")
        approved = preflight_mod.build_report(require_clean_tree=True, human_approval_record_present=True)
        if approved.get("ready_for_scheduler_implementation_slice") is not True:
            failures.append("human approval record should open next implementation slice readiness")
        if approved.get("ready_for_scheduler_enablement") is not False:
            failures.append("human approval still must not enable scheduler in PS-Q16F")
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
        "guard": "ps_q16f_scheduler_enablement_preflight",
        "phase": "phase3_prediction_system_scheduler_enablement_preflight_human_checkpoint",
        "contract": {
            "preflight_only": True,
            "human_decision_checkpoint": True,
            "uses_latest_prediction_source_smoke": "build_warroom_live_inference_smoke_payload" in source_text,
            "uses_producer_status_panel": "build_prediction_warroom_non_ui_scheduled_producer_status_panel_packet" in source_text,
            "scheduler_enabled": False,
            "scheduled_loop_enabled": False,
            "warroom_ui_trigger_enabled": False,
            "autotrade_trigger_candidate_deferred": True,
            "expected_dirty_only": not unexpected_dirty,
        },
        "dirty_paths": sorted(dirty_paths),
        "unexpected_dirty": sorted(unexpected_dirty),
        "failures": failures,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


def test_ps_q16f_scheduler_enablement_preflight_guard() -> None:
    assert main() == 0


if __name__ == "__main__":
    raise SystemExit(main())
