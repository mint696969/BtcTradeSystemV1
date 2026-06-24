# path: ./tools/test_phase4a_prediction_system_ps_q18bb_legacy_component_reference_audit_archive_delete_decision_guard.py
# desc: Focused guard for PS-Q18BB legacy component reference audit/archive-delete decision.

from __future__ import annotations

import ast
import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "btcts_next" / "src"
for path in (REPO_ROOT, SRC_ROOT):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from tools.test_phase4a_prediction_system_ps_q18bb_legacy_component_reference_audit_archive_delete_decision import (  # noqa: E402
    FALSE_BOUNDARIES,
    LEGACY_COMPONENT_STEMS,
    build_ps_q18bb_legacy_component_reference_audit_packet,
)

DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q18BB_LEGACY_COMPONENT_REFERENCE_AUDIT_ARCHIVE_DELETE_DECISION_2026-06-24.md"
UNIT = REPO_ROOT / "tools/test_phase4a_prediction_system_ps_q18bb_legacy_component_reference_audit_archive_delete_decision.py"
WARROOM_PAGE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py"
EXPECTED_DIRTY = {
    "docs/strategy/PREDICTION_SYSTEM_PS_Q18BB_LEGACY_COMPONENT_REFERENCE_AUDIT_ARCHIVE_DELETE_DECISION_2026-06-24.md",
    "tools/test_phase4a_prediction_system_ps_q18bb_close_guard.py",
    "tools/test_phase4a_prediction_system_ps_q18bb_legacy_component_reference_audit_archive_delete_decision.py",
    "tools/test_phase4a_prediction_system_ps_q18bb_legacy_component_reference_audit_archive_delete_decision_guard.py",
}


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def _dirty_paths() -> set[str]:
    proc = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True)
    return {line[3:].replace(chr(92), "/") for line in proc.stdout.splitlines() if line.strip() and "/__pycache__/" not in line and not line.endswith(".pyc")}


def main_guard() -> int:
    failures: list[str] = []
    for path in (UNIT,):
        try:
            ast.parse(_read(path), filename=str(path))
        except SyntaxError as exc:
            failures.append(f"syntax failed: {path.relative_to(REPO_ROOT)}: {exc}")
    packet = build_ps_q18bb_legacy_component_reference_audit_packet()
    if packet.get("warroom_page_legacy_import_refs") is not False:
        failures.append(f"warroom_page still references legacy stems: {packet.get('warroom_page_hit_stems')}")
    if packet.get("component_modules_deleted_this_slice") is not False:
        failures.append("component modules must not be deleted in audit slice")
    if packet.get("immediate_physical_delete_decision") != "defer":
        failures.append("immediate delete decision must be defer")
    if packet.get("future_extension_contracts_preserved") is not True:
        failures.append("future extension contracts must be preserved")
    if packet.get("legacy_component_stem_count") != len(LEGACY_COMPONENT_STEMS):
        failures.append("legacy component stem count mismatch")
    for key in FALSE_BOUNDARIES:
        if packet.get(key) is not False:
            failures.append(f"{key} must stay false")
    warroom_text = _read(WARROOM_PAGE)
    if "Prediction WarRoom latest summary observation quick status" not in warroom_text:
        failures.append("quick status label must remain in warroom_page")
    import inspect

    body_source = inspect.getsource(__import__(
        "btcts.apps.operator_ui.views.warroom_page",
        fromlist=["_render_warroom_page_body"],
    )._render_warroom_page_body)
    if "Prediction WarRoom real payload review" in body_source:
        failures.append("legacy real payload review label must not return to WarRoom render body")
    doc_text = _read(DOC) if DOC.exists() else ""
    for marker in (
        "PS-Q18BB",
        "warroom_page_normal_render_path_refs=false",
        "component_modules_deleted_this_slice=false",
        "immediate_physical_delete_decision=defer",
        "archive_delete_decision=preserve_as_spec_or_contract_until_reference_audit_zero_or_docs_only_archive",
        "future_extension_contracts_preserved=true",
        "prediction_widgets real component code is not legacy trash",
        "normal_ui_operator_first=true",
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
        "guard": "ps_q18bb_legacy_component_reference_audit_archive_delete_decision_guard",
        "dirty_paths": sorted(dirty),
        "unexpected_dirty": sorted(unexpected),
        "missing_dirty": sorted(missing),
        "failures": failures,
        "immediate_physical_delete_decision": packet.get("immediate_physical_delete_decision"),
        "component_modules_deleted_this_slice": packet.get("component_modules_deleted_this_slice"),
        "legacy_component_stem_count": packet.get("legacy_component_stem_count"),
    }
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


def test_ps_q18bb_reference_audit_archive_delete_decision_guard() -> None:
    assert main_guard() == 0


if __name__ == "__main__":
    raise SystemExit(main_guard())
