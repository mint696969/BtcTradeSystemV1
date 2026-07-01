# path: ./tools/diagnose_phase4a_prediction_system_ps_q26q_warroom_focus_section_renderer.py
# desc: Diagnostic for PS-Q26Q WarRoom focus section renderer externalization.

from __future__ import annotations

import json
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "btcts_next" / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from btcts.apps.operator_ui.prediction_warroom.panels.warroom_focus_sections import (  # noqa: E402
    WARROOM_FOCUS_SECTION_RENDERER_VERSION,
    build_warroom_focus_section_renderer_packet,
)

DIAGNOSTIC_VERSION = "prediction_warroom.ps_q26q_warroom_focus_section_renderer.v1"
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q26Q_WARROOM_FOCUS_SECTION_RENDERER_2026-07-01.md"
PAGE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py"
SECTION_RENDERER = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/warroom_focus_sections.py"
APP_TEST = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_focus_section_renderer_q26q.py"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig") if path.exists() else ""


def run_warroom_focus_section_renderer_diagnostic() -> dict:
    blockers: list[str] = []
    doc = _read(DOC)
    page = _read(PAGE)
    renderer = _read(SECTION_RENDERER)
    app_test = _read(APP_TEST)
    for marker in (
        "ps_q26q_warroom_focus_section_renderer=true",
        "externalized_section_renderer_file=btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/warroom_focus_sections.py",
        "warroom_page_change_boundary=import_and_focus_section_renderer_calls_only",
        "section_renderer_externalized=true",
        "would_send_to_broker=false",
    ):
        if marker not in doc:
            blockers.append(f"doc_marker_required:{marker}")
    for marker in (
        "from btcts.apps.operator_ui.prediction_warroom.panels.warroom_focus_sections import",
        "render_warroom_focus_section",
    ):
        if marker not in page:
            blockers.append(f"page_marker_required:{marker}")
    for forbidden in ("warroom_focus_section_expanded", "warroom_focus_section_label"):
        if forbidden in page:
            blockers.append(f"page_direct_policy_lookup_forbidden:{forbidden}")
    for section_id in (
        "operator_focus_nav",
        "prediction_quick_status_detail",
        "live_nowcast",
        "latest_prediction_read_model",
        "header_alert_operator",
        "market_evidence_detail",
        "operator_support_detail",
    ):
        if f'render_warroom_focus_section("{section_id}")' not in page:
            blockers.append(f"page_focus_section_call_required:{section_id}")
    for marker in (
        "WARROOM_FOCUS_SECTION_RENDERER_VERSION",
        "def render_warroom_focus_section",
        "def build_warroom_focus_section_renderer_packet",
        "live_shell.render_folded_section",
        "warroom_focus_section_label",
        "warroom_focus_section_expanded",
    ):
        if marker not in renderer:
            blockers.append(f"renderer_marker_required:{marker}")
    for marker in (
        "test_q26q_focus_section_renderer_packet_is_safe_and_policy_backed",
        "test_q26q_warroom_page_uses_focus_section_renderer_not_direct_policy_lookup",
    ):
        if marker not in app_test:
            blockers.append(f"test_marker_required:{marker}")

    packet = build_warroom_focus_section_renderer_packet()
    if packet.get("focus_section_renderer_version") != WARROOM_FOCUS_SECTION_RENDERER_VERSION:
        blockers.append("focus_section_renderer_version_mismatch")
    if packet.get("section_renderer_externalized") is not True:
        blockers.append("section_renderer_externalized_not_true")
    if packet.get("warroom_page_change_boundary") != "import_and_focus_section_renderer_calls_only":
        blockers.append("warroom_page_change_boundary_mismatch")
    if packet.get("section_count") != 7:
        blockers.append(f"section_count_not_7:{packet.get('section_count')}")
    for key in ("read_only", "display_only", "non_executing", "layout_only_change", "keeps_existing_panels_available"):
        if packet.get(key) is not True:
            blockers.append(f"packet_true_required:{key}")
    for key in ("runtime_artifact_write_allowed", "status_artifact_write_allowed", "prediction_artifact_write_allowed", "view_artifact_write_allowed", "scheduler_enabled", "producer_enabled", "autotrade_trigger_allowed", "broker_private_api_allowed", "ledger_append_allowed", "mode_apply_allowed", "parameter_apply_allowed", "would_send_to_broker"):
        if packet.get(key) is not False:
            blockers.append(f"packet_false_required:{key}")

    return {
        "ok": True,
        "diagnostic_version": DIAGNOSTIC_VERSION,
        "ready": not blockers,
        "blockers": blockers,
        "packet": packet,
        "safety": {
            "production_ui_code_changed": True,
            "layout_only_change": True,
            "section_renderer_externalized": True,
            "uses_externalized_layout_policy_module": True,
            "warroom_page_change_boundary": "import_and_focus_section_renderer_calls_only",
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
    result = run_warroom_focus_section_renderer_diagnostic()
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result.get("ready") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
