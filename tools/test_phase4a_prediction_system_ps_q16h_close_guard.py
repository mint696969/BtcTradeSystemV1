# path: ./tools/test_phase4a_prediction_system_ps_q16h_close_guard.py
# desc: Close guard for PS-Q16H disabled scheduler wrapper skeleton.

from __future__ import annotations

import ast
import json
import subprocess
from pathlib import Path

from _btcts_bootstrap import ensure_btcts_on_syspath

ensure_btcts_on_syspath()

from btcts.apps.operator_ui.components.prediction_warroom_disabled_scheduler_design_packet import (  # noqa: E402
    DISABLED_SCHEDULER_DESIGN_PACKET_VERSION,
)
from btcts.apps.operator_ui.components.prediction_warroom_disabled_scheduler_wrapper_skeleton import (  # noqa: E402
    DISABLED_SCHEDULER_WRAPPER_SKELETON_VERSION,
    build_prediction_warroom_disabled_scheduler_wrapper_skeleton,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_disabled_scheduler_wrapper_skeleton.py"
UNIT = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/tests/test_prediction_warroom_disabled_scheduler_wrapper_skeleton.py"
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q16H_DISABLED_SCHEDULER_WRAPPER_SKELETON_2026-06-22.md"
FOCUSED_GUARD = "tools/test_phase4a_prediction_system_ps_q16h_disabled_scheduler_wrapper_skeleton_guard.py"
EXPECTED_DIRTY = {
    "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_disabled_scheduler_wrapper_skeleton.py",
    "btcts_next/src/btcts/apps/operator_ui/tests/test_prediction_warroom_disabled_scheduler_wrapper_skeleton.py",
    "docs/strategy/PREDICTION_SYSTEM_PS_Q16H_DISABLED_SCHEDULER_WRAPPER_SKELETON_2026-06-22.md",
    "tools/test_phase4a_prediction_system_ps_q16h_disabled_scheduler_wrapper_skeleton_guard.py",
    "tools/test_phase4a_prediction_system_ps_q16h_close_guard.py",
}


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def _dirty_paths() -> set[str]:
    proc = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True)
    return {line[3:].replace(chr(92), "/") for line in proc.stdout.splitlines() if line.strip()}


def _design(*, ready: bool = True) -> dict:
    return {
        "design_version": DISABLED_SCHEDULER_DESIGN_PACKET_VERSION,
        "ready_for_disabled_scheduler_wrapper_slice": ready,
        "ready_for_scheduler_enablement": False,
        "scheduler_registration_performed": False,
        "scheduled_loop_enabled": False,
        "scheduler_enablement_command_generated": False,
    }


