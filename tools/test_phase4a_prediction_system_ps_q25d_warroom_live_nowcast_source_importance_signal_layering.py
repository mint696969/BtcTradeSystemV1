# path: ./tools/test_phase4a_prediction_system_ps_q25d_warroom_live_nowcast_source_importance_signal_layering.py
# desc: Focused pytest guard for PS-Q25D WarRoom Live Nowcast source importance and signal layering.

from __future__ import annotations

import json
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "btcts_next" / "src"
for candidate in (REPO_ROOT, SRC_ROOT):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

from tools.diagnose_phase4a_prediction_system_ps_q25d_warroom_live_nowcast_source_importance_signal_layering import (  # noqa: E402
    run_warroom_live_nowcast_source_importance_signal_layering_diagnostic,
)

DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q25D_WARROOM_LIVE_NOWCAST_SOURCE_IMPORTANCE_SIGNAL_LAYERING_2026-06-30.md"
PANEL = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/warroom_live_market_nowcast_panel.py"


def test_q25d_doc_markers() -> None:
    text = DOC.read_text(encoding="utf-8-sig")
    for marker in (
        "ps_q25d_warroom_live_nowcast_source_importance_signal_layering=true",
        "warroom_live_nowcast_source_layering_added=true",
        "source_importance_rows_visible=true",
        "source_layer_summary_rows_visible=true",
        "prediction_input_gate_visible=true",
        "operator_read_order_visible=true",
        "current_state_not_prediction=true",
        "foundation_integrity_layer_supported=true",
        "microstructure_now_layer_supported=true",
        "trade_flow_now_layer_supported=true",
        "operational_pressure_layer_supported=true",
        "prediction_input_gate_layer_supported=true",
        "current_nowcast_profile_supported=true",
        "tactical_5m_profile_supported=true",
        "tactical_15m_profile_supported=true",
        "scenario_30m_1h_profile_supported=true",
        "runtime_artifact_write_allowed=false",
        "scheduler_action_changed=false",
        "autotrade_trigger_allowed=false",
        "broker_private_api_allowed=false",
    ):
        assert marker in text, marker


def test_q25d_diagnostic_ready() -> None:
    result = run_warroom_live_nowcast_source_importance_signal_layering_diagnostic()
    assert result["ok"] is True
    assert result["ready"] is True, result["blockers"]
    assert result["blockers"] == []
    normal = result["normal_layering"]
    warning = result["warning_layering"]
    assert normal["source_layering_version"] == "prediction_warroom.live_nowcast_source_importance_signal_layering.ps_q25d.v1"
    assert normal["nowcast_role"] == "current_market_state_not_prediction"
    assert normal["prediction_input_gate"] == "prediction_input_foundation_usable"
    assert warning["prediction_input_gate"] == "prediction_input_foundation_caution"
    assert normal["source_importance_row_count"] >= 7
    assert "foundation_integrity" in normal["read_order"]
    assert "microstructure_now" in normal["read_order"]
    assert "trade_flow_now" in normal["read_order"]
    assert "売買指示ではありません" in normal["operator_instruction_text"]
    safety = result["safety"]
    assert safety["warroom_display_only"] is True
    assert safety["current_state_not_prediction"] is True
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


def test_q25d_panel_safe_and_render_markers() -> None:
    text = PANEL.read_text(encoding="utf-8")
    for marker in (
        "WARROOM_LIVE_NOWCAST_SOURCE_LAYERING_VERSION",
        "build_warroom_live_nowcast_source_importance_packet",
        "warroom_live_nowcast_source_layer_summary_rows",
        "_render_warroom_live_nowcast_source_layering",
        "prediction_input_gate",
        "foundation_integrity",
        "tactical_5m",
        "scenario_30m_1h",
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
    test_q25d_doc_markers()
    test_q25d_diagnostic_ready()
    test_q25d_panel_safe_and_render_markers()
    print(json.dumps({"ok": True}, ensure_ascii=False))
