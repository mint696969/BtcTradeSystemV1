# path: ./tools/test_phase4a_prediction_system_ps_q18ab_close_guard.py
# desc: Close guard for PS-Q18AB latest_prediction_summary_widget safe WarRoom display mount panel.

from __future__ import annotations

import json
import subprocess
from pathlib import Path
import sys

BTCTS_SRC = Path(__file__).resolve().parents[1] / "btcts_next" / "src"
if str(BTCTS_SRC) not in sys.path:
    sys.path.insert(0, str(BTCTS_SRC))

from btcts.apps.operator_ui.prediction_warroom.panels.latest_prediction_summary_widget_q18ab_safe_display_mount_panel import FALSE_BOUNDARIES, TRUE_BOUNDARIES, build_latest_prediction_summary_widget_q18ab_safe_display_mount_panel_packet

REPO_ROOT = Path(__file__).resolve().parents[1]
EXPECTED_DIRTY = {
    "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py",
    "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/__init__.py",
    "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/latest_prediction_summary_widget_q18ab_safe_display_mount_panel.py",
    "docs/strategy/PREDICTION_SYSTEM_PS_Q18AB_LATEST_PREDICTION_SUMMARY_WIDGET_SAFE_WARROOM_DISPLAY_MOUNT_2026-06-24.md",
    "tools/test_phase4a_prediction_system_ps_q18ab_latest_prediction_summary_widget_safe_warroom_display_mount.py",
    "tools/test_phase4a_prediction_system_ps_q18ab_safe_warroom_display_mount_guard.py",
    "tools/test_phase4a_prediction_system_ps_q18ab_close_guard.py",
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
    packet = build_latest_prediction_summary_widget_q18ab_safe_display_mount_panel_packet()
    if packet.get("ok") is not True:
        failures.append(f"Q18AB packet must be ok: {packet}")
    if packet.get("safe_display_mount_panel_row_count") != 12:
        failures.append("safe display mount panel row count must be 12")
    if packet.get("warroom_display_mounted") is not True:
        failures.append("warroom display mounted must be true")
    for key in TRUE_BOUNDARIES:
        if packet.get(key) is not True:
            failures.append(f"{key} must be true")
    for key in FALSE_BOUNDARIES:
        if packet.get(key) is not False:
            failures.append(f"{key} must stay false")
    for key in ("actual_source_read_invoked", "real_prediction_widget_rendering_allowed", "render_latest_prediction_summary_widget_invoked", "refresh_invocation_allowed", "runtime_artifact_write_allowed", "autotrade_trigger_allowed", "broker_private_api_allowed"):
        if packet.get(key) is not False:
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
        "guard": "ps_q18ab_close_guard",
        "phase": "phase3_latest_prediction_summary_widget_safe_warroom_display_mount_before_exists_result_schema_read_refresh_and_writes",
        "contract": {
            "ps_q18ab_closed": not failures,
            "safe_display_mount_panel_row_count": int(packet.get("safe_display_mount_panel_row_count") or 0),
            "warroom_display_mounted": packet.get("warroom_display_mounted") is True,
            "actual_source_read_invoked": False,
            "real_prediction_widget_rendering_allowed": False,
            "refresh_invocation_allowed": False,
            "runtime_artifact_write_allowed": False,
            "path_shape_preview": packet.get("path_shape_preview"),
            "next_slice": "filesystem exists-check execution",
        },
        "dirty_paths": sorted(dirty),
        "unexpected_dirty": sorted(unexpected),
        "missing_dirty": sorted(missing),
        "failures": failures,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


def test_ps_q18ab_close_guard() -> None:
    assert main_guard() == 0


if __name__ == "__main__":
    raise SystemExit(main_guard())
