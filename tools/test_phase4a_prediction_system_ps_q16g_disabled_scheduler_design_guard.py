# path: ./tools/test_phase4a_prediction_system_ps_q16g_disabled_scheduler_design_guard.py
# desc: Focused guard for PS-Q16G disabled scheduler design packet/runbook-only slice.

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
EXPECTED_DIRTY = {
    "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_disabled_scheduler_design_packet.py",
    "btcts_next/src/btcts/apps/operator_ui/tests/test_prediction_warroom_disabled_scheduler_design_packet.py",
    "docs/strategy/PREDICTION_SYSTEM_PS_Q16G_DISABLED_SCHEDULER_DESIGN_2026-06-22.md",
    "tools/test_phase4a_prediction_system_ps_q16g_close_guard.py",
    "tools/test_phase4a_prediction_system_ps_q16g_disabled_scheduler_design_guard.py",
}
FORBIDDEN_SOURCE_TOKENS = (
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
    "scheduler_registration_performed: bool = True",
    "scheduled_loop_enabled: bool = True",
    "runtime_artifact_write_automation_enabled: bool = True",
    "latest_prediction_refresh_performed_by_this_design: bool = True",
    "status_artifact_write_performed_by_this_design: bool = True",
    "warroom_ui_trigger_enabled: bool = True",
    "autotrade_trigger_allowed: bool = True",
    "broker_private_api_allowed: bool = True",
    "parameter_apply_allowed: bool = True",
)
REQUIRED_DOC_MARKERS = (
    "PS-Q16G records a design-only packet",
    "design_only=true",
    "runbook_only=true",
    "human_decision_record_required=true",
    "ready_for_disabled_scheduler_wrapper_slice=true",
    "ready_for_scheduler_enablement=false",
    "scheduler_enablement_command_generated=false",
    "scheduler_registration_performed=false",
    "scheduled_loop_enabled=false",
    "PS-Q16H: disabled scheduler wrapper skeleton",
)
FORBIDDEN_DOC_MARKERS = (
    "scheduler_registration=true",
    "scheduled_loop=true",
    "runtime_artifact_write_automation=true",
    "latest_prediction_refresh=true",
    "status_artifact_write=true",
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


def _preflight() -> dict:
    return {
        "ok": True,
        "preflight_passed": True,
        "ready_for_scheduler_enablement": False,
        "scheduler_registration_performed": False,
        "scheduled_loop_enabled": False,
        "latest_prediction": {
            "prediction_run_id": "prediction_system.ps_q16g.guard:BTC_JPY:bitFlyer:2026-06-22T12:00:00Z",
            "generated_at": "2026-06-22T12:00:00Z",
            "age_sec": 60,
        },
        "producer_status": {
            "producer_state": "manual_refresh_exported_status_written",
            "last_success_at": "2026-06-22T12:00:00Z",
            "last_success_generated_at": "2026-06-22T12:00:00Z",
            "last_prediction_run_id": "prediction_system.ps_q16g.guard:BTC_JPY:bitFlyer:2026-06-22T12:00:00Z",
        },
        "warning_reasons": ["latest_prediction_source_has_warnings:6"],
    }


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
    source_text = _read(MODULE) if MODULE.exists() else ""
    for token in FORBIDDEN_SOURCE_TOKENS:
        if token in source_text:
            failures.append(f"forbidden source token: {token}")
    if DISABLED_SCHEDULER_DESIGN_PACKET_VERSION != "prediction_warroom_disabled_scheduler_design_packet.ps_q16g.v1":
        failures.append("version mismatch")
    ready = build_prediction_warroom_disabled_scheduler_design_packet(
        ps_q16f_preflight_report=_preflight(),
        human_decision_record_present=True,
        human_decision_source="operator_chat_next_go_2026_06_22",
    ).to_dict()
    if ready.get("design_state") != "disabled_scheduler_design_ready_for_future_wrapper_slice":
        failures.append(f"ready packet state mismatch: {ready}")
    if ready.get("ready_for_disabled_scheduler_wrapper_slice") is not True:
        failures.append("ready_for_disabled_scheduler_wrapper_slice should be true")
    for key in (
        "ready_for_scheduler_enablement",
        "scheduler_enablement_command_generated",
        "scheduler_registration_performed",
        "scheduled_loop_enabled",
        "runtime_artifact_write_automation_enabled",
        "latest_prediction_refresh_performed_by_this_design",
        "status_artifact_write_performed_by_this_design",
        "warroom_ui_trigger_enabled",
        "autotrade_trigger_allowed",
        "broker_private_api_allowed",
        "parameter_apply_allowed",
        "parameter_staging_write_allowed",
        "freshness_bypass_added",
        "force_ready_added",
    ):
        if ready.get(key) is not False:
            failures.append(f"{key} must stay false")
    blocked = build_prediction_warroom_disabled_scheduler_design_packet(ps_q16f_preflight_report=_preflight()).to_dict()
    if "human_decision_record_required_for_ps_q16g_design" not in blocked.get("blocked_reasons", []):
        failures.append("human decision blocker missing")
    forbidden = build_prediction_warroom_disabled_scheduler_design_packet(
        ps_q16f_preflight_report=_preflight(),
        human_decision_record_present=True,
        human_decision_source="operator_chat_next_go_2026_06_22",
        request_scheduler_enable=True,
        request_generate_enablement_command=True,
        request_approval_or_ledger_or_autotrade_or_broker=True,
    ).to_dict()
    if forbidden.get("ready_for_disabled_scheduler_wrapper_slice") is not False:
        failures.append("forbidden request should block readiness")
    doc_text = _read(DOC) if DOC.exists() else ""
    for marker in REQUIRED_DOC_MARKERS:
        if marker not in doc_text:
            failures.append(f"missing doc marker: {marker}")
    for marker in FORBIDDEN_DOC_MARKERS:
        if marker in doc_text:
            failures.append(f"forbidden doc marker present: {marker}")
    dirty = _dirty_paths()
    unexpected_dirty = dirty - EXPECTED_DIRTY
    if unexpected_dirty:
        failures.append(f"unexpected dirty paths: {sorted(unexpected_dirty)}")
    result = {
        "ok": not failures,
        "guard": "ps_q16g_disabled_scheduler_design",
        "phase": "phase3_prediction_system_disabled_scheduler_design_runbook_only",
        "contract": {
            "design_only": True,
            "runbook_only": True,
            "ready_for_disabled_scheduler_wrapper_slice": True,
            "scheduler_enabled": False,
            "scheduled_loop_enabled": False,
            "runtime_artifact_write_automation_enabled": False,
            "warroom_ui_trigger_enabled": False,
            "autotrade_trigger_candidate_deferred": True,
            "expected_dirty_only": not unexpected_dirty,
        },
        "dirty_paths": sorted(dirty),
        "unexpected_dirty": sorted(unexpected_dirty),
        "failures": failures,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


def test_ps_q16g_disabled_scheduler_design_guard() -> None:
    assert main() == 0


if __name__ == "__main__":
    raise SystemExit(main())
