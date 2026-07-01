# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/warroom_focus_sections.py
# desc: WarRoom focus section renderer wrapper. Layout-only wiring helper; no runtime writes, producer/scheduler, AutoTrade, broker, ledger, mode, or parameter behavior.

from __future__ import annotations

from typing import Any

from btcts.apps.operator_ui.components import live_shell
from btcts.apps.operator_ui.prediction_warroom.panels.warroom_focus_layout_policy import (
    build_warroom_focus_layout_policy_packet,
    warroom_focus_section_expanded,
    warroom_focus_section_label,
)

WARROOM_FOCUS_SECTION_RENDERER_VERSION = "prediction_warroom.focus_section_renderer.ps_q26q.v1"


def render_warroom_focus_section(section_id: str) -> Any:
    """Return the configured folded-section context manager for a WarRoom focus section."""
    return live_shell.render_folded_section(
        warroom_focus_section_label(section_id),
        expanded=warroom_focus_section_expanded(section_id),
    )


def build_warroom_focus_section_renderer_packet() -> dict[str, object]:
    policy_packet = build_warroom_focus_layout_policy_packet()
    return {
        "ok": True,
        "focus_section_renderer_version": WARROOM_FOCUS_SECTION_RENDERER_VERSION,
        "uses_externalized_layout_policy_module": True,
        "warroom_page_change_boundary": "import_and_focus_section_renderer_calls_only",
        "section_renderer_externalized": True,
        "section_count": policy_packet.get("section_count"),
        "rows": policy_packet.get("rows"),
        "operator_focus_nav_expanded_default": policy_packet.get("operator_focus_nav_expanded_default"),
        "quick_status_detail_folded_default": policy_packet.get("quick_status_detail_folded_default"),
        "live_nowcast_expanded_default": policy_packet.get("live_nowcast_expanded_default"),
        "latest_prediction_read_model_expanded_default": policy_packet.get("latest_prediction_read_model_expanded_default"),
        "header_alert_operator_expanded_default": policy_packet.get("header_alert_operator_expanded_default"),
        "market_evidence_detail_folded_default": policy_packet.get("market_evidence_detail_folded_default"),
        "operator_support_detail_folded_default": policy_packet.get("operator_support_detail_folded_default"),
        "secondary_detail_sections_folded_default": policy_packet.get("secondary_detail_sections_folded_default"),
        "keeps_existing_panels_available": True,
        "layout_only_change": True,
        "production_ui_code_changed": True,
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
    }
