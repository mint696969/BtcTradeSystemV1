# path: ./tools/test_phase4a_prediction_system_ps_q16k_once_run_execution_design_checkpoint_guard.py
# desc: Focused guard for PS-Q16K once-run execution design checkpoint.

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
EXPECTED_DIRTY = {
    "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_once_run_execution_design_checkpoint.py",
    "btcts_next/src/btcts/apps/operator_ui/tests/test_prediction_warroom_once_run_execution_design_checkpoint.py",
    "docs/strategy/PREDICTION_SYSTEM_PS_Q16K_ONCE_RUN_EXECUTION_DESIGN_CHECKPOINT_2026-06-22.md",
    "tools/test_phase4a_prediction_system_ps_q16k_close_guard.py",
    "tools/test_phase4a_prediction_system_ps_q16k_once_run_execution_design_checkpoint_guard.py",
}
FORBIDDEN_MODULE_TOKENS = (
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
    "manual_refresh_invoked_by_this_checkpoint: bool = True",
    "status_artifact_write_performed_by_this_checkpoint: bool = True",
    "lock_file_created_by_this_checkpoint: bool = True",
)
REQUIRED_DOC_MARKERS = (
    "PS-Q16K records a separate human-approved execution design checkpoint",
    "checkpoint_only=true",
    "read_only=true",
    "non_executing=true",
    "ready_for_future_guarded_once_run_execution_design_slice=true",
    "ready_for_execution_enablement=false",
    "execution_enabled=false",
    "future_slice_may_create_lock_only_after_separate_approval=false_in_ps_q16k",
    "manual_refresh_invoked=false",
    "lock_file_created=false",
    "PS-Q16L: guarded once-run execution plan packet",
)
FORBIDDEN_DOC_MARKERS = (
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
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def _dirty_paths() -> set[str]:
    proc = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True)
    return {line[3:].replace(chr(92), "/") for line in proc.stdout.splitlines() if line.strip()}


def _dry_run(*, lock_present: bool = False, age: int = 1, ok: bool = True) -> dict:
    return {
        "ok": ok,
        "dry_run_only": True,
        "decision": {
            "checker_version": DISABLED_ONCE_RUN_CHECKER_VERSION,
            "checker_state": "once_run_checker_disabled_ready_no_lock",
            "simulated_decision": "ready_no_lock_no_execution" if not lock_present and ok else "skip_existing_lock",
            "blocker_count": 0 if ok else 1,
            "ready_for_future_disabled_once_run_checker_implementation": ok,
            "preflight_latest_age_sec": age,
            "lock_present": lock_present,
            "status_ready": True,
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
        "status_observation": {"status_ready": True},
    }


def _assert_false_boundaries(packet: dict, failures: list[str]) -> None:
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
        "autotrade_trigger_allowed",
        "broker_private_api_allowed",
        "parameter_apply_allowed",
        "parameter_staging_write_allowed",
        "freshness_bypass_added",
        "force_ready_added",
    ):
        if packet.get(key) is not False:
            failures.append(f"{key} must stay false")


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
    for token in FORBIDDEN_MODULE_TOKENS:
        if token in module_text:
            failures.append(f"forbidden module token: {token}")
    if ONCE_RUN_EXECUTION_DESIGN_CHECKPOINT_VERSION != "prediction_warroom_once_run_execution_design_checkpoint.ps_q16k.v1":
        failures.append("version mismatch")
    ready = build_prediction_warroom_once_run_execution_design_checkpoint(
        ps_q16j_dry_run_report=_dry_run(),
        human_execution_design_record_present=True,
        human_execution_design_source="guard",
    ).to_dict()
    if ready.get("checkpoint_state") != "once_run_execution_design_checkpoint_ready_for_future_guarded_slice":
        failures.append(f"ready state mismatch: {ready}")
    if ready.get("ready_for_future_guarded_once_run_execution_design_slice") is not True:
        failures.append("future design readiness should be true")
    _assert_false_boundaries(ready, failures)
    locked = build_prediction_warroom_once_run_execution_design_checkpoint(
        ps_q16j_dry_run_report=_dry_run(lock_present=True),
        human_execution_design_record_present=True,
        human_execution_design_source="guard",
    ).to_dict()
    if "ps_q16j_lock_present_or_unconfirmed_absent" not in locked.get("blocked_reasons", []):
        failures.append("lock-present blocker missing")
    stale = build_prediction_warroom_once_run_execution_design_checkpoint(
        ps_q16j_dry_run_report=_dry_run(age=4000),
        human_execution_design_record_present=True,
        human_execution_design_source="guard",
    ).to_dict()
    if "ps_q16j_latest_age_stale" not in stale.get("blocked_reasons", []):
        failures.append("stale blocker missing")
    forbidden = build_prediction_warroom_once_run_execution_design_checkpoint(
        ps_q16j_dry_run_report=_dry_run(),
        human_execution_design_record_present=True,
        human_execution_design_source="guard",
        request_execute_manual_refresh=True,
        request_status_artifact_write=True,
        request_lock_file_create=True,
        request_scheduler_enable=True,
        request_approval_or_ledger_or_autotrade_or_broker=True,
    ).to_dict()
    if forbidden.get("ready_for_future_guarded_once_run_execution_design_slice") is not False:
        failures.append("forbidden requests must block future design readiness")
    _assert_false_boundaries(forbidden, failures)
    doc_text = _read(DOC) if DOC.exists() else ""
    for marker in REQUIRED_DOC_MARKERS:
        if marker not in doc_text:
            failures.append(f"missing doc marker: {marker}")
    for marker in FORBIDDEN_DOC_MARKERS:
        if marker in doc_text:
            failures.append(f"forbidden doc marker present: {marker}")
    dirty = _dirty_paths()
    unexpected = dirty - EXPECTED_DIRTY
    if unexpected:
        failures.append(f"unexpected dirty paths: {sorted(unexpected)}")
    result = {
        "ok": not failures,
        "guard": "ps_q16k_once_run_execution_design_checkpoint",
        "phase": "phase3_prediction_system_once_run_execution_design_checkpoint",
        "contract": {
            "checkpoint_only": True,
            "read_only": True,
            "non_executing": True,
            "ready_for_future_guarded_once_run_execution_design_slice": True,
            "execution_enabled": False,
            "manual_refresh_invoked": False,
            "status_artifact_write_performed": False,
            "lock_file_created": False,
            "scheduler_enabled": False,
            "autotrade_trigger_candidate_deferred": True,
            "expected_dirty_only": not unexpected,
        },
        "dirty_paths": sorted(dirty),
        "unexpected_dirty": sorted(unexpected),
        "failures": failures,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


def test_ps_q16k_once_run_execution_design_checkpoint_guard() -> None:
    assert main() == 0


if __name__ == "__main__":
    raise SystemExit(main())
