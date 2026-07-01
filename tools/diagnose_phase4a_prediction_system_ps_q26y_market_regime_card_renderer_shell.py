# path: ./tools/diagnose_phase4a_prediction_system_ps_q26y_market_regime_card_renderer_shell.py
# desc: Diagnostic for PS-Q26Y market regime card renderer shell.

from __future__ import annotations

import json
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "btcts_next" / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from btcts.apps.operator_ui.prediction_warroom.panels.warroom_market_regime_card_panel import (  # noqa: E402
    WARROOM_MARKET_REGIME_CARD_RENDERER_VERSION,
    build_sample_market_regime_cards,
    build_warroom_market_regime_card_renderer_packet,
    market_regime_cards_html,
)

DIAGNOSTIC_VERSION = "prediction_warroom.ps_q26y_market_regime_card_renderer_shell.v1"
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q26Y_MARKET_REGIME_CARD_RENDERER_SHELL_2026-07-01.md"
PANEL = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/warroom_market_regime_card_panel.py"
WARROOM_PAGE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py"
APP_TEST = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/tests/test_market_regime_card_renderer_q26y.py"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig") if path.exists() else ""


def run_market_regime_card_renderer_shell_diagnostic() -> dict:
    blockers: list[str] = []
    doc = _read(DOC)
    panel = _read(PANEL)
    page = _read(WARROOM_PAGE)
    app_test = _read(APP_TEST)
    for marker in (
        "ps_q26y_market_regime_card_renderer_shell=true",
        "base_reentry=PS_Q26X_MARKET_REGIME_CARD_CONTRACT_DONE",
        "sample_data_only=true",
        "live_data_connected=false",
        "warroom_page_changed=false",
        "warroom_page_mounted=false",
        "streamlit_render_function_declared=true",
        "streamlit_render_invoked_by_page=false",
        "horizontal_scroll_required=true",
        "cards_do_not_shrink=true",
        "full_width_target_horizon=24時間後",
        "freshness_encoded_by_badge_only=true",
        "border_meaning=evidence_quality",
        "runtime_read_allowed=false",
        "would_send_to_broker=false",
    ):
        if marker not in doc:
            blockers.append(f"doc_marker_required:{marker}")
    for marker in (
        "WARROOM_MARKET_REGIME_CARD_RENDERER_VERSION",
        "def build_sample_market_regime_cards",
        "def market_regime_cards_html",
        "def render_warroom_market_regime_card_shell",
        "overflow-x: auto",
        "min-width: 168px",
        "flex: 0 0 168px",
        "unsafe_allow_html=True",
    ):
        if marker not in panel:
            blockers.append(f"panel_marker_required:{marker}")
    q26z_sample_mount_present = "render_warroom_market_regime_card_shell" in page
    if "WARROOM_MARKET_REGIME_CARD_RENDERER_VERSION" in page:
        blockers.append("warroom_page_should_not_import_q26y_version_constant")
    for marker in (
        "test_q26y_sample_cards_cover_horizons_and_unknown",
        "test_q26y_html_uses_horizontal_scroll_and_fixed_card_width",
        "test_q26y_packet_preserves_safety_and_no_page_mount",
        "test_q26y_renderer_shell_remains_safe_after_later_mount",
    ):
        if marker not in app_test:
            blockers.append(f"test_marker_required:{marker}")

    cards = build_sample_market_regime_cards()
    packet = build_warroom_market_regime_card_renderer_packet()
    html = market_regime_cards_html(cards)
    if packet.get("renderer_version") != WARROOM_MARKET_REGIME_CARD_RENDERER_VERSION:
        blockers.append("renderer_version_mismatch")
    if packet.get("card_count") != 8:
        blockers.append("card_count_mismatch")
    if packet.get("horizons")[-1:] != ["24時間後"]:
        blockers.append("last_horizon_not_24h")
    if not any(card.get("regime_code") == "UNKNOWN" for card in cards):
        blockers.append("unknown_card_missing")
    for key in ("sample_data_only", "market_regime_first", "streamlit_render_function_declared", "horizontal_scroll_required", "cards_do_not_shrink", "detail_disclosure_available", "freshness_encoded_by_badge_only", "background_tone_is_readability_first", "production_ui_code_changed", "layout_only_change", "read_only", "display_only", "non_executing"):
        if packet.get(key) is not True:
            blockers.append(f"packet_true_required:{key}")
    for key in ("live_data_connected", "warroom_page_changed", "warroom_page_mounted", "other_prediction_cards_implemented", "streamlit_render_invoked_by_page", "runtime_read_allowed", "runtime_artifact_write_allowed", "status_artifact_write_allowed", "prediction_artifact_write_allowed", "view_artifact_write_allowed", "scheduler_enabled", "producer_enabled", "autotrade_trigger_allowed", "broker_private_api_allowed", "ledger_append_allowed", "mode_apply_allowed", "parameter_apply_allowed", "would_send_to_broker"):
        if packet.get(key) is not False:
            blockers.append(f"packet_false_required:{key}")
    for marker in ("overflow-x: auto", "min-width: 168px", "flex: 0 0 168px", "予測不能", "24時間後", "summary>詳細"):
        if marker not in html:
            blockers.append(f"html_marker_required:{marker}")

    return {
        "ok": True,
        "diagnostic_version": DIAGNOSTIC_VERSION,
        "ready": not blockers,
        "blockers": blockers,
        "packet": packet,
        "html_preview_contains_cards": "market-regime-card-shell" in html,
        "q26z_sample_mount_present": q26z_sample_mount_present,
        "safety": {
            "market_regime_first": True,
            "sample_data_only": True,
            "live_data_connected": False,
            "production_ui_code_changed": True,
            "warroom_page_changed": False,
            "warroom_page_mounted": False,
            "streamlit_render_function_declared": True,
            "streamlit_render_invoked_by_page": False,
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
    result = run_market_regime_card_renderer_shell_diagnostic()
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result.get("ready") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
