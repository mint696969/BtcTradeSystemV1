# path: ./tools/diagnose_phase4a_prediction_system_ps_q27c_market_regime_card_selected_detail_panel.py
# desc: Diagnostic for PS-Q27C market regime card detail overlay.

from __future__ import annotations

import json
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
SRC_ROOT = REPO_ROOT / "btcts_next" / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from btcts.apps.operator_ui.prediction_warroom.panels.warroom_market_regime_card_panel import (  # noqa: E402
    WARROOM_MARKET_REGIME_CARD_SELECTED_DETAIL_PANEL_VERSION,
    build_warroom_market_regime_card_renderer_packet,
    market_regime_cards_html,
)
from tools.diagnose_phase4a_prediction_system_ps_q27b_market_regime_card_detail_popover import run_market_regime_card_detail_popover_diagnostic  # noqa: E402
from tools.diagnose_phase4a_prediction_system_ps_q27a_market_regime_card_visual_tune import run_market_regime_card_visual_tune_diagnostic  # noqa: E402
from tools.diagnose_phase4a_prediction_system_ps_q26z_market_regime_card_warroom_mount_sample_only import run_market_regime_card_warroom_mount_sample_only_diagnostic  # noqa: E402

DIAGNOSTIC_VERSION = "prediction_warroom.ps_q27c_market_regime_card_detail_overlay.v1"
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q27C_MARKET_REGIME_CARD_SELECTED_DETAIL_PANEL_2026-07-01.md"
PANEL = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/warroom_market_regime_card_panel.py"
WARROOM_PAGE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig") if path.exists() else ""


