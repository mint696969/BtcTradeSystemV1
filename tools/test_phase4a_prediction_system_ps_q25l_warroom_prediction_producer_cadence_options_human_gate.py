# path: ./tools/test_phase4a_prediction_system_ps_q25l_warroom_prediction_producer_cadence_options_human_gate.py
# desc: Focused pytest guard for PS-Q25L WarRoom prediction producer cadence options human-gate decision packet.

from __future__ import annotations

import json
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "btcts_next" / "src"
for candidate in (REPO_ROOT, SRC_ROOT):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

from tools.diagnose_phase4a_prediction_system_ps_q25l_warroom_prediction_producer_cadence_options_human_gate import run_warroom_prediction_producer_cadence_options_human_gate_diagnostic  # noqa: E402

DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q25L_WARROOM_PREDICTION_PRODUCER_CADENCE_OPTIONS_HUMAN_GATE_2026-06-30.md"
CONTRACT = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_non_ui_scheduled_producer_contract.py"


def test_q25l_doc_markers() -> None:
    text = DOC.read_text(encoding="utf-8-sig")
    for marker in ("ps_q25l_warroom_prediction_producer_cadence_options_human_gate=true", "cadence_option_decision_packet_added=true", "planning_only=true", "decision_packet_only=true", "human_gate_required_before_any_change=true", "producer_cadence_changed=false", "scheduler_action_changed=false", "autotrade_trigger_allowed=false", "broker_private_api_allowed=false"):
        assert marker in text, marker


def test_q25l_diagnostic_ready() -> None:
    result = run_warroom_prediction_producer_cadence_options_human_gate_diagnostic()
    assert result["ok"] is True
    assert result["ready"] is True, result["blockers"]
    assert result["blockers"] == []
    packet = result["packet"]
    assert packet["cadence_option_decision_version"] == "prediction_warroom.producer_cadence_options_human_gate.ps_q25l.v1"
    assert packet["decision_state"] == "cadence_options_ready_human_gate_decision_required"
    assert packet["option_row_count"] == 4
    assert packet["options_requiring_gate_count"] == 3
    assert packet["recommended_safe_default_option_id"] == "keep_current_300s_context_only_until_gate"
    assert result["blocked_selected_option_packet"]["decision_state"] == "blocked_or_waiting_for_explicit_human_gate"
    assert result["gated_apply_packet"]["decision_state"] == "blocked_or_waiting_for_explicit_human_gate"
    safety = result["safety"]
    assert safety["planning_only"] is True
    assert safety["decision_packet_only"] is True
    assert safety["contract_only"] is True
    for key in ("producer_cadence_changed", "scheduler_action_changed", "scheduler_enabled", "producer_enabled", "runtime_artifact_write_allowed", "status_artifact_write_allowed", "prediction_artifact_write_allowed", "view_artifact_write_allowed", "latest_manifest_written", "run_sidecars_written", "autotrade_trigger_allowed", "broker_private_api_allowed", "ledger_append_allowed", "mode_apply_allowed", "parameter_apply_allowed", "would_send_to_broker"):
        assert safety[key] is False


def test_q25l_contract_safe_and_markers() -> None:
    text = CONTRACT.read_text(encoding="utf-8-sig")
    for marker in ("PREDICTION_WARROOM_PRODUCER_CADENCE_OPTION_DECISION_VERSION", "CADENCE_OPTION_DECISION_CANDIDATES", "build_prediction_warroom_producer_cadence_option_decision_packet", "keep_current_300s_context_only_until_gate", "single_producer_60s_candidate", "producer_cadence_changed"):
        assert marker in text, marker
    for forbidden in ("Set-ScheduledTask", "Enable-ScheduledTask", "Disable-ScheduledTask", "Register-ScheduledTask", "New-ScheduledTaskTrigger", "append_decision_jsonl", "run_shadow_decision_from_snapshot", "submit_mode_change_command_request", "validate_and_append_command", "send_order(", "place_order(", "create_order(", ".write_text(", ".write_bytes(", "os.replace", "shutil.copy2"):
        assert forbidden not in text, forbidden


if __name__ == "__main__":
    test_q25l_doc_markers()
    test_q25l_diagnostic_ready()
    test_q25l_contract_safe_and_markers()
    print(json.dumps({"ok": True}, ensure_ascii=False))
