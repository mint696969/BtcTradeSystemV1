# path: ./tools/test_phase4a_prediction_system_ps_q25s_warroom_prediction_single_producer_60s_implementation_planning.py
# desc: Focused pytest guard for PS-Q25S WarRoom prediction single producer 60s implementation planning.

from __future__ import annotations

import json
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.diagnose_phase4a_prediction_system_ps_q25s_warroom_prediction_single_producer_60s_implementation_planning import run_warroom_prediction_single_producer_60s_implementation_planning_diagnostic  # noqa: E402

DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q25S_WARROOM_PREDICTION_SINGLE_PRODUCER_60S_IMPLEMENTATION_PLANNING_2026-06-30.md"


def test_q25s_doc_markers() -> None:
    text = DOC.read_text(encoding="utf-8-sig")
    for marker in ("ps_q25s_warroom_prediction_single_producer_60s_implementation_planning=true", "cadence_option_selected=true", "selected_option_id=single_producer_60s_candidate", "selected_target_cadence_sec=60", "implementation_planning_only=true", "implementation_allowed_by_this_packet=false", "must_stop_before_code_or_scheduler_change=true", "production_code_changed=false", "producer_cadence_changed=false", "scheduler_action_changed=false", "broker_private_api_allowed=false"):
        assert marker in text, marker


def test_q25s_diagnostic_ready() -> None:
    result = run_warroom_prediction_single_producer_60s_implementation_planning_diagnostic()
    assert result["ok"] is True
    assert result["ready"] is True, result["blockers"]
    assert result["blockers"] == []
    packet = result["packet"]
    assert packet["q25m_gate_token_received"] is True
    assert packet["gate_token_matches_expected"] is True
    assert packet["cadence_option_selected"] is True
    assert packet["selected_option_id"] == "single_producer_60s_candidate"
    assert packet["selected_option_family"] == "single_producer"
    assert packet["selected_target_cadence_sec"] == 60
    assert packet["implementation_planning_only"] is True
    assert packet["implementation_plan_added"] is True
    assert packet["implementation_allowed_by_this_packet"] is False
    assert packet["must_stop_before_code_or_scheduler_change"] is True
    assert packet["requires_next_slice_for_disabled_implementation_preflight"] is True
    guards = packet["future_guard_conditions"]
    assert guards["no_overlap_runs"] is True
    assert guards["default_enabled"] is False
    assert guards["scheduler_enabled_initially"] is False
    assert guards["producer_enabled_initially"] is False
    assert guards["runtime_artifact_write_initially"] is False
    assert guards["status_artifact_write_initially"] is False
    assert guards["warroom_ui_trigger"] is False
    safety = result["safety"]
    assert safety["production_code_changed"] is False
    assert safety["implementation_allowed_by_this_packet"] is False
    for key in ("producer_cadence_changed", "scheduler_action_changed", "scheduler_enabled", "producer_enabled", "runtime_artifact_write_allowed", "status_artifact_write_allowed", "prediction_artifact_write_allowed", "view_artifact_write_allowed", "latest_manifest_written", "run_sidecars_written", "autotrade_trigger_allowed", "broker_private_api_allowed", "ledger_append_allowed", "mode_apply_allowed", "parameter_apply_allowed", "would_send_to_broker"):
        assert safety[key] is False


if __name__ == "__main__":
    test_q25s_doc_markers()
    test_q25s_diagnostic_ready()
    print(json.dumps({"ok": True}, ensure_ascii=False))
