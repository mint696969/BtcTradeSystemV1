# path: ./tools/test_phase4a_prediction_system_ps_q18z_latest_prediction_summary_widget_one_source_no_read_filesystem_existence_check_dry_run_result_display_packet_guard.py
# desc: Focused guard for PS-Q18Z latest_prediction_summary_widget one-source no-read filesystem existence-check dry-run result display packet.

from __future__ import annotations

import ast
import json
import subprocess
from pathlib import Path

from check_phase4a_prediction_system_ps_q18q_latest_prediction_summary_widget_one_source_resolver_dry_run_path_shape_preflight import EXPECTED_PATH_SHAPE_PREVIEW
from check_phase4a_prediction_system_ps_q18z_latest_prediction_summary_widget_one_source_no_read_filesystem_existence_check_dry_run_result_display_packet import CHECKER_VERSION, build_report, main
from btcts.apps.operator_ui.prediction_warroom.contracts.latest_prediction_summary_widget_q18z_display_packet import (
    FALSE_BOUNDARIES,
    LATEST_PREDICTION_SUMMARY_WIDGET_Q18Z_DISPLAY_PACKET_ACK,
    LATEST_PREDICTION_SUMMARY_WIDGET_Q18Z_DISPLAY_PACKET_KIND,
    LATEST_PREDICTION_SUMMARY_WIDGET_Q18Z_DISPLAY_PACKET_STATE,
    TRUE_BOUNDARIES,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
CONTRACT = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/contracts/latest_prediction_summary_widget_q18z_display_packet.py"
PRESENTER = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/presenters/latest_prediction_summary_widget_q18z_display_rows.py"
TOOL = REPO_ROOT / "tools/check_phase4a_prediction_system_ps_q18z_latest_prediction_summary_widget_one_source_no_read_filesystem_existence_check_dry_run_result_display_packet.py"
UNIT = REPO_ROOT / "tools/test_phase4a_prediction_system_ps_q18z_latest_prediction_summary_widget_one_source_no_read_filesystem_existence_check_dry_run_result_display_packet.py"
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q18Z_LATEST_PREDICTION_SUMMARY_WIDGET_ONE_SOURCE_NO_READ_FILESYSTEM_EXISTENCE_CHECK_DRY_RUN_RESULT_DISPLAY_PACKET_2026-06-24.md"
EXPECTED_DIRTY = {
    "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/__init__.py",
    "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/contracts/__init__.py",
    "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/contracts/latest_prediction_summary_widget_q18z_display_packet.py",
    "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/presenters/__init__.py",
    "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/presenters/latest_prediction_summary_widget_q18z_display_rows.py",
    "docs/strategy/PREDICTION_SYSTEM_PS_Q18Z_LATEST_PREDICTION_SUMMARY_WIDGET_ONE_SOURCE_NO_READ_FILESYSTEM_EXISTENCE_CHECK_DRY_RUN_RESULT_DISPLAY_PACKET_2026-06-24.md",
    "tools/check_phase4a_prediction_system_ps_q18z_latest_prediction_summary_widget_one_source_no_read_filesystem_existence_check_dry_run_result_display_packet.py",
    "tools/test_phase4a_prediction_system_ps_q18z_latest_prediction_summary_widget_one_source_no_read_filesystem_existence_check_dry_run_result_display_packet.py",
    "tools/test_phase4a_prediction_system_ps_q18z_latest_prediction_summary_widget_one_source_no_read_filesystem_existence_check_dry_run_result_display_packet_guard.py",
    "tools/test_phase4a_prediction_system_ps_q18z_close_guard.py",
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
        for forbidden in (
            "import streamlit", "st.", "Path(", "open(", "read_text(", "read_bytes(", "write_text(", "write_bytes(",
            "data_read", "data_slice", "glob(", "rglob(", "exists(", "is_file(", "stat(", "render_latest_prediction_summary_widget(",
            "send_order(", "create_order(",
        ):
            if forbidden in text:
                failures.append(f"forbidden token in {path.relative_to(REPO_ROOT)}: {forbidden}")
    report = build_report(use_observed_fixture=True)
    if report.get("ok") is not True:
        failures.append(f"observed fixture display packet should be ok: {report}")
    if report.get("checker_version") != CHECKER_VERSION:
        failures.append("checker version mismatch")
    if report.get("display_packet_ack") != LATEST_PREDICTION_SUMMARY_WIDGET_Q18Z_DISPLAY_PACKET_ACK:
        failures.append("display packet ack mismatch")
    if report.get("display_packet_kind") != LATEST_PREDICTION_SUMMARY_WIDGET_Q18Z_DISPLAY_PACKET_KIND:
        failures.append("display packet kind mismatch")
    if report.get("display_packet_state") != LATEST_PREDICTION_SUMMARY_WIDGET_Q18Z_DISPLAY_PACKET_STATE:
        failures.append("display packet state mismatch")
    if report.get("display_packet_row_count") != 12:
        failures.append("expected 12 display packet rows")
    if report.get("source_candidate_count") != 1:
        failures.append("expected one source candidate")
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
    for marker in (
        "PS-Q18Z",
        "display_packet_row_count=12",
        "warroom_display_mount_allowed=false",
        "streamlit_render_invoked=false",
        "actual_source_read_invoked=false",
        "source_artifact_exists_checked=false",
        "autotrade_trigger_allowed=false",
        "broker_private_api_allowed=false",
        "Next: WarRoom mount preflight/gate",
    ):
        if marker not in doc_text:
            failures.append(f"missing doc marker: {marker}")
    dirty = _dirty_paths()
    unexpected = dirty - EXPECTED_DIRTY
    missing = EXPECTED_DIRTY - dirty
    if unexpected:
        failures.append(f"unexpected dirty paths: {sorted(unexpected)}")
    if missing:
        failures.append(f"missing expected dirty paths: {sorted(missing)}")
    result = {"ok": not failures, "guard": "ps_q18z_latest_prediction_summary_widget_one_source_no_read_filesystem_existence_check_dry_run_result_display_packet_guard", "dirty_paths": sorted(dirty), "unexpected_dirty": sorted(unexpected), "missing_dirty": sorted(missing), "failures": failures}
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


def test_ps_q18z_latest_prediction_summary_widget_one_source_no_read_filesystem_existence_check_dry_run_result_display_packet_guard() -> None:
    assert main_guard() == 0


if __name__ == "__main__":
    raise SystemExit(main_guard())
