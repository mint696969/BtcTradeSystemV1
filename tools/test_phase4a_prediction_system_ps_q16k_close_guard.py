# path: ./tools/test_phase4a_prediction_system_ps_q16k_close_guard.py
# desc: Close guard for PS-Q16K once-run execution design checkpoint.

from __future__ import annotations

import ast
import json
import subprocess
from pathlib import Path

from _btcts_bootstrap import ensure_btcts_on_syspath

ensure_btcts_on_syspath()

from btcts.apps.operator_ui.components.prediction_warroom_disabled_once_run_checker import DISABLED_ONCE_RUN_CHECKER_VERSION  # noqa: E402
from btcts.apps.operator_ui.components.prediction_warroom_once_run_execution_design_checkpoint import (  # noqa: E402
    ONCE_RUN_EXECUTION_DESIGN_CHECKPOINT_VERSION,
    build_prediction_warroom_once_run_execution_design_checkpoint,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_once_run_execution_design_checkpoint.py"
UNIT = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/tests/test_prediction_warroom_once_run_execution_design_checkpoint.py"
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q16K_ONCE_RUN_EXECUTION_DESIGN_CHECKPOINT_2026-06-22.md"
FOCUSED_GUARD = "tools/test_phase4a_prediction_system_ps_q16k_once_run_execution_design_checkpoint_guard.py"
EXPECTED_DIRTY = {
    "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_once_run_execution_design_checkpoint.py",
    "btcts_next/src/btcts/apps/operator_ui/tests/test_prediction_warroom_once_run_execution_design_checkpoint.py",
    "docs/strategy/PREDICTION_SYSTEM_PS_Q16K_ONCE_RUN_EXECUTION_DESIGN_CHECKPOINT_2026-06-22.md",
    "tools/test_phase4a_prediction_system_ps_q16k_once_run_execution_design_checkpoint_guard.py",
    "tools/test_phase4a_prediction_system_ps_q16k_close_guard.py",
}


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def _dirty_paths() -> set[str]:
    proc = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True)
    return {line[3:].replace(chr(92), "/") for line in proc.stdout.splitlines() if line.strip()}


def _dry_run(*, lock_present: bool = False, age: int = 1, ok: bool = True, status_ready: bool = True) -> dict:
    simulated = "ready_no_lock_no_execution" if ok and not lock_present and status_ready else "skip_existing_lock" if lock_present else "blocked"
    return {
        "ok": ok,
        "dry_run_only": True,
        "decision": {
            "checker_version": DISABLED_ONCE_RUN_CHECKER_VERSION,
            "checker_state": "once_run_checker_disabled_ready_no_lock" if simulated == "ready_no_lock_no_execution" else "once_run_checker_disabled_blocked",
            "simulated_decision": simulated,
            "blocker_count": 0 if ok else 1,
            "ready_for_future_disabled_once_run_checker_implementation": ok,
            "preflight_latest_age_sec": age,
            "lock_present": lock_present,
            "status_ready": status_ready,
            "manual_refresh_invoked_by_this_checker": False,
            "latest_prediction_refresh_performed_by_this_checker": False,
            "status_artifact_write_performed_by_this_checker": False,
            "lock_file_created_by_this_checker": False,
            "scheduler_enabled": False,
            "os_scheduler_registration_performed": False,
            "scheduled_loop_enabled": False,
            "warroom_ui_trigger_enabled": False,
            "autotrade_trigger_allowed": False,
            "broker_private_api_allowed": False,
            "parameter_apply_allowed": False,
            "parameter_staging_write_allowed": False,
            "freshness_bypass_added": False,
            "force_ready_added": False,
        },
        "lock_observation": {"lock_present": lock_present},
        "status_observation": {"status_ready": status_ready},
    }


def _assert_never_executed(packet: dict, failures: list[str]) -> None:
    for key in (
        "ready_for_execution_enablement",
        "execution_enabled",
        "manual_refresh_invoked_by_this_checkpoint",
        "latest_prediction_refresh_performed_by_this_checkpoint",
        "status_artifact_write_performed_by_this_checkpoint",
        "runtime_artifact_write_performed_by_this_checkpoint",
        "lock_file_created_by_this_checkpoint",
        "lock_file_deleted_by_this_checkpoint",
        "wrapper_enabled",
        "scheduler_enabled",
        "os_scheduler_registration_performed",
        "scheduled_loop_enabled",
        "enablement_command_generated",
        "warroom_ui_trigger_enabled",
        "ui_triggered_runner_execution",
        "approval_or_authorization_allowed",
        "ledger_append_allowed",
        "autotrade_trigger_allowed",
        "broker_private_api_allowed",
        "parameter_apply_allowed",
        "parameter_staging_write_allowed",
        "would_send_to_broker",
        "would_write_collector_state",
        "freshness_bypass_added",
        "force_ready_added",
    ):
        if packet.get(key) is not False:
            failures.append(f"{key} must remain false")
    for key in ("checkpoint_only", "read_only", "non_executing"):
        if packet.get(key) is not True:
            failures.append(f"{key} must be true")


