# path: ./tools/diagnose_phase4a_prediction_system_ps_q27b_market_regime_card_detail_popover.py
# desc: Diagnostic for PS-Q27B market regime card detail popover.

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
    WARROOM_MARKET_REGIME_CARD_DETAIL_POPOVER_VERSION,
    build_warroom_market_regime_card_renderer_packet,
    market_regime_cards_html,
)
from tools.diagnose_phase4a_prediction_system_ps_q27a_market_regime_card_visual_tune import run_market_regime_card_visual_tune_diagnostic  # noqa: E402
from tools.diagnose_phase4a_prediction_system_ps_q26z_market_regime_card_warroom_mount_sample_only import run_market_regime_card_warroom_mount_sample_only_diagnostic  # noqa: E402

DIAGNOSTIC_VERSION = "prediction_warroom.ps_q27b_market_regime_card_detail_popover.v1"
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q27B_MARKET_REGIME_CARD_DETAIL_POPOVER_2026-07-01.md"
PANEL = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/warroom_market_regime_card_panel.py"
WARROOM_PAGE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig") if path.exists() else ""


def run_market_regime_card_detail_popover_diagnostic() -> dict:
    blockers: list[str] = []
    doc = _read(DOC)
    panel = _read(PANEL)
    page = _read(WARROOM_PAGE)
    q27a = run_market_regime_card_visual_tune_diagnostic()
    q26z = run_market_regime_card_warroom_mount_sample_only_diagnostic()
    packet = build_warroom_market_regime_card_renderer_packet()
    html = market_regime_cards_html(packet["cards"])

    for marker in (
        "ps_q27b_market_regime_card_detail_popover=true",
        "base_reentry=PS_Q27A_MARKET_REGIME_CARD_VISUAL_TUNE_DONE",
        "visual_interaction_tune_only=true",
        "detail_disclosure_mode=popover",
        "detail_popover_enabled=true",
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
        "WARROOM_MARKET_REGIME_CARD_DETAIL_POPOVER_VERSION",
        "detail_disclosure_mode",
        "detail_popover_enabled",
        "inline_detail_expansion_enabled",
        "no_vertical_layout_shift_on_detail_open",
        "mr-popover-details",
        "mr-detail-popover",
        "position: absolute",
        "z-index: 40",
    ):
        if marker not in panel:
            blockers.append(f"panel_marker_required:{marker}")
    for marker in (
        "mr-popover-details",
        "mr-detail-button",
        "mr-detail-popover",
        "position: absolute",
        "z-index: 40",
        "summary class='mr-detail-button'",
        "概要",
        "読み方",
        "情報源",
    ):
        if marker not in html:
            blockers.append(f"html_marker_required:{marker}")
    for forbidden in ("<details class='mr-details'>", "class='mr-details'", "<summary>詳細</summary>"):
        if forbidden in html:
            blockers.append(f"inline_detail_marker_should_be_removed:{forbidden}")
    if packet.get("detail_popover_version") != WARROOM_MARKET_REGIME_CARD_DETAIL_POPOVER_VERSION:
        blockers.append("detail_popover_version_missing_from_packet")
    if packet.get("detail_disclosure_mode") != "popover":
        blockers.append("detail_disclosure_mode_should_be_popover")
    if packet.get("detail_popover_enabled") is not True:
        blockers.append("detail_popover_enabled_required")
    if packet.get("inline_detail_expansion_enabled") is not False:
        blockers.append("inline_detail_expansion_should_be_false")
    if packet.get("no_vertical_layout_shift_on_detail_open") is not True:
        blockers.append("no_vertical_layout_shift_flag_required")
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
    if q27a.get("ready") is not True:
        blockers.append("q27a_diagnostic_not_ready")
    if q26z.get("ready") is not True:
        blockers.append("q26z_diagnostic_not_ready")

    return {
        "ok": True,
        "diagnostic_version": DIAGNOSTIC_VERSION,
        "ready": not blockers,
        "blockers": blockers,
        "detail_popover_version": WARROOM_MARKET_REGIME_CARD_DETAIL_POPOVER_VERSION,
        "packet": packet,
        "q27a_ready": q27a.get("ready"),
        "q26z_ready": q26z.get("ready"),
        "safety": {
            "visual_interaction_tune_only": True,
            "production_ui_code_changed": True,
            "warroom_page_changed": False,
            "warroom_page_mounted_unchanged": True,
            "sample_data_only": True,
            "live_data_connected": False,
            "detail_disclosure_mode": "popover",
            "detail_popover_enabled": True,
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
    result = run_market_regime_card_detail_popover_diagnostic()
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result.get("ready") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
