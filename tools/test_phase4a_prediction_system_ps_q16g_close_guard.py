# path: ./tools/test_phase4a_prediction_system_ps_q16g_close_guard.py
# desc: Close guard for PS-Q16G disabled scheduler design packet/runbook-only slice.

from __future__ import annotations

import ast
import json
import subprocess
from pathlib import Path

from _btcts_bootstrap import ensure_btcts_on_syspath

ensure_btcts_on_syspath()

from btcts.apps.operator_ui.components.prediction_warroom_disabled_scheduler_design_packet import (  # noqa: E402
    DISABLED_SCHEDULER_DESIGN_PACKET_VERSION,
    build_prediction_warroom_disabled_scheduler_design_packet,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_disabled_scheduler_design_packet.py"
UNIT = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/tests/test_prediction_warroom_disabled_scheduler_design_packet.py"
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q16G_DISABLED_SCHEDULER_DESIGN_2026-06-22.md"
FOCUSED_GUARD = "tools/test_phase4a_prediction_system_ps_q16g_disabled_scheduler_design_guard.py"
EXPECTED_DIRTY = {
    "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_disabled_scheduler_design_packet.py",
    "btcts_next/src/btcts/apps/operator_ui/tests/test_prediction_warroom_disabled_scheduler_design_packet.py",
    "docs/strategy/PREDICTION_SYSTEM_PS_Q16G_DISABLED_SCHEDULER_DESIGN_2026-06-22.md",
    "tools/test_phase4a_prediction_system_ps_q16g_disabled_scheduler_design_guard.py",
    "tools/test_phase4a_prediction_system_ps_q16g_close_guard.py",
}


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def _dirty_paths() -> set[str]:
    proc = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True)
    return {line[3:].replace(chr(92), "/") for line in proc.stdout.splitlines() if line.strip()}


def _preflight(*, ok: bool = True, age_sec: int = 60) -> dict:
    return {
        "ok": ok,
        "preflight_passed": ok,
        "ready_for_scheduler_enablement": False,
        "scheduler_registration_performed": False,
        "scheduled_loop_enabled": False,
        "latest_prediction": {
            "prediction_run_id": "prediction_system.ps_q16g.close:BTC_JPY:bitFlyer:2026-06-22T12:00:00Z",
            "generated_at": "2026-06-22T12:00:00Z",
            "age_sec": age_sec,
        },
        "producer_status": {
            "producer_state": "manual_refresh_exported_status_written",
            "last_success_at": "2026-06-22T12:00:00Z",
            "last_success_generated_at": "2026-06-22T12:00:00Z",
            "last_prediction_run_id": "prediction_system.ps_q16g.close:BTC_JPY:bitFlyer:2026-06-22T12:00:00Z",
        },
        "warning_reasons": ["latest_prediction_source_has_warnings:6"],
    }