def main() -> int:
    failures: list[str] = []
    for path in (MODULE, UNIT, DOC):
        if not path.exists():
            failures.append(f"missing file: {path.relative_to(REPO_ROOT)}")
            continue
        if path.suffix == ".py":
            try:
                ast.parse(_read(path), filename=str(path))
            except SyntaxError as exc:
                failures.append(f"syntax failed: {path.relative_to(REPO_ROOT)}: {exc}")
    module_text = _read(MODULE) if MODULE.exists() else ""
    unit_text = _read(UNIT) if UNIT.exists() else ""
    doc_text = _read(DOC) if DOC.exists() else ""
    for marker in (
        "ONCE_RUN_EXECUTION_DESIGN_CHECKPOINT_VERSION",
        "consume_ps_q16j_dry_run_report_only",
        "require_decision_ready_no_lock_no_execution",
        "require_lock_absent_in_dry_run_evidence",
        "require_status_ready_in_dry_run_evidence",
        "declare_future_lock_create_status_write_refresh_sequence_but_do_not_execute",
        "manual_refresh_invoked_by_this_checkpoint: bool = False",
        "latest_prediction_refresh_performed_by_this_checkpoint: bool = False",
        "status_artifact_write_performed_by_this_checkpoint: bool = False",
        "runtime_artifact_write_performed_by_this_checkpoint: bool = False",
        "lock_file_created_by_this_checkpoint: bool = False",
        "lock_file_deleted_by_this_checkpoint: bool = False",
        "ready_for_execution_enablement: bool = False",
        "execution_enabled: bool = False",
    ):
        if marker not in module_text:
            failures.append(f"missing module marker: {marker}")
    for forbidden in (
        "subprocess",
        "write_text(",
        "write_bytes(",
        "replace(",
        "open(",
        "mkdir(",
        "unlink(",
        "build_prediction_warroom_bounded_manual_refresh_runner(",
        "build_prediction_warroom_latest_payload_actual_export_runner(",
        "send_order(",
        "create_order(",
        "append_decision(",
        "append_command(",
    ):
        if forbidden in module_text:
            failures.append(f"forbidden module token: {forbidden}")
    if "sys.path.insert(0, str(Path(__file__).resolve().parents[4]))" not in unit_text:
        failures.append("unit test must bootstrap btcts_next/src for direct pytest path")
    for marker in (
        "checkpoint_only=true",
        "read_only=true",
        "non_executing=true",
        "ready_for_future_guarded_once_run_execution_design_slice=true",
        "ready_for_execution_enablement=false",
        "execution_enabled=false",
        "future_slice_may_create_lock_only_after_separate_approval=false_in_ps_q16k",
        "future_slice_may_invoke_manual_refresh_only_after_separate_approval=false_in_ps_q16k",
        "future_slice_may_write_status_only_after_separate_approval=false_in_ps_q16k",
        "manual_refresh_invoked=false",
        "latest_prediction_refresh=false",
        "status_artifact_write=false",
        "runtime_artifact_write=false",
        "lock_file_created=false",
        "lock_file_deleted=false",
        "PS-Q16L: guarded once-run execution plan packet",
    ):
        if marker not in doc_text:
            failures.append(f"missing doc marker: {marker}")
    for forbidden in (
        "execution_enabled=true",
        "scheduler_registration=true",
        "os_scheduler_registration=true",
        "scheduled_loop=true",
        "latest_prediction_refresh=true",
        "manual_refresh_invoked=true",
        "status_artifact_write=true",
        "runtime_artifact_write=true",
        "lock_file_created=true",
        "WarRoom UI trigger=true",
        "parameter_apply=true",
        "parameter_staging_write=true",
        "approval_or_ledger_or_autotrade_or_broker=true",
        "freshness_bypass_added=true",
        "force_ready_added=true",
    ):
        if forbidden in doc_text:
            failures.append(f"forbidden doc marker present: {forbidden}")
    if ONCE_RUN_EXECUTION_DESIGN_CHECKPOINT_VERSION != "prediction_warroom_once_run_execution_design_checkpoint.ps_q16k.v1":
        failures.append("version mismatch")

    ready = build_prediction_warroom_once_run_execution_design_checkpoint(
        ps_q16j_dry_run_report=_dry_run(),
        human_execution_design_record_present=True,
        human_execution_design_source="close_guard",
    ).to_dict()
    if ready.get("checkpoint_state") != "once_run_execution_design_checkpoint_ready_for_future_guarded_slice":
        failures.append(f"ready state mismatch: {ready}")
    if ready.get("ready_for_future_guarded_once_run_execution_design_slice") is not True:
        failures.append("ready_for_future_guarded_once_run_execution_design_slice must be true for clean dry-run evidence")
    _assert_never_executed(ready, failures)

    missing_human = build_prediction_warroom_once_run_execution_design_checkpoint(
        ps_q16j_dry_run_report=_dry_run(),
    ).to_dict()
    if "human_execution_design_record_required_for_ps_q16k" not in missing_human.get("blocked_reasons", []):
        failures.append("missing human execution design record blocker")
    _assert_never_executed(missing_human, failures)

    locked = build_prediction_warroom_once_run_execution_design_checkpoint(
        ps_q16j_dry_run_report=_dry_run(lock_present=True),
        human_execution_design_record_present=True,
        human_execution_design_source="close_guard",
    ).to_dict()
    if "ps_q16j_lock_present_or_unconfirmed_absent" not in locked.get("blocked_reasons", []):
        failures.append("lock-present blocker missing")
    stale = build_prediction_warroom_once_run_execution_design_checkpoint(
        ps_q16j_dry_run_report=_dry_run(age=4000),
        human_execution_design_record_present=True,
        human_execution_design_source="close_guard",
    ).to_dict()
    if "ps_q16j_latest_age_stale" not in stale.get("blocked_reasons", []):
        failures.append("stale dry-run blocker missing")
    status_bad = build_prediction_warroom_once_run_execution_design_checkpoint(
        ps_q16j_dry_run_report=_dry_run(status_ready=False),
        human_execution_design_record_present=True,
        human_execution_design_source="close_guard",
    ).to_dict()
    if "ps_q16j_status_not_ready" not in status_bad.get("blocked_reasons", []):
        failures.append("status-not-ready blocker missing")
    forbidden = build_prediction_warroom_once_run_execution_design_checkpoint(
        ps_q16j_dry_run_report=_dry_run(),
        human_execution_design_record_present=True,
        human_execution_design_source="close_guard",
        request_execute_manual_refresh=True,
        request_latest_prediction_refresh=True,
        request_status_artifact_write=True,
        request_lock_file_create=True,
        request_lock_file_delete=True,
        request_scheduler_enable=True,
        request_os_scheduler_registration=True,
        request_scheduled_loop_enable=True,
        request_generate_enablement_command=True,
        request_warroom_ui_trigger=True,
        request_parameter_apply=True,
        request_parameter_staging_write=True,
        request_approval_or_ledger_or_autotrade_or_broker=True,
    ).to_dict()
    if forbidden.get("ready_for_future_guarded_once_run_execution_design_slice") is not False:
        failures.append("forbidden requests must block design readiness")
    _assert_never_executed(forbidden, failures)

    dirty = _dirty_paths()
    unexpected = dirty - EXPECTED_DIRTY
    if unexpected:
        failures.append(f"unexpected dirty paths: {sorted(unexpected)}")
    result = {
        "ok": not failures,
        "guard": "ps_q16k_close_guard",
        "phase": "phase3_prediction_system_once_run_execution_design_checkpoint_closed",
        "focused_guards_to_run_before_commit": [FOCUSED_GUARD],
        "contract": {
            "ps_q16k_closed": not failures,
            "checkpoint_only": True,
            "read_only": True,
            "non_executing": True,
            "ready_for_future_guarded_once_run_execution_design_slice": True,
            "ready_for_execution_enablement": False,
            "execution_enabled": False,
            "manual_refresh_invoked": False,
            "latest_prediction_refresh_performed": False,
            "status_artifact_write_performed": False,
            "runtime_artifact_write_performed": False,
            "lock_file_created": False,
            "lock_file_deleted": False,
            "scheduler_enabled": False,
            "os_scheduler_registration_performed": False,
            "scheduled_loop_enabled": False,
            "autotrade_trigger_candidate_deferred": True,
            "next_slice": "PS-Q16L guarded once-run execution plan packet; design-only unless explicitly approved and still no execution/write/lock creation",
        },
        "dirty_paths": sorted(dirty),
        "unexpected_dirty": sorted(unexpected),
        "failures": failures,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


def test_ps_q16k_close_guard() -> None:
    assert main() == 0


if __name__ == "__main__":
    raise SystemExit(main())
