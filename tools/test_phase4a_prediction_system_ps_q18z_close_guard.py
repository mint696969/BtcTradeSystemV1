# path: ./tools/test_phase4a_prediction_system_ps_q18z_close_guard.py
# desc: Close guard for PS-Q18Z latest_prediction_summary_widget one-source no-read filesystem existence-check dry-run result display packet.

from __future__ import annotations

import json
import subprocess
from pathlib import Path

from check_phase4a_prediction_system_ps_q18z_latest_prediction_summary_widget_one_source_no_read_filesystem_existence_check_dry_run_result_display_packet import build_report
from btcts.apps.operator_ui.prediction_warroom.contracts.latest_prediction_summary_widget_q18z_display_packet import FALSE_BOUNDARIES, TRUE_BOUNDARIES

REPO_ROOT = Path(__file__).resolve().parents[1]
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
    report = build_report(use_observed_fixture=True)
    if report.get("ok") is not True:
        failures.append(f"Q18Z report must be ok: {report}")
    if report.get("display_packet_row_count") != 12:
        failures.append("Q18Z display packet row count must be 12")
    for key in TRUE_BOUNDARIES:
        if report.get(key) is not True:
            failures.append(f"{key} must be true")
    for key in FALSE_BOUNDARIES:
        if report.get(key) is not False:
            failures.append(f"{key} must stay false")
    for key in (
        "warroom_display_mount_allowed",
        "warroom_display_mounted",
        "source_artifact_exists_checked",
        "source_artifact_schema_checked",
        "actual_source_read_invoked",
        "streamlit_render_invoked",
        "real_prediction_widget_rendering_allowed",
        "runtime_artifact_write_allowed",
        "autotrade_trigger_allowed",
        "broker_private_api_allowed",
    ):
        if report.get(key) is not False:
            failures.append(f"{key} must remain false in close guard")
    dirty = _dirty_paths()
    unexpected = dirty - EXPECTED_DIRTY
    missing = EXPECTED_DIRTY - dirty
    if unexpected:
        failures.append(f"unexpected dirty paths: {sorted(unexpected)}")
    if missing:
        failures.append(f"missing expected dirty paths: {sorted(missing)}")
    result = {
        "ok": not failures,
        "guard": "ps_q18z_close_guard",
        "phase": "phase3_latest_prediction_summary_widget_one_source_no_read_filesystem_existence_check_dry_run_result_display_packet_before_mount_render_exists_result_schema_read_refresh_and_writes",
        "contract": {
            "ps_q18z_closed": not failures,
            "display_packet_row_count": int(report.get("display_packet_row_count") or 0),
            "source_candidate_count": int(report.get("source_candidate_count") or 0),
            "display_packet_kind": report.get("display_packet_kind"),
            "display_packet_state": report.get("display_packet_state"),
            "warroom_display_mount_allowed": False,
            "warroom_display_mounted": False,
            "source_artifact_exists_checked": False,
            "source_artifact_schema_checked": False,
            "actual_source_read_invoked": False,
            "streamlit_render_invoked": False,
            "real_prediction_widget_rendering_allowed": False,
            "path_shape_preview": report.get("path_shape_preview"),
            "next_slice": "WarRoom mount preflight/gate",
        },
        "dirty_paths": sorted(dirty),
        "unexpected_dirty": sorted(unexpected),
        "missing_dirty": sorted(missing),
        "failures": failures,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


def test_ps_q18z_close_guard() -> None:
    assert main_guard() == 0


if __name__ == "__main__":
    raise SystemExit(main_guard())
