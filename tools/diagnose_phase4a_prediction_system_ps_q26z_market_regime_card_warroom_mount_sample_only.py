# path: ./tools/diagnose_phase4a_prediction_system_ps_q26z_market_regime_card_warroom_mount_sample_only.py
# desc: Diagnostic for PS-Q26Z sample-only market regime card WarRoom mount.

from __future__ import annotations

import json
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "btcts_next" / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from btcts.apps.operator_ui.prediction_warroom.panels.warroom_focus_layout_policy import (  # noqa: E402
    build_warroom_focus_layout_policy_packet,
    warroom_focus_section_expanded,
    warroom_focus_section_label,
)
from btcts.apps.operator_ui.prediction_warroom.panels.warroom_focus_sections import build_warroom_focus_section_renderer_packet  # noqa: E402
from btcts.apps.operator_ui.prediction_warroom.panels.warroom_market_regime_card_panel import build_warroom_market_regime_card_renderer_packet  # noqa: E402

DIAGNOSTIC_VERSION = "prediction_warroom.ps_q26z_market_regime_card_warroom_mount_sample_only.v1"
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q26Z_MARKET_REGIME_CARD_WARROOM_MOUNT_SAMPLE_ONLY_2026-07-01.md"
WARROOM_PAGE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py"
POLICY = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/warroom_focus_layout_policy.py"
SECTIONS = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/warroom_focus_sections.py"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig") if path.exists() else ""


def run_market_regime_card_warroom_mount_sample_only_diagnostic() -> dict:
    blockers: list[str] = []
    doc = _read(DOC)
    page = _read(WARROOM_PAGE)
    policy_text = _read(POLICY)
    sections_text = _read(SECTIONS)
    for marker in (
        "ps_q26z_market_regime_card_warroom_mount_sample_only=true",
        "base_reentry=PS_Q26Y_MARKET_REGIME_CARD_RENDERER_SHELL_DONE",
        "sample_data_only=true",
        "live_data_connected=false",
        "warroom_page_changed=true",
        "warroom_page_mounted=true",
        "streamlit_render_invoked_by_page=true",
        "runtime_read_allowed=false",
        "would_send_to_broker=false",
    ):
        if marker not in doc:
            blockers.append(f"doc_marker_required:{marker}")
    for marker in (
        "render_warroom_market_regime_card_shell",
        'render_warroom_focus_section("market_regime_card_sample")',
    ):
        if marker not in page:
            blockers.append(f"warroom_page_marker_required:{marker}")
    if "market_regime_card_sample" not in policy_text:
        blockers.append("policy_missing_market_regime_card_sample")
    if "market_regime_card_sample_expanded_default" not in sections_text:
        blockers.append("section_renderer_missing_market_regime_card_sample_forward")

    policy = build_warroom_focus_layout_policy_packet()
    section_packet = build_warroom_focus_section_renderer_packet()
    renderer = build_warroom_market_regime_card_renderer_packet()
    if warroom_focus_section_label("market_regime_card_sample") != "地合いカード / sample preview":
        blockers.append("market_regime_card_label_mismatch")
    if warroom_focus_section_expanded("market_regime_card_sample") is not True:
        blockers.append("market_regime_card_should_be_expanded_default")
    if policy.get("section_count") != 8:
        blockers.append("policy_section_count_should_be_8")
    if section_packet.get("section_count") != 8:
        blockers.append("section_renderer_count_should_be_8")
    if section_packet.get("market_regime_card_sample_expanded_default") is not True:
        blockers.append("section_renderer_market_regime_expanded_flag_missing")
    if renderer.get("sample_data_only") is not True:
        blockers.append("renderer_should_remain_sample_only")
    if renderer.get("live_data_connected") is not False:
        blockers.append("renderer_live_data_should_remain_false")
    if renderer.get("runtime_read_allowed") is not False:
        blockers.append("renderer_runtime_read_should_remain_false")
    if page.find('render_warroom_focus_section("operator_focus_nav")') > page.find('render_warroom_focus_section("market_regime_card_sample")'):
        blockers.append("market_regime_card_should_follow_operator_focus_nav")
    if page.find('render_warroom_focus_section("market_regime_card_sample")') > page.find('render_warroom_focus_section("prediction_quick_status_detail")'):
        blockers.append("market_regime_card_should_precede_quick_status")

    safety = {
        "market_regime_first": True,
        "other_prediction_cards_implemented": False,
        "production_ui_code_changed": True,
        "warroom_page_changed": True,
        "warroom_page_mounted": True,
        "sample_data_only": True,
        "live_data_connected": False,
        "streamlit_render_function_declared": True,
        "streamlit_render_invoked_by_page": True,
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
    }
    return {
        "ok": True,
        "diagnostic_version": DIAGNOSTIC_VERSION,
        "ready": not blockers,
        "blockers": blockers,
        "policy_section_count": policy.get("section_count"),
        "section_renderer_count": section_packet.get("section_count"),
        "renderer_packet": renderer,
        "safety": safety,
    }


def main() -> int:
    result = run_market_regime_card_warroom_mount_sample_only_diagnostic()
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result.get("ready") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
