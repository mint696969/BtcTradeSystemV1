# path: ./tools/test_phase4a_prediction_system_ps_q25g_warroom_prediction_artifact_horizon_freshness_expiry_visibility.py
# desc: Focused pytest guard for PS-Q25G WarRoom prediction artifact horizon freshness/expiry visibility.

from __future__ import annotations

import json
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "btcts_next" / "src"
for candidate in (REPO_ROOT, SRC_ROOT):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

from tools.diagnose_phase4a_prediction_system_ps_q25g_warroom_prediction_artifact_horizon_freshness_expiry_visibility import (  # noqa: E402
    run_warroom_prediction_artifact_horizon_freshness_expiry_visibility_diagnostic,
)

DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q25G_WARROOM_PREDICTION_ARTIFACT_HORIZON_FRESHNESS_EXPIRY_VISIBILITY_2026-06-30.md"
PANEL = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/latest_prediction_warroom_read_model_display_panel.py"


def test_q25g_doc_markers() -> None:
    text = DOC.read_text(encoding="utf-8-sig")
    for marker in (
        "ps_q25g_warroom_prediction_artifact_horizon_freshness_expiry_visibility=true",
        "prediction_horizon_expiry_visibility_added=true",
        "operator_visible_horizon_expiry=true",
        "horizon_expiry_rows_visible=true",
        "overall_horizon_expiry_state_visible=true",
        "short_horizon_expired_or_stale_visible=true",
        "horizon_15s_supported=true",
        "horizon_60s_supported=true",
        "horizon_300s_supported=true",
        "horizon_900s_supported=true",
        "producer_cadence_changed=false",
        "scheduler_action_changed=false",
        "autotrade_trigger_allowed=false",
        "broker_private_api_allowed=false",
    ):
        assert marker in text, marker


def test_q25g_diagnostic_ready() -> None:
    result = run_warroom_prediction_artifact_horizon_freshness_expiry_visibility_diagnostic()
    assert result["ok"] is True
    assert result["ready"] is True, result["blockers"]
    assert result["blockers"] == []
    fresh = result["fresh_expiry"]
    stale = result["stale_expiry"]
    panel_packet = result["panel_packet"]
    assert fresh["horizon_expiry_version"] == "prediction_warroom.prediction_artifact_horizon_freshness_expiry.ps_q25g.v1"
    assert fresh["overall_horizon_expiry_state"] == "all_selected_horizons_within_ttl"
    assert stale["short_horizon_expired_or_stale"] is True
    assert len(stale["horizon_expiry_rows"]) == 4
    assert panel_packet["operator_visible_horizon_expiry"] is True
    assert panel_packet["short_horizon_expired_or_stale"] is True
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


def test_q25g_panel_safe_and_render_markers() -> None:
    text = PANEL.read_text(encoding="utf-8")
    for marker in (
        "WARROOM_PREDICTION_HORIZON_EXPIRY_VERSION",
        "latest_prediction_warroom_horizon_expiry_rows",
        "latest_prediction_warroom_horizon_expiry_packet",
        "_render_prediction_horizon_expiry",
        "overall_horizon_expiry_state",
        "short_horizon_expired_or_stale",
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
    test_q25g_doc_markers()
    test_q25g_diagnostic_ready()
    test_q25g_panel_safe_and_render_markers()
    print(json.dumps({"ok": True}, ensure_ascii=False))
