# path: ./tools/diagnose_phase4a_prediction_system_ps_q26n_warroom_operator_focus_nav.py
# desc: Diagnostic for PS-Q26N WarRoom operator focus navigation layout-only UI cleanup.

from __future__ import annotations

import json
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "btcts_next" / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from btcts.apps.operator_ui.prediction_warroom.panels.warroom_operator_focus_nav_panel import (  # noqa: E402
    WARROOM_OPERATOR_FOCUS_NAV_VERSION,
    build_warroom_operator_focus_nav_packet,
)

DIAGNOSTIC_VERSION = "prediction_warroom.ps_q26n_warroom_operator_focus_nav.v1"
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q26N_WARROOM_OPERATOR_FOCUS_NAV_2026-07-01.md"
WARROOM_PAGE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py"
PANEL = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/warroom_operator_focus_nav_panel.py"
TEST = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_operator_focus_nav_q26n.py"


def run_warroom_operator_focus_nav_diagnostic() -> dict:
    blockers: list[str] = []
    doc = DOC.read_text(encoding="utf-8-sig") if DOC.exists() else ""
    page = WARROOM_PAGE.read_text(encoding="utf-8-sig") if WARROOM_PAGE.exists() else ""
    panel = PANEL.read_text(encoding="utf-8-sig") if PANEL.exists() else ""
    test = TEST.read_text(encoding="utf-8-sig") if TEST.exists() else ""
    for marker in (
        "ps_q26n_warroom_operator_focus_nav=true",
        "production_ui_code_changed=true",
        "externalized_panel_module=true",
        "warroom_page_change_boundary=import_and_single_render_call_only",
        "operator_first_navigation_visible=true",
        "layout_only_change=true",
        "would_send_to_broker=false",
    ):
        if marker not in doc:
            blockers.append(f"doc_marker_required:{marker}")
    for marker in (
        "from btcts.apps.operator_ui.prediction_warroom.panels.warroom_operator_focus_nav_panel import",
        "render_warroom_operator_focus_nav",
        "最初に見る場所 / WarRoom 入口",
    ):
        if marker not in page:
            blockers.append(f"warroom_page_marker_required:{marker}")
    for marker in (
        "def warroom_operator_focus_nav_rows()",
        "def build_warroom_operator_focus_nav_packet()",
        "def render_warroom_operator_focus_nav()",
        "WARROOM_OPERATOR_FOCUS_NAV_VERSION",
    ):
        if marker not in panel:
            blockers.append(f"panel_marker_required:{marker}")
    for forbidden in (
        "def warroom_operator_focus_nav_rows()",
        "def build_warroom_operator_focus_nav_packet()",
        "def _render_warroom_operator_focus_nav()",
    ):
        if forbidden in page:
            blockers.append(f"warroom_page_should_not_contain_externalized_logic:{forbidden}")
    for marker in (
        "test_q26n_focus_nav_rows_are_operator_first_and_safe",
        "test_q26n_render_body_places_focus_nav_before_guide_with_external_panel",
    ):
        if marker not in test:
            blockers.append(f"test_marker_required:{marker}")

    packet = build_warroom_operator_focus_nav_packet()
    rows = packet.get("rows") if isinstance(packet.get("rows"), list) else []
    joined = json.dumps(packet, ensure_ascii=False)
    if packet.get("focus_nav_version") != WARROOM_OPERATOR_FOCUS_NAV_VERSION:
        blockers.append("focus_nav_version_mismatch")
    if packet.get("operator_first_navigation_visible") is not True:
        blockers.append("operator_first_navigation_visible_not_true")
    if packet.get("externalized_panel_module") is not True:
        blockers.append("externalized_panel_module_not_true")
    if packet.get("top_expanded_default") is not True:
        blockers.append("top_expanded_default_not_true")
    if packet.get("row_count") != 5 or len(rows) != 5:
        blockers.append(f"row_count_not_5:{packet.get('row_count')}/{len(rows)}")
    if "現在状態 nowcast" not in joined or "リアルタイム予測表示" not in joined:
        blockers.append("primary_focus_targets_missing")
    if joined.find("現在状態 nowcast") > joined.find("リアルタイム予測表示"):
        blockers.append("nowcast_not_before_prediction")
    for key in (
        "read_only",
        "display_only",
        "non_executing",
        "layout_only_change",
    ):
        if packet.get(key) is not True:
            blockers.append(f"packet_true_required:{key}")
    for key in (
        "runtime_artifact_write_allowed",
        "status_artifact_write_allowed",
        "prediction_artifact_write_allowed",
        "view_artifact_write_allowed",
        "scheduler_enabled",
        "producer_enabled",
        "autotrade_trigger_allowed",
        "broker_private_api_allowed",
        "ledger_append_allowed",
        "mode_apply_allowed",
        "parameter_apply_allowed",
        "would_send_to_broker",
    ):
        if packet.get(key) is not False:
            blockers.append(f"packet_false_required:{key}")
    header_index = page.find('live_shell.render_compact_page_header(get_text(lang, "warroom_title"))')
    nav_index = page.find('live_shell.render_folded_section("最初に見る場所 / WarRoom 入口", expanded=True)')
    guide_index = page.find('live_shell.render_folded_section(get_text(lang, "ui_label_guide"), expanded=False)')
    if not (0 <= header_index < nav_index < guide_index):
        blockers.append("render_order_header_nav_guide_invalid")

    return {
        "ok": True,
        "diagnostic_version": DIAGNOSTIC_VERSION,
        "ready": not blockers,
        "blockers": blockers,
        "packet": packet,
        "safety": {
            "production_ui_code_changed": True,
            "layout_only_change": True,
            "externalized_panel_module": True,
            "warroom_page_change_boundary": "import_and_single_render_call_only",
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
    result = run_warroom_operator_focus_nav_diagnostic()
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result.get("ready") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
