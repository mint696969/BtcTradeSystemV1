# path: ./tools/test_phase4a_prediction_system_ps_q17y_close_guard.py
# desc: Close guard for PS-Q17Y WarRoom prediction widget actual-source preflight.

from __future__ import annotations

import ast
import json
import subprocess
from pathlib import Path

from check_phase4a_prediction_system_ps_q17y_warroom_prediction_widget_actual_source_preflight import ACTUAL_SOURCE_PREFLIGHT_VERSION, CHECKER_VERSION, WIDGET_FAMILY_ORDER, build_report, main

REPO_ROOT = Path(__file__).resolve().parents[1]
TOOL = REPO_ROOT / "tools/check_phase4a_prediction_system_ps_q17y_warroom_prediction_widget_actual_source_preflight.py"
UNIT = REPO_ROOT / "tools/test_phase4a_prediction_system_ps_q17y_warroom_prediction_widget_actual_source_preflight.py"
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q17Y_WARROOM_PREDICTION_WIDGET_ACTUAL_SOURCE_PREFLIGHT_2026-06-22.md"
FOCUSED_GUARD = "tools/test_phase4a_prediction_system_ps_q17y_warroom_prediction_widget_actual_source_preflight_guard.py"
CLOSE_REL = "tools/test_phase4a_prediction_system_ps_q17y_close_guard.py"
EXPECTED_DIRTY = {
    "tools/check_phase4a_prediction_system_ps_q17y_warroom_prediction_widget_actual_source_preflight.py",
    "tools/test_phase4a_prediction_system_ps_q17y_warroom_prediction_widget_actual_source_preflight.py",
    "docs/strategy/PREDICTION_SYSTEM_PS_Q17Y_WARROOM_PREDICTION_WIDGET_ACTUAL_SOURCE_PREFLIGHT_2026-06-22.md",
    "tools/test_phase4a_prediction_system_ps_q17y_warroom_prediction_widget_actual_source_preflight_guard.py",
    "tools/test_phase4a_prediction_system_ps_q17y_close_guard.py",
}


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def _dirty_paths() -> set[str]:
    proc = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True)
    return {line[3:].replace(chr(92), "/") for line in proc.stdout.splitlines() if line.strip()}


def _assert_boundary(report: dict, failures: list[str]) -> None:
    for key in ("read_only", "non_executing", "actual_source_preflight_only"):
        if report.get(key) is not True:
            failures.append(f"{key} must be true")
    if report.get("source_binding_contract_ready") is not True:
        failures.append("source_binding_contract_ready must be true")
    for key in (
        "source_artifact_resolution_allowed",
        "actual_source_bound",
        "source_artifact_resolved",
        "freshness_checked_against_d_hot",
        "readiness_row_visible_in_warroom",
        "real_prediction_widget_rendering_allowed",
        "warroom_widget_rendering_allowed",
        "warroom_page_mutation_allowed",
        "warroom_mount_patch_allowed",
        "actual_source_read_allowed",
        "d_hot_actual_read_allowed",
        "warroom_ui_trigger_enabled",
        "refresh_invocation_allowed",
        "scheduler_enabled",
        "runtime_artifact_write_allowed",
        "status_artifact_write_allowed",
        "confidence_increase_allowed",
        "signal_reliability_claim_allowed",
        "parameter_candidate_reliability_claim_allowed",
        "parameter_tuning_allowed",
        "parameter_apply_allowed",
        "parameter_staging_write_allowed",
        "approval_or_authorization_allowed",
        "ledger_append_allowed",
        "autotrade_trigger_allowed",
        "broker_private_api_allowed",
        "would_write_runtime_artifact",
        "would_write_collector_state",
        "would_send_to_broker",
    ):
        if report.get(key) is not False:
            failures.append(f"{key} must stay false")


