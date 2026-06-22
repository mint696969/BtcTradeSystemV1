# path: ./tools/test_phase4a_prediction_system_ps_q16l_guarded_once_run_execution_plan_packet_guard.py
# desc: Focused guard for PS-Q16L guarded once-run execution plan packet.

from __future__ import annotations

import ast
import json
import subprocess
from pathlib import Path

from _btcts_bootstrap import ensure_btcts_on_syspath

ensure_btcts_on_syspath()

from btcts.apps.operator_ui.components.prediction_warroom_guarded_once_run_execution_plan_packet import (  # noqa: E402
    GUARDED_ONCE_RUN_EXECUTION_PLAN_PACKET_VERSION,
    build_prediction_warroom_guarded_once_run_execution_plan_packet,
)
from btcts.apps.operator_ui.components.prediction_warroom_once_run_execution_design_checkpoint import (  # noqa: E402
    ONCE_RUN_EXECUTION_DESIGN_CHECKPOINT_VERSION,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_guarded_once_run_execution_plan_packet.py"
UNIT = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/tests/test_prediction_warroom_guarded_once_run_execution_plan_packet.py"
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q16L_GUARDED_ONCE_RUN_EXECUTION_PLAN_PACKET_2026-06-22.md"
EXPECTED_DIRTY = {
    "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_guarded_once_run_execution_plan_packet.py",
    "btcts_next/src/btcts/apps/operator_ui/tests/test_prediction_warroom_guarded_once_run_execution_plan_packet.py",
    "docs/strategy/PREDICTION_SYSTEM_PS_Q16L_GUARDED_ONCE_RUN_EXECUTION_PLAN_PACKET_2026-06-22.md",
    "tools/test_phase4a_prediction_system_ps_q16l_close_guard.py",
    "tools/test_phase4a_prediction_system_ps_q16l_guarded_once_run_execution_plan_packet_guard.py",
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
    "execution_enabled: bool = True",
    "lock_file_created_by_this_plan: bool = True",
)
REQUIRED_DOC_MARKERS = (
    "PS-Q16L converts the PS-Q16K checkpoint into an ordered guarded once-run execution plan packet",
    "plan_only=true",
    "read_only=true",
    "non_executing=true",
    "ready_for_future_guarded_once_run_execution_implementation_slice=true",
    "ready_for_execution_enablement=false",
    "execution_enabled=false",
    "future_step_05_create_single_run_lock_in_future_slice_only",
    "manual_refresh_invoked=false",
    "lock_file_created=false",
    "PS-Q16M: guarded once-run implementation skeleton",
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


def _checkpoint(*, ready: bool = True) -> dict:
    return {
        "checkpoint_version": ONCE_RUN_EXECUTION_DESIGN_CHECKPOINT_VERSION,
        "ready_for_future_guarded_once_run_execution_design_slice": ready,
        "checkpoint_only": True,
        "read_only": True,
        "non_executing": True,
        "ready_for_execution_enablement": False,
        "execution_enabled": False,
        "manual_refresh_invoked_by_this_checkpoint": False,
        "latest_prediction_refresh_performed_by_this_checkpoint": False,
        "status_artifact_write_performed_by_this_checkpoint": False,
        "runtime_artifact_write_performed_by_this_checkpoint": False,
        "lock_file_created_by_this_checkpoint": False,
        "lock_file_deleted_by_this_checkpoint": False,
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
    }


def _assert_false_boundaries(packet: dict, failures: list[str]) -> None:
    for key in (
        "ready_for_execution_enablement",
        "execution_enabled",
        "manual_refresh_invoked_by_this_plan",
        "latest_prediction_refresh_performed_by_this_plan",
        "status_artifact_write_performed_by_this_plan",
        "runtime_artifact_write_performed_by_this_plan",
        "lock_file_created_by_this_plan",
        "lock_file_deleted_by_this_plan",
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
    if GUARDED_ONCE_RUN_EXECUTION_PLAN_PACKET_VERSION != "prediction_warroom_guarded_once_run_execution_plan_packet.ps_q16l.v1":
        failures.append("version mismatch")
    ready = build_prediction_warroom_guarded_once_run_execution_plan_packet(
        ps_q16k_checkpoint_packet=_checkpoint(),
        human_execution_plan_record_present=True,
        human_execution_plan_source="guard",
    ).to_dict()
    if ready.get("plan_state") != "guarded_once_run_execution_plan_ready_for_future_implementation_slice":
        failures.append(f"ready state mismatch: {ready}")
    if ready.get("ready_for_future_guarded_once_run_execution_implementation_slice") is not True:
        failures.append("future implementation readiness should be true")
    _assert_false_boundaries(ready, failures)
    no_human = build_prediction_warroom_guarded_once_run_execution_plan_packet(
        ps_q16k_checkpoint_packet=_checkpoint(),
    ).to_dict()
    if "human_execution_plan_record_required_for_ps_q16l" not in no_human.get("blocked_reasons", []):
        failures.append("missing human plan record blocker")
    unready = build_prediction_warroom_guarded_once_run_execution_plan_packet(
        ps_q16k_checkpoint_packet=_checkpoint(ready=False),
        human_execution_plan_record_present=True,
        human_execution_plan_source="guard",
    ).to_dict()
    if "ps_q16k_checkpoint_not_ready_for_guarded_execution_plan" not in unready.get("blocked_reasons", []):
        failures.append("unready checkpoint blocker missing")
    forbidden = build_prediction_warroom_guarded_once_run_execution_plan_packet(
        ps_q16k_checkpoint_packet=_checkpoint(),
        human_execution_plan_record_present=True,
        human_execution_plan_source="guard",
        request_execute_plan=True,
        request_execute_manual_refresh=True,
        request_status_artifact_write=True,
        request_lock_file_create=True,
        request_scheduler_enable=True,
        request_approval_or_ledger_or_autotrade_or_broker=True,
    ).to_dict()
    if forbidden.get("ready_for_future_guarded_once_run_execution_implementation_slice") is not False:
        failures.append("forbidden requests must block future implementation readiness")
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
        "guard": "ps_q16l_guarded_once_run_execution_plan_packet",
        "phase": "phase3_prediction_system_guarded_once_run_execution_plan_packet",
        "contract": {
            "plan_only": True,
            "read_only": True,
            "non_executing": True,
            "ready_for_future_guarded_once_run_execution_implementation_slice": True,
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


def test_ps_q16l_guarded_once_run_execution_plan_packet_guard() -> None:
    assert main() == 0


if __name__ == "__main__":
    raise SystemExit(main())
