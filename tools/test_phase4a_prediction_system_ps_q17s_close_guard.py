# path: ./tools/test_phase4a_prediction_system_ps_q17s_close_guard.py
# desc: Close guard for PS-Q17S WarRoom prediction widget read-only component skeleton implementation.

from __future__ import annotations

import ast
import json
import subprocess
from pathlib import Path

from check_phase4a_prediction_system_ps_q17s_warroom_prediction_widget_read_only_component_skeleton_implementation import CHECKER_VERSION, COMPONENT_SKELETON_IMPLEMENTATION_VERSION, WIDGET_FAMILY_ORDER, build_report, main

REPO_ROOT = Path(__file__).resolve().parents[1]
TOOL = REPO_ROOT / "tools/check_phase4a_prediction_system_ps_q17s_warroom_prediction_widget_read_only_component_skeleton_implementation.py"
UNIT = REPO_ROOT / "tools/test_phase4a_prediction_system_ps_q17s_warroom_prediction_widget_read_only_component_skeleton_implementation.py"
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q17S_WARROOM_PREDICTION_WIDGET_READ_ONLY_COMPONENT_SKELETON_IMPLEMENTATION_2026-06-22.md"
FOCUSED_GUARD = "tools/test_phase4a_prediction_system_ps_q17s_warroom_prediction_widget_read_only_component_skeleton_implementation_guard.py"
CLOSE_REL = "tools/test_phase4a_prediction_system_ps_q17s_close_guard.py"
COMPONENT_FILES = (
    "btcts_next/src/btcts/apps/operator_ui/components/prediction_widgets/__init__.py",
    "btcts_next/src/btcts/apps/operator_ui/components/prediction_widgets/_shared.py",
    "btcts_next/src/btcts/apps/operator_ui/components/prediction_widgets/latest_prediction_summary_widget.py",
    "btcts_next/src/btcts/apps/operator_ui/components/prediction_widgets/prediction_delta_widget.py",
    "btcts_next/src/btcts/apps/operator_ui/components/prediction_widgets/scenario_trace_widget.py",
    "btcts_next/src/btcts/apps/operator_ui/components/prediction_widgets/evidence_weighting_widget.py",
    "btcts_next/src/btcts/apps/operator_ui/components/prediction_widgets/invalidation_rewrite_widget.py",
    "btcts_next/src/btcts/apps/operator_ui/components/prediction_widgets/source_quality_freshness_widget.py",
    "btcts_next/src/btcts/apps/operator_ui/components/prediction_widgets/warning_blocker_widget.py",
    "btcts_next/src/btcts/apps/operator_ui/components/prediction_widgets/signal_strength_calibration_widget.py",
    "btcts_next/src/btcts/apps/operator_ui/components/prediction_widgets/parameter_candidate_comparison_widget.py",
    "btcts_next/src/btcts/apps/operator_ui/components/prediction_widgets/replay_outcome_calibration_widget.py",
    "btcts_next/src/btcts/apps/operator_ui/components/prediction_widgets/producer_freshness_status_widget.py",
    "btcts_next/src/btcts/apps/operator_ui/components/prediction_widgets/runtime_boundary_safety_widget.py",
)
EXPECTED_DIRTY = {
    *COMPONENT_FILES,
    "tools/check_phase4a_prediction_system_ps_q17s_warroom_prediction_widget_read_only_component_skeleton_implementation.py",
    "tools/test_phase4a_prediction_system_ps_q17s_warroom_prediction_widget_read_only_component_skeleton_implementation.py",
    "docs/strategy/PREDICTION_SYSTEM_PS_Q17S_WARROOM_PREDICTION_WIDGET_READ_ONLY_COMPONENT_SKELETON_IMPLEMENTATION_2026-06-22.md",
    "tools/test_phase4a_prediction_system_ps_q17s_warroom_prediction_widget_read_only_component_skeleton_implementation_guard.py",
    "tools/test_phase4a_prediction_system_ps_q17s_close_guard.py",
}


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def _dirty_paths() -> set[str]:
    proc = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True)
    paths: set[str] = set()
    for line in proc.stdout.splitlines():
        if not line.strip():
            continue
        item = line[3:].replace(chr(92), "/")
        if " -> " in item:
            item = item.split(" -> ", 1)[1]
        if item.endswith("/"):
            expanded = subprocess.run(
                ["git", "ls-files", "--others", "--exclude-standard", "--", item],
                cwd=REPO_ROOT,
                text=True,
                capture_output=True,
                check=True,
            )
            for expanded_line in expanded.stdout.splitlines():
                if expanded_line.strip():
                    paths.add(expanded_line.replace(chr(92), "/"))
        else:
            paths.add(item)
    return paths


