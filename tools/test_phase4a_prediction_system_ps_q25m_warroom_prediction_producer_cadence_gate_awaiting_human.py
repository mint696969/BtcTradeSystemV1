# path: ./tools/test_phase4a_prediction_system_ps_q25m_warroom_prediction_producer_cadence_gate_awaiting_human.py
# desc: Focused pytest guard for PS-Q25M WarRoom prediction producer cadence gate awaiting human decision.

from __future__ import annotations

import json
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "btcts_next" / "src"
for candidate in (REPO_ROOT, SRC_ROOT):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

from tools.diagnose_phase4a_prediction_system_ps_q25m_warroom_prediction_producer_cadence_gate_awaiting_human import run_warroom_prediction_producer_cadence_gate_awaiting_human_diagnostic  # noqa: E402

DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q25M_WARROOM_PREDICTION_PRODUCER_CADENCE_GATE_AWAITING_HUMAN_2026-06-30.md"
CONTRACT = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_non_ui_scheduled_producer_contract.py"


def test_q25m_doc_markers() -> None:
    text = DOC.read_text(encoding="utf-8-sig")
    for marker in ("ps_q25m_warroom_prediction_producer_cadence_gate_awaiting_human=true", "cadence_gate_awaiting_human_packet_added=true", "gate_marker_only=true", "human_decision_recorded=false", "implementation_allowed_by_this_packet=false", "must_stop_before_implementation=true", "producer_cadence_changed=false", "scheduler_action_changed=false", "broker_private_api_allowed=false"):
        assert marker in text, marker


def test_q25m_diagnostic_ready() -> None:
    result = run_warroom_prediction_producer_cadence_gate_awaiting_human_diagnostic()
    assert result["ok"] is True
    assert result["ready"] is True, result["blockers"]
    assert result["blockers"] == []
    packet = result["default_packet"]
    assert packet["cadence_gate_awaiting_human_version"] == "prediction_warroom.producer_cadence_gate_awaiting_human.ps_q25m.v1"
    assert packet["gate_state"] == "awaiting_human_cadence_gate_decision"
    assert packet["human_decision_recorded"] is False
    assert packet["implementation_allowed_by_this_packet"] is False
    assert packet["must_stop_before_implementation"] is True
    assert result["safe_default_packet"]["gate_state"] == "safe_default_selected_no_change"
    assert result["gated_intent_packet"]["gate_state"] == "human_gate_intent_detected_separate_implementation_slice_required"
    assert result["implementation_request_packet"]["implementation_allowed_by_this_packet"] is False
    safety = result["safety"]
    assert safety["planning_only"] is True
    assert safety["gate_marker_only"] is True
    assert safety["decision_packet_only"] is True
    for key in ("human_decision_recorded", "implementation_allowed_by_this_packet", "producer_cadence_changed", "scheduler_action_changed", "scheduler_enabled", "producer_enabled", "runtime_artifact_write_allowed", "status_artifact_write_allowed", "prediction_artifact_write_allowed", "view_artifact_write_allowed", "latest_manifest_written", "run_sidecars_written", "autotrade_trigger_allowed", "broker_private_api_allowed", "ledger_append_allowed", "mode_apply_allowed", "parameter_apply_allowed", "would_send_to_broker"):
        assert safety[key] is False


def test_q25m_contract_safe_and_markers() -> None:
    text = CONTRACT.read_text(encoding="utf-8-sig")
    for marker in ("PREDICTION_WARROOM_PRODUCER_CADENCE_GATE_AWAITING_HUMAN_VERSION", "PREDICTION_WARROOM_PRODUCER_CADENCE_GATE_DECISION_TOKEN", "build_prediction_warroom_producer_cadence_gate_awaiting_human_packet", "must_stop_before_implementation", "implementation_allowed_by_this_packet"):
        assert marker in text, marker
    for forbidden in ("Set-ScheduledTask", "Enable-ScheduledTask", "Disable-ScheduledTask", "Register-ScheduledTask", "New-ScheduledTaskTrigger", "append_decision_jsonl", "run_shadow_decision_from_snapshot", "submit_mode_change_command_request", "validate_and_append_command", "send_order(", "place_order(", "create_order(", ".write_text(", ".write_bytes(", "os.replace", "shutil.copy2"):
        assert forbidden not in text, forbidden


if __name__ == "__main__":
    test_q25m_doc_markers()
    test_q25m_diagnostic_ready()
    test_q25m_contract_safe_and_markers()
    print(json.dumps({"ok": True}, ensure_ascii=False))