def _assert_all_disabled(packet: dict, failures: list[str]) -> None:
    for key in (
        "ready_for_scheduler_enablement",
        "ready_for_runtime_artifact_write_automation",
        "wrapper_enabled",
        "scheduler_enabled",
        "os_scheduler_registration_performed",
        "scheduled_loop_enabled",
        "enablement_command_generated",
        "manual_refresh_invoked_by_this_skeleton",
        "latest_prediction_refresh_performed_by_this_skeleton",
        "status_artifact_write_performed_by_this_skeleton",
        "lock_file_created_by_this_skeleton",
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
    for key in ("skeleton_only", "read_only", "non_executing"):
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
        "DISABLED_SCHEDULER_WRAPPER_SKELETON_VERSION",
        "declare_no_os_scheduler_registration",
        "declare_no_automatic_loop",
        "declare_no_enablement_command_generation",
        "declare_single_run_lock_policy_without_creating_lock_file",
        "declare_manual_refresh_invocation_boundary_without_invoking_it",
        "ready_for_future_disabled_operator_shell_wrapper_implementation",
        "wrapper_enabled: bool = False",
        "scheduler_enabled: bool = False",
        "os_scheduler_registration_performed: bool = False",
        "scheduled_loop_enabled: bool = False",
        "manual_refresh_invoked_by_this_skeleton: bool = False",
        "status_artifact_write_performed_by_this_skeleton: bool = False",
        "lock_file_created_by_this_skeleton: bool = False",
    ):
        if marker not in module_text:
            failures.append(f"missing module marker: {marker}")
    if "sys.path.insert(0, str(Path(__file__).resolve().parents[4]))" not in unit_text:
        failures.append("unit test must bootstrap btcts_next/src for direct pytest path")
    for forbidden in (
        "write_text(",
        "write_bytes(",
        "open(",
        "build_prediction_warroom_bounded_manual_refresh_runner(",
        "build_prediction_warroom_latest_payload_actual_export_runner(",
        "send_order(",
        "create_order(",
        "append_decision(",
        "append_command(",
    ):
        if forbidden in module_text:
            failures.append(f"forbidden module token: {forbidden}")
    for marker in (
        "skeleton_only=true",
        "operator_shell_wrapper_skeleton_only=true",
        "future_entrypoint_default=disabled",
        "ready_for_future_disabled_operator_shell_wrapper_implementation=true",
        "ready_for_scheduler_enablement=false",
        "wrapper_enabled=false",
        "scheduler_enabled=false",
        "os_scheduler_registration_performed=false",
        "scheduled_loop_enabled=false",
        "enablement_command_generated=false",
        "lock_file_created_by_this_skeleton=false",
        "PS-Q16I: disabled operator-shell wrapper once-run checker",
    ):
        if marker not in doc_text:
            failures.append(f"missing doc marker: {marker}")
    if DISABLED_SCHEDULER_WRAPPER_SKELETON_VERSION != "prediction_warroom_disabled_scheduler_wrapper_skeleton.ps_q16h.v1":
        failures.append("version mismatch")

    ready = build_prediction_warroom_disabled_scheduler_wrapper_skeleton(
        ps_q16g_design_packet=_design(),
        human_wrapper_skeleton_record_present=True,
        human_wrapper_skeleton_source="operator_chat_next_go_2026_06_22",
    ).to_dict()
    if ready.get("skeleton_state") != "disabled_scheduler_wrapper_skeleton_ready_for_future_disabled_implementation":
        failures.append(f"ready skeleton state mismatch: {ready}")
    if ready.get("ready_for_future_disabled_operator_shell_wrapper_implementation") is not True:
        failures.append("ready future disabled wrapper implementation should be true")
    _assert_all_disabled(ready, failures)

    no_human = build_prediction_warroom_disabled_scheduler_wrapper_skeleton(ps_q16g_design_packet=_design()).to_dict()
    if "human_wrapper_skeleton_record_required_for_ps_q16h" not in no_human.get("blocked_reasons", []):
        failures.append("missing human wrapper skeleton record blocker")
    bad_design = build_prediction_warroom_disabled_scheduler_wrapper_skeleton(
        ps_q16g_design_packet=_design(ready=False),
        human_wrapper_skeleton_record_present=True,
        human_wrapper_skeleton_source="operator_chat_next_go_2026_06_22",
    ).to_dict()
    if "ps_q16g_design_not_ready_for_disabled_scheduler_wrapper_slice" not in bad_design.get("blocked_reasons", []):
        failures.append("missing unready design blocker")
    forbidden = build_prediction_warroom_disabled_scheduler_wrapper_skeleton(
        ps_q16g_design_packet=_design(),
        human_wrapper_skeleton_record_present=True,
        human_wrapper_skeleton_source="operator_chat_next_go_2026_06_22",
        request_scheduler_enable=True,
        request_os_scheduler_registration=True,
        request_scheduled_loop_enable=True,
        request_runtime_artifact_write_automation_enable=True,
        request_generate_enablement_command=True,
        request_execute_manual_refresh=True,
        request_status_artifact_write=True,
        request_warroom_ui_trigger=True,
        request_parameter_apply=True,
        request_parameter_staging_write=True,
        request_approval_or_ledger_or_autotrade_or_broker=True,
    ).to_dict()
    if forbidden.get("ready_for_future_disabled_operator_shell_wrapper_implementation") is not False:
        failures.append("forbidden requests must block future wrapper implementation readiness")
    _assert_all_disabled(forbidden, failures)

    dirty = _dirty_paths()
    unexpected = dirty - EXPECTED_DIRTY
    if unexpected:
        failures.append(f"unexpected dirty paths: {sorted(unexpected)}")
    result = {
        "ok": not failures,
        "guard": "ps_q16h_close_guard",
        "phase": "phase3_prediction_system_disabled_scheduler_wrapper_skeleton_closed",
        "focused_guards_to_run_before_commit": [FOCUSED_GUARD],
        "contract": {
            "ps_q16h_closed": not failures,
            "skeleton_only": True,
            "ready_for_future_disabled_operator_shell_wrapper_implementation": True,
            "wrapper_enabled": False,
            "scheduler_enabled": False,
            "os_scheduler_registration_performed": False,
            "scheduled_loop_enabled": False,
            "enablement_command_generated": False,
            "manual_refresh_invoked_by_this_skeleton": False,
            "status_artifact_write_performed_by_this_skeleton": False,
            "lock_file_created_by_this_skeleton": False,
            "autotrade_trigger_candidate_deferred": True,
            "next_slice": "PS-Q16I disabled operator-shell wrapper once-run checker; still no scheduling and no refresh execution unless separately approved",
        },
        "dirty_paths": sorted(dirty),
        "unexpected_dirty": sorted(unexpected),
        "failures": failures,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


def test_ps_q16h_close_guard() -> None:
    assert main() == 0


if __name__ == "__main__":
    raise SystemExit(main())