def _assert_false_boundaries(report: dict, failures: list[str]) -> None:
    for key in ("read_only", "non_executing", "component_skeleton_implementation", "component_files_created", "diagnostic_only", "warroom_widget_design_premise"):
        if report.get(key) is not True:
            failures.append(f"{key} must be true")
    if report.get("contract_only") is not False:
        failures.append("contract_only must be false because component skeleton files are created")
    for key in (
        "component_import_allowed_by_warroom_page",
        "streamlit_render_allowed",
        "warroom_widget_rendering_allowed",
        "warroom_page_mutation_allowed",
        "warroom_page_import_patch_allowed",
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
    for relative in COMPONENT_FILES:
        path = REPO_ROOT / relative
        if not path.exists():
            failures.append(f"missing component file: {relative}")
            continue
        text = _read(path)
        try:
            ast.parse(text, filename=str(path))
        except SyntaxError as exc:
            failures.append(f"syntax failed: {relative}: {exc}")
        for forbidden in (
            "import streamlit",
            "st.",
            "Path(",
            "read_text(",
            "write_text(",
            "open(",
            "data_read",
            "data_slice",
            "send_order(",
            "create_order(",
            "append_decision(",
            "append_command(",
        ):
            if forbidden in text:
                failures.append(f"forbidden component token in {relative}: {forbidden}")
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
        'CHECKER = "ps_q17s_warroom_prediction_widget_read_only_component_skeleton_implementation"',
        'CHECKER_VERSION = "check_phase4a_prediction_system_ps_q17s_warroom_prediction_widget_read_only_component_skeleton_implementation.v1"',
        'COMPONENT_SKELETON_IMPLEMENTATION_VERSION = "warroom_prediction_widget_read_only_component_skeleton_implementation.v1"',
        "PS_Q17R_SOURCE_CHECKER_VERSION",
        "COMPONENT_PACKAGE",
        "component_files_created",
        "component_import_allowed_by_warroom_page",
        "streamlit_render_allowed",
        "actual_source_read_allowed",
        "PS-Q17T WarRoom prediction widget page mount/import contract",
    ):
        if marker not in tool_text:
            failures.append(f"missing tool marker: {marker}")
    for forbidden in (
        "from pathlib import Path",
        "read_text(",
        "write_text(",
        "write_bytes(",
        "open(",
        "mkdir(",
        "unlink(",
        "replace(",
        "data_read",
        "data_slice",
        "allow_actual_read=True",
        "build_report(hot_root=",
        "append_decision(",
        "append_command(",
        "send_order(",
        "create_order(",
    ):
        if forbidden in tool_text:
            failures.append(f"forbidden tool token: {forbidden}")
    if "test_ps_q17s_imports_and_calls_all_component_skeleton_modules_from_q17r_fixture" not in unit_text:
        failures.append("unit test must cover importing/calling all component skeleton modules")
    if "test_ps_q17s_component_packets_stay_render_disabled_and_read_only" not in unit_text:
        failures.append("unit test must cover render-disabled read-only packets")
    if CLOSE_REL not in focused_text:
        failures.append("focused guard expected dirty set must include close guard")

    if CHECKER_VERSION != "check_phase4a_prediction_system_ps_q17s_warroom_prediction_widget_read_only_component_skeleton_implementation.v1":
        failures.append("checker version mismatch")
    if COMPONENT_SKELETON_IMPLEMENTATION_VERSION != "warroom_prediction_widget_read_only_component_skeleton_implementation.v1":
        failures.append("implementation version mismatch")
    if len(WIDGET_FAMILY_ORDER) != 12:
        failures.append("widget family order should have 12 entries")

    report = build_report(use_observed_fixture=True)
    if report.get("ok") is not True:
        failures.append(f"observed fixture implementation should be ok: {report}")
    if report.get("stage") != "warroom_prediction_widget_read_only_component_skeleton_implementation_before_warroom_import_mount_and_rendering":
        failures.append("stage mismatch")
    if report.get("source_q17r_report_valid") is not True:
        failures.append("source Q17R report should validate")
    if report.get("component_module_count") != 12:
        failures.append("expected 12 component modules")
    if report.get("component_packet_count") != 12:
        failures.append("expected 12 component packets")
    if report.get("component_module_validation_failures"):
        failures.append(f"component module failures: {report.get('component_module_validation_failures')}")
    if report.get("streamlit_render_blockers") != list(WIDGET_FAMILY_ORDER):
        failures.append("all widget families must block streamlit rendering")
    if report.get("warroom_page_import_blockers") != list(WIDGET_FAMILY_ORDER):
        failures.append("all widget families must block warroom page import")
    if report.get("actual_source_read_blockers") != list(WIDGET_FAMILY_ORDER):
        failures.append("all widget families must block actual source reads")
    if report.get("recommended_first_validation") != "latest_prediction_summary_widget_component_skeleton_implementation_guard":
        failures.append("recommended first validation mismatch")

    packets = {packet.get("widget_family_id"): packet for packet in report.get("component_packets", [])}
    for widget_id in WIDGET_FAMILY_ORDER:
        packet = packets.get(widget_id, {})
        if not packet:
            failures.append(f"missing packet: {widget_id}")
            continue
        if packet.get("component_state") != "read_only_component_skeleton_render_disabled":
            failures.append(f"component state mismatch: {widget_id}")
        if packet.get("component_function_name") != f"render_{widget_id}":
            failures.append(f"function name mismatch: {widget_id}")
        if not str(packet.get("component_module_path") or "").endswith(f"prediction_widgets.{widget_id}"):
            failures.append(f"component module path mismatch: {widget_id}")
        for key in ("read_only", "non_executing", "component_skeleton_only", "fallback_component_only", "display_packet_only"):
            if packet.get(key) is not True:
                failures.append(f"packet true boundary missing: {widget_id}:{key}")
        for key in (
            "streamlit_render_allowed",
            "streamlit_render_invoked",
            "warroom_page_import_patch_allowed",
            "warroom_page_mutation_allowed",
            "warroom_mount_patch_allowed",
            "actual_source_read_allowed",
            "actual_source_read_attempted",
            "d_hot_actual_read_allowed",
            "refresh_invocation_allowed",
            "runtime_artifact_write_allowed",
            "status_artifact_write_allowed",
            "parameter_apply_allowed",
            "parameter_staging_write_allowed",
            "ledger_append_allowed",
            "autotrade_trigger_allowed",
            "broker_private_api_allowed",
        ):
            if packet.get(key) is not False:
                failures.append(f"packet false boundary not false: {widget_id}:{key}")
    _assert_false_boundaries(report, failures)

    blocked = build_report()
    if blocked.get("ok") is not False:
        failures.append("missing Q17R source should block")
    if blocked.get("component_packets"):
        failures.append("blocked report must not emit component packets")
    if main(["--use-observed-fixture"]) != 0:
        failures.append("CLI observed fixture should return 0")
    if main([]) != 1:
        failures.append("CLI without source should return 1")

    for marker in (
        "checker=check_phase4a_prediction_system_ps_q17s_warroom_prediction_widget_read_only_component_skeleton_implementation.v1",
        "component_skeleton_implementation_version=warroom_prediction_widget_read_only_component_skeleton_implementation.v1",
        "component_skeleton_implementation=true",
        "component_files_created=true",
        "contract_only=false",
        "component_module_count=12",
        "component_packet_count=12",
        "all component_state=read_only_component_skeleton_render_disabled",
        "no_warroom_page_import_patch",
        "no_streamlit_render",
        "no_actual_source_read",
        "PS-Q17T: WarRoom prediction widget page mount/import contract",
    ):
        if marker not in doc_text:
            failures.append(f"missing doc marker: {marker}")
    for forbidden in (
        "streamlit_render_allowed=true",
        "warroom_widget_rendering_allowed=true",
        "warroom_page_mutation_allowed=true",
        "warroom_page_import_patch_allowed=true",
        "warroom_mount_patch_allowed=true",
        "d_hot_actual_read_allowed=true",
        "actual_source_read_allowed=true",
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
        "guard": "ps_q17s_close_guard",
        "phase": "phase3_warroom_prediction_widget_component_skeleton_implementation_closed_before_warroom_page_import_mount_and_rendering",
        "focused_guards_to_run_before_commit": [FOCUSED_GUARD],
        "contract": {
            "ps_q17s_closed": not failures,
            "component_skeleton_implementation": True,
            "component_files_created": True,
            "warroom_page_import_patch_allowed": False,
            "warroom_page_mutation_allowed": False,
            "warroom_mount_patch_allowed": False,
            "streamlit_render_allowed": False,
            "actual_source_read_allowed": False,
            "refresh_invocation_allowed": False,
            "no_d_hot_actual_read": True,
            "no_runtime_write": True,
            "no_status_write": True,
            "no_parameter_apply": True,
            "no_parameter_staging_write": True,
            "no_ledger_append": True,
            "no_autotrade": True,
            "no_broker": True,
            "next_slice": "PS-Q17T WarRoom prediction widget page mount/import contract or actual-source preflight",
        },
        "dirty_paths": sorted(dirty),
        "unexpected_dirty": sorted(unexpected),
        "missing_dirty": sorted(missing_dirty),
        "failures": failures,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


def test_ps_q17s_close_guard() -> None:
    assert main_guard() == 0


if __name__ == "__main__":
    raise SystemExit(main_guard())
