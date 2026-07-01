# path: ./tools/diagnose_phase4a_prediction_system_ps_q26r_warroom_quick_status_panel_extraction.py
# desc: Diagnostic for PS-Q26R WarRoom quick-status panel extraction with compatibility wrappers.

from __future__ import annotations

import json
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "btcts_next" / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from btcts.apps.operator_ui.prediction_warroom.panels import warroom_latest_prediction_quick_status_panel as panel  # noqa: E402
from btcts.apps.operator_ui.views import warroom_page  # noqa: E402

DIAGNOSTIC_VERSION = "prediction_warroom.ps_q26r_warroom_quick_status_panel_extraction.v1"
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q26R_WARROOM_QUICK_STATUS_PANEL_EXTRACTION_2026-07-01.md"
PAGE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py"
PANEL = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/warroom_latest_prediction_quick_status_panel.py"
APP_TEST = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_quick_status_panel_extraction_q26r.py"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig") if path.exists() else ""


def run_warroom_quick_status_panel_extraction_diagnostic() -> dict:
    blockers: list[str] = []
    doc = _read(DOC)
    page = _read(PAGE)
    panel_text = _read(PANEL)
    app_test = _read(APP_TEST)
    for marker in (
        "ps_q26r_warroom_quick_status_panel_extraction=true",
        "externalized_panel_file=btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/warroom_latest_prediction_quick_status_panel.py",
        "warroom_page_change_boundary=thin_compatibility_wrappers_only",
        "quick_status_implementation_externalized=true",
        "legacy_private_api_wrappers_preserved=true",
        "would_send_to_broker=false",
    ):
        if marker not in doc:
            blockers.append(f"doc_marker_required:{marker}")
    for marker in (
        "warroom_latest_prediction_quick_status_panel as quick_status_panel",
        "PS-Q26R compatibility wrappers",
        "PS_Q18AU_OBSERVATION_QUICK_STATUS",
        "Prediction WarRoom latest summary observation quick status",
        "def _prediction_warroom_latest_prediction_observation_cleanup_summary_packet",
        "def _render_prediction_warroom_latest_prediction_observation_cleanup_summary_section",
        "quick_status_panel._render_prediction_warroom_latest_prediction_observation_cleanup_summary_section",
    ):
        if marker not in page:
            blockers.append(f"page_marker_required:{marker}")
    if "q18aj = q18aj_packet if isinstance" in page:
        blockers.append("quick_status_packet_body_still_in_warroom_page")
    for marker in (
        "WARROOM_LATEST_PREDICTION_QUICK_STATUS_PANEL_VERSION",
        "def _prediction_warroom_latest_prediction_observation_cleanup_summary_packet",
        "def _prediction_warroom_latest_prediction_observation_cleanup_summary_rows",
        "def _render_prediction_warroom_latest_prediction_observation_cleanup_summary_section",
        "q18aj = q18aj_packet if isinstance",
    ):
        if marker not in panel_text:
            blockers.append(f"panel_marker_required:{marker}")
    for marker in (
        "test_q26r_quick_status_panel_exports_safe_packet_and_keeps_legacy_wrapper",
        "test_q26r_warroom_page_is_thin_wrapper_and_panel_holds_implementation",
    ):
        if marker not in app_test:
            blockers.append(f"test_marker_required:{marker}")

    sample_q18aj = {"auto_refresh_enabled": True, "fragment_refresh_enabled": True, "broad_page_reload_disabled": True, "refresh_heartbeat_utc": "hb"}
    sample_q18ak = {"freshness_state": "unknown", "safe_fallback_reason_codes": ["source_generated_at_missing"]}
    page_packet = warroom_page._prediction_warroom_latest_prediction_observation_cleanup_summary_packet(q18aj_packet=sample_q18aj, q18ak_packet=sample_q18ak)
    panel_packet = panel._prediction_warroom_latest_prediction_observation_cleanup_summary_packet(q18aj_packet=sample_q18aj, q18ak_packet=sample_q18ak)
    if page_packet != panel_packet:
        blockers.append("compatibility_wrapper_packet_mismatch")
    for key in ("real_rendering_enabled", "component_runtime_binding_allowed", "runtime_artifact_write_allowed", "status_artifact_write_allowed", "parameter_apply_allowed", "ledger_append_allowed", "autotrade_trigger_allowed", "broker_private_api_allowed", "would_send_to_broker"):
        if page_packet.get(key) is not False:
            blockers.append(f"packet_false_required:{key}")

    return {
        "ok": True,
        "diagnostic_version": DIAGNOSTIC_VERSION,
        "ready": not blockers,
        "blockers": blockers,
        "packet": {
            "ok": not blockers,
            "quick_status_panel_version": getattr(panel, "WARROOM_LATEST_PREDICTION_QUICK_STATUS_PANEL_VERSION", None),
            "quick_status_implementation_externalized": True,
            "legacy_private_api_wrappers_preserved": True,
            "legacy_searchable_markers_preserved": True,
            "warroom_page_change_boundary": "thin_compatibility_wrappers_only",
            "page_packet_matches_panel_packet": page_packet == panel_packet,
            "observation_cleanup_state": page_packet.get("observation_cleanup_state"),
            "read_only": True,
            "display_only": True,
            "non_executing": True,
            "runtime_artifact_write_allowed": False,
            "status_artifact_write_allowed": False,
            "prediction_artifact_write_allowed": False,
            "view_artifact_write_allowed": False,
            "scheduler_enabled": False,
            "producer_enabled": False,
            "autotrade_trigger_allowed": False,
            "broker_private_api_allowed": False,
            "ledger_append_allowed": False,
            "mode_apply_allowed": False,
            "parameter_apply_allowed": False,
            "would_send_to_broker": False,
        },
        "safety": {
            "production_ui_code_changed": True,
            "structural_cleanup_only": True,
            "layout_only_change": True,
            "read_only": True,
            "display_only": True,
            "non_executing": True,
            "runtime_artifact_write_allowed": False,
            "status_artifact_write_allowed": False,
            "prediction_artifact_write_allowed": False,
            "view_artifact_write_allowed": False,
            "scheduler_enabled": False,
            "producer_enabled": False,
            "autotrade_trigger_allowed": False,
            "broker_private_api_allowed": False,
            "ledger_append_allowed": False,
            "mode_apply_allowed": False,
            "parameter_apply_allowed": False,
            "would_send_to_broker": False,
        },
    }


def main() -> int:
    result = run_warroom_quick_status_panel_extraction_diagnostic()
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result.get("ready") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
