# path: ./tools/test_phase4a_prediction_system_ps_q18aa_latest_prediction_summary_widget_warroom_mount_preflight_gate_guard.py
# desc: Focused guard for PS-Q18AA latest_prediction_summary_widget WarRoom mount preflight gate.

from __future__ import annotations

import ast
import json
import subprocess
from pathlib import Path

from check_phase4a_prediction_system_ps_q18q_latest_prediction_summary_widget_one_source_resolver_dry_run_path_shape_preflight import EXPECTED_PATH_SHAPE_PREVIEW
from check_phase4a_prediction_system_ps_q18aa_latest_prediction_summary_widget_warroom_mount_preflight_gate import CHECKER_VERSION, build_report, main
from btcts.apps.operator_ui.prediction_warroom.contracts.latest_prediction_summary_widget_q18aa_mount_preflight_gate import FALSE_BOUNDARIES, LATEST_PREDICTION_SUMMARY_WIDGET_Q18AA_MOUNT_PREFLIGHT_GATE_ACK, LATEST_PREDICTION_SUMMARY_WIDGET_Q18AA_MOUNT_PREFLIGHT_GATE_KIND, LATEST_PREDICTION_SUMMARY_WIDGET_Q18AA_MOUNT_PREFLIGHT_GATE_STATE, TRUE_BOUNDARIES

REPO_ROOT = Path(__file__).resolve().parents[1]
CONTRACT = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/contracts/latest_prediction_summary_widget_q18aa_mount_preflight_gate.py"
PRESENTER = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/presenters/latest_prediction_summary_widget_q18aa_mount_preflight_gate_rows.py"
TOOL = REPO_ROOT / "tools/check_phase4a_prediction_system_ps_q18aa_latest_prediction_summary_widget_warroom_mount_preflight_gate.py"
UNIT = REPO_ROOT / "tools/test_phase4a_prediction_system_ps_q18aa_latest_prediction_summary_widget_warroom_mount_preflight_gate.py"
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q18AA_LATEST_PREDICTION_SUMMARY_WIDGET_WARROOM_MOUNT_PREFLIGHT_GATE_2026-06-24.md"
EXPECTED_DIRTY = {
    "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/contracts/latest_prediction_summary_widget_q18aa_mount_preflight_gate.py",
    "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/presenters/latest_prediction_summary_widget_q18aa_mount_preflight_gate_rows.py",
    "docs/strategy/PREDICTION_SYSTEM_PS_Q18AA_LATEST_PREDICTION_SUMMARY_WIDGET_WARROOM_MOUNT_PREFLIGHT_GATE_2026-06-24.md",
    "tools/check_phase4a_prediction_system_ps_q18aa_latest_prediction_summary_widget_warroom_mount_preflight_gate.py",
    "tools/test_phase4a_prediction_system_ps_q18aa_close_guard.py",
    "tools/test_phase4a_prediction_system_ps_q18aa_latest_prediction_summary_widget_warroom_mount_preflight_gate.py",
    "tools/test_phase4a_prediction_system_ps_q18aa_latest_prediction_summary_widget_warroom_mount_preflight_gate_guard.py",
}


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def _is_noise_path(rel: str) -> bool:
    return "/__pycache__/" in rel or rel.endswith(".pyc")


def _dirty_paths() -> set[str]:
    proc = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True)
    paths: set[str] = set()
    for line in proc.stdout.splitlines():
        if not line.strip():
            continue
        rel = line[3:].replace(chr(92), "/")
        absolute = REPO_ROOT / rel
        if rel.endswith("/") and absolute.exists():
            for child in absolute.rglob("*"):
                if child.is_file():
                    child_rel = child.relative_to(REPO_ROOT).as_posix()
                    if not _is_noise_path(child_rel):
                        paths.add(child_rel)
        elif not _is_noise_path(rel):
            paths.add(rel)
    return paths


