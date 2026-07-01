# path: ./tools/diagnose_phase4a_prediction_system_ps_q26v_warroom_operator_focus_route_table_fold.py
# desc: Diagnostic for PS-Q26V WarRoom operator focus route table fold.

from __future__ import annotations

import json
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "btcts_next" / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from btcts.apps.operator_ui.prediction_warroom.panels.warroom_operator_focus_nav_panel import (  # noqa: E402
    WARROOM_OPERATOR_FOCUS_ROUTE_TABLE_FOLD_VERSION,
    build_warroom_operator_focus_nav_packet,
)

DIAGNOSTIC_VERSION = "prediction_warroom.ps_q26v_warroom_operator_focus_route_table_fold.v1"
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q26V_WARROOM_OPERATOR_FOCUS_ROUTE_TABLE_FOLD_2026-07-01.md"
PANEL = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/warroom_operator_focus_nav_panel.py"
PAGE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py"
APP_TEST = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_operator_focus_route_table_fold_q26v.py"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig") if path.exists() else ""


def run_warroom_operator_focus_route_table_fold_diagnostic() -> dict:
    blockers: list[str] = []
    doc = _read(DOC)
    panel = _read(PANEL)
    page = _read(PAGE)
    app_test = _read(APP_TEST)
    for marker in (
        "ps_q26v_warroom_operator_focus_route_table_fold=true",
        "warroom_page_slimming_main_goal=false",
        "route_table_folded_default=true",
        "reduces_first_screen_table_density=true",
        "visual_only_change=true",
        "would_send_to_broker=false",
    ):
        if marker not in doc:
            blockers.append(f"doc_marker_required:{marker}")
    for marker in (
        "WARROOM_OPERATOR_FOCUS_ROUTE_TABLE_FOLD_VERSION",
        "def warroom_operator_focus_route_table_fold_label()",
        "route_table_folded_default",
        "reduces_first_screen_table_density",
        "with st.expander(str(packet[\"route_table_label\"]), expanded=False)",
    ):
        if marker not in panel:
            blockers.append(f"panel_marker_required:{marker}")
    if "WARROOM_OPERATOR_FOCUS_ROUTE_TABLE_FOLD_VERSION" in page:
        blockers.append("warroom_page_should_not_change_for_route_table_fold")
    for marker in (
        "test_q26v_route_text_remains_visible_while_route_table_is_folded",
        "test_q26v_render_folds_route_table_and_does_not_touch_page",
    ):
        if marker not in app_test:
            blockers.append(f"test_marker_required:{marker}")

    packet = build_warroom_operator_focus_nav_packet()
    if packet.get("focus_route_table_fold_version") != WARROOM_OPERATOR_FOCUS_ROUTE_TABLE_FOLD_VERSION:
        blockers.append("focus_route_table_fold_version_mismatch")
    for key in ("visual_route_text_visible", "visual_route_strip_visible", "route_table_available", "route_table_folded_default", "detail_table_folded_default", "command_cards_visible", "read_only", "display_only", "non_executing", "layout_only_change", "visual_only_change", "reduces_first_screen_table_density"):
        if packet.get(key) is not True:
            blockers.append(f"packet_true_required:{key}")
    for key in ("warroom_page_changed", "warroom_page_slimming_main_goal"):
        if packet.get(key) is not False:
            blockers.append(f"packet_false_required:{key}")
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
            "warroom_page_changed": False,
            "warroom_page_slimming_main_goal": False,
            "visual_only_change": True,
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
    result = run_warroom_operator_focus_route_table_fold_diagnostic()
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result.get("ready") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
