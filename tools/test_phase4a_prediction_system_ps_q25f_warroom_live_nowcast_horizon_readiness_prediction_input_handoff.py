# path: ./tools/test_phase4a_prediction_system_ps_q25f_warroom_live_nowcast_horizon_readiness_prediction_input_handoff.py
# desc: Focused pytest guard for PS-Q25F WarRoom Live Nowcast horizon readiness and prediction-input handoff.

from __future__ import annotations

import json
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "btcts_next" / "src"
for candidate in (REPO_ROOT, SRC_ROOT):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

from tools.diagnose_phase4a_prediction_system_ps_q25f_warroom_live_nowcast_horizon_readiness_prediction_input_handoff import (  # noqa: E402
    run_warroom_live_nowcast_horizon_readiness_prediction_input_handoff_diagnostic,
)

DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q25F_WARROOM_LIVE_NOWCAST_HORIZON_READINESS_PREDICTION_INPUT_HANDOFF_2026-06-30.md"
PANEL = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/warroom_live_market_nowcast_panel.py"


def test_q25f_doc_markers() -> None:
    text = DOC.read_text(encoding="utf-8-sig")
    for marker in (
        "ps_q25f_warroom_live_nowcast_horizon_readiness_prediction_input_handoff=true",
        "warroom_live_nowcast_horizon_readiness_added=true",
        "horizon_readiness_rows_visible=true",
        "overall_horizon_readiness_visible=true",
        "prediction_input_handoff_visible=true",
        "horizon_5m_supported=true",
        "horizon_15m_supported=true",
        "horizon_30m_supported=true",
        "horizon_1h_supported=true",
        "current_state_not_prediction=true",
        "producer_cadence_changed=false",
        "scheduler_action_changed=false",
        "autotrade_trigger_allowed=false",
        "broker_private_api_allowed=false",
    ):
        assert marker in text, marker


def test_q25f_diagnostic_ready() -> None:
    result = run_warroom_live_nowcast_horizon_readiness_prediction_input_handoff_diagnostic()
    assert result["ok"] is True
    assert result["ready"] is True, result["blockers"]
    assert result["blockers"] == []
    normal = result["normal_readiness"]
    warning = result["warning_readiness"]
    critical = result["critical_readiness"]
    assert normal["horizon_readiness_version"] == "prediction_warroom.live_nowcast_horizon_readiness_prediction_input_handoff.ps_q25f.v1"
    assert normal["nowcast_role"] == "current_market_state_not_prediction"
    assert normal["overall_horizon_readiness"] == "all_horizons_ready"
    assert warning["overall_horizon_readiness"] in {"horizons_read_with_caution", "longer_horizons_context_only", "horizons_not_ready"}
    assert critical["overall_horizon_readiness"] == "horizons_not_ready"
    assert len(normal["horizon_readiness_rows"]) == 4
    horizons = {row["horizon"] for row in normal["horizon_readiness_rows"]}
    assert horizons == {"5m", "15m", "30m", "1h"}
    safety = result["safety"]
    assert safety["warroom_display_only"] is True
    assert safety["current_state_not_prediction"] is True
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


def test_q25f_panel_safe_and_render_markers() -> None:
    text = PANEL.read_text(encoding="utf-8")
    for marker in (
        "WARROOM_LIVE_NOWCAST_HORIZON_READINESS_VERSION",
        "_HORIZON_READINESS_CONFIG",
        "build_warroom_live_nowcast_horizon_readiness_packet",
        "warroom_live_nowcast_horizon_readiness_summary_rows",
        "_render_warroom_live_nowcast_horizon_readiness",
        "overall_horizon_readiness",
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
    test_q25f_doc_markers()
    test_q25f_diagnostic_ready()
    test_q25f_panel_safe_and_render_markers()
    print(json.dumps({"ok": True}, ensure_ascii=False))
