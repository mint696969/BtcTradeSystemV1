# path: ./tools/test_phase4a_prediction_system_ps_q23r_closeout_steady_state_guard_sync.py
# desc: Focused pytest guard for PS-Q23R closeout and steady-state guard sync.

from __future__ import annotations

import json
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "btcts_next" / "src"
for candidate in (REPO_ROOT, SRC_ROOT):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

from tools.diagnose_phase4a_prediction_system_ps_q23r_closeout_steady_state_guard_sync import (  # noqa: E402
    DIAGNOSTIC_VERSION,
    EXPECTED_FOCUS,
    EXPECTED_GATE,
    EXPECTED_SLICE,
    run_ps_q23r_closeout_steady_state_guard_sync,
)

SPEC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q23R_CLOSEOUT_AND_STEADY_STATE_GUARD_SYNC_2026-06-29.md"
DIAG = REPO_ROOT / "tools/diagnose_phase4a_prediction_system_ps_q23r_closeout_steady_state_guard_sync.py"


def test_spec_declares_closeout_guard_contract() -> None:
    text = SPEC.read_text(encoding="utf-8-sig")
    for marker in (
        "ps_q23r_closeout_and_steady_state_guard_sync=true",
        f"canonical_reentry={EXPECTED_GATE}",
        f"room_current_focus={EXPECTED_FOCUS}",
        "legacy_latest_compact_after_scheduled_tick=true",
        "legacy_latest_compact_record_count=24",
        "sidecar_forecast_records_full_count=110",
        "latest_manifest_full_sidecars_retained=true",
        "manifest_first_reader_distributed=true",
        "legacy_fallback_ready=true",
        "work_policy_one_shot_patch_runner=true",
        "scheduler_action_changed=false",
        "runtime_artifact_write_changed=false",
        "broker_autotrade=false",
    ):
        assert marker in text, marker


def test_live_room_and_artifact_closeout_ready() -> None:
    result = run_ps_q23r_closeout_steady_state_guard_sync()
    assert result["ok"] is True
    assert result["diagnostic_version"] == DIAGNOSTIC_VERSION
    assert result["ready"] is True, result["blockers"]
    assert result["blockers"] == []
    assert result["q23r_non_dirty_blockers"] == []
    room = result["room"]
    assert room["status_marker_present"] is True
    assert room["focus_current_focus"] == EXPECTED_FOCUS
    assert room["focus_latest_slice"] == EXPECTED_SLICE
    assert room["state_current_gate"] == EXPECTED_GATE
    assert room["state_latest_completed_slice"] == EXPECTED_SLICE
    assert room["work_policy_default_method"] == "one_shot_patch_runner"
    assert room["handoff_exists"] is True
    artifact = result["artifact_summary"]
    assert artifact["legacy_compact_record_count"] == 24
    assert artifact["legacy_original_record_count"] == 110
    assert artifact["manifest_record_count"] == 110
    assert artifact["forecast_records_line_count"] == 110
    assert artifact["manifest_first_source_artifact_mode"] == "distributed"
    assert artifact["legacy_fallback_ready"] is True
    safety = result["safety"]
    assert safety["read_only_diagnostic"] is True
    assert safety["latest_prediction_artifact_written"] is False
    assert safety["status_artifact_written"] is False
    assert safety["latest_manifest_written"] is False
    assert safety["run_sidecars_written"] is False
    assert safety["runtime_artifact_write_enabled"] is False
    assert safety["scheduler_action_changed"] is False
    assert safety["scheduler_enabled_by_this_tool"] is False
    assert safety["trigger_added"] is False
    assert safety["broker_private_api_allowed"] is False
    assert safety["autotrade_trigger_allowed"] is False
    assert safety["would_send_to_broker"] is False


def test_diagnostic_is_no_write_no_scheduler_no_broker() -> None:
    text = DIAG.read_text(encoding="utf-8")
    for forbidden in (
        "Set-ScheduledTask",
        "Enable-ScheduledTask",
        "Disable-ScheduledTask",
        "Register-ScheduledTask",
        "New-ScheduledTaskTrigger",
        "send_order(",
        "place_order(",
        ".write_text(",
        ".write_bytes(",
        "os.replace",
        "shutil.copy2",
        "Copy-Item",
    ):
        assert forbidden not in text, forbidden


if __name__ == "__main__":
    test_spec_declares_closeout_guard_contract()
    test_live_room_and_artifact_closeout_ready()
    test_diagnostic_is_no_write_no_scheduler_no_broker()
    print(json.dumps({"ok": True}, ensure_ascii=False))
