# path: ./tools/test_phase4a_prediction_system_ps_q18ay_warroom_operator_first_cleanup_preflight_guard.py
# desc: Focused guard for PS-Q18AY WarRoom operator-first cleanup preflight.

from __future__ import annotations

import ast
import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.test_phase4a_prediction_system_ps_q18ay_warroom_operator_first_cleanup_preflight import (  # noqa: E402
    FALSE_BOUNDARIES,
    KEEP_NORMAL_UI,
    PRESERVE_FOR_FUTURE,
    REMOVE_FROM_NORMAL_UI_FIRST,
    build_ps_q18ay_warroom_operator_first_cleanup_preflight_packet,
)

DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q18AY_WARROOM_OPERATOR_FIRST_CLEANUP_PREFLIGHT_2026-06-24.md"
UNIT = REPO_ROOT / "tools/test_phase4a_prediction_system_ps_q18ay_warroom_operator_first_cleanup_preflight.py"
WARROOM_PAGE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py"
EXPECTED_DIRTY = {
    "docs/strategy/PREDICTION_SYSTEM_PS_Q18AY_WARROOM_OPERATOR_FIRST_CLEANUP_PREFLIGHT_2026-06-24.md",
    "tools/test_phase4a_prediction_system_ps_q18ay_close_guard.py",
    "tools/test_phase4a_prediction_system_ps_q18ay_warroom_operator_first_cleanup_preflight.py",
    "tools/test_phase4a_prediction_system_ps_q18ay_warroom_operator_first_cleanup_preflight_guard.py",
}


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def _dirty_paths() -> set[str]:
    proc = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True)
    return {line[3:].replace(chr(92), "/") for line in proc.stdout.splitlines() if line.strip() and "/__pycache__/" not in line and not line.endswith(".pyc")}


def main_guard() -> int:
    failures: list[str] = []
    try:
        ast.parse(_read(UNIT), filename=str(UNIT))
    except SyntaxError as exc:
        failures.append(f"syntax failed: {UNIT.relative_to(REPO_ROOT)}: {exc}")
    packet = build_ps_q18ay_warroom_operator_first_cleanup_preflight_packet()
    if packet.get("warroom_cleanup_goal") != "operator_first_normal_ui_with_diagnostics_out_of_path":
        failures.append("cleanup goal mismatch")
    if packet.get("normal_ui_keep_count") != len(KEEP_NORMAL_UI):
        failures.append("keep count mismatch")
    if packet.get("remove_from_normal_ui_first_count") != len(REMOVE_FROM_NORMAL_UI_FIRST):
        failures.append("remove count mismatch")
    if packet.get("preserve_for_future_implementation_design_count") != len(PRESERVE_FOR_FUTURE):
        failures.append("preserve count mismatch")
    if packet.get("component_file_delete_allowed_this_slice") is not False:
        failures.append("component file deletion must not be allowed in preflight")
    if packet.get("delete_requires_reference_audit") is not True:
        failures.append("delete must require reference audit")
    for key in FALSE_BOUNDARIES:
        if packet.get(key) is not False:
            failures.append(f"{key} must stay false")
    warroom_text = _read(WARROOM_PAGE)
    for marker in (
        "Prediction WarRoom latest summary observation quick status",
        "Prediction WarRoom real payload review",
        "warroom_reading_blocks=",
        "render_folded_section",
    ):
        if marker not in warroom_text:
            failures.append(f"current WarRoom marker missing: {marker}")
    if warroom_text.count("render_folded_section") < 10:
        failures.append("expected current WarRoom to still have many folded sections before cleanup")
    doc_text = _read(DOC) if DOC.exists() else ""
    for marker in (
        "PS-Q18AY",
        "warroom_cleanup_goal=operator_first_normal_ui_with_diagnostics_out_of_path",
        "latest_prediction_observation_quick_status",
        "prediction_warroom_real_payload_review",
        "payload_to_widget_props_mapping_contract",
        "delete_component_files_only_if_runtime_path_false",
        "PS-Q18AZ: WarRoom operator-first render path cleanup",
        "real_prediction_widget_rendering_allowed=false",
        "broker_private_api_allowed=false",
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
    result = {
        "ok": not failures,
        "guard": "ps_q18ay_warroom_operator_first_cleanup_preflight_guard",
        "dirty_paths": sorted(dirty),
        "unexpected_dirty": sorted(unexpected),
        "missing_dirty": sorted(missing),
        "failures": failures,
        "cleanup_goal": packet.get("warroom_cleanup_goal"),
        "keep_count": packet.get("normal_ui_keep_count"),
        "remove_count": packet.get("remove_from_normal_ui_first_count"),
        "preserve_count": packet.get("preserve_for_future_implementation_design_count"),
    }
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


def test_ps_q18ay_warroom_operator_first_cleanup_preflight_guard() -> None:
    assert main_guard() == 0


if __name__ == "__main__":
    raise SystemExit(main_guard())
