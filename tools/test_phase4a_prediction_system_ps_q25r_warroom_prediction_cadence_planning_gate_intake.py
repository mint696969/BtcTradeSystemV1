# path: ./tools/test_phase4a_prediction_system_ps_q25r_warroom_prediction_cadence_planning_gate_intake.py
# desc: Focused pytest guard for PS-Q25R WarRoom prediction cadence planning gate intake.

from __future__ import annotations

import json
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.diagnose_phase4a_prediction_system_ps_q25r_warroom_prediction_cadence_planning_gate_intake import run_warroom_prediction_cadence_planning_gate_intake_diagnostic  # noqa: E402

DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q25R_WARROOM_PREDICTION_CADENCE_PLANNING_GATE_INTAKE_2026-06-30.md"


def test_q25r_doc_markers() -> None:
    text = DOC.read_text(encoding="utf-8-sig")
    for marker in ("ps_q25r_warroom_prediction_cadence_planning_gate_intake=true", "q25m_gate_token_received=true", "planning_intake_only=true", "cadence_option_selected=false", "selected_option_id=unselected", "implementation_allowed_by_this_packet=false", "must_stop_before_producer_or_scheduler_change=true", "production_code_changed=false", "producer_cadence_changed=false", "scheduler_action_changed=false", "broker_private_api_allowed=false"):
        assert marker in text, marker


def test_q25r_diagnostic_ready() -> None:
    result = run_warroom_prediction_cadence_planning_gate_intake_diagnostic()
    assert result["ok"] is True
    assert result["ready"] is True, result["blockers"]
    assert result["blockers"] == []
    packet = result["packet"]
    assert packet["q25m_gate_token_received"] is True
    assert packet["gate_token_matches_expected"] is True
    assert packet["planning_intake_only"] is True
    assert packet["implementation_planning_lane_opened"] is True
    assert packet["cadence_option_selected"] is False
    assert packet["selected_option_id"] == "unselected"
    assert packet["option_selection_required_before_implementation_plan"] is True
    assert len(packet["available_options"]) == 4
    assert packet["implementation_allowed_by_this_packet"] is False
    assert packet["must_stop_before_producer_or_scheduler_change"] is True
    safety = result["safety"]
    assert safety["production_code_changed"] is False
    assert safety["implementation_allowed_by_this_packet"] is False
    for key in ("producer_cadence_changed", "scheduler_action_changed", "scheduler_enabled", "producer_enabled", "runtime_artifact_write_allowed", "status_artifact_write_allowed", "prediction_artifact_write_allowed", "view_artifact_write_allowed", "latest_manifest_written", "run_sidecars_written", "autotrade_trigger_allowed", "broker_private_api_allowed", "ledger_append_allowed", "mode_apply_allowed", "parameter_apply_allowed", "would_send_to_broker"):
        assert safety[key] is False


if __name__ == "__main__":
    test_q25r_doc_markers()
    test_q25r_diagnostic_ready()
    print(json.dumps({"ok": True}, ensure_ascii=False))