def run_market_regime_card_selected_detail_panel_diagnostic() -> dict:
    blockers: list[str] = []
    doc = _read(DOC)
    panel = _read(PANEL)
    page = _read(WARROOM_PAGE)
    packet = build_warroom_market_regime_card_renderer_packet()
    html = market_regime_cards_html(packet["cards"])
    q27b = run_market_regime_card_detail_popover_diagnostic()
    q27a = run_market_regime_card_visual_tune_diagnostic()
    q26z = run_market_regime_card_warroom_mount_sample_only_diagnostic()

    for marker in (
        "ps_q27c_market_regime_card_detail_overlay=true",
        "base_reentry=PS_Q27B_MARKET_REGIME_CARD_DETAIL_POPOVER_DONE",
        "detail_disclosure_mode=card_overlay",
        "card_detail_overlay_enabled=true",
        "overlay_covers_card_row=true",
        "overlay_close_button_enabled=true",
        "selected_detail_panel_enabled=false",
        "detail_popover_enabled=false",
        "inline_detail_expansion_enabled=false",
        "no_vertical_layout_shift_on_detail_open=true",
        "card_width_px=208",
        "horizon_font_size_rem=0.92rem",
        "warroom_page_changed=false",
        "sample_data_only=true",
        "live_data_connected=false",
        "runtime_read_allowed=false",
        "would_send_to_broker=false",
    ):
        if marker not in doc:
            blockers.append(f"doc_marker_required:{marker}")
    for marker in (
        "WARROOM_MARKET_REGIME_CARD_SELECTED_DETAIL_PANEL_VERSION",
        "detail_disclosure_mode",
        "mr-detail-radio",
        "market-regime-card-stage",
        "mr-card-detail-overlay",
        "mr-overlay-close",
        "mr-overlay-detail-content",
    ):
        if marker not in panel:
            blockers.append(f"panel_marker_required:{marker}")
    for marker in (
        "market-regime-card-root",
        "market-regime-card-stage",
        "mr-detail-radio",
        "mr-detail-selector-button",
        "mr-card-detail-overlay",
        "mr-overlay-close",
        "mr-overlay-detail-content",
        "地合いカード詳細",
        "position: absolute",
        "z-index: 40",
        "overflow-x: auto",
    ):
        if marker not in html:
            blockers.append(f"html_marker_required:{marker}")
    for forbidden in ("mr-popover-details", "mr-detail-popover", "mr-selected-detail-panel", "選択中カードの詳細", "<details class='mr-details'>"):
        if forbidden in html:
            blockers.append(f"old_detail_marker_should_be_removed:{forbidden}")
    if packet.get("selected_detail_panel_version") != WARROOM_MARKET_REGIME_CARD_SELECTED_DETAIL_PANEL_VERSION:
        blockers.append("q27c_version_missing_from_packet")
    if packet.get("detail_disclosure_mode") != "card_overlay":
        blockers.append("detail_disclosure_mode_should_be_card_overlay")
    if packet.get("card_detail_overlay_enabled") is not True:
        blockers.append("card_detail_overlay_enabled_required")
    if packet.get("overlay_covers_card_row") is not True:
        blockers.append("overlay_covers_card_row_required")
    if packet.get("overlay_close_button_enabled") is not True:
        blockers.append("overlay_close_button_enabled_required")
    if packet.get("selected_detail_panel_enabled") is not False:
        blockers.append("selected_detail_panel_should_be_false")
    if packet.get("detail_popover_enabled") is not False:
        blockers.append("detail_popover_should_be_false")
    if packet.get("inline_detail_expansion_enabled") is not False:
        blockers.append("inline_detail_expansion_should_be_false")
    if packet.get("no_vertical_layout_shift_on_detail_open") is not True:
        blockers.append("no_vertical_layout_shift_on_detail_open_required")
    if packet.get("card_width_px") != 208:
        blockers.append("card_width_should_remain_208")
    if packet.get("horizon_font_size_rem") != "0.92rem":
        blockers.append("horizon_font_size_should_remain_0_92rem")
    for key in ("sample_data_only", "horizontal_scroll_required", "cards_do_not_shrink", "freshness_encoded_by_badge_only", "read_only", "display_only", "non_executing"):
        if packet.get(key) is not True:
            blockers.append(f"packet_true_required:{key}")
    for key in ("live_data_connected", "runtime_read_allowed", "runtime_artifact_write_allowed", "status_artifact_write_allowed", "prediction_artifact_write_allowed", "view_artifact_write_allowed", "scheduler_enabled", "producer_enabled", "autotrade_trigger_allowed", "broker_private_api_allowed", "ledger_append_allowed", "mode_apply_allowed", "parameter_apply_allowed", "would_send_to_broker"):
        if packet.get(key) is not False:
            blockers.append(f"packet_false_required:{key}")
    if "render_warroom_market_regime_card_shell" not in page:
        blockers.append("warroom_page_mount_missing")
    if q27b.get("ready") is not True:
        blockers.append("q27b_diagnostic_not_ready")
    if q27a.get("ready") is not True:
        blockers.append("q27a_diagnostic_not_ready")
    if q26z.get("ready") is not True:
        blockers.append("q26z_diagnostic_not_ready")

    return {
        "ok": True,
        "diagnostic_version": DIAGNOSTIC_VERSION,
        "ready": not blockers,
        "blockers": blockers,
        "selected_detail_panel_version": WARROOM_MARKET_REGIME_CARD_SELECTED_DETAIL_PANEL_VERSION,
        "packet": packet,
        "q27b_ready": q27b.get("ready"),
        "q27a_ready": q27a.get("ready"),
        "q26z_ready": q26z.get("ready"),
        "safety": {
            "visual_interaction_tune_only": True,
            "production_ui_code_changed": True,
            "warroom_page_changed": False,
            "warroom_page_mounted_unchanged": True,
            "sample_data_only": True,
            "live_data_connected": False,
            "detail_disclosure_mode": "card_overlay",
            "card_detail_overlay_enabled": True,
            "overlay_covers_card_row": True,
            "overlay_close_button_enabled": True,
            "selected_detail_panel_enabled": False,
            "detail_popover_enabled": False,
            "inline_detail_expansion_enabled": False,
            "no_vertical_layout_shift_on_detail_open": True,
            "read_only": True,
            "display_only": True,
            "non_executing": True,
            "runtime_read_allowed": False,
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
    result = run_market_regime_card_selected_detail_panel_diagnostic()
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result.get("ready") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
