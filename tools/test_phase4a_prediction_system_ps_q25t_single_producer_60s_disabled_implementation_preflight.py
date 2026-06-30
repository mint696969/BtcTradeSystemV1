# path: ./tools/test_phase4a_prediction_system_ps_q25t_single_producer_60s_disabled_implementation_preflight.py
# desc: Focused pytest guard for PS-Q25T single producer 60s disabled implementation preflight.

from __future__ import annotations

import json
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.diagnose_phase4a_prediction_system_ps_q25t_single_producer_60s_disabled_implementation_preflight import run_single_producer_60s_disabled_implementation_preflight_diagnostic  # noqa: E402

DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q25T_SINGLE_PRODUCER_60S_DISABLED_IMPLEMENTATION_PREFLIGHT_2026-06-30.md"


def test_q25t_doc_markers() -> None:
    text = DOC.read_text(encoding="utf-8-sig")
    for marker in ("ps_q25t_single_producer_60s_disabled_implementation_preflight=true", "selected_option_id=single_producer_60s_candidate", "selected_target_cadence_sec=60", "disabled_implementation_preflight_added=true", "preflight_only=true", "implementation_allowed_by_this_packet=false", "production_code_changed=false", "producer_cadence_changed=false", "scheduler_action_changed=false", "scheduler_enabled=false", "manual_one_shot_run_allowed=false", "scheduler_enablement_allowed=false", "broker_private_api_allowed=false"):
        assert marker in text, marker


def test_q25t_diagnostic_ready_and_safe() -> None:
    result = run_single_producer_60s_disabled_implementation_preflight_diagnostic()
    assert result["ok"] is True
    assert result["ready"] is True, result["blockers"]
    assert result["blockers"] == []
    packet = result["packet"]
    assert packet["selected_option_id"] == "single_producer_60s_candidate"
    assert packet["selected_target_cadence_sec"] == 60
    assert packet["disabled_implementation_preflight_added"] is True
    assert packet["preflight_only"] is True
    assert packet["source_candidate_count"] == 7
    shape = packet["required_future_shape"]
    assert shape["no_overlap_runs"] is True
    assert shape["single_run_lock_required"] is True
    assert shape["on_existing_lock"] == "skip_and_report_status"
    assert shape["default_enabled"] is False
    assert shape["scheduler_enabled_initially"] is False
    assert shape["producer_enabled_initially"] is False
    assert shape["runtime_artifact_write_initially"] is False
    assert shape["status_artifact_write_initially"] is False
    assert shape["latest_prediction_artifact_write_initially"] is False
    assert shape["warroom_ui_trigger"] is False
    assert shape["manual_one_shot_requires_separate_gate"] is True
    assert shape["scheduler_enablement_requires_separate_gate"] is True
    safety = result["safety"]
    assert safety["production_code_changed"] is False
    assert safety["implementation_allowed_by_this_packet"] is False
    assert safety["manual_one_shot_run_allowed"] is False
    assert safety["scheduler_enablement_allowed"] is False
    for key in ("producer_cadence_changed", "scheduler_action_changed", "scheduler_enabled", "producer_enabled", "runtime_artifact_write_allowed", "status_artifact_write_allowed", "prediction_artifact_write_allowed", "view_artifact_write_allowed", "latest_manifest_written", "run_sidecars_written", "autotrade_trigger_allowed", "broker_private_api_allowed", "ledger_append_allowed", "mode_apply_allowed", "parameter_apply_allowed", "would_send_to_broker"):
        assert safety[key] is False


if __name__ == "__main__":
    test_q25t_doc_markers()
    test_q25t_diagnostic_ready_and_safe()
    print(json.dumps({"ok": True}, ensure_ascii=False))