def main_guard() -> int:
    failures: list[str] = []
    for path in (TOOL, UNIT, DOC, REPO_ROOT / FOCUSED_GUARD):
        if not path.exists():
            failures.append(f"missing file: {path.relative_to(REPO_ROOT)}")
            continue
        if path.suffix == ".py":
            try:
                ast.parse(_read(path), filename=str(path))
            except SyntaxError as exc:
                failures.append(f"syntax failed: {path.relative_to(REPO_ROOT)}: {exc}")

    tool_text = _read(TOOL) if TOOL.exists() else ""
    unit_text = _read(UNIT) if UNIT.exists() else ""
    focused_text = _read(REPO_ROOT / FOCUSED_GUARD) if (REPO_ROOT / FOCUSED_GUARD).exists() else ""
    doc_text = _read(DOC) if DOC.exists() else ""
    for marker in (
        'CHECKER = "ps_q17y_warroom_prediction_widget_actual_source_preflight"',
        'CHECKER_VERSION = "check_phase4a_prediction_system_ps_q17y_warroom_prediction_widget_actual_source_preflight.v1"',
        'ACTUAL_SOURCE_PREFLIGHT_VERSION = "warroom_prediction_widget_actual_source_preflight.v1"',
        "build_ps_q17p_report",
        "build_ps_q17x_report",
        "source_binding_contract_ready",
        "actual_source_binding_ready",
        "actual_source_bound",
        "source_artifact_resolved",
        "freshness_checked_against_d_hot",
        "source_artifact_resolution_allowed",
        "readiness_row_visible_in_warroom",
        "PS-Q17Z WarRoom prediction widget source readiness row mount",
    ):
        if marker not in tool_text:
            failures.append(f"missing tool marker: {marker}")
    for forbidden in (
        "from pathlib import Path",
        "open(",
        "read_text(",
        "write_text(",
        "data_read",
        "data_slice",
        "allow_actual_read=True",
        "actual_source_read_allowed=True",
        "d_hot_actual_read_allowed=True",
        "append_decision(",
        "append_command(",
        "send_order(",
        "create_order(",
    ):
        if forbidden in tool_text:
            failures.append(f"forbidden tool token: {forbidden}")
    if "test_ps_q17y_builds_actual_source_preflight_rows_from_q17p_and_q17x_fixtures" not in unit_text:
        failures.append("unit test must cover Q17P/Q17X fixtures")
    if "test_ps_q17y_rows_keep_actual_read_binding_render_refresh_and_writes_disabled" not in unit_text:
        failures.append("unit test must cover disabled read/binding/render/refresh/write boundaries")
    if CLOSE_REL not in focused_text:
        failures.append("focused guard expected dirty set must include close guard")

    if CHECKER_VERSION != "check_phase4a_prediction_system_ps_q17y_warroom_prediction_widget_actual_source_preflight.v1":
        failures.append("checker version mismatch")
    if ACTUAL_SOURCE_PREFLIGHT_VERSION != "warroom_prediction_widget_actual_source_preflight.v1":
        failures.append("preflight version mismatch")
    report = build_report(use_observed_fixture=True)
    if report.get("ok") is not True:
        failures.append(f"observed fixture preflight should be ok: {report}")
    if report.get("use_observed_fixture") is not True:
        failures.append("observed fixture flag should be true")
    if report.get("source_q17p_report_valid") is not True:
        failures.append("source Q17P report should validate")
    if report.get("source_q17x_report_valid") is not True:
        failures.append("source Q17X report should validate")
    if report.get("preflight_row_count") != 12:
        failures.append("expected 12 preflight rows")
    if report.get("unique_source_packet_count") != 9:
        failures.append("expected 9 unique source packets")
    if [row.get("widget_family_id") for row in report.get("preflight_rows", [])] != list(WIDGET_FAMILY_ORDER):
        failures.append("preflight row order mismatch")
    if sorted(report.get("unique_source_packet_ids", [])) != sorted({row.get("source_packet_id") for row in report.get("preflight_rows", [])}):
        failures.append("unique source packet ids mismatch")
    for row in report.get("preflight_rows", []):
        widget_id = row.get("widget_family_id")
        if row.get("actual_source_binding_ready") is not True:
            failures.append(f"binding should be ready: {widget_id}")
        for field in ("source_packet_id", "freshness_field", "source_artifact_ref_field", "release_gate_field", "source_checker_version"):
            if not row.get(field):
                failures.append(f"row field missing: {widget_id}:{field}")
        for key in (
            "actual_source_bound",
            "source_artifact_resolved",
            "freshness_checked_against_d_hot",
            "readiness_row_visible_in_warroom",
            "real_widget_render_ready",
            "render_allowed",
            "actual_source_read_allowed",
            "d_hot_actual_read_allowed",
            "refresh_invocation_allowed",
            "runtime_artifact_write_allowed",
            "status_artifact_write_allowed",
            "confidence_increase_allowed",
            "parameter_apply_allowed",
            "parameter_staging_write_allowed",
            "ledger_append_allowed",
            "autotrade_trigger_allowed",
            "broker_private_api_allowed",
        ):
            if row.get(key) is not False:
                failures.append(f"row {key} must stay false: {widget_id}")
    _assert_boundary(report, failures)

    blocked = build_report()
    if blocked.get("ok") is not False:
        failures.append("missing source should block")
    if blocked.get("preflight_row_count") != 0:
        failures.append("blocked report should have zero preflight rows")
    if main(["--use-observed-fixture"]) != 0:
        failures.append("CLI observed fixture should return 0")
    if main([]) != 1:
        failures.append("CLI without source should return 1")

    for marker in (
        "checker=check_phase4a_prediction_system_ps_q17y_warroom_prediction_widget_actual_source_preflight.v1",
        "actual_source_preflight_version=warroom_prediction_widget_actual_source_preflight.v1",
        "source_q17p_checker=check_phase4a_prediction_system_ps_q17p_warroom_prediction_widget_integration_design_checkpoint.v1",
        "source_q17x_checker=check_phase4a_prediction_system_ps_q17x_warroom_prediction_widget_disabled_section_page_body_review_mount.v1",
        "preflight_row_count=12",
        "source_binding_contract_ready=true",
        "actual_source_preflight_only=true",
        "source_artifact_resolution_allowed=false",
        "actual_source_bound=false",
        "source_artifact_resolved=false",
        "freshness_checked_against_d_hot=false",
        "readiness_row_visible_in_warroom=false",
        "real_prediction_widget_rendering_allowed=false",
        "actual_source_read_allowed=false",
        "d_hot_actual_read_allowed=false",
        "no_actual_source_read",
        "no_d_hot_actual_read",
        "PS-Q17Z: WarRoom prediction widget source readiness row mount",
    ):
        if marker not in doc_text:
            failures.append(f"missing doc marker: {marker}")
    for forbidden in (
        "actual_source_read_allowed=true",
        "d_hot_actual_read_allowed=true",
        "source_artifact_resolution_allowed=true",
        "actual_source_bound=true",
        "source_artifact_resolved=true",
        "freshness_checked_against_d_hot=true",
        "real_prediction_widget_rendering_allowed=true",
        "warroom_widget_rendering_allowed=true",
        "warroom_page_mutation_allowed=true",
        "confidence_increase_allowed=true",
        "parameter_apply_allowed=true",
        "parameter_staging_write_allowed=true",
        "ledger_append_allowed=true",
        "autotrade_trigger_allowed=true",
        "broker_private_api_allowed=true",
        "warroom_ui_trigger_enabled=true",
        "refresh_invocation_allowed=true",
        "scheduler_enabled=true",
    ):
        if forbidden in doc_text:
            failures.append(f"forbidden doc marker present: {forbidden}")

    dirty = _dirty_paths()
    unexpected = dirty - EXPECTED_DIRTY
    missing_dirty = EXPECTED_DIRTY - dirty
    if unexpected:
        failures.append(f"unexpected dirty paths: {sorted(unexpected)}")
    if missing_dirty:
        failures.append(f"missing expected dirty paths: {sorted(missing_dirty)}")
    result = {
        "ok": not failures,
        "guard": "ps_q17y_close_guard",
        "phase": "phase3_warroom_prediction_widget_actual_source_preflight_closed_before_source_resolution_d_hot_read_and_real_widget_rendering",
        "focused_guards_to_run_before_commit": [FOCUSED_GUARD],
        "contract": {
            "ps_q17y_closed": not failures,
            "actual_source_preflight_only": True,
            "source_binding_contract_ready": True,
            "preflight_row_count": int(report.get("preflight_row_count") or 0),
            "unique_source_packet_count": int(report.get("unique_source_packet_count") or 0),
            "source_artifact_resolution_allowed": False,
            "actual_source_bound": False,
            "source_artifact_resolved": False,
            "freshness_checked_against_d_hot": False,
            "readiness_row_visible_in_warroom": False,
            "real_prediction_widget_rendering_allowed": False,
            "actual_source_read_allowed": False,
            "d_hot_actual_read_allowed": False,
            "refresh_invocation_allowed": False,
            "no_runtime_write": True,
            "no_status_write": True,
            "no_parameter_apply": True,
            "no_parameter_staging_write": True,
            "no_ledger_append": True,
            "no_autotrade": True,
            "no_broker": True,
            "next_slice": "PS-Q17Z WarRoom prediction widget source readiness row mount or actual-source read probe",
        },
        "dirty_paths": sorted(dirty),
        "unexpected_dirty": sorted(unexpected),
        "missing_dirty": sorted(missing_dirty),
        "failures": failures,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


def test_ps_q17y_close_guard() -> None:
    assert main_guard() == 0


if __name__ == "__main__":
    raise SystemExit(main_guard())
