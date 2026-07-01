# path: ./tools/diagnose_phase4a_prediction_system_ps_q26t_warroom_operator_focus_command_cards.py
# desc: Diagnostic for PS-Q26T WarRoom operator focus command cards.

from __future__ import annotations

import json
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "btcts_next" / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from btcts.apps.operator_ui.prediction_warroom.panels.warroom_operator_focus_nav_panel import (  # noqa: E402
    WARROOM_OPERATOR_FOCUS_COMMAND_CARDS_VERSION,
    build_warroom_operator_focus_nav_packet,
    warroom_operator_focus_card_rows,
)

DIAGNOSTIC_VERSION = "prediction_warroom.ps_q26t_warroom_operator_focus_command_cards.v1"
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q26T_WARROOM_OPERATOR_FOCUS_COMMAND_CARDS_2026-07-01.md"
PANEL = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/warroom_operator_focus_nav_panel.py"
PAGE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py"
APP_TEST = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_operator_focus_command_cards_q26t.py"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig") if path.exists() else ""


def run_warroom_operator_focus_command_cards_diagnostic() -> dict:
    blockers: list[str] = []
    doc = _read(DOC)
    panel = _read(PANEL)
    page = _read(PAGE)
    app_test = _read(APP_TEST)
    for marker in (
        "ps_q26t_warroom_operator_focus_command_cards=true",
        "warroom_page_slimming_main_goal=false",
        "command_cards_visible=true",
        "improves_first_screen_glanceability=true",
        "visual_only_change=true",
        "would_send_to_broker=false",
    ):
        if marker not in doc:
            blockers.append(f"doc_marker_required:{marker}")
    for marker in (
        "WARROOM_OPERATOR_FOCUS_COMMAND_CARDS_VERSION",
        "def warroom_operator_focus_card_rows()",
        "command_cards_visible",
        "improves_first_screen_glanceability",
        "st.columns",
    ):
        if marker not in panel:
            blockers.append(f"panel_marker_required:{marker}")
    if "WARROOM_OPERATOR_FOCUS_COMMAND_CARDS_VERSION" in page:
        blockers.append("warroom_page_should_not_change_for_command_cards")
    for marker in (
        "test_q26t_command_cards_are_three_primary_reading_cards",
        "test_q26t_packet_marks_command_cards_visual_only_and_page_untouched",
    ):
        if marker not in app_test:
            blockers.append(f"test_marker_required:{marker}")

    cards = warroom_operator_focus_card_rows()
    packet = build_warroom_operator_focus_nav_packet()
    if packet.get("focus_command_cards_version") != WARROOM_OPERATOR_FOCUS_COMMAND_CARDS_VERSION:
        blockers.append("focus_command_cards_version_mismatch")
    if packet.get("command_cards_visible") is not True:
        blockers.append("command_cards_visible_not_true")
    if packet.get("card_row_count") != 3 or len(cards) != 3:
        blockers.append(f"card_row_count_not_3:{packet.get('card_row_count')}/{len(cards)}")
    if [card.get("card_id") for card in cards] != ["current_state", "prediction_read", "operator_alert"]:
        blockers.append("card_order_invalid")
    for key in ("read_only", "display_only", "non_executing", "layout_only_change", "visual_only_change", "improves_first_screen_glanceability"):
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
    result = run_warroom_operator_focus_command_cards_diagnostic()
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result.get("ready") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
