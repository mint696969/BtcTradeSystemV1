# path: ./tools/test_phase4a_prediction_system_ps_q16h_disabled_scheduler_wrapper_skeleton_guard.py
# desc: Focused guard for PS-Q16H disabled scheduler wrapper skeleton.

from __future__ import annotations

import ast
import json
import subprocess
from pathlib import Path

from _btcts_bootstrap import ensure_btcts_on_syspath

ensure_btcts_on_syspath()

from btcts.apps.operator_ui.components.prediction_warroom_disabled_scheduler_wrapper_skeleton import (  # noqa: E402
    DISABLED_SCHEDULER_WRAPPER_SKELETON_VERSION,
    build_prediction_warroom_disabled_scheduler_wrapper_skeleton,
)
from btcts.apps.operator_ui.components.prediction_warroom_disabled_scheduler_design_packet import (  # noqa: E402
    DISABLED_SCHEDULER_DESIGN_PACKET_VERSION,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_disabled_scheduler_wrapper_skeleton.py"
UNIT = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/tests/test_prediction_warroom_disabled_scheduler_wrapper_skeleton.py"
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q16H_DISABLED_SCHEDULER_WRAPPER_SKELETON_2026-06-22.md"
EXPECTED_DIRTY = {
    "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_disabled_scheduler_wrapper_skeleton.py",
    "btcts_next/src/btcts/apps/operator_ui/tests/test_prediction_warroom_disabled_scheduler_wrapper_skeleton.py",
    "docs/strategy/PREDICTION_SYSTEM_PS_Q16H_DISABLED_SCHEDULER_WRAPPER_SKELETON_2026-06-22.md",
    "tools/test_phase4a_prediction_system_ps_q16h_close_guard.py",
    "tools/test_phase4a_prediction_system_ps_q16h_disabled_scheduler_wrapper_skeleton_guard.py",
}
FORBIDDEN_MODULE_TOKENS = (
    "subprocess",
    "write_text(",
    "write_bytes(",
    "replace(",
    "open(",
    "requests",
    "httpx",
    "ccxt",
    "pybitflyer",
    "websocket",
    "build_prediction_warroom_bounded_manual_refresh_runner(",
    "build_prediction_warroom_latest_payload_actual_export_runner(",
    "send_order(",
    "create_order(",
    "append_decision(",
    "append_command(",
    "wrapper_enabled: bool = True",
    "scheduler_enabled: bool = True",
    "os_scheduler_registration_performed: bool = True",
    "scheduled_loop_enabled: bool = True",
    "enablement_command_generated: bool = True",
    "manual_refresh_invoked_by_this_skeleton: bool = True",
    "latest_prediction_refresh_performed_by_this_skeleton: bool = True",
    "status_artifact_write_performed_by_this_skeleton: bool = True",
    "lock_file_created_by_this_skeleton: bool = True",
)
REQUIRED_DOC_MARKERS = (
    "PS-Q16H defines a disabled-by-default non-UI scheduler wrapper skeleton",
    "skeleton_only=true",
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
)
FORBIDDEN_DOC_MARKERS = (
    "scheduler_registration=true",
    "os_scheduler_registration=true",
    "scheduled_loop=true",
    "runtime_artifact_write_automation=true",
    "latest_prediction_refresh=true",
    "manual_refresh_invoked=true",
    "status_artifact_write=true",
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


def _design() -> dict:
    return {
        "design_version": DISABLED_SCHEDULER_DESIGN_PACKET_VERSION,
        "ready_for_disabled_scheduler_wrapper_slice": True,
        "ready_for_scheduler_enablement": False,
        "scheduler_registration_performed": False,
        "scheduled_loop_enabled": False,
        "scheduler_enablement_command_generated": False,
    }


def _assert_false_boundaries(packet: dict, failures: list[str]) -> None:
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
        failures.append("future disabled implementation readiness should be true")
    _assert_false_boundaries(ready, failures)
    blocked = build_prediction_warroom_disabled_scheduler_wrapper_skeleton(ps_q16g_design_packet=_design()).to_dict()
    if "human_wrapper_skeleton_record_required_for_ps_q16h" not in blocked.get("blocked_reasons", []):
        failures.append("human wrapper skeleton record blocker missing")
    forbidden = build_prediction_warroom_disabled_scheduler_wrapper_skeleton(
        ps_q16g_design_packet=_design(),
        human_wrapper_skeleton_record_present=True,
        human_wrapper_skeleton_source="operator_chat_next_go_2026_06_22",
        request_scheduler_enable=True,
        request_os_scheduler_registration=True,
        request_execute_manual_refresh=True,
        request_status_artifact_write=True,
        request_approval_or_ledger_or_autotrade_or_broker=True,
    ).to_dict()
    if forbidden.get("ready_for_future_disabled_operator_shell_wrapper_implementation") is not False:
        failures.append("forbidden requests must block skeleton readiness")
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
        "guard": "ps_q16h_disabled_scheduler_wrapper_skeleton",
        "phase": "phase3_prediction_system_disabled_scheduler_wrapper_skeleton",
        "contract": {
            "skeleton_only": True,
            "ready_for_future_disabled_operator_shell_wrapper_implementation": True,
            "wrapper_enabled": False,
            "scheduler_enabled": False,
            "os_scheduler_registration_performed": False,
            "scheduled_loop_enabled": False,
            "manual_refresh_invoked_by_this_skeleton": False,
            "status_artifact_write_performed_by_this_skeleton": False,
            "autotrade_trigger_candidate_deferred": True,
            "expected_dirty_only": not unexpected,
        },
        "dirty_paths": sorted(dirty),
        "unexpected_dirty": sorted(unexpected),
        "failures": failures,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


def test_ps_q16h_disabled_scheduler_wrapper_skeleton_guard() -> None:
    assert main() == 0


if __name__ == "__main__":
    raise SystemExit(main())