def main_guard() -> int:
    failures: list[str] = []
    for path in (CONTRACT, PRESENTER, TOOL, UNIT, DOC):
        if not path.exists():
            failures.append(f"missing file: {path.relative_to(REPO_ROOT)}")
            continue
        if path.suffix == ".py":
            try:
                ast.parse(_read(path), filename=str(path))
            except SyntaxError as exc:
                failures.append(f"syntax failed: {path.relative_to(REPO_ROOT)}: {exc}")
    for path in (CONTRACT, PRESENTER):
        text = _read(path) if path.exists() else ""
        for forbidden in ("import streamlit", "st.", "Path(", "open(", "read_text(", "read_bytes(", "write_text(", "write_bytes(", "data_read", "data_slice", "glob(", "rglob(", "exists(", "is_file(", "stat(", "render_latest_prediction_summary_widget(", "send_order(", "create_order("):
            if forbidden in text:
                failures.append(f"forbidden token in {path.relative_to(REPO_ROOT)}: {forbidden}")
    report = build_report(use_observed_fixture=True)
    if report.get("ok") is not True:
        failures.append(f"observed fixture mount preflight gate should be ok: {report}")
    if report.get("checker_version") != CHECKER_VERSION:
        failures.append("checker version mismatch")
    if report.get("mount_preflight_gate_ack") != LATEST_PREDICTION_SUMMARY_WIDGET_Q18AA_MOUNT_PREFLIGHT_GATE_ACK:
        failures.append("mount preflight gate ack mismatch")
    if report.get("mount_preflight_gate_kind") != LATEST_PREDICTION_SUMMARY_WIDGET_Q18AA_MOUNT_PREFLIGHT_GATE_KIND:
        failures.append("mount preflight gate kind mismatch")
    if report.get("mount_preflight_gate_state") != LATEST_PREDICTION_SUMMARY_WIDGET_Q18AA_MOUNT_PREFLIGHT_GATE_STATE:
        failures.append("mount preflight gate state mismatch")
    if report.get("mount_preflight_gate_row_count") != 12:
        failures.append("expected 12 mount preflight gate rows")
    if report.get("display_packet_row_count") != 12:
        failures.append("expected source display packet row count 12")
    if report.get("source_candidate_count") != 1:
        failures.append("expected one source candidate")
    if report.get("safe_display_mount_candidate") is not True:
        failures.append("safe display mount candidate should be declared")
    if report.get("path_shape_preview") != EXPECTED_PATH_SHAPE_PREVIEW:
        failures.append("path shape preview mismatch")
    for key in TRUE_BOUNDARIES:
        if report.get(key) is not True:
            failures.append(f"{key} must be true")
    for key in FALSE_BOUNDARIES:
        if report.get(key) is not False:
            failures.append(f"{key} must stay false")
    if main(["--use-observed-fixture"]) != 0:
        failures.append("CLI observed fixture should return 0")
    if main([]) != 1:
        failures.append("CLI without source should return 1")
    doc_text = _read(DOC) if DOC.exists() else ""
    for marker in ("PS-Q18AA", "mount_preflight_gate_row_count=12", "safe_display_mount_candidate=true", "warroom_page_mutation_allowed=false", "warroom_display_mount_allowed=false", "streamlit_render_invoked=false", "actual_source_read_invoked=false", "Next: Safe WarRoom display mount"):
        if marker not in doc_text:
            failures.append(f"missing doc marker: {marker}")
    dirty = _dirty_paths()
    unexpected = dirty - EXPECTED_DIRTY
    missing = EXPECTED_DIRTY - dirty
    if unexpected:
        failures.append(f"unexpected dirty paths: {sorted(unexpected)}")
    if missing:
        failures.append(f"missing expected dirty paths: {sorted(missing)}")
    result = {"ok": not failures, "guard": "ps_q18aa_latest_prediction_summary_widget_warroom_mount_preflight_gate_guard", "dirty_paths": sorted(dirty), "unexpected_dirty": sorted(unexpected), "missing_dirty": sorted(missing), "failures": failures}
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


def test_ps_q18aa_latest_prediction_summary_widget_warroom_mount_preflight_gate_guard() -> None:
    assert main_guard() == 0


if __name__ == "__main__":
    raise SystemExit(main_guard())
