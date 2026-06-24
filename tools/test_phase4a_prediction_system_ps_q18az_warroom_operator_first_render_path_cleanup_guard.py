# path: ./tools/test_phase4a_prediction_system_ps_q18az_warroom_operator_first_render_path_cleanup_guard.py
# desc: Focused guard for PS-Q18AZ WarRoom operator-first render path cleanup.

from __future__ import annotations

import ast
import inspect
import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "btcts_next" / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

import btcts.apps.operator_ui.views.warroom_page as warroom_page  # noqa: E402
from btcts.apps.operator_ui.views.warroom_page import (  # noqa: E402
    _warroom_operator_first_render_path_cleanup_packet,
)

DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q18AZ_WARROOM_OPERATOR_FIRST_RENDER_PATH_CLEANUP_2026-06-24.md"
WARROOM_PAGE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py"
UNIT = REPO_ROOT / "tools/test_phase4a_prediction_system_ps_q18az_warroom_operator_first_render_path_cleanup.py"
EXPECTED_DIRTY = {
    "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py",
    "docs/strategy/PREDICTION_SYSTEM_PS_Q18AZ_WARROOM_OPERATOR_FIRST_RENDER_PATH_CLEANUP_2026-06-24.md",
    "tools/test_phase4a_prediction_system_ps_q18az_close_guard.py",
    "tools/test_phase4a_prediction_system_ps_q18az_warroom_operator_first_render_path_cleanup.py",
    "tools/test_phase4a_prediction_system_ps_q18az_warroom_operator_first_render_path_cleanup_guard.py",
}

REMOVED_NORMAL_UI_LABELS = (
    "Prediction WarRoom real payload review",
    "Prediction WarRoom disabled widget skeleton review",
    "Prediction WarRoom source readiness preflight",
    "Prediction WarRoom source read probe status",
    "Prediction WarRoom latest summary props candidate status",
    "Prediction WarRoom latest summary render-disabled packet status",
    "Prediction WarRoom latest summary mapped payload render-disabled packet status",
    "Prediction WarRoom latest summary mapped payload values",
    "Prediction WarRoom latest summary operator value summary",
    "Prediction WarRoom latest summary real source handoff preflight",
    "Prediction WarRoom latest summary safe display mount",
    "Prediction WarRoom mount review",
)

FALSE_BOUNDARIES = (
    "real_prediction_widget_rendering_allowed",
    "real_prediction_widget_render_invoked",
    "streamlit_real_widget_render_invoked",
    "component_runtime_binding_allowed",
    "component_props_bound_to_runtime",
    "runtime_artifact_write_allowed",
    "status_artifact_write_allowed",
    "parameter_apply_allowed",
    "parameter_staging_write_allowed",
    "ledger_append_allowed",
    "autotrade_trigger_allowed",
    "broker_private_api_allowed",
    "would_send_to_broker",
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def _dirty_paths() -> set[str]:
    proc = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True)
    return {line[3:].replace(chr(92), "/") for line in proc.stdout.splitlines() if line.strip() and "/__pycache__/" not in line and not line.endswith(".pyc")}


def main_guard() -> int:
    failures: list[str] = []
    for path in (WARROOM_PAGE, UNIT):
        try:
            ast.parse(_read(path), filename=str(path))
        except SyntaxError as exc:
            failures.append(f"syntax failed: {path.relative_to(REPO_ROOT)}: {exc}")
    packet = _warroom_operator_first_render_path_cleanup_packet()
    if packet.get("cleanup_state") != "normal_warroom_ui_operator_first_dev_preflight_sections_removed":
        failures.append("cleanup state mismatch")
    if packet.get("prediction_warroom_dev_preflight_sections_rendered_in_normal_path") is not False:
        failures.append("dev/preflight sections must not render in normal path")
    if packet.get("legacy_dev_helpers_deleted_this_slice") is not False:
        failures.append("legacy helpers must not be deleted in PS-Q18AZ")
    if packet.get("removed_section_count") != len(REMOVED_NORMAL_UI_LABELS):
        failures.append("removed section count mismatch")
    for key in FALSE_BOUNDARIES:
        if packet.get(key) is not False:
            failures.append(f"{key} must stay false")
    body_source = inspect.getsource(warroom_page._render_warroom_page_body)
    if "Prediction WarRoom latest summary observation quick status" not in body_source:
        failures.append("quick status section must remain in render body")
    if "_record_warroom_operator_first_render_path_cleanup_state" not in body_source:
        failures.append("cleanup state recorder must be called in render body")
    for label in REMOVED_NORMAL_UI_LABELS:
        if label in body_source:
            failures.append(f"removed label still in render body: {label}")
    full_text = _read(WARROOM_PAGE)
    for preserved_marker in (
        "def _render_prediction_warroom_lowered_display_packet_visibility_review_section",
        "def _render_prediction_warroom_latest_prediction_summary_widget_q18aj_bounded_auto_refresh_panel_section",
        "def _render_prediction_warroom_latest_prediction_summary_widget_q18ak_freshness_error_fallback_panel_section",
    ):
        if preserved_marker not in full_text:
            failures.append(f"future extension helper unexpectedly removed: {preserved_marker}")
    if full_text.count("with live_shell.render_folded_section") > 6:
        failures.append("too many folded sections remain in WarRoom render path after cleanup")
    doc_text = _read(DOC) if DOC.exists() else ""
    for marker in (
        "PS-Q18AZ",
        "cleanup_state=normal_warroom_ui_operator_first_dev_preflight_sections_removed",
        "prediction_warroom_dev_preflight_sections_rendered_in_normal_path=false",
        "future_extension_contracts_preserved=true",
        "removed_section_count=12",
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
        "guard": "ps_q18az_warroom_operator_first_render_path_cleanup_guard",
        "dirty_paths": sorted(dirty),
        "unexpected_dirty": sorted(unexpected),
        "missing_dirty": sorted(missing),
        "failures": failures,
        "cleanup_state": packet.get("cleanup_state"),
        "removed_section_count": packet.get("removed_section_count"),
    }
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


def test_ps_q18az_warroom_operator_first_render_path_cleanup_guard() -> None:
    assert main_guard() == 0


if __name__ == "__main__":
    raise SystemExit(main_guard())
