# path: ./tools/test_phase4a_prediction_system_ps_q25i_warroom_prediction_panel_section_order_compact_layout_polish.py
# desc: Focused pytest guard for PS-Q25I WarRoom prediction panel section order and compact layout polish.

from __future__ import annotations

import json
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "btcts_next" / "src"
for candidate in (REPO_ROOT, SRC_ROOT):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

from tools.diagnose_phase4a_prediction_system_ps_q25i_warroom_prediction_panel_section_order_compact_layout_polish import (  # noqa: E402
    run_warroom_prediction_panel_section_order_compact_layout_polish_diagnostic,
)

DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q25I_WARROOM_PREDICTION_PANEL_SECTION_ORDER_COMPACT_LAYOUT_POLISH_2026-06-30.md"
PANEL = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/latest_prediction_warroom_read_model_display_panel.py"


def test_q25i_doc_markers() -> None:
    text = DOC.read_text(encoding="utf-8-sig")
    for marker in (
        "ps_q25i_warroom_prediction_panel_section_order_compact_layout_polish=true",
        "prediction_compact_layout_added=true",
        "operator_visible_compact_layout=true",
        "compact_layout_rendered=true",
        "compact_layout_top_priority=operator_action_guidance_first",
        "compact_layout_rows_visible=true",
        "compact_layout_detail_tables_still_visible=true",
        "layout_only_change=true",
        "producer_cadence_changed=false",
        "scheduler_action_changed=false",
        "autotrade_trigger_allowed=false",
        "broker_private_api_allowed=false",
    ):
        assert marker in text, marker


def test_q25i_diagnostic_ready() -> None:
    result = run_warroom_prediction_panel_section_order_compact_layout_polish_diagnostic()
    assert result["ok"] is True
    assert result["ready"] is True, result["blockers"]
    assert result["blockers"] == []
    compact = result["compact_layout"]
    packet = result["panel_packet"]
    assert compact["compact_layout_version"] == "prediction_warroom.prediction_panel_section_order_compact_layout.ps_q25i.v1"
    assert compact["compact_layout_top_priority"] == "operator_action_guidance_first"
    assert compact["compact_layout_detail_tables_still_visible"] is True
    assert len(compact["compact_layout_rows"]) == 5
    assert packet["operator_visible_compact_layout"] is True
    assert packet["compact_layout_rendered"] is True
    safety = result["safety"]
    assert safety["layout_only_change"] is True
    assert safety["warroom_display_only"] is True
    assert safety["producer_cadence_changed"] is False
    for key in (
        "runtime_artifact_write_allowed",
        "status_artifact_write_allowed",
        "prediction_artifact_write_allowed",
        "view_artifact_write_allowed",
        "scheduler_action_changed",
        "scheduler_enabled",
        "autotrade_trigger_allowed",
        "broker_private_api_allowed",
        "ledger_append_allowed",
        "mode_apply_allowed",
        "parameter_apply_allowed",
        "would_send_to_broker",
    ):
        assert safety[key] is False


def test_q25i_panel_safe_and_render_markers() -> None:
    text = PANEL.read_text(encoding="utf-8")
    for marker in (
        "WARROOM_PREDICTION_COMPACT_LAYOUT_VERSION",
        "latest_prediction_warroom_compact_layout_rows",
        "latest_prediction_warroom_compact_layout_packet",
        "_render_prediction_compact_operator_header",
        "compact_layout_rendered",
        "operator_action_guidance_first",
    ):
        assert marker in text, marker
    render_body_start = text.find("def _render_panel_body")
    render_body_end = text.find("\ndef render_latest_prediction_warroom_display_panel", render_body_start)
    render_body_text = text[render_body_start:render_body_end]
    assert render_body_text.find("_render_prediction_compact_operator_header") < render_body_text.find("_render_refresh_status_strip")
    for forbidden in (
        "Set-ScheduledTask",
        "Enable-ScheduledTask",
        "Disable-ScheduledTask",
        "Register-ScheduledTask",
        "New-ScheduledTaskTrigger",
        "append_decision_jsonl",
        "run_shadow_decision_from_snapshot",
        "submit_mode_change_command_request",
        "validate_and_append_command",
        "send_order(",
        "place_order(",
        "create_order(",
        ".write_text(",
        ".write_bytes(",
        "os.replace",
        "shutil.copy2",
    ):
        assert forbidden not in text, forbidden


if __name__ == "__main__":
    test_q25i_doc_markers()
    test_q25i_diagnostic_ready()
    test_q25i_panel_safe_and_render_markers()
    print(json.dumps({"ok": True}, ensure_ascii=False))
