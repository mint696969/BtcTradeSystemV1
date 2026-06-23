# path: ./tools/test_phase4a_prediction_system_ps_q18aa_close_guard.py
# desc: Close guard for PS-Q18AA latest_prediction_summary_widget WarRoom mount preflight gate.

from __future__ import annotations

import json
import subprocess
from pathlib import Path

from check_phase4a_prediction_system_ps_q18aa_latest_prediction_summary_widget_warroom_mount_preflight_gate import build_report
from btcts.apps.operator_ui.prediction_warroom.contracts.latest_prediction_summary_widget_q18aa_mount_preflight_gate import FALSE_BOUNDARIES, TRUE_BOUNDARIES

REPO_ROOT = Path(__file__).resolve().parents[1]
EXPECTED_DIRTY = {
    "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/contracts/latest_prediction_summary_widget_q18aa_mount_preflight_gate.py",
    "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/presenters/latest_prediction_summary_widget_q18aa_mount_preflight_gate_rows.py",
    "docs/strategy/PREDICTION_SYSTEM_PS_Q18AA_LATEST_PREDICTION_SUMMARY_WIDGET_WARROOM_MOUNT_PREFLIGHT_GATE_2026-06-24.md",
    "tools/check_phase4a_prediction_system_ps_q18aa_latest_prediction_summary_widget_warroom_mount_preflight_gate.py",
    "tools/test_phase4a_prediction_system_ps_q18aa_close_guard.py",
    "tools/test_phase4a_prediction_system_ps_q18aa_latest_prediction_summary_widget_warroom_mount_preflight_gate.py",
    "tools/test_phase4a_prediction_system_ps_q18aa_latest_prediction_summary_widget_warroom_mount_preflight_gate_guard.py",
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
        failures.append(f"Q18AA report must be ok: {report}")
    if report.get("mount_preflight_gate_row_count") != 12:
        failures.append("Q18AA mount preflight gate row count must be 12")
    if report.get("safe_display_mount_candidate") is not True:
        failures.append("Q18AA safe display mount candidate must be true")
    for key in TRUE_BOUNDARIES:
        if report.get(key) is not True:
            failures.append(f"{key} must be true")
    for key in FALSE_BOUNDARIES:
        if report.get(key) is not False:
            failures.append(f"{key} must stay false")
    for key in ("warroom_page_mutation_allowed", "warroom_body_call_allowed", "warroom_display_mount_allowed", "warroom_display_mounted", "source_artifact_exists_checked", "source_artifact_schema_checked", "actual_source_read_invoked", "streamlit_render_invoked", "real_prediction_widget_rendering_allowed", "runtime_artifact_write_allowed", "autotrade_trigger_allowed", "broker_private_api_allowed"):
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
        "guard": "ps_q18aa_close_guard",
        "phase": "phase3_latest_prediction_summary_widget_warroom_mount_preflight_gate_before_page_mutation_mount_render_exists_result_schema_read_refresh_and_writes",
        "contract": {
            "ps_q18aa_closed": not failures,
            "mount_preflight_gate_row_count": int(report.get("mount_preflight_gate_row_count") or 0),
            "display_packet_row_count": int(report.get("display_packet_row_count") or 0),
            "source_candidate_count": int(report.get("source_candidate_count") or 0),
            "safe_display_mount_candidate": bool(report.get("safe_display_mount_candidate")),
            "mount_preflight_gate_kind": report.get("mount_preflight_gate_kind"),
            "mount_preflight_gate_state": report.get("mount_preflight_gate_state"),
            "warroom_page_mutation_allowed": False,
            "warroom_display_mount_allowed": False,
            "warroom_display_mounted": False,
            "actual_source_read_invoked": False,
            "streamlit_render_invoked": False,
            "real_prediction_widget_rendering_allowed": False,
            "path_shape_preview": report.get("path_shape_preview"),
            "next_slice": "Safe WarRoom display mount",
        },
        "dirty_paths": sorted(dirty),
        "unexpected_dirty": sorted(unexpected),
        "missing_dirty": sorted(missing),
        "failures": failures,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


def test_ps_q18aa_close_guard() -> None:
    assert main_guard() == 0


if __name__ == "__main__":
    raise SystemExit(main_guard())
