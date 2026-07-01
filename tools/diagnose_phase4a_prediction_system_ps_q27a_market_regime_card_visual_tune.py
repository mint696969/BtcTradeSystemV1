# path: ./tools/diagnose_phase4a_prediction_system_ps_q27a_market_regime_card_visual_tune.py
# desc: Diagnostic for PS-Q27A market regime card visual tune.

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
    MARKET_REGIME_CARD_HORIZON_FONT_SIZE_REM,
    MARKET_REGIME_CARD_WIDTH_PX,
    WARROOM_MARKET_REGIME_CARD_VISUAL_TUNE_VERSION,
    build_warroom_market_regime_card_renderer_packet,
    market_regime_cards_html,
)
from tools.diagnose_phase4a_prediction_system_ps_q26z_market_regime_card_warroom_mount_sample_only import run_market_regime_card_warroom_mount_sample_only_diagnostic  # noqa: E402

DIAGNOSTIC_VERSION = "prediction_warroom.ps_q27a_market_regime_card_visual_tune.v1"
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q27A_MARKET_REGIME_CARD_VISUAL_TUNE_2026-07-01.md"
PANEL = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/warroom_market_regime_card_panel.py"
WARROOM_PAGE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig") if path.exists() else ""


def run_market_regime_card_visual_tune_diagnostic() -> dict:
    blockers: list[str] = []
    doc = _read(DOC)
    panel = _read(PANEL)
    page = _read(WARROOM_PAGE)
    q26z = run_market_regime_card_warroom_mount_sample_only_diagnostic()
    packet = build_warroom_market_regime_card_renderer_packet()
    html = market_regime_cards_html(packet["cards"])

    for marker in (
        "ps_q27a_market_regime_card_visual_tune=true",
        "base_reentry=PS_Q26Z_MARKET_REGIME_CARD_WARROOM_MOUNT_SAMPLE_ONLY_DONE",
        "visual_tune_only=true",
        "card_width_px_before=168",
        "card_width_px_after=208",
        "card_width_expanded_by_px=40",
        "horizon_font_size_rem_before=0.82",
        "horizon_font_size_rem_after=0.92",
        "horizon_label_text_unchanged=true",
        "warroom_page_changed=false",
        "sample_data_only=true",
        "live_data_connected=false",
        "runtime_read_allowed=false",
        "would_send_to_broker=false",
    ):
        if marker not in doc:
            blockers.append(f"doc_marker_required:{marker}")
    for marker in (
        "WARROOM_MARKET_REGIME_CARD_VISUAL_TUNE_VERSION",
        "MARKET_REGIME_CARD_WIDTH_PX = 208",
        'MARKET_REGIME_CARD_HORIZON_FONT_SIZE_REM = "0.92rem"',
        "MARKET_REGIME_CARD_WIDTH_PX = 208",
        "MARKET_REGIME_CARD_HORIZON_FONT_SIZE_REM",
        "def market_regime_cards_html",
    ):
        if marker not in panel:
            blockers.append(f"panel_marker_required:{marker}")
    for marker in (
        "min-width: 208px",
        "max-width: 208px",
        "flex: 0 0 208px",
        "font-size: 0.92rem",
        "現在",
        "24時間後",
    ):
        if marker not in html:
            blockers.append(f"html_marker_required:{marker}")
    if MARKET_REGIME_CARD_WIDTH_PX != 208:
        blockers.append("card_width_px_should_be_208")
    if MARKET_REGIME_CARD_HORIZON_FONT_SIZE_REM != "0.92rem":
        blockers.append("horizon_font_size_should_be_0_92rem")
    if packet.get("visual_tune_version") != WARROOM_MARKET_REGIME_CARD_VISUAL_TUNE_VERSION:
        blockers.append("visual_tune_version_missing_from_packet")
    if packet.get("card_width_px") != 208:
        blockers.append("packet_card_width_px_mismatch")
    if packet.get("horizon_font_size_rem") != "0.92rem":
        blockers.append("packet_horizon_font_size_mismatch")
    if packet.get("horizon_label_text_unchanged") is not True:
        blockers.append("horizon_label_text_should_be_unchanged")
    for key in ("sample_data_only", "horizontal_scroll_required", "cards_do_not_shrink", "freshness_encoded_by_badge_only", "read_only", "display_only", "non_executing"):
        if packet.get(key) is not True:
            blockers.append(f"packet_true_required:{key}")
    for key in ("live_data_connected", "runtime_read_allowed", "runtime_artifact_write_allowed", "status_artifact_write_allowed", "prediction_artifact_write_allowed", "view_artifact_write_allowed", "scheduler_enabled", "producer_enabled", "autotrade_trigger_allowed", "broker_private_api_allowed", "ledger_append_allowed", "mode_apply_allowed", "parameter_apply_allowed", "would_send_to_broker"):
        if packet.get(key) is not False:
            blockers.append(f"packet_false_required:{key}")
    if "render_warroom_market_regime_card_shell" not in page:
        blockers.append("warroom_page_mount_missing")
    if q26z.get("ready") is not True:
        blockers.append("q26z_diagnostic_not_ready")

    return {
        "ok": True,
        "diagnostic_version": DIAGNOSTIC_VERSION,
        "ready": not blockers,
        "blockers": blockers,
        "visual_tune_version": WARROOM_MARKET_REGIME_CARD_VISUAL_TUNE_VERSION,
        "card_width_px": MARKET_REGIME_CARD_WIDTH_PX,
        "horizon_font_size_rem": MARKET_REGIME_CARD_HORIZON_FONT_SIZE_REM,
        "packet": packet,
        "q26z_ready": q26z.get("ready"),
        "safety": {
            "visual_tune_only": True,
            "production_ui_code_changed": True,
            "warroom_page_changed": False,
            "warroom_page_mounted_unchanged": True,
            "sample_data_only": True,
            "live_data_connected": False,
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
    result = run_market_regime_card_visual_tune_diagnostic()
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result.get("ready") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
