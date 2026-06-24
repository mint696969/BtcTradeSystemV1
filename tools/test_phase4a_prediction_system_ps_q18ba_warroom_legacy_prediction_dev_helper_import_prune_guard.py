# path: ./tools/test_phase4a_prediction_system_ps_q18ba_warroom_legacy_prediction_dev_helper_import_prune_guard.py
# desc: Focused guard for PS-Q18BA WarRoom legacy prediction dev helper/import prune.

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

DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q18BA_WARROOM_LEGACY_PREDICTION_DEV_HELPER_IMPORT_PRUNE_2026-06-24.md"
WARROOM_PAGE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py"
UNIT = REPO_ROOT / "tools/test_phase4a_prediction_system_ps_q18ba_warroom_legacy_prediction_dev_helper_import_prune.py"
EXPECTED_DIRTY = {
    "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py",
    "docs/strategy/PREDICTION_SYSTEM_PS_Q18BA_WARROOM_LEGACY_PREDICTION_DEV_HELPER_IMPORT_PRUNE_2026-06-24.md",
    "tools/test_phase4a_prediction_system_ps_q18ba_close_guard.py",
    "tools/test_phase4a_prediction_system_ps_q18ba_warroom_legacy_prediction_dev_helper_import_prune.py",
    "tools/test_phase4a_prediction_system_ps_q18ba_warroom_legacy_prediction_dev_helper_import_prune_guard.py",
}

REMOVED_MARKERS = (
    "build_prediction_warroom_ui_mount_presenter_packet",
    "render_prediction_warroom_lowered_display_packet_visibility_review_panel",
    "apply_prediction_warroom_actual_review_packet_live_session_seed_page_mount",
    "render_prediction_warroom_latest_prediction_source_review_panel",
    "render_prediction_warroom_realtime_review_preflight_panel",
    "render_prediction_warroom_non_ui_scheduled_producer_status_panel",
    "build_prediction_warroom_prediction_widgets_disabled_section_review_packet",
    "build_prediction_warroom_prediction_widget_source_readiness_preflight_packet",
    "build_prediction_warroom_prediction_widget_source_read_probe_status_packet",
    "build_latest_prediction_summary_widget_props_candidate_status_packet",
    "build_latest_prediction_summary_widget_render_disabled_packet_status_packet",
    "build_latest_prediction_summary_widget_mapped_payload_render_disabled_packet_status_packet",
    "build_latest_prediction_summary_widget_mapped_payload_value_rows_packet",
    "build_latest_prediction_summary_widget_operator_value_summary_packet",
    "build_latest_prediction_summary_widget_real_source_handoff_preflight_packet",
    "render_latest_prediction_summary_widget_q18ab_safe_display_mount_panel",
    "render_latest_prediction_summary_widget_q18ai_warroom_render_disabled_packet_panel",
    "render_latest_prediction_summary_widget_q18aj_bounded_auto_refresh_panel",
    "render_latest_prediction_summary_widget_q18ak_freshness_error_fallback_panel",
    "render_prediction_delta_widget",
    "render_runtime_boundary_safety_widget",
    "def _render_prediction_warroom_ui_mount_review_section",
    "def _render_prediction_warroom_lowered_display_packet_visibility_review_section",
    "def _render_prediction_warroom_prediction_widgets_disabled_section_review_mount",
    "def _render_prediction_warroom_latest_prediction_summary_widget_real_source_handoff_preflight_section",
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
    text = _read(WARROOM_PAGE)
    for marker in REMOVED_MARKERS:
        if marker in text:
            failures.append(f"legacy marker still present: {marker}")
    for keep_marker in (
        "build_latest_prediction_summary_widget_q18aj_bounded_auto_refresh_panel_packet",
        "build_latest_prediction_summary_widget_q18ak_freshness_error_fallback_panel_packet",
        "def _prediction_warroom_latest_prediction_observation_cleanup_summary_packet",
        "def _render_prediction_warroom_latest_prediction_observation_cleanup_summary_section",
        "def _warroom_operator_first_render_path_cleanup_packet",
    ):
        if keep_marker not in text:
            failures.append(f"required marker missing: {keep_marker}")
    body_source = inspect.getsource(warroom_page._render_warroom_page_body)
    if "Prediction WarRoom latest summary observation quick status" not in body_source:
        failures.append("quick status must remain in render body")
    if "Prediction WarRoom real payload review" in body_source:
        failures.append("legacy real payload review must not return to render body")
    packet = warroom_page._warroom_operator_first_render_path_cleanup_packet()
    if packet.get("normal_ui_path_operator_first") is not True:
        failures.append("normal UI path must stay operator-first")
    for key in FALSE_BOUNDARIES:
        if packet.get(key) is not False:
            failures.append(f"{key} must stay false")
    doc_text = _read(DOC) if DOC.exists() else ""
    for marker in (
        "PS-Q18BA",
        "warroom_page_legacy_prediction_dev_helpers_pruned=true",
        "legacy_prediction_dev_helper_function_count_removed=29",
        "component_modules_deleted=false",
        "future_extension_contracts_preserved=true",
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
        "guard": "ps_q18ba_warroom_legacy_prediction_dev_helper_import_prune_guard",
        "dirty_paths": sorted(dirty),
        "unexpected_dirty": sorted(unexpected),
        "missing_dirty": sorted(missing),
        "failures": failures,
        "component_modules_deleted": False,
        "future_extension_contracts_preserved": True,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


def test_ps_q18ba_warroom_legacy_prediction_dev_helper_import_prune_guard() -> None:
    assert main_guard() == 0


if __name__ == "__main__":
    raise SystemExit(main_guard())