def _assert_all_disabled(packet: dict, failures: list[str]) -> None:
    for key in (
        "ready_for_scheduler_enablement",
        "ready_for_runtime_artifact_write_automation",
        "scheduler_enablement_command_generated",
        "scheduler_registration_performed",
        "scheduled_loop_enabled",
        "runtime_artifact_write_automation_enabled",
        "latest_prediction_refresh_performed_by_this_design",
        "status_artifact_write_performed_by_this_design",
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
    for key in ("design_only", "read_only", "non_executing"):
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
        "DISABLED_SCHEDULER_DESIGN_PACKET_VERSION",
        "require_explicit_human_decision_record_for_design_slice",
        "declare_no_scheduler_enablement_in_ps_q16g",
        "declare_no_runtime_write_automation_in_ps_q16g",
        "declare_no_command_generation_in_ps_q16g",
        "ready_for_disabled_scheduler_wrapper_slice",
        "ready_for_scheduler_enablement: bool = False",
        "scheduler_registration_performed: bool = False",
        "scheduled_loop_enabled: bool = False",
        "latest_prediction_refresh_performed_by_this_design: bool = False",
        "status_artifact_write_performed_by_this_design: bool = False",
    ):
        if marker not in module_text:
            failures.append(f"missing module marker: {marker}")
    if "sys.path.insert(0, str(Path(__file__).resolve().parents[4]))" not in unit_text:
        failures.append("unit test must bootstrap btcts_next/src for direct pytest path")
    for forbidden in (
        "subprocess",
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
        "design_only=true",
        "runbook_only=true",
        "human_decision_record_required=true",
        "ready_for_scheduler_enablement=false",
        "scheduler_enablement_command_generated=false",
        "scheduler_registration_performed=false",
        "scheduled_loop_enabled=false",
        "PS-Q16H: disabled scheduler wrapper skeleton",
    ):
        if marker not in doc_text:
            failures.append(f"missing doc marker: {marker}")
    if DISABLED_SCHEDULER_DESIGN_PACKET_VERSION != "prediction_warroom_disabled_scheduler_design_packet.ps_q16g.v1":
        failures.append("version mismatch")

    ready = build_prediction_warroom_disabled_scheduler_design_packet(
        ps_q16f_preflight_report=_preflight(),
        human_decision_record_present=True,
        human_decision_source="operator_chat_next_go_2026_06_22",
    ).to_dict()
    if ready.get("design_state") != "disabled_scheduler_design_ready_for_future_wrapper_slice":
        failures.append(f"ready design state mismatch: {ready}")
    if ready.get("ready_for_disabled_scheduler_wrapper_slice") is not True:
        failures.append("ready_for_disabled_scheduler_wrapper_slice must be true only for design readiness")
    _assert_all_disabled(ready, failures)

    no_human = build_prediction_warroom_disabled_scheduler_design_packet(ps_q16f_preflight_report=_preflight()).to_dict()
    if "human_decision_record_required_for_ps_q16g_design" not in no_human.get("blocked_reasons", []):
        failures.append("missing human decision record blocker")
    failed_preflight = build_prediction_warroom_disabled_scheduler_design_packet(
        ps_q16f_preflight_report=_preflight(ok=False),
        human_decision_record_present=True,
        human_decision_source="operator_chat_next_go_2026_06_22",
    ).to_dict()
    if "ps_q16f_preflight_not_passed" not in failed_preflight.get("blocked_reasons", []):
        failures.append("missing failed preflight blocker")
    stale = build_prediction_warroom_disabled_scheduler_design_packet(
        ps_q16f_preflight_report=_preflight(age_sec=4000),
        human_decision_record_present=True,
        human_decision_source="operator_chat_next_go_2026_06_22",
    ).to_dict()
    if "latest_prediction_too_stale_for_disabled_scheduler_design" not in stale.get("blocked_reasons", []):
        failures.append("missing stale latest prediction blocker")
    forbidden = build_prediction_warroom_disabled_scheduler_design_packet(
        ps_q16f_preflight_report=_preflight(),
        human_decision_record_present=True,
        human_decision_source="operator_chat_next_go_2026_06_22",
        request_scheduler_enable=True,
        request_scheduled_loop_enable=True,
        request_runtime_artifact_write_automation_enable=True,
        request_generate_enablement_command=True,
        request_warroom_ui_trigger=True,
        request_parameter_apply=True,
        request_parameter_staging_write=True,
        request_approval_or_ledger_or_autotrade_or_broker=True,
    ).to_dict()
    if forbidden.get("ready_for_disabled_scheduler_wrapper_slice") is not False:
        failures.append("forbidden requests must block disabled wrapper design readiness")
    _assert_all_disabled(forbidden, failures)

    dirty = _dirty_paths()
    unexpected = dirty - EXPECTED_DIRTY
    if unexpected:
        failures.append(f"unexpected dirty paths: {sorted(unexpected)}")
    result = {
        "ok": not failures,
        "guard": "ps_q16g_close_guard",
        "phase": "phase3_prediction_system_disabled_scheduler_design_runbook_only_closed",
        "focused_guards_to_run_before_commit": [FOCUSED_GUARD],
        "contract": {
            "ps_q16g_closed": not failures,
            "design_only": True,
            "runbook_only": True,
            "scheduler_enabled": False,
            "scheduled_loop_enabled": False,
            "runtime_artifact_write_automation_enabled": False,
            "latest_prediction_refresh_performed_by_this_design": False,
            "status_artifact_write_performed_by_this_design": False,
            "warroom_ui_trigger_enabled": False,
            "autotrade_trigger_candidate_deferred": True,
            "next_slice": "PS-Q16H disabled scheduler wrapper skeleton, still disabled by default and no OS registration",
        },
        "dirty_paths": sorted(dirty),
        "unexpected_dirty": sorted(unexpected),
        "failures": failures,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


def test_ps_q16g_close_guard() -> None:
    assert main() == 0


if __name__ == "__main__":
    raise SystemExit(main())
