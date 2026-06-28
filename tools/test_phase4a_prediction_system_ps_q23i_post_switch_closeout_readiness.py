# path: ./tools/test_phase4a_prediction_system_ps_q23i_post_switch_closeout_readiness.py
# desc: Focused guard for PS-Q23I post-switch closeout/readiness diagnostic.

from __future__ import annotations

import json
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.diagnose_phase4a_prediction_system_ps_q23g_scheduler_sidecar_action_plan_no_write import (  # noqa: E402
    SIDECAR_CONFIRMATION_FLAG,
    SIDECAR_ENABLE_FLAG,
    candidate_silent_launcher_sidecar_args,
    expected_silent_launcher_args,
)
from tools.diagnose_phase4a_prediction_system_ps_q23i_post_switch_closeout_readiness import (  # noqa: E402
    DIAGNOSTIC_VERSION,
    ROLLBACK_CONFIRMATION_CANDIDATE,
    build_post_switch_closeout,
)
from tools.run_phase4a_prediction_system_ps_q21w_register_disabled_scheduler_once import TASK_NAME, TASK_PATH  # noqa: E402
from tools.run_phase4a_prediction_system_ps_q23b_gated_dual_write_sidecars_once import REQUIRED_CONFIRMATION as REQUIRED_DISTRIBUTED_SIDECAR_CONFIRMATION  # noqa: E402

SPEC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q23I_POST_SWITCH_CLOSEOUT_READINESS_2026-06-28.md"
TOOL = REPO_ROOT / "tools/diagnose_phase4a_prediction_system_ps_q23i_post_switch_closeout_readiness.py"


def _task(args: str | None = None) -> dict:
    return {
        "ok": True,
        "task_exists": True,
        "task_name": TASK_NAME,
        "task_path": TASK_PATH,
        "state": "Ready",
        "action_execute": r"C:\BtcTradeSystem\.venv\Scripts\pythonw.exe",
        "action_arguments": args or candidate_silent_launcher_sidecar_args(),
        "trigger_count": 1,
    }


def _manifest() -> dict:
    return {
        "generated_at": "2026-06-28T15:15:38Z",
        "latest_manifest_written_at": "2026-06-28T15:15:41Z",
        "record_count": 110,
        "run_dir": "prediction/runs/2026-06-28/151538_generated_at_2026-06-28T15_15_38Z",
        "legacy_latest_retained": True,
        "legacy_latest_modified": False,
        "status_artifact_written": False,
    }


def _q23e(mode: str = "distributed", stale: bool = False) -> dict:
    return {
        "ok": True,
        "source_artifact_mode": mode,
        "selected_generated_at": "2026-06-28T15:15:38Z",
        "selected_record_count": 110,
        "distributed_reader_ready": True,
        "distributed_stale_vs_legacy": stale,
        "legacy_fallback_ready": True,
        "read_model": {"freshness_state": "fresh", "record_count": 110},
    }


def test_spec_declares_read_only_closeout_contract() -> None:
    text = SPEC.read_text(encoding="utf-8-sig")
    for marker in (
        "ps_q23i_post_switch_closeout_readiness=true",
        "read_only_closeout=true",
        "scheduled_sidecar_dual_write_observed=true",
        "rollback_plan_only=true",
        "reader_default_change_ready_check_only=true",
        "scheduler_action_changed_by_this_tool=false",
        "broker_autotrade=false",
    ):
        assert marker in text, marker


def test_closeout_ready_with_sidecar_scheduler_and_distributed_reader() -> None:
    result = build_post_switch_closeout(repo_status_short="", scheduler_task=_task(), latest_manifest=_manifest(), q23e=_q23e())
    assert result["diagnostic_version"] == DIAGNOSTIC_VERSION
    assert result["post_switch_closeout_ready"] is True
    assert result["reader_default_change_preflight_ready"] is True
    assert result["rollback_plan_ready"] is True
    assert result["blockers"] == []
    assert result["scheduled_sidecar_dual_write_enabled_observed"] is True
    assert result["trigger_count"] == 1
    assert result["rollback_candidate_action_arguments"] == expected_silent_launcher_args()
    assert result["rollback_confirmation_candidate"] == ROLLBACK_CONFIRMATION_CANDIDATE
    assert result["q23e"]["source_artifact_mode"] == "distributed"
    assert result["q23e"]["distributed_stale_vs_legacy"] is False
    assert result["scheduler_action_changed_by_this_tool"] is False
    assert result["rollback_executed"] is False
    assert result["ui_default_call_path_changed"] is False
    assert result["latest_manifest_written"] is False
    assert result["run_sidecars_written"] is False
    assert result["would_send_to_broker"] is False


def test_closeout_blocks_when_reader_falls_back_or_sidecar_flags_absent() -> None:
    result = build_post_switch_closeout(
        repo_status_short="",
        scheduler_task=_task(args=expected_silent_launcher_args()),
        latest_manifest=_manifest(),
        q23e=_q23e(mode="legacy_fallback", stale=True),
    )
    assert result["post_switch_closeout_ready"] is False
    assert "scheduler_action_must_include_sidecar_flags" in result["blockers"]
    assert "q23e_distributed_must_not_be_stale_vs_legacy" in result["blockers"]
    assert "q23e_source_artifact_mode_must_be_distributed" in result["blockers"]
    assert result["scheduler_action_changed_by_this_tool"] is False


def test_candidate_args_still_include_expected_sidecar_flags() -> None:
    args = candidate_silent_launcher_sidecar_args()
    assert SIDECAR_ENABLE_FLAG in args
    assert SIDECAR_CONFIRMATION_FLAG in args
    assert REQUIRED_DISTRIBUTED_SIDECAR_CONFIRMATION in args


def test_tool_contains_no_mutation_or_broker_code() -> None:
    text = TOOL.read_text(encoding="utf-8")
    for forbidden in (
        "Set-ScheduledTask",
        "Enable-ScheduledTask",
        "Disable-ScheduledTask",
        "Register-ScheduledTask",
        "New-ScheduledTaskTrigger",
        "Start-ScheduledTask",
        "send_order(",
        "place_order(",
        ".write_text(",
        ".write_bytes(",
        "os.replace",
    ):
        assert forbidden not in text, forbidden
    assert "rollback_candidate_action_arguments" in text
    assert "reader_default_change_preflight_ready" in text


if __name__ == "__main__":
    test_spec_declares_read_only_closeout_contract()
    test_closeout_ready_with_sidecar_scheduler_and_distributed_reader()
    test_closeout_blocks_when_reader_falls_back_or_sidecar_flags_absent()
    test_candidate_args_still_include_expected_sidecar_flags()
    test_tool_contains_no_mutation_or_broker_code()
    print(json.dumps({"ok": True}))
