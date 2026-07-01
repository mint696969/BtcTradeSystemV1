# path: ./tools/diagnose_phase4a_prediction_system_ps_q27d_market_regime_card_typography_badge_tune.py
# desc: Diagnostic for PS-Q27D market regime card typography and freshness badge visual tune.

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
    WARROOM_MARKET_REGIME_CARD_TYPOGRAPHY_BADGE_TUNE_VERSION,
    build_warroom_market_regime_card_renderer_packet,
    market_regime_cards_html,
)
from tools.diagnose_phase4a_prediction_system_ps_q27c_market_regime_card_selected_detail_panel import run_market_regime_card_selected_detail_panel_diagnostic  # noqa: E402
from tools.diagnose_phase4a_prediction_system_ps_q27b_market_regime_card_detail_popover import run_market_regime_card_detail_popover_diagnostic  # noqa: E402

DIAGNOSTIC_VERSION = "prediction_warroom.ps_q27d_market_regime_card_typography_badge_tune.v1"
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q27D_MARKET_REGIME_CARD_TYPOGRAPHY_BADGE_TUNE_2026-07-01.md"
PANEL = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/warroom_market_regime_card_panel.py"
WARROOM_PAGE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig") if path.exists() else ""


def run_market_regime_card_typography_badge_tune_diagnostic() -> dict:
    blockers: list[str] = []
    doc = _read(DOC)
    panel = _read(PANEL)
    page = _read(WARROOM_PAGE)
    q27c = run_market_regime_card_selected_detail_panel_diagnostic()
    q27b = run_market_regime_card_detail_popover_diagnostic()
    packet = build_warroom_market_regime_card_renderer_packet()
    html = market_regime_cards_html(packet["cards"])

    for marker in (
        "ps_q27d_market_regime_card_typography_badge_tune=true",
        "base_reentry=PS_Q27C_MARKET_REGIME_CARD_DETAIL_OVERLAY_DONE",
        "visual_typography_tune_only=true",
        "time_axis_font_size_unchanged=true",
        "horizon_font_size_rem=0.92rem",
        "regime_font_size_after=1.14rem",
        "confidence_font_size_after=1.60rem",
        "tag_font_size_after=1.04rem",
        "freshness_badge_visibility_tuned=true",
        "freshness_badge_font_size_after=0.78rem",
        "freshness_badge_font_weight_after=900",
        "freshness_badge_min_width_after=42px",
        "detail_overlay_background=#F2F4F7",
        "detail_overlay_background_matches_unknown=true",
        "warroom_page_changed=false",
        "sample_data_only=true",
        "live_data_connected=false",
        "runtime_read_allowed=false",
        "would_send_to_broker=false",
    ):
        if marker not in doc:
            blockers.append(f"doc_marker_required:{marker}")
    for marker in (
        "WARROOM_MARKET_REGIME_CARD_TYPOGRAPHY_BADGE_TUNE_VERSION",
        "typography_badge_tune_version",
        "time_axis_font_size_unchanged",
        "regime_font_size_rem",
        "confidence_font_size_rem",
        "tag_font_size_rem",
        "freshness_badge_visibility_tuned",
        "freshness_badge_min_width_px",
    ):
        if marker not in panel:
            blockers.append(f"panel_marker_required:{marker}")
    for marker in (
        "font-size: 0.92rem",
        "font-size: 1.14rem",
        "font-size: 1.60rem",
        "font-size: 1.04rem",
        "font-size: 0.78rem",
        "font-weight: 900",
        "min-width: 42px",
        "letter-spacing: 0.02em",
        "padding: 3px 8px",
        "border: 1px solid rgba(16, 24, 40, 0.22)",
        "background: #F2F4F7",
    ):
        if marker not in html:
            blockers.append(f"html_marker_required:{marker}")
    if packet.get("typography_badge_tune_version") != WARROOM_MARKET_REGIME_CARD_TYPOGRAPHY_BADGE_TUNE_VERSION:
        blockers.append("typography_badge_tune_version_missing_from_packet")
    expected = {
        "time_axis_font_size_unchanged": True,
        "freshness_badge_visibility_tuned": True,
        "regime_font_size_rem": "1.14rem",
        "confidence_font_size_rem": "1.60rem",
        "tag_font_size_rem": "1.04rem",
        "freshness_badge_font_size_rem": "0.78rem",
        "freshness_badge_font_weight": 900,
        "freshness_badge_min_width_px": 42,
        "detail_overlay_background": "#F2F4F7",
        "detail_overlay_background_matches_unknown": True,
    }
    for key, value in expected.items():
        if packet.get(key) != value:
            blockers.append(f"packet_value_required:{key}={value!r}")
    if packet.get("horizon_font_size_rem") != "0.92rem":
        blockers.append("packet_horizon_font_size_changed")
    if packet.get("detail_disclosure_mode") != "card_overlay":
        blockers.append("detail_overlay_should_remain")
    if packet.get("card_width_px") != 208:
        blockers.append("card_width_should_remain_208")
    for key in ("sample_data_only", "horizontal_scroll_required", "cards_do_not_shrink", "freshness_encoded_by_badge_only", "read_only", "display_only", "non_executing"):
        if packet.get(key) is not True:
            blockers.append(f"packet_true_required:{key}")
    for key in ("live_data_connected", "runtime_read_allowed", "runtime_artifact_write_allowed", "status_artifact_write_allowed", "prediction_artifact_write_allowed", "view_artifact_write_allowed", "scheduler_enabled", "producer_enabled", "autotrade_trigger_allowed", "broker_private_api_allowed", "ledger_append_allowed", "mode_apply_allowed", "parameter_apply_allowed", "would_send_to_broker"):
        if packet.get(key) is not False:
            blockers.append(f"packet_false_required:{key}")
    if "render_warroom_market_regime_card_shell" not in page:
        blockers.append("warroom_page_mount_missing")
    if q27c.get("ready") is not True:
        blockers.append("q27c_diagnostic_not_ready")
    if q27b.get("ready") is not True:
        blockers.append("q27b_diagnostic_not_ready")

    return {
        "ok": True,
        "diagnostic_version": DIAGNOSTIC_VERSION,
        "ready": not blockers,
        "blockers": blockers,
        "typography_badge_tune_version": WARROOM_MARKET_REGIME_CARD_TYPOGRAPHY_BADGE_TUNE_VERSION,
        "packet": packet,
        "q27c_ready": q27c.get("ready"),
        "q27b_ready": q27b.get("ready"),
        "safety": {
            "visual_typography_tune_only": True,
            "production_ui_code_changed": True,
            "warroom_page_changed": False,
            "warroom_page_mounted_unchanged": True,
            "sample_data_only": True,
            "live_data_connected": False,
            "time_axis_font_size_unchanged": True,
            "detail_disclosure_mode": "card_overlay",
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
    result = run_market_regime_card_typography_badge_tune_diagnostic()
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result.get("ready") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
