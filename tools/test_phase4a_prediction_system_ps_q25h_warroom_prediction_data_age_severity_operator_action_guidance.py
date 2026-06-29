# path: ./tools/test_phase4a_prediction_system_ps_q25h_warroom_prediction_data_age_severity_operator_action_guidance.py
# desc: Focused pytest guard for PS-Q25H WarRoom prediction data age severity and operator action guidance.

from __future__ import annotations

import json
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "btcts_next" / "src"
for candidate in (REPO_ROOT, SRC_ROOT):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

from tools.diagnose_phase4a_prediction_system_ps_q25h_warroom_prediction_data_age_severity_operator_action_guidance import (  # noqa: E402
    run_warroom_prediction_data_age_severity_operator_action_guidance_diagnostic,
)

DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q25H_WARROOM_PREDICTION_DATA_AGE_SEVERITY_OPERATOR_ACTION_GUIDANCE_2026-06-30.md"
PANEL = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/latest_prediction_warroom_read_model_display_panel.py"


def test_q25h_doc_markers() -> None:
    text = DOC.read_text(encoding="utf-8-sig")
    for marker in (
        "ps_q25h_warroom_prediction_data_age_severity_operator_action_guidance=true",
        "prediction_operator_action_guidance_added=true",
        "operator_visible_action_guidance=true",
        "operator_action_severity_visible=true",
        "prediction_tactical_readiness_visible=true",
        "ignore_live_tactical_horizons_visible=true",
        "context_only_horizons_visible=true",
        "wait_for_new_prediction_artifact_visible=true",
        "do_not_confuse_ui_heartbeat_with_prediction_update_visible=true",
        "producer_cadence_changed=false",
        "scheduler_action_changed=false",
        "autotrade_trigger_allowed=false",
        "broker_private_api_allowed=false",
    ):
        assert marker in text, marker


def test_q25h_diagnostic_ready() -> None:
    result = run_warroom_prediction_data_age_severity_operator_action_guidance_diagnostic()
    assert result["ok"] is True
    assert result["ready"] is True, result["blockers"]
    assert result["blockers"] == []
    fresh = result["fresh_guidance"]
    stale = result["stale_guidance"]
    panel_packet = result["panel_packet"]
    assert fresh["operator_action_guidance_version"] == "prediction_warroom.prediction_data_age_severity_operator_action_guidance.ps_q25h.v1"
    assert fresh["operator_action_severity"] == "ok"
    assert stale["operator_action_severity"] == "critical"
    assert stale["prediction_tactical_readiness"] == "tactical_predictions_not_ready"
    assert "15s" in stale["ignore_live_tactical_horizons"]
    assert stale["wait_for_new_prediction_artifact"] is True
    assert panel_packet["operator_visible_action_guidance"] is True
    assert panel_packet["operator_action_severity"] == "critical"
    safety = result["safety"]
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


def test_q25h_panel_safe_and_render_markers() -> None:
    text = PANEL.read_text(encoding="utf-8")
    for marker in (
        "WARROOM_PREDICTION_OPERATOR_ACTION_GUIDANCE_VERSION",
        "latest_prediction_warroom_operator_action_guidance_packet",
        "_render_prediction_operator_action_guidance",
        "operator_action_severity",
        "prediction_tactical_readiness",
        "wait_for_new_prediction_artifact",
    ):
        assert marker in text, marker
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
    test_q25h_doc_markers()
    test_q25h_diagnostic_ready()
    test_q25h_panel_safe_and_render_markers()
    print(json.dumps({"ok": True}, ensure_ascii=False))
