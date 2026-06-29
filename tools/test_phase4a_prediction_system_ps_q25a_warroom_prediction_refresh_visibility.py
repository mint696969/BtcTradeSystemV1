# path: ./tools/test_phase4a_prediction_system_ps_q25a_warroom_prediction_refresh_visibility.py
# desc: Focused pytest guard for PS-Q25A WarRoom prediction refresh visibility.

from __future__ import annotations

import json
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "btcts_next" / "src"
for candidate in (REPO_ROOT, SRC_ROOT):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

from tools.diagnose_phase4a_prediction_system_ps_q25a_warroom_prediction_refresh_visibility import (  # noqa: E402
    run_warroom_prediction_refresh_visibility_diagnostic,
)

DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q25A_WARROOM_PREDICTION_REFRESH_VISIBILITY_2026-06-30.md"
PANEL = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/latest_prediction_warroom_read_model_display_panel.py"


def test_q25a_doc_markers() -> None:
    text = DOC.read_text(encoding="utf-8-sig")
    for marker in (
        "ps_q25a_warroom_prediction_refresh_visibility=true",
        "warroom_prediction_panel_update_visibility_added=true",
        "prediction_data_generated_at_visible=true",
        "prediction_data_generated_at_jst_visible=true",
        "panel_refresh_heartbeat_jst_visible=true",
        "prediction_data_generation_and_panel_refresh_separated=true",
        "fragment_flag_status_uses_actual_render_argument=true",
        "autotrade_trigger_allowed=false",
        "broker_private_api_allowed=false",
        "runtime_artifact_write_allowed=false",
        "scheduler_action_changed=false",
    ):
        assert marker in text, marker


def test_q25a_diagnostic_ready() -> None:
    result = run_warroom_prediction_refresh_visibility_diagnostic()
    assert result["ok"] is True
    assert result["ready"] is True, result["blockers"]
    assert result["blockers"] == []
    packet = result["packet"]
    assert packet["prediction_update_visibility_version"] == "prediction_warroom.warroom_prediction_refresh_visibility.ps_q25a.v1"
    assert packet["operator_visible_prediction_update_visibility"] is True
    assert packet["prediction_update_visibility_rendered"] is True
    assert packet["prediction_data_generated_at_utc"] == "2026-06-29T17:40:20Z"
    assert "JST" in packet["prediction_data_generated_at_jst"]
    assert "JST" in packet["refresh_heartbeat_jst"]
    assert packet["warroom_prediction_display_auto_refresh_enabled"] is True
    assert packet["fragment_enabled"] is True
    assert packet["refresh_interval_sec"] == 5
    assert "prediction_data_generated_at_changes_only_when_producer_writes_new_artifact" in packet["prediction_update_visibility_note"]
    safety = result["safety"]
    assert safety["warroom_display_only"] is True
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


def test_panel_uses_render_argument_for_refresh_status() -> None:
    text = PANEL.read_text(encoding="utf-8")
    assert "def _render_panel_body(*, fragment_enabled: bool = True)" in text
    assert "fragment_enabled=bool(fragment_enabled)" in text
    body = text.split("def _render_panel_body", 1)[1].split("def render_latest_prediction_warroom_display_panel", 1)[0]
    assert "live_shell.supports_streamlit_fragment()" not in body
    assert "_render_prediction_update_visibility_strip(packet, lang=lang)" in text
    assert "latest_prediction_warroom_update_visibility_rows" in text


if __name__ == "__main__":
    test_q25a_doc_markers()
    test_q25a_diagnostic_ready()
    test_panel_uses_render_argument_for_refresh_status()
    print(json.dumps({"ok": True}, ensure_ascii=False))
